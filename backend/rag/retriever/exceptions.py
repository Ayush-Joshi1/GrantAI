"""Exceptions used by retriever implementations."""


class RetrieverError(Exception):
    """Base class for retriever errors."""
    pass


class NoResultsError(RetrieverError):
    """Raised when a retrieval returns no results and that is considered an error."""
    pass
