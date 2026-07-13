"""Orchestrates the RAG pipeline: load -> split -> embed -> index -> retrieve."""
from __future__ import annotations

import logging
from typing import Iterable, List, Optional

from backend.rag.config import get_rag_settings
from backend.rag.exceptions import RAGPipelineError
from backend.rag.interfaces import (
    Document,
    DocumentChunk,
    RetrievalResult,
    RAGPipeline as RAGPipelineABC,
)

logger = logging.getLogger("rag.pipeline")


class RAGPipeline(RAGPipelineABC):
    """Concrete RAG pipeline that composes loader, splitter, embedding and vectorstore.

    Components are injected to keep the pipeline testable and modular.
    """

    def __init__(
        self,
        loader,
        splitter_service,
        embedding_service,
        vector_service,
        retriever_service,
        settings=None,
    ) -> None:
        self.loader = loader
        self.splitter_service = splitter_service
        self.embedding_service = embedding_service
        self.vector_service = vector_service
        self.retriever_service = retriever_service
        self.settings = settings or get_rag_settings()

    def build_index(self, sources: list[str]) -> None:
        logger.info("RAGPipeline.build_index: starting with %d sources", len(sources))
        try:
            documents: List[Document] = []
            for src in sources:
                logger.info("Loading documents from %s", src)
                loaded = self.loader.load(src)
                documents.extend(loaded)

            logger.info("Splitting %d documents", len(documents))
            chunks = self.splitter_service.split_many(documents)

            texts = [c.page_content for c in chunks]
            logger.info("Generating embeddings for %d chunks", len(texts))
            embeddings = self.embedding_service.embed_texts(texts)

            # Convert LangChain chunks to local DocumentChunk dataclass
            doc_chunks: List[DocumentChunk] = []
            for chunk in chunks:
                meta = dict(chunk.metadata or {})
                chunk_id = meta.get("chunk_id") or f"{meta.get('source', 'unknown')}:{meta.get('chunk_index', 0)}:{hash(chunk.page_content)}"
                doc_chunks.append(DocumentChunk(id=chunk_id, content=chunk.page_content, metadata=meta, source_id=meta.get("source_id")))

            logger.info("Adding %d chunks to vector store", len(doc_chunks))
            self.vector_service.add(doc_chunks, embeddings)
            # persist index
            try:
                self.vector_service.store.save_index()
            except Exception:
                logger.exception("Failed to save index after build_index")

            logger.info("RAGPipeline.build_index: completed")
        except Exception as exc:
            logger.exception("RAGPipeline.build_index failed: %s", exc)
            raise RAGPipelineError(str(exc)) from exc

    def update_index(self, sources: list[str]) -> None:
        logger.info("RAGPipeline.update_index: updating with %d sources", len(sources))
        try:
            # For now, update semantics == build_index (append/overwrite)
            self.build_index(sources)
        except Exception as exc:
            logger.exception("RAGPipeline.update_index failed: %s", exc)
            raise RAGPipelineError(str(exc)) from exc

    def retrieve(
        self,
        query: str,
        top_k: int,
        similarity_threshold: Optional[float] = None,
        metadata_filter: Optional[dict] = None,
    ) -> List[RetrievalResult]:
        logger.info("RAGPipeline.retrieve query=%s top_k=%d", query, top_k)
        try:
            results = self.retriever_service.retrieve(query, top_k, similarity_threshold=similarity_threshold, metadata_filter=metadata_filter)
            logger.info("RAGPipeline.retrieve returned %d results", len(results))
            return results
        except Exception as exc:
            logger.exception("RAGPipeline.retrieve failed: %s", exc)
            raise RAGPipelineError(str(exc)) from exc

    def search(self, query: str, top_k: int, metadata_filter: Optional[dict] = None) -> List[RetrievalResult]:
        return self.retrieve(query, top_k, similarity_threshold=self.settings.similarity_threshold, metadata_filter=metadata_filter)
