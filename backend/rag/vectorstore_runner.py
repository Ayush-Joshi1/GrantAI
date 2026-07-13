from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path
from typing import Any

import numpy as np

from backend.rag.config import get_rag_settings
from backend.rag.interfaces import DocumentChunk
from backend.rag.logging_config import configure_rag_logging
from backend.rag.vectorstore.faiss_store import FAISSVectorStore
from backend.rag.vectorstore.service import VectorStoreService
from backend.rag.vectorstore.exceptions import VectorStoreError

logger = logging.getLogger("rag.vectorstore_runner")


class VectorStoreBuildService:
    def __init__(self, settings=None) -> None:
        self.settings = settings or get_rag_settings()
        self.index_path = Path(self.settings.vector_store_path)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)

    def build_from_embeddings(
        self,
        embeddings_file: str | Path | None = None,
        output_dir: str | Path | None = None,
    ) -> dict[str, Any]:
        configure_rag_logging()
        start_time = time.time()
        embeddings_path = Path(embeddings_file or "backend/data/reports/embeddings.json")
        output_path = Path(output_dir or "backend/data/reports")
        output_path.mkdir(parents=True, exist_ok=True)

        if not embeddings_path.exists():
            raise VectorStoreError(f"Embeddings file not found: {embeddings_path}")

        payload = json.loads(embeddings_path.read_text(encoding="utf-8"))
        chunks = []
        embeddings = []
        for item in payload:
            embedding = item.get("embedding") or []
            if not embedding:
                continue
            metadata = dict(item.get("metadata") or {})
            chunk_id = item.get("chunk_id") or metadata.get("chunk_id") or ""
            if not chunk_id:
                continue
            chunks.append(
                DocumentChunk(
                    id=chunk_id,
                    content=item.get("text") or "",
                    metadata=metadata,
                )
            )
            embeddings.append(embedding)

        if not chunks:
            raise VectorStoreError("No embeddable chunks available for FAISS indexing")

        store = FAISSVectorStore(index_path=str(self.index_path), dim=len(embeddings[0]), metric=self.settings.vector_metric)
        service = VectorStoreService(store=store)
        service.add(chunks, embeddings)
        store.save_index()

        validation = self.validate_index(store, chunks)
        report = {
            "total_vectors": len(chunks),
            "indexed_documents": len({chunk.metadata.get("original_document_id") for chunk in chunks if chunk.metadata.get("original_document_id")}),
            "embedding_dimension": len(embeddings[0]),
            "index_type": "IndexFlatIP" if self.settings.vector_metric.upper() == "IP" else "IndexFlatL2",
            "storage_size": os.path.getsize(self.index_path) if self.index_path.exists() else 0,
            "creation_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "validation": validation,
            "processing_time_seconds": round(time.time() - start_time, 3),
        }
        (output_path / "vectorstore_report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"),
        logger.info("FAISS index built with %d vectors", len(chunks))
        return {"store": store, "report": report}

    def validate_index(self, store: FAISSVectorStore, chunks: list[DocumentChunk]) -> dict[str, Any]:
        meta_ids = set(store._chunkid_to_int.keys())
        chunk_ids = {chunk.id for chunk in chunks}
        missing_chunks = sorted(chunk_ids - meta_ids)
        missing_metadata = [chunk.id for chunk in chunks if not chunk.metadata]
        duplicate_ids = len(chunk_ids) != len(chunk_ids)
        return {
            "all_chunks_present": not missing_chunks,
            "missing_chunks": missing_chunks,
            "all_vectors_have_metadata": not missing_metadata,
            "missing_metadata_chunks": missing_metadata,
            "duplicate_vector_ids": duplicate_ids,
            "original_pdf_mapping_present": all(chunk.metadata.get("original_document_id") for chunk in chunks),
        }


def build_vector_store(output_dir: str | Path | None = None) -> dict[str, Any]:
    service = VectorStoreBuildService()
    return service.build_from_embeddings(output_dir=output_dir)


if __name__ == "__main__":
    build_vector_store()
