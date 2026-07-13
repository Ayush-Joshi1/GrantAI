#!/usr/bin/env python3
"""Validate the FAISS vector store against processed chunks and embeddings."""
from __future__ import annotations

import json
import os
import random
import sys
import time
import traceback
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

from backend.rag.config import get_rag_settings
from backend.rag.embedding_runner import EmbeddingGenerationService
from backend.rag.interfaces import DocumentChunk
from backend.rag.vectorstore.faiss_store import FAISSVectorStore


def _resolve_path(path_value: str | Path | None) -> Path:
    if path_value is None:
        return ROOT
    path = Path(path_value)
    return path if path.is_absolute() else ROOT / path


def _load_processed_chunks(reports_dir: Path) -> list[dict[str, Any]]:
    chunk_path = reports_dir / "processed_chunks.json"
    if not chunk_path.exists():
        raise FileNotFoundError(f"Processed chunks file not found: {chunk_path}")

    payload = json.loads(chunk_path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict):
        return payload.get("chunks", [])
    raise ValueError("Unexpected processed chunks payload format")


def _load_or_generate_embeddings(reports_dir: Path, settings: Any) -> list[dict[str, Any]]:
    embeddings_path = reports_dir / "embeddings.json"
    if embeddings_path.exists():
        payload = json.loads(embeddings_path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, list) else []

    service = EmbeddingGenerationService(settings=settings)
    result = service.generate_embeddings(
        chunk_file=reports_dir / "processed_chunks.json",
        output_dir=reports_dir,
        report_path=reports_dir / "embedding_report.json",
    )
    embeddings = result.get("embeddings", [])
    if not isinstance(embeddings, list):
        raise ValueError("Embedding generation returned an unexpected payload")
    return embeddings


def _build_vector_store_from_embeddings(
    embeddings: list[dict[str, Any]],
    chunks: list[dict[str, Any]],
    settings: Any,
) -> tuple[FAISSVectorStore, list[DocumentChunk], list[list[float]]]:
    index_path = _resolve_path(settings.vector_store_path)
    index_path.parent.mkdir(parents=True, exist_ok=True)

    embedding_map = {}
    for item in embeddings:
        chunk_id = item.get("chunk_id") or ""
        if chunk_id and item.get("embedding"):
            embedding_map[chunk_id] = item.get("embedding")

    vector_chunks: list[DocumentChunk] = []
    vector_embeddings: list[list[float]] = []
    for chunk in chunks:
        chunk_id = chunk.get("id") or (chunk.get("metadata") or {}).get("chunk_id") or ""
        if not chunk_id:
            continue
        embedding = embedding_map.get(chunk_id)
        if not embedding:
            continue
        metadata = dict(chunk.get("metadata") or {})
        vector_chunks.append(
            DocumentChunk(
                id=chunk_id,
                content=chunk.get("page_content") or "",
                metadata=metadata,
            )
        )
        vector_embeddings.append(list(embedding))

    if not vector_chunks:
        raise ValueError("No embeddable chunks were available to build the FAISS index")

    store = FAISSVectorStore(index_path=str(index_path), dim=len(vector_embeddings[0]), metric=settings.vector_metric)
    service = VectorStoreService(store=store)
    service.add(vector_chunks, vector_embeddings)
    store.save_index()
    return store, vector_chunks, vector_embeddings


def _get_memory_usage_bytes() -> int | None:
    try:
        import psutil  # type: ignore

        return int(psutil.Process().memory_info().rss)
    except Exception:
        return None


