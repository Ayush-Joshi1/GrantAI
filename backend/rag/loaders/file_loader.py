"""File-based document loader implementations for RAG."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

try:
    from langchain_community.document_loaders import CSVLoader, JSONLoader, PyPDFLoader, TextLoader
except ImportError:  # pragma: no cover - fallback for older langchain versions
    from langchain.document_loaders import CSVLoader, JSONLoader, PyPDFLoader, TextLoader

from backend.rag.interfaces import Document
from backend.rag.loaders.exceptions import DocumentLoadError

logger = logging.getLogger("rag.loaders")

_SUPPORTED_EXTENSIONS = {
    ".pdf": PyPDFLoader,
    ".txt": TextLoader,
    ".csv": CSVLoader,
    ".json": JSONLoader,
}

_DOCUMENT_TYPE_MAP = {
    ".pdf": "pdf",
    ".txt": "text",
    ".csv": "csv",
    ".json": "json",
}


class FileDocumentLoader:
    """Loads documents from supported files and directories."""

    def load(self, source: str | Path | None = None, report_path: str | Path | None = None) -> list[Document]:
        """Load all supported documents from a path and emit a summary report.

        Args:
            source: A file path or directory path.
            report_path: Optional path for the JSON loading report.

        Returns:
            A list of loaded Document objects.

        Raises:
            DocumentLoadError: when the source path is invalid or no supported files are found.
        """
        if source is None:
            source = "backend/data/raw"
        path = Path(source)
        if not path.exists():
            message = f"Source path does not exist: {source}"
            logger.error(message)
            raise DocumentLoadError(message)

        files = self._collect_files(path)
        if not files:
            message = f"No supported files found under: {source}"
            logger.warning(message)
            self._write_report(report_path or self._default_report_path(), 0, 0, 0, 0, 0)
            raise DocumentLoadError(message)

        documents: list[Document] = []
        successfully_loaded = 0
        failed_files = 0
        total_pages = 0
        total_extracted_characters = 0

        for file_path in files:
            try:
                loaded_docs = self._load_file(file_path, path)
                documents.extend(loaded_docs)
                successfully_loaded += 1
                total_pages += len(loaded_docs)
                total_extracted_characters += sum(len(doc.content or "") for doc in loaded_docs)
            except Exception as exc:
                failed_files += 1
                message = f"Failed to load file {file_path}: {exc}"
                logger.exception(message)

        self._write_report(
            report_path or self._default_report_path(),
            len(files),
            successfully_loaded,
            failed_files,
            total_pages,
            total_extracted_characters,
        )
        return documents

    def _default_report_path(self) -> Path:
        return Path("backend/data/reports/document_loading_report.json")

    def _collect_files(self, path: Path) -> list[Path]:
        if path.is_file():
            return [path] if path.suffix.lower() in _SUPPORTED_EXTENSIONS else []
        return [p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in _SUPPORTED_EXTENSIONS]

    def _load_file(self, file_path: Path, source_root: Path) -> list[Document]:
        loader_cls = _SUPPORTED_EXTENSIONS.get(file_path.suffix.lower())
        if loader_cls is None:
            raise DocumentLoadError(f"Unsupported file type: {file_path.suffix}")

        loader = self._instantiate_loader(loader_cls, file_path)
        loaded_docs = loader.load()
        return [self._normalize_document(doc, file_path, source_root) for doc in loaded_docs]

    def _instantiate_loader(self, loader_cls: type, file_path: Path):
        if loader_cls is JSONLoader:
            return loader_cls(str(file_path), jq_schema=None)
        return loader_cls(str(file_path))

    def _normalize_document(self, loaded_doc: Any, file_path: Path, source_root: Path) -> Document:
        content = getattr(loaded_doc, "page_content", None) or getattr(loaded_doc, "content", "")
        metadata = getattr(loaded_doc, "metadata", {}) or {}
        page_number = metadata.get("page_number") or metadata.get("page") or 1
        relative_path = file_path.relative_to(source_root) if source_root in file_path.parents else file_path
        source_folder = relative_path.parent.as_posix() if relative_path.parent != Path(".") else ""
        metadata.update(
            {
                "source": str(file_path),
                "filename": file_path.name,
                "source_folder": source_folder,
                "page_number": page_number,
                "document_type": _DOCUMENT_TYPE_MAP.get(file_path.suffix.lower(), file_path.suffix.lower().lstrip(".")),
                "file_name": file_path.name,
                "file_extension": file_path.suffix.lower(),
            }
        )
        return Document(
            id=f"{file_path.name}:{len(content)}:{hash(content)}",
            content=content,
            metadata=metadata,
        )

    def _write_report(
        self,
        report_path: str | Path | None,
        total_files: int,
        successfully_loaded: int,
        failed_files: int,
        total_pages: int,
        total_extracted_characters: int,
    ) -> None:
        if not report_path:
            return
        output_path = Path(report_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "total_files": total_files,
            "successfully_loaded": successfully_loaded,
            "failed_files": failed_files,
            "total_pages": total_pages,
            "total_extracted_characters": total_extracted_characters,
        }
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
