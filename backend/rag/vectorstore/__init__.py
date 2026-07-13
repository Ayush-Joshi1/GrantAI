"""Vector store package exports for RAG."""

from backend.rag.vectorstore.exceptions import VectorStoreError, DocumentNotFoundError
from backend.rag.vectorstore.faiss_store import FAISSVectorStore
from backend.rag.vectorstore.service import VectorStoreService

__all__ = [
    "FAISSVectorStore",
    "VectorStoreService",
    "VectorStoreError",
    "DocumentNotFoundError",
]
"""Vector store package for the RAG layer."""
