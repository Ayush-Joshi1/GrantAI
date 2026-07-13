"""Exceptions used by the vector store implementations."""


class VectorStoreError(Exception):
    """Base class for vector store errors."""
    pass


class DocumentNotFoundError(VectorStoreError):
    """Raised when a document/chunk cannot be found in the store."""
    pass
