"""Evaluation utilities for the production retrieval pipeline."""
from __future__ import annotations

import json
import logging
import statistics
import time
from pathlib import Path
from typing import Any

from backend.rag.config import get_rag_settings
from backend.rag.rag_service import RAGService

logger = logging.getLogger("rag.evaluation")


class RetrievalEvaluator:
    """Evaluate semantic retrieval quality using realistic founder queries."""

    def __init__(self, service: RAGService | None = None, settings: Any | None = None) -> None:
        self.settings = settings or get_rag_settings()
        self.service = service or RAGService(settings=self.settings)

    def evaluate(self, queries: list[str] | None = None, output_dir: str | Path | None = None) -> dict[str, Any]:
        output_path = Path(output_dir or "backend/data/reports")
        output_path.mkdir(parents=True, exist_ok=True)

        query_list = queries or [
            "Which grants support AI startups?",
            "Which grants support biotechnology startups?",
            "Which schemes support prototype development?",
            "Startup India Seed Fund eligibility",
            "MeitY startup grants",
            "NIDHI PRAYAS funding",
            "BIRAC BIG grant",
            "Early-stage funding schemes",
            "Commercialization grants",
            "Incubation support",
        ]

        reports: list[dict[str, Any]] = []
        latencies: list[float] = []
        scores: list[float] = []
        chunk_counts: list[int] = []
        metadata_completeness: list[float] = []

        for query in query_list:
            result = self.service.retrieve(query=query, top_k=5)
            results = result.get("results", [])
            latencies.append(float(result.get("retrieval_time_ms", 0.0)))
            scores.append(float(results[0]["score"]) if results else 0.0)
            chunk_counts.append(len(results))
            metadata_complete = 0
            for item in results:
                metadata = item.get("metadata") or {}
                if metadata.get("grant_name") and metadata.get("organization") and metadata.get("document_type"):
                    metadata_complete += 1
            metadata_completeness.append(round(metadata_complete / max(len(results), 1), 3))

            reports.append(
                {
                    "query": query,
                    "retrieved_chunks": len(results),
                    "similarity_score": results[0]["score"] if results else None,
                    "retrieval_time_ms": result.get("retrieval_time_ms"),
                    "metadata_completeness": round(metadata_complete / max(len(results), 1), 3),
                    "source_documents": [item.get("source_document") for item in results],
                    "page_numbers": [item.get("page_number") for item in results],
                    "results": results,
                }
            )

        summary = {
            "total_queries": len(query_list),
            "average_retrieval_latency_ms": round(statistics.mean(latencies), 3) if latencies else 0.0,
            "average_similarity_score": round(statistics.mean(scores), 6) if scores else 0.0,
            "average_retrieved_chunks": round(statistics.mean(chunk_counts), 3) if chunk_counts else 0.0,
            "metadata_completeness": round(statistics.mean(metadata_completeness), 3) if metadata_completeness else 0.0,
            "retrieval_consistency": round(statistics.mean(chunk_counts), 3) if chunk_counts else 0.0,
        }

        retriever_report_path = output_path / "retriever_report.json"
        evaluation_report_path = output_path / "evaluation_report.json"
        retriever_report_path.write_text(json.dumps(reports, indent=2, ensure_ascii=False), encoding="utf-8")
        evaluation_report_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
        logger.info("Wrote retrieval reports to %s and %s", retriever_report_path, evaluation_report_path)
        return {"retriever_report": reports, "evaluation_report": summary}
