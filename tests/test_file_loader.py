from __future__ import annotations

import json
from pathlib import Path

from backend.rag.loaders.file_loader import FileDocumentLoader


def test_loader_recurses_and_writes_loading_report(tmp_path: Path) -> None:
    source_dir = tmp_path / "corpus"
    source_dir.mkdir()
    (source_dir / "nested").mkdir()

    (source_dir / "notes.txt").write_text("hello from the corpus", encoding="utf-8")
    (source_dir / "nested" / "guide.pdf").write_bytes(b"not a real pdf")
    (source_dir / "ignore.md").write_text("unsupported", encoding="utf-8")

    report_path = tmp_path / "reports" / "document_loading_report.json"
    loader = FileDocumentLoader()

    documents = loader.load(str(source_dir), report_path=str(report_path))

    assert len(documents) == 1
    doc = documents[0]
    assert doc.metadata["filename"] == "notes.txt"
    assert doc.metadata["source_folder"] == ""
    assert doc.metadata["page_number"] == 1
    assert doc.metadata["document_type"] == "text"
    assert doc.content == "hello from the corpus"

    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["total_files"] == 2
    assert report["successfully_loaded"] == 1
    assert report["failed_files"] == 1
    assert report["total_pages"] == 1
    assert report["total_extracted_characters"] == len(doc.content)
