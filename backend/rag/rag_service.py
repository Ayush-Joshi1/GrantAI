"""Reusable orchestration service for the production RAG retrieval pipeline."""
from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

from backend.rag.config import get_rag_settings
from backend.rag.embedding_runner import EmbeddingGenerationService
from backend.rag.embeddings.provider import SentenceTransformerProvider
from backend.rag.retriever.semantic_retriever import SemanticRetriever
from backend.rag.retriever.service import RetrieverService
from backend.rag.vectorstore.faiss_store import FAISSVectorStore
from backend.rag.vectorstore.service import VectorStoreService
from backend.rag.vectorstore_runner import VectorStoreBuildService

logger = logging.getLogger("rag.service")


class RAGService:
    """Coordinate embedding generation, vector indexing, and semantic retrieval."""

    def __init__(self, settings: Any | None = None) -> None:
        self.settings = settings or get_rag_settings()
        self._embedding_provider = SentenceTransformerProvider(
            model_name=self.settings.embedding_model_name,
            batch_size=self.settings.embedding_batch_size,
            device=self.settings.embedding_device,
        )
        self._vector_service: VectorStoreService | None = None
        self._retriever_service: RetrieverService | None = None

    def _resolve_path(self, path_value: str | Path | None) -> Path:
        path = Path(path_value or self.settings.vector_store_path)
        if path.is_absolute():
            return path
        return (Path.cwd() / path).resolve()

    def _ensure_vector_service(self) -> VectorStoreService:
        if self._vector_service is not None:
            return self._vector_service

        index_path = self._resolve_path("data/rag/faiss.index")
        index_path.parent.mkdir(parents=True, exist_ok=True)
        store = FAISSVectorStore(index_path=str(index_path), dim=768, metric=self.settings.vector_metric)
        self._vector_service = VectorStoreService(store=store)
        return self._vector_service

    def _ensure_retriever_service(self) -> RetrieverService:
        if self._retriever_service is not None:
            return self._retriever_service

        retriever = SemanticRetriever(
            vector_service=self._ensure_vector_service(),
            embedding_provider=self._embedding_provider,
        )
        self._retriever_service = RetrieverService(retriever=retriever)
        return self._retriever_service

    def build_index(self, chunk_file: str | Path | None = None, output_dir: str | Path | None = None) -> dict[str, Any]:
        embedding_service = EmbeddingGenerationService(settings=self.settings)
        embedding_result = embedding_service.generate_embeddings(
            chunk_file=chunk_file,
            output_dir=output_dir,
            report_path=str(Path(output_dir or "backend/data/reports") / "embedding_report.json") if output_dir else None,
        )
        vector_service = VectorStoreBuildService(settings=self.settings)
        vector_result = vector_service.build_from_embeddings(
            embeddings_file=Path(output_dir or "backend/data/reports") / "embeddings.json" if output_dir else None,
            output_dir=output_dir,
        )
        self._vector_service = VectorStoreService(store=vector_result["store"])
        self._retriever_service = None
        return {"embeddings": embedding_result.get("report", {}), "vectorstore": vector_result.get("report", {})}

    def update_index(self, chunk_file: str | Path | None = None, output_dir: str | Path | None = None) -> dict[str, Any]:
        return self.build_index(chunk_file=chunk_file, output_dir=output_dir)

    def retrieve(
        self,
        query: str,
        top_k: int = 5,
        similarity_threshold: float | None = None,
        filters: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        started = time.perf_counter()
        service = self._ensure_retriever_service()
        results = service.retrieve(
            query=query,
            top_k=top_k,
            similarity_threshold=similarity_threshold,
            metadata_filter=self._normalize_filters(filters),
        )
        return {
            "query": query,
            "retrieval_time_ms": round((time.perf_counter() - started) * 1000, 3),
            "results": [
                {
                    "rank": index,
                    "score": round(float(result.score), 6),
                    "chunk_id": result.chunk_id,
                    "grant_name": result.metadata.get("grant_name"),
                    "organization": result.metadata.get("organization"),
                    "page_number": result.metadata.get("page_number"),
                    "source_document": result.metadata.get("source") or result.metadata.get("filename"),
                    "metadata": result.metadata,
                    "content": result.content,
                }
                for index, result in enumerate(results, start=1)
            ],
        }

    def retrieve_with_filters(self, query: str, filters: dict[str, Any] | None = None, top_k: int = 5) -> dict[str, Any]:
        return self.retrieve(query=query, top_k=top_k, filters=filters)

    def search(self, query: str, top_k: int = 5) -> dict[str, Any]:
        return self.retrieve(query=query, top_k=top_k)

    def search_by_grant(self, grant_name: str, top_k: int = 5) -> dict[str, Any]:
        return self.retrieve(query=grant_name, top_k=top_k, filters={"grant_name": grant_name})

    def search_by_organization(self, organization: str, top_k: int = 5) -> dict[str, Any]:
        return self.retrieve(query=organization, top_k=top_k, filters={"organization": organization})

    def search_by_sector(self, sector: str, top_k: int = 5) -> dict[str, Any]:
        return self.retrieve(query=sector, top_k=top_k, filters={"sector": sector})

    def search_by_stage(self, startup_stage: str, top_k: int = 5) -> dict[str, Any]:
        return self.retrieve(query=startup_stage, top_k=top_k, filters={"startup_stage": startup_stage})

    def _normalize_filters(self, filters: dict[str, Any] | None) -> dict[str, Any] | None:
        if not filters:
            return None
        normalized = {}
        for key, value in filters.items():
            if value is None or value == "":
                continue
            normalized[key] = value
        return normalized
