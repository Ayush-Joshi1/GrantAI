"""Service layer for vector store operations."""
from __future__ import annotations

import logging
from typing import Iterable, List

from backend.rag.interfaces import DocumentChunk
from backend.rag.vectorstore.exceptions import VectorStoreError
from backend.rag.vectorstore.faiss_store import FAISSVectorStore

logger = logging.getLogger("rag.vectorstore.service")


class VectorStoreService:
    """Thin service that delegates to a VectorStore implementation.

    This class exists to allow DI and to centralize any future cross-cutting
    concerns such as transactions or access control.
    """

    def __init__(self, store: FAISSVectorStore):
        self.store = store

    def add(self, chunks: Iterable[DocumentChunk], embeddings: List[List[float]]) -> None:
        try:
            self.store.add_documents(list(chunks), embeddings)
        except Exception as exc:
            logger.exception("Failed to add documents to vector store: %s", exc)
            raise VectorStoreError(str(exc)) from exc

    def update(self, chunks: Iterable[DocumentChunk], embeddings: List[List[float]]) -> None:
        try:
            self.store.update_documents(list(chunks), embeddings)
        except Exception as exc:
            logger.exception("Failed to update documents in vector store: %s", exc)
            raise VectorStoreError(str(exc)) from exc

    def delete(self, chunk_ids: Iterable[str]) -> None:
        try:
            self.store.delete_documents(list(chunk_ids))
        except Exception as exc:
            logger.exception("Failed to delete documents from vector store: %s", exc)
            raise VectorStoreError(str(exc)) from exc

    def search(self, query_embedding: List[float], top_k: int, metadata_filter: dict | None = None):
        return self.store.search(query_embedding, top_k, metadata_filter=metadata_filter)
