"""Sentence Transformer embedding provider for RAG."""
from __future__ import annotations

import logging
from typing import Iterable

from sentence_transformers import SentenceTransformer
from tenacity import (  # type: ignore[import]
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from backend.rag.embeddings.exceptions import EmbeddingError
from backend.rag.interfaces import EmbeddingProvider

logger = logging.getLogger("rag.embeddings.provider")


class SentenceTransformerProvider(EmbeddingProvider):
    """Embedding provider based on Sentence Transformers."""

    def __init__(self, model_name: str, batch_size: int = 32, device: str | None = "cpu"):
        self.model_name = model_name
        self.batch_size = batch_size
        self.device = device
        self.model = self._load_model()

    def _load_model(self) -> SentenceTransformer:
        try:
            logger.info("Loading SentenceTransformer model %s on device %s", self.model_name, self.device)
            return SentenceTransformer(self.model_name, device=self.device)
        except Exception as exc:
            message = f"Failed to initialize SentenceTransformer model {self.model_name}: {exc}"
            logger.exception(message)
            raise EmbeddingError(message) from exc

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            logger.debug("No texts provided for embedding.")
            return []

        self._validate_texts(texts)
        logger.info("Embedding batch of %d texts", len(texts))
        embeddings = self._encode_batch(texts)
        return embeddings.tolist() if hasattr(embeddings, "tolist") else [list(row) for row in embeddings]

    def embed_single(self, text: str) -> list[float]:
        if not text or not text.strip():
            raise EmbeddingError("Text for single embedding must not be empty.")
        return self.embed([text])[0]

    def embed_query(self, query: str) -> list[float]:
        if not query or not query.strip():
            raise EmbeddingError("Query text must not be empty.")
        return self.embed_single(query)

    def _validate_texts(self, texts: list[str]) -> None:
        if any(not isinstance(text, str) for text in texts):
            raise EmbeddingError("All texts must be strings for embedding.")

    @retry(
        retry=retry_if_exception_type(EmbeddingError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True,
    )
    def _encode_batch(self, texts: list[str]):
        try:
            return self.model.encode(
                texts,
                batch_size=self.batch_size,
                show_progress_bar=False,
                convert_to_numpy=True,
            )
        except Exception as exc:
            message = f"Failed to encode texts with SentenceTransformer: {exc}"
            logger.exception(message)
            raise EmbeddingError(message) from exc
