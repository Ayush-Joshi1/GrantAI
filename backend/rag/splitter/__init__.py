"""Text splitter package for the RAG layer."""

from backend.rag.splitter.exceptions import EmptyDocumentError, TextSplitterError
from backend.rag.splitter.service import TextSplitterService
from backend.rag.splitter.strategy import (
    RecursiveCharacterTextSplitterStrategy,
    TextSplitterStrategy,
)

__all__ = [
    "TextSplitterService",
    "TextSplitterStrategy",
    "RecursiveCharacterTextSplitterStrategy",
    "TextSplitterError",
    "EmptyDocumentError",
]
