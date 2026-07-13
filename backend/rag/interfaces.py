from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Document:
    id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DocumentChunk:
    id: str
    content: str
    metadata: dict[str, Any] = field(default_factory=dict)
    source_id: str | None = None


@dataclass(frozen=True)
class RetrievalResult:
    chunk_id: str
    content: str
    metadata: dict[str, Any]
    score: float


class DocumentLoader(ABC):
    @abstractmethod
    def load(self, source: str) -> list[Document]:
        raise NotImplementedError


class TextSplitter(ABC):
    @abstractmethod
    def split(self, document: Document) -> list[DocumentChunk]:
        raise NotImplementedError


class EmbeddingProvider(ABC):
    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        raise NotImplementedError


class VectorStore(ABC):
    @abstractmethod
    def add_documents(self, chunks: list[DocumentChunk], embeddings: list[list[float]]) -> None:
        raise NotImplementedError

    @abstractmethod
    def search(
        self,
        query_embedding: list[float],
        top_k: int,
        metadata_filter: dict[str, object] | None = None,
    ) -> list[RetrievalResult]:
        """Search the vector store for nearest neighbors.

        Args:
            query_embedding: Embedding vector for the query.
            top_k: Number of neighbors to return.
            metadata_filter: Optional key/value pairs to filter results by metadata.
        """
        raise NotImplementedError

    @abstractmethod
    def persist(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def load(self) -> None:
        raise NotImplementedError


class Retriever(ABC):
    @abstractmethod
    def retrieve(
        self,
        query: str,
        top_k: int,
        similarity_threshold: float | None = None,
        metadata_filter: dict[str, object] | None = None,
    ) -> list[RetrievalResult]:
        """Retrieve relevant document chunks for a query.

        Args:
            query: The user query text.
            top_k: Maximum number of results to return.
            similarity_threshold: Optional minimum similarity score to include.
            metadata_filter: Optional metadata key/value pairs to filter results.
        """
        raise NotImplementedError


class RAGPipeline(ABC):
    @abstractmethod
    def ingest(self, sources: list[str]) -> None:
        raise NotImplementedError

    @abstractmethod
    def query(self, query: str, top_k: int) -> list[RetrievalResult]:
        raise NotImplementedError