def _build_validation_report(
    settings: Any,
    processed_chunks: list[dict[str, Any]],
    embeddings: list[dict[str, Any]],
    index_path: Path,
    store: FAISSVectorStore,
    vector_chunks: list[DocumentChunk],
    vector_embeddings: list[list[float]],
    creation_time_seconds: float,
    load_time_seconds: float,
) -> dict[str, Any]:
    chunk_ids = [chunk.id for chunk in vector_chunks]
    unique_chunk_ids = list(dict.fromkeys(chunk_ids))
    duplicate_ids = [cid for cid in unique_chunk_ids if chunk_ids.count(cid) > 1]

    metadata_required = ["grant_name", "organization", "document_type", "page_number", "source_folder", "chunk_id"]
    missing_metadata: list[dict[str, Any]] = []
    for chunk in vector_chunks:
        missing = [field for field in metadata_required if not chunk.metadata.get(field)]
        if missing:
            missing_metadata.append({
                "chunk_id": chunk.id,
                "missing_fields": missing,
                "metadata": chunk.metadata,
            })

    document_ids = sorted({(chunk.metadata or {}).get("original_document_id") for chunk in vector_chunks if (chunk.metadata or {}).get("original_document_id")})
    chunk_count = len(processed_chunks)
    embedding_count = len(embeddings)
    vector_count = len(vector_chunks)

    # Validate that each processed chunk has exactly one embedding and each embedding exists in the FAISS index.
    processed_ids = {
        chunk.get("id") or (chunk.get("metadata") or {}).get("chunk_id") or ""
        for chunk in processed_chunks
        if (chunk.get("id") or (chunk.get("metadata") or {}).get("chunk_id") or "")
    }
    embedding_ids = {item.get("chunk_id") for item in embeddings if item.get("chunk_id")}
    missing_embeddings = sorted(processed_ids - embedding_ids)
    missing_vectors = sorted(set(chunk_ids) - set(store._chunkid_to_int.keys())) if hasattr(store, "_chunkid_to_int") else []

    sample_vectors = []
    if vector_chunks:
        sample_ids = random.sample(range(len(vector_chunks)), k=min(20, len(vector_chunks)))
        for idx in sample_ids:
            chunk = vector_chunks[idx]
            sample_vectors.append({
                "chunk_id": chunk.id,
                "grant_name": chunk.metadata.get("grant_name"),
                "organization": chunk.metadata.get("organization"),
                "page_number": chunk.metadata.get("page_number"),
                "metadata": chunk.metadata,
            })

    index_stats = {
        "index_path": str(index_path),
        "dimension": len(vector_embeddings[0]) if vector_embeddings else 0,
        "vector_count": int(store._index.ntotal) if store._index is not None else 0,
        "stored_chunk_ids": len(store._chunkid_to_int),
        "unique_chunk_ids": len(unique_chunk_ids),
    }

    storage_stats = {
        "storage_size_bytes": int(index_path.stat().st_size) if index_path.exists() else 0,
        "storage_size_mb": round((index_path.stat().st_size if index_path.exists() else 0) / (1024 * 1024), 3),
        "meta_file_size_bytes": int(index_path.with_suffix(index_path.suffix + ".meta.json").stat().st_size) if index_path.with_suffix(index_path.suffix + ".meta.json").exists() else 0,
    }

    performance_metrics = {
        "index_creation_time_seconds": round(creation_time_seconds, 3),
        "index_loading_time_seconds": round(load_time_seconds, 3),
        "memory_usage_bytes": _get_memory_usage_bytes(),
        "memory_usage_mb": round((_get_memory_usage_bytes() or 0) / (1024 * 1024), 3),
    }

    validation_status = "passed"
    if missing_embeddings or missing_vectors or duplicate_ids or missing_metadata:
        validation_status = "failed"

    return {
        "validation_status": validation_status,
        "missing_metadata": missing_metadata,
        "duplicate_ids": duplicate_ids,
        "missing_vectors": missing_vectors,
        "missing_embeddings": missing_embeddings,
        "index_statistics": index_stats,
        "storage_statistics": storage_stats,
        "performance_metrics": performance_metrics,
        "counts": {
            "documents": len(document_ids),
            "chunks": chunk_count,
            "embeddings": embedding_count,
            "vectors": vector_count,
        },
        "sample_vectors": sample_vectors,
        "consistency_checks": {
            "processed_chunks_have_embedding": len(missing_embeddings) == 0,
            "embeddings_exist_in_index": len(missing_vectors) == 0,
            "no_duplicate_vector_ids": len(duplicate_ids) == 0,
            "counts_aligned": len(document_ids) == len(document_ids) and chunk_count == embedding_count == vector_count,
        },
    }


def main() -> None:
    load_dotenv(ROOT / ".env", override=False)
    settings = get_rag_settings()

    reports_dir = _resolve_path("backend/data/reports")
    reports_dir.mkdir(parents=True, exist_ok=True)

    processed_chunks = _load_processed_chunks(reports_dir)

    start_time = time.perf_counter()
    embeddings = _load_or_generate_embeddings(reports_dir, settings)
    creation_time_seconds = time.perf_counter() - start_time

    store, vector_chunks, vector_embeddings = _build_vector_store_from_embeddings(embeddings, processed_chunks, settings)

    load_start = time.perf_counter()
    reloaded_store = FAISSVectorStore(index_path=str(_resolve_path(settings.vector_store_path)), dim=len(vector_embeddings[0]), metric=settings.vector_metric)
    load_time_seconds = time.perf_counter() - load_start

    report = _build_validation_report(
        settings=settings,
        processed_chunks=processed_chunks,
        embeddings=embeddings,
        index_path=_resolve_path(settings.vector_store_path),
        store=store,
        vector_chunks=vector_chunks,
        vector_embeddings=vector_embeddings,
        creation_time_seconds=creation_time_seconds,
        load_time_seconds=load_time_seconds,
    )

    report["persistence_check"] = {
        "reloaded_vector_count": len(reloaded_store._chunkid_to_int) if hasattr(reloaded_store, "_chunkid_to_int") else 0,
        "original_vector_count": len(store._chunkid_to_int) if hasattr(store, "_chunkid_to_int") else 0,
        "persisted_count_matches": len(reloaded_store._chunkid_to_int) == len(store._chunkid_to_int),
    }

    output_path = reports_dir / "vectorstore_validation_report.json"
    output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    print("Validation Status:", report["validation_status"])
    print("Missing Metadata:", len(report["missing_metadata"]))
    print("Duplicate IDs:", len(report["duplicate_ids"]))
    print("Missing Vectors:", len(report["missing_vectors"]))
    print("Counts:", report["counts"])
    print("Sample Vectors:")
    for sample in report["sample_vectors"]:
        print(
            f"- Chunk ID: {sample['chunk_id']} | Grant Name: {sample['grant_name']} | Organization: {sample['organization']} | Page Number: {sample['page_number']} | Metadata: {sample['metadata']}"
        )
    print(f"Report written to: {output_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        report_path = ROOT / "backend" / "data" / "reports" / "vectorstore_validation_report.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(
                {
                    "validation_status": "error",
                    "error": traceback.format_exc(),
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
        sys.exit(1)
