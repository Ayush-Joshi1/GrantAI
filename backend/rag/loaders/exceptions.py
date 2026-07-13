"""Loader-specific exceptions for RAG document ingestion."""

class DocumentLoadError(Exception):
    """Raised when document loading fails due to unsupported sources or parsing errors."""
    pass
