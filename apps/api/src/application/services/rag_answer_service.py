from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from backend.rag.config import get_rag_settings
from backend.rag.embeddings.provider import SentenceTransformerProvider
from backend.rag.interfaces import RetrievalResult
from backend.rag.retriever.exceptions import RetrieverError
from backend.rag.retriever.semantic_retriever import SemanticRetriever
from backend.rag.retriever.service import RetrieverService
from backend.rag.vectorstore.faiss_store import FAISSVectorStore
from backend.rag.vectorstore.service import VectorStoreService
from src.core.errors.exceptions import UpstreamError, ValidationError
from src.infrastructure.ibm.granite_client import GraniteClient
from src.prompts.rag.grounded_prompt_builder import GroundedPromptBuilder

if TYPE_CHECKING:
    from backend.rag.rag_service import RAGService

logger = logging.getLogger("api.application.rag_answer")

INSUFFICIENT_CONTEXT_FALLBACK = "The available Government grant documents do not contain enough relevant information to answer this question confidently."


@dataclass(frozen=True)
class RAGAnswerSource:
    grant_name: str | None = None
    organization: str | None = None
    source_document: str | None = None
    page_number: int | None = None


@dataclass(frozen=True)
class RAGAnswerResult:
    answer: str
    sources: list[RAGAnswerSource] = field(default_factory=list)


class RAGAnswerService:
    """Compose retrieval, prompt formatting, and Granite generation for grounded answers."""

    def __init__(
        self,
        retrieval_client: Any | None = None,
        prompt_builder: GroundedPromptBuilder | None = None,
        granite_client: GraniteClient | None = None,
        settings: Any | None = None,
    ) -> None:
        self.settings = settings or get_rag_settings()
        self.retrieval_client = retrieval_client or self._build_default_retrieval_client()
        self.prompt_builder = prompt_builder or GroundedPromptBuilder()
        self.granite_client = granite_client or GraniteClient(settings=self.settings)

    def answer(self, query: str) -> RAGAnswerResult:
        if not query or not query.strip():
            raise ValidationError("Query must not be empty.")

        logger.info("RAG answer processing started", extra={"query_length": len(query.strip())})
        started_at = time.perf_counter()

        try:
            retrieval_results = self._retrieve(query)
        except RetrieverError as exc:
            logger.exception("Retrieval failed for RAG answer")
            raise UpstreamError("GrantAI could not retrieve relevant grant information at the moment.") from exc
        except Exception as exc:
            logger.exception("Unexpected retrieval failure for RAG answer")
            raise UpstreamError("GrantAI could not retrieve relevant grant information at the moment.") from exc

        if not retrieval_results:
            logger.info("RAG answer insufficient context: no retrieval results")
            return RAGAnswerResult(answer=INSUFFICIENT_CONTEXT_FALLBACK, sources=[])

        if not self._has_usable_content(retrieval_results):
            logger.info("RAG answer insufficient context: retrieved content is unusable")
            return RAGAnswerResult(answer=INSUFFICIENT_CONTEXT_FALLBACK, sources=[])

        logger.info(
            "RAG answer retrieval completed",
            extra={"retrieval_result_count": len(retrieval_results), "duration_ms": round((time.perf_counter() - started_at) * 1000, 3)},
        )

        try:
            prompt = self.prompt_builder.build_prompt(query, retrieval_results)
        except Exception as exc:
            logger.exception("Prompt construction failed")
            raise UpstreamError("GrantAI could not build a grounded prompt at the moment.") from exc

        if not prompt or not prompt.strip():
            raise UpstreamError("GrantAI could not build a grounded prompt at the moment.")

        logger.info(
            "RAG answer prompt constructed",
            extra={"duration_ms": round((time.perf_counter() - started_at) * 1000, 3)},
        )

        try:
            answer_text = self.granite_client.generate(prompt)
        except Exception as exc:
            logger.exception("Granite generation failed")
            raise UpstreamError("GrantAI could not generate a response at the moment. Please try again.") from exc

        if not answer_text or not answer_text.strip():
            raise UpstreamError("GrantAI could not generate a response at the moment. Please try again.")

        sources = self._extract_sources(retrieval_results)
        logger.info(
            "RAG answer completed",
            extra={"source_count": len(sources), "duration_ms": round((time.perf_counter() - started_at) * 1000, 3)},
        )
        return RAGAnswerResult(answer=answer_text.strip(), sources=sources)

    def _retrieve(self, query: str) -> list[RetrievalResult]:
        return self.retrieval_client.retrieve(
            query=query,
            top_k=self.settings.top_k,
            similarity_threshold=self.settings.similarity_threshold,
        )

    def _has_usable_content(self, retrieval_results: list[RetrievalResult]) -> bool:
        return any(result.content and result.content.strip() for result in retrieval_results)

    def _extract_sources(self, retrieval_results: list[RetrievalResult]) -> list[RAGAnswerSource]:
        sources: list[RAGAnswerSource] = []
        seen: set[tuple[str, str, str, str]] = set()

        for result in retrieval_results:
            metadata = result.metadata or {}
            grant_name = self._coerce_optional_text(metadata.get("grant_name"))
            organization = self._coerce_optional_text(metadata.get("organization"))
            source_document = self._coerce_optional_text(
                metadata.get("file_name")
                or metadata.get("document_name")
                or metadata.get("source_document")
                or metadata.get("source_url")
            )
            page_number = self._coerce_optional_int(metadata.get("page_number"))

            dedupe_key = (
                grant_name or "",
                organization or "",
                source_document or "",
                str(page_number) if page_number is not None else "",
            )
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            sources.append(
                RAGAnswerSource(
                    grant_name=grant_name,
                    organization=organization,
                    source_document=source_document,
                    page_number=page_number,
                )
            )

        return sources

    def _build_default_retrieval_client(self) -> Any:
        try:
            embedding_provider = SentenceTransformerProvider(
                model_name=self.settings.embedding_model_name,
                batch_size=self.settings.embedding_batch_size,
                device=self.settings.embedding_device,
            )
            vector_store = FAISSVectorStore(
                index_path=str(self.settings.vector_store_path),
                dim=768,
                metric=self.settings.vector_metric,
            )
            vector_service = VectorStoreService(store=vector_store)
            retriever = SemanticRetriever(vector_service=vector_service, embedding_provider=embedding_provider)
            return RetrieverService(retriever=retriever)
        except ModuleNotFoundError as exc:
            raise UpstreamError("Retrieval dependencies are unavailable.") from exc

    def _coerce_optional_text(self, value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
            return value or None
        if isinstance(value, (int, float)):
            return str(value)
        return str(value)

    def _coerce_optional_int(self, value: Any) -> int | None:
        if value is None:
            return None
        if isinstance(value, bool):
            return None
        if isinstance(value, int):
            return value
        if isinstance(value, float):
            return int(value)
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return None
            try:
                return int(stripped)
            except ValueError:
                return None
        return None
