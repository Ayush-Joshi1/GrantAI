"""Embedding service abstraction for RAG."""
from __future__ import annotations

import logging
from typing import Iterable

from backend.rag.interfaces import EmbeddingProvider
from backend.rag.embeddings.exceptions import EmbeddingError

logger = logging.getLogger("rag.embeddings.service")


class EmbeddingService:
    """Service layer that handles embedding operations via provider injection."""

    def __init__(self, provider: EmbeddingProvider):
        self.provider = provider

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            logger.debug("No texts provided to embed.")
            return []

        logger.info("Embedding %d texts", len(texts))
        try:
            return self.provider.embed(texts)
        except Exception as exc:
            message = f"Embedding service failed for batch of {len(texts)} texts: {exc}"
            logger.exception(message)
            raise EmbeddingError(message) from exc

    def embed_single_text(self, text: str) -> list[float]:
        if not text or not text.strip():
            message = "Single text embedding payload must not be empty."
            logger.error(message)
            raise EmbeddingError(message)

        return self.embed_texts([text])[0]

    def embed_query(self, query: str) -> list[float]:
        if not query or not query.strip():
            message = "Query embedding payload must not be empty."
            logger.error(message)
            raise EmbeddingError(message)

        return self.embed_single_text(query)

    def embed_documents(self, documents: Iterable[str]) -> list[list[float]]:
        texts = [text for text in documents if text and text.strip()]
        logger.info("Embedding %d document texts", len(texts))
        return self.embed_texts(texts)
