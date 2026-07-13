"""Pluggable text splitter strategies for RAG."""
from __future__ import annotations

import logging
import re
from abc import ABC, abstractmethod
from typing import Iterable

try:
    from langchain.schema import Document as LangChainDocument
except ImportError:  # pragma: no cover - fallback for newer langchain versions
    from langchain_core.documents import Document as LangChainDocument

try:
    from langchain.text_splitter import RecursiveCharacterTextSplitter
except ImportError:  # pragma: no cover - fallback for newer langchain versions
    from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.rag.splitter.exceptions import EmptyDocumentError, TextSplitterError

logger = logging.getLogger("rag.splitter.strategy")


class TextSplitterStrategy(ABC):
    """Strategy interface for document splitting."""

    @abstractmethod
    def split(self, documents: Iterable[LangChainDocument]) -> list[LangChainDocument]:
        raise NotImplementedError


class RecursiveCharacterTextSplitterStrategy(TextSplitterStrategy):
    """Text splitter using LangChain's recursive character splitter."""

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_chunk_size = chunk_size + 200

    def split(self, documents: Iterable[LangChainDocument]) -> list[LangChainDocument]:
        documents = list(documents)
        if not documents:
            logger.debug("No documents provided to split.")
            return []

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=["\n\n", "\n", ". ", " ", ""],
            keep_separator=True,
        )

        chunked_documents: list[LangChainDocument] = []
        empty_documents = 0

        for document_index, document in enumerate(documents):
            content = getattr(document, "page_content", None)
            if not content or not content.strip():
                message = f"Skipping empty document at index {document_index}."
                logger.warning(message)
                empty_documents += 1
                continue

            logger.info(
                "Splitting document %d with chunk_size=%d chunk_overlap=%d",
                document_index,
                self.chunk_size,
                self.chunk_overlap,
            )

            raw_chunks = splitter.split_documents([document])
            base_chunks = [self._normalize_text(chunk.page_content) for chunk in raw_chunks]
            merged_chunks = self._merge_base_chunks(base_chunks)
            total_chunks = len(merged_chunks)
            for chunk_index, cleaned_content in enumerate(merged_chunks):
                if not cleaned_content:
                    logger.warning("Skipping empty chunk %d for document %d", chunk_index, document_index)
                    continue

                metadata = dict(document.metadata or {})
                metadata["chunk_index"] = chunk_index
                metadata["chunk_number"] = chunk_index + 1
                metadata["total_chunks"] = total_chunks
                metadata["original_document_index"] = document_index
                metadata["original_document_id"] = metadata.get("original_document_id") or metadata.get("source_id") or document.id
                metadata["source"] = metadata.get("source", metadata.get("file_name", metadata.get("filename", "unknown")))
                metadata["source_folder"] = metadata.get("source_folder") or metadata.get("folder") or "unknown"
                metadata["file_name"] = metadata.get("file_name") or metadata.get("filename") or "unknown"
                metadata["document_type"] = metadata.get("document_type") or "unknown"
                metadata["page_number"] = metadata.get("page_number") or 1
                metadata["organization"] = metadata.get("organization") or "unknown"
                metadata["chunk_id"] = metadata.get("chunk_id") or f"{metadata.get('source_id') or metadata.get('source') or document.id}:{chunk_index + 1}"
                metadata["chunk_size"] = len(cleaned_content)

                chunked_documents.append(
                    LangChainDocument(
                        page_content=cleaned_content,
                        metadata=metadata,
                    )
                )

        if empty_documents == len(documents):
            raise EmptyDocumentError("All supplied documents were empty.")

        return chunked_documents

    def _merge_base_chunks(self, base_chunks: list[str]) -> list[str]:
        if not base_chunks:
            return []

        merged_chunks: list[str] = []
        index = 0
        while index < len(base_chunks):
            current = base_chunks[index]
            if not current:
                index += 1
                continue

            cursor = index
            while cursor + 1 < len(base_chunks):
                next_chunk = base_chunks[cursor + 1]
                if not next_chunk:
                    cursor += 1
                    continue

                candidate = self._join_chunks(current, next_chunk)
                if len(candidate) > self.max_chunk_size:
                    break

                if self._should_extend_chunk(current, next_chunk, candidate):
                    current = candidate
                    cursor += 1
                    continue

                break

            merged_chunks.append(current)
            index = cursor + 1

        return merged_chunks

    def _join_chunks(self, current: str, next_chunk: str) -> str:
        if not current:
            return next_chunk
        if not next_chunk:
            return current
        return f"{current}\n\n{next_chunk}"

    def _should_extend_chunk(self, current: str, next_chunk: str, candidate: str) -> bool:
        if not current or not next_chunk:
            return False
        if len(candidate) > self.max_chunk_size:
            return False

        if self._is_heading_follow_on(current, next_chunk):
            return True

        if self._is_list_continuation(current, next_chunk):
            return True

        if self._ends_mid_sentence(current):
            return True

        return False

    def _is_heading_follow_on(self, current: str, next_chunk: str) -> bool:
        last_line = self._last_non_empty_line(current)
        next_line = self._first_non_empty_line(next_chunk)
        if not last_line or not next_line:
            return False
        if len(last_line) > 80:
            return False
        if re.match(r"^\d+([.)]\s|\.\s)", last_line):
            return False
        if last_line.endswith((".", "!", "?", ":")):
            return False
        return not self._looks_like_heading(next_line)

    def _is_list_continuation(self, current: str, next_chunk: str) -> bool:
        current_tail = current.rstrip().splitlines()[-1] if current.rstrip() else ""
        next_head = next_chunk.strip().splitlines()[0] if next_chunk.strip() else ""
        return bool(re.match(r"^(?:[-*•]|\d+[.)])\s", current_tail)) and bool(re.match(r"^(?:[-*•]|\d+[.)])\s", next_head))

    def _ends_mid_sentence(self, text: str) -> bool:
        stripped = text.strip()
        if not stripped:
            return False
        if stripped.endswith((".", "!", "?", ":", ";")):
            return False
        if re.search(r"[.!?]['\")\]]?$", stripped):
            return False
        return True

    def _looks_like_heading(self, line: str) -> bool:
        stripped = line.strip()
        if not stripped:
            return False
        if stripped.startswith(("#", "-", "*", "•")):
            return True
        return len(stripped.split()) <= 8 and not re.search(r"[.!?]$", stripped)

    def _last_non_empty_line(self, text: str) -> str:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return lines[-1] if lines else ""

    def _first_non_empty_line(self, text: str) -> str:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return lines[0] if lines else ""

    def _normalize_text(self, text: str) -> str:
        if not text:
            return ""

        normalized = text.replace("\r\n", "\n").replace("\r", "\n")
        normalized = re.sub(r"[ \t\f\v]+", " ", normalized)
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)
        normalized = re.sub(r"[ \t]*\n[ \t]*", "\n", normalized)
        return normalized.strip()
