#!/usr/bin/env python3
"""Validate the semantic retrieval layer with the configured benchmark queries."""
from __future__ import annotations

import json
import sys
import time
import traceback
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

from backend.rag.config import get_rag_settings
from backend.rag.embeddings.provider import SentenceTransformerProvider
from backend.rag.retriever.semantic_retriever import SemanticRetriever
from backend.rag.retriever.service import RetrieverService
from backend.rag.vectorstore.faiss_store import FAISSVectorStore
from backend.rag.vectorstore.service import VectorStoreService


def _load_index(settings: Any) -> tuple[FAISSVectorStore, VectorStoreService]:
    index_path = Path(settings.vector_store_path)
    index_path = index_path if index_path.is_absolute() else ROOT / index_path
    index_path.parent.mkdir(parents=True, exist_ok=True)

    store = FAISSVectorStore(index_path=str(index_path), dim=768, metric=settings.vector_metric)
    service = VectorStoreService(store=store)
    return store, service


def main() -> None:
    load_dotenv(ROOT / ".env", override=False)
    settings = get_rag_settings()

    reports_dir = ROOT / "backend" / "data" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    _, vector_service = _load_index(settings)
    embedding_provider = SentenceTransformerProvider(
        model_name=settings.embedding_model_name,
        batch_size=settings.embedding_batch_size,
        device=settings.embedding_device,
    )
    retriever = SemanticRetriever(vector_service=vector_service, embedding_provider=embedding_provider)
    service = RetrieverService(retriever=retriever)

    queries = [
        "Which grants support AI startups?",
        "Which grants are available for biotechnology startups?",
        "Startup India Seed Fund eligibility",
        "Prototype funding schemes",
        "MeitY startup grants",
        "NIDHI PRAYAS funding",
        "BIRAC BIG grant",
    ]

    results_payload: list[dict[str, Any]] = []
    for query in queries:
        started = time.perf_counter()
        raw_results = service.retrieve(query=query, top_k=5, similarity_threshold=0.0)
        latency_ms = round((time.perf_counter() - started) * 1000, 3)

        formatted_results = []
        for index, result in enumerate(raw_results, start=1):
            formatted_results.append(
                {
                    "rank": index,
                    "score": round(float(result.score), 6),
                    "chunk_id": result.chunk_id,
                    "grant_name": result.metadata.get("grant_name"),
                    "organization": result.metadata.get("organization"),
                    "page_number": result.metadata.get("page_number"),
                    "source_document": result.metadata.get("source") or result.metadata.get("filename"),
                    "metadata": result.metadata,
                    "content": result.content,
                }
            )

        results_payload.append(
            {
                "query": query,
                "retrieval_time_ms": latency_ms,
                "retrieved_documents": len({item["source_document"] for item in formatted_results if item["source_document"]}),
                "similarity_score": formatted_results[0]["score"] if formatted_results else None,
                "metadata": formatted_results[0]["metadata"] if formatted_results else {},
                "results": formatted_results,
            }
        )

    report_path = reports_dir / "retriever_report.json"
    report_path.write_text(json.dumps(results_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print("Retriever validation completed")
    for entry in results_payload:
        print(f"- Query: {entry['query']}")
        print(f"  Retrieved Documents: {entry['retrieved_documents']}")
        print(f"  Similarity Score: {entry['similarity_score']}")
        print(f"  Retrieval Time: {entry['retrieval_time_ms']} ms")
        print(f"  Metadata: {entry['metadata']}")
    print(f"Report written to: {report_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
