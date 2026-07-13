"""End-to-end RAG pipeline test harness.

This script builds an index from files in `tests/data/`, runs sample queries,
and prints retrieved chunks, metadata, similarity scores, and execution time.

Usage:
    python -m tests.rag_e2e_test

Dependencies:
    - faiss-cpu
    - sentence-transformers
    - langchain

This is a diagnostic tool to validate retrieval quality before connecting any LLM.
Do not use IBM Granite or any LLM in this test.
"""
from __future__ import annotations

import logging
import time
from pathlib import Path
from pprint import pprint

from backend.rag.logging_config import configure_rag_logging
from backend.rag.config import get_rag_settings

# components
from backend.rag.loaders import FileDocumentLoader
from backend.rag.splitter import (
    TextSplitterService,
    RecursiveCharacterTextSplitterStrategy,
)
from backend.rag.embeddings import SentenceTransformerProvider, EmbeddingError
from backend.rag.embeddings.service import EmbeddingService
from backend.rag.vectorstore import FAISSVectorStore, VectorStoreService
from backend.rag.retriever import FAISSRetriever, RetrieverService
from backend.rag.pipeline import RAGPipeline


def main():
    configure_rag_logging()
    settings = get_rag_settings()
    logger = logging.getLogger("tests.rag_e2e_test")

    data_dir = Path(__file__).parent / "data"
    if not data_dir.exists():
        logger.error("Data directory not found: %s", data_dir)
        return

    # initialize components
    loader = FileDocumentLoader()

    splitter_strategy = RecursiveCharacterTextSplitterStrategy(
        chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap
    )
    splitter_service = TextSplitterService(strategy=splitter_strategy)

    try:
        embedding_provider = SentenceTransformerProvider(
            model_name=settings.embedding_model_name,
            batch_size=settings.embedding_batch_size,
            device=settings.embedding_device,
        )
    except Exception as exc:
        logger.exception("Failed to initialize embedding provider: %s", exc)
        return

    embedding_service = EmbeddingService(provider=embedding_provider)

    # create FAISS store using provider dimension
    try:
        dim = embedding_provider.model.get_sentence_embedding_dimension()
    except Exception:
        # fallback to a reasonable default
        dim = 384

    index_path = settings.vector_store_path
    faiss_store = FAISSVectorStore(index_path=index_path, dim=dim, metric=settings.vector_metric)
    vector_service = VectorStoreService(store=faiss_store)

    retriever = FAISSRetriever(vector_service=vector_service, embedding_provider=embedding_provider)
    retriever_service = RetrieverService(retriever=retriever)

    pipeline = RAGPipeline(
        loader=loader,
        splitter_service=splitter_service,
        embedding_service=embedding_service,
        vector_service=vector_service,
        retriever_service=retriever_service,
    )

    # Build index
    start = time.time()
    try:
        pipeline.build_index([str(data_dir)])
    except Exception as exc:
        logger.exception("Pipeline build_index failed: %s", exc)
        return
    build_time = time.time() - start

    print("Built index in %.2f seconds" % build_time)

    # Sample queries
    queries = [
        "grant funding opportunities",
        "recommendation engine for proposals",
        "LangChain document loaders",
    ]

    for q in queries:
        print("\nQuery:\n", q)
        t0 = time.time()
        results = pipeline.search(q, top_k=settings.top_k)
        elapsed = time.time() - t0
        print(f"Retrieved {len(results)} results in {elapsed:.3f}s")
        for i, r in enumerate(results, start=1):
            print(f"\nResult #{i} (score={r.score:.4f})")
            print("Content:\n", (r.content[:500] + "...") if len(r.content) > 500 else r.content)
            print("Metadata:")
            pprint(r.metadata)

    print("\nTest complete. Index build time: %.2f seconds" % build_time)


if __name__ == "__main__":
    main()
