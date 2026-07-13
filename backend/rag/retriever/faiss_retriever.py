"""Retriever implementation that queries a VectorStore (FAISS) for relevant chunks."""
from __future__ import annotations

import logging
from typing import List, Optional

from backend.rag.interfaces import RetrievalResult, Retriever
from backend.rag.vectorstore.service import VectorStoreService
from backend.rag.retriever.exceptions import RetrieverError

logger = logging.getLogger("rag.retriever.faiss")


class FAISSRetriever(Retriever):
    """Retriever that wraps a `VectorStoreService` and performs semantic searches.

    This class does not generate answers; it only returns matching chunks with
    content, metadata and similarity scores.
    """

    def __init__(self, vector_service: VectorStoreService, embedding_provider=None):
        self.vector_service = vector_service
        self.embedding_provider = embedding_provider

    def retrieve(
        self,
        query: str,
        top_k: int,
        similarity_threshold: float | None = None,
        metadata_filter: dict[str, object] | None = None,
    ) -> List[RetrievalResult]:
        if not query or not query.strip():
            raise RetrieverError("Query text must not be empty")

        if self.embedding_provider is None:
            raise RetrieverError("Embedding provider is required for retrieval")

        # embed the query using the provided embedding provider
        query_embedding = self.embedding_provider.embed_query(query)

        try:
            results = self.vector_service.search(query_embedding, top_k, metadata_filter=metadata_filter)
        except Exception as exc:
            logger.exception("Vector store search failed: %s", exc)
            raise RetrieverError(str(exc)) from exc

        if similarity_threshold is not None:
            results = [r for r in results if r.score >= similarity_threshold]

        return results
