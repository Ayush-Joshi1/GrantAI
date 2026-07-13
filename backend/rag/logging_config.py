"""Logging configuration for the RAG backend."""
from __future__ import annotations

import logging
from backend.rag.config import get_rag_settings


def configure_rag_logging(level: str | None = None) -> None:
    """Configure root logging for the RAG backend.

    If `level` is not provided, the value from `RAGSettings.logging_level`
    will be used (environment-configurable).
    """
    if level is None:
        try:
            settings = get_rag_settings()
            level = settings.logging_level
        except Exception:
            level = "INFO"

    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger = logging.getLogger("rag")
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Mirror handlers to common uvicorn logger if present
    try:
        logging.getLogger("uvicorn").handlers = logging.getLogger().handlers
        logging.getLogger("uvicorn").setLevel(getattr(logging, level.upper(), logging.INFO))
    except Exception:
        pass
