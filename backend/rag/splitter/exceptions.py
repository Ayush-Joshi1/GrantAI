"""Splitter-specific exceptions for RAG."""

class TextSplitterError(Exception):
    """Base exception for text splitter failures."""
    pass


class EmptyDocumentError(TextSplitterError):
    """Raised when a document contains no text eligible for splitting."""
    pass
