from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "apps" / "api"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from backend.rag.config import get_rag_settings
from src.application.services.rag_answer_service import RAGAnswerService

QUERIES = [
    "I have an AI startup in Pune. What grants may be relevant?",
    "What grants are available for biotechnology startups?",
    "I need ₹50 lakh for an MVP. Which funding schemes may be relevant?",
    "Which grants support women founders?",
    "What documents are required for Startup India Seed Fund?",
    "What are the eligibility requirements for the Startup India Seed Fund Scheme?",
    "Which schemes support technology startups?",
    "Tell me the weather in Pune tomorrow.",
]


def main() -> None:
    settings = get_rag_settings()
    service = RAGAnswerService(settings=settings)
    print("RAG diagnostic harness")
    print(f"top_k={settings.top_k}")
    print(f"similarity_threshold={settings.similarity_threshold}")
    print(f"embedding_model={settings.embedding_model_name}")
    print(f"index_path={settings.vector_store_path}")
    print(f"granite_model={os.getenv('GRANITE_MODEL_ID') or os.getenv('WATSONX_MODEL_ID') or os.getenv('MODEL_ID') or 'ibm/granite-8b-code-instruct'}")
    print("=" * 80)

    for query in QUERIES:
        retrieval_started = time.perf_counter()
        retrieval_results = service.retrieval_client.retrieve(
            query=query,
            top_k=settings.top_k,
            similarity_threshold=settings.similarity_threshold,
        )
        retrieval_elapsed = round((time.perf_counter() - retrieval_started) * 1000, 3)

        print(f"QUERY: {query}")
        print(f"retrieval_count={len(retrieval_results)}")
        print(f"retrieval_latency_ms={retrieval_elapsed}")
        print("retrieved_samples=")
        for item in retrieval_results[:3]:
            print(
                json.dumps(
                    {
                        "chunk_id": item.chunk_id,
                        "score": item.score,
                        "grant_name": item.metadata.get("grant_name"),
                        "organization": item.metadata.get("organization"),
                        "source_document": item.metadata.get("file_name") or item.metadata.get("source_document") or item.metadata.get("source_url"),
                        "page_number": item.metadata.get("page_number"),
                        "preview": (item.content or "")[:180].replace("\n", " "),
                    },
                    ensure_ascii=False,
                )
            )

        try:
            answer_started = time.perf_counter()
            result = service.answer(query)
            answer_elapsed = round((time.perf_counter() - answer_started) * 1000, 3)
            print(f"answer={result.answer}")
            print(f"sources={len(result.sources)}")
            print(f"generation_latency_ms={answer_elapsed}")
        except Exception as exc:
            print(f"pipeline_error={type(exc).__name__}: {exc}")

        print("=" * 80)


if __name__ == "__main__":
    main()
