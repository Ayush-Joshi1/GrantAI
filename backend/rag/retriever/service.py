"""Retriever service that provides higher-level retrieval operations."""
from __future__ import annotations

import logging
from typing import Any

from backend.rag.interfaces import RetrievalResult, Retriever
from backend.rag.retriever.exceptions import RetrieverError

logger = logging.getLogger("rag.retriever.service")


class RetrieverService:
    """Service layer around a `Retriever` to support DI and cross-cutting concerns."""

    def __init__(self, retriever: Retriever):
        self.retriever = retriever

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: float | None = None,
        metadata_filter: dict[str, Any] | None = None,
    ) -> list[RetrievalResult]:
        try:
            return self.retriever.retrieve(query, top_k, similarity_threshold=similarity_threshold, metadata_filter=metadata_filter)
        except Exception as exc:
            logger.exception("Retrieval failed: %s", exc)
            raise RetrieverError(str(exc)) from exc
