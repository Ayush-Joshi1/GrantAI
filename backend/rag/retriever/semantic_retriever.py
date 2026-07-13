"""Production semantic retriever built on the vector-store abstraction."""
from __future__ import annotations

import logging
from typing import Any

from backend.rag.interfaces import EmbeddingProvider, Retriever, RetrievalResult
from backend.rag.retriever.exceptions import RetrieverError
from backend.rag.vectorstore.service import VectorStoreService

logger = logging.getLogger("rag.retriever.semantic")


class SemanticRetriever(Retriever):
    """Retrieve relevant chunks by embedding the query and searching the vector store."""

    def __init__(self, vector_service: VectorStoreService, embedding_provider: EmbeddingProvider | None = None):
        self.vector_service = vector_service
        self.embedding_provider = embedding_provider

    def retrieve(
        self,
        query: str,
        top_k: int,
        similarity_threshold: float | None = None,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[RetrievalResult]:
        if not query or not query.strip():
            raise RetrieverError("Query text must not be empty")

        if self.embedding_provider is None:
            raise RetrieverError("Embedding provider is required for retrieval")

        query_embedding = self.embedding_provider.embed_query(query)

        try:
            results = self.vector_service.search(query_embedding, top_k, metadata_filter=metadata_filter)
        except Exception as exc:
            logger.exception("Vector store search failed: %s", exc)
            raise RetrieverError(str(exc)) from exc

        if similarity_threshold is not None:
            results = [result for result in results if result.score >= similarity_threshold]

        return results
