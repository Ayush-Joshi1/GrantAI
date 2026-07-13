"""Reusable splitter service for the RAG pipeline."""
from __future__ import annotations

import logging
from typing import Iterable

try:
    from langchain.schema import Document as LangChainDocument
except ImportError:  # pragma: no cover - fallback for newer langchain versions
    from langchain_core.documents import Document as LangChainDocument

from backend.rag.interfaces import Document as LocalDocument
from backend.rag.splitter.exceptions import EmptyDocumentError, TextSplitterError
from backend.rag.splitter.strategy import TextSplitterStrategy

logger = logging.getLogger("rag.splitter.service")


class TextSplitterService:
    """Service that converts documents into retrievable text chunks."""

    def __init__(self, strategy: TextSplitterStrategy):
        self.strategy = strategy

    def split(self, document: LocalDocument | LangChainDocument) -> list[LangChainDocument]:
        """Split a single document into chunks."""
        return self.split_many([document])

    def split_many(self, documents: Iterable[LocalDocument | LangChainDocument]) -> list[LangChainDocument]:
        """Split multiple documents into optimized chunks."""
        normalized_documents = [self._normalize_document(doc) for doc in documents]
        try:
            return self.strategy.split(normalized_documents)
        except EmptyDocumentError as exc:
            logger.warning("One or more documents were empty: %s", exc)
            return []
        except TextSplitterError:
            raise
        except Exception as exc:
            message = f"Text splitter failed: {exc}"
            logger.exception(message)
            raise TextSplitterError(message) from exc

    def _normalize_document(self, document: LocalDocument | LangChainDocument) -> LangChainDocument:
        if isinstance(document, LangChainDocument):
            return document

        if not isinstance(document, LocalDocument):
            message = f"Document must be a LangChain Document or local Document dataclass, got {type(document)}"
            logger.error(message)
            raise TextSplitterError(message)

        metadata = dict(document.metadata or {})
        metadata["source_id"] = metadata.get("source_id", document.id)
        return LangChainDocument(page_content=document.content, metadata=metadata)
