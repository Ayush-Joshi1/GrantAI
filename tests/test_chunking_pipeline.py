from __future__ import annotations

from backend.rag.interfaces import Document
from backend.rag.splitter import RecursiveCharacterTextSplitterStrategy, TextSplitterService


def test_splitter_adds_traceable_metadata_and_skips_empty_chunks() -> None:
    document = Document(
        id="doc-123",
        content=(
            "# Eligibility Criteria\n\n"
            "Applicants must be registered startups.\n\n"
            "The grant covers product development and market access.\n\n"
            "Additional guidance is available in the appendix."
        ),
        metadata={
            "filename": "sample.pdf",
            "source_folder": "birac",
            "page_number": 2,
            "document_type": "pdf",
            "organization": "Biotech Industries",
        },
    )

    service = TextSplitterService(
        RecursiveCharacterTextSplitterStrategy(chunk_size=120, chunk_overlap=20)
    )

    chunks = service.split(document)

    assert chunks, "expected at least one chunk"
    assert all(chunk.metadata.get("chunk_id") for chunk in chunks)
    assert all(chunk.metadata.get("chunk_number") for chunk in chunks)
    assert all(chunk.metadata.get("total_chunks") for chunk in chunks)
    assert all(chunk.metadata.get("file_name") == "sample.pdf" for chunk in chunks)
    assert all(chunk.metadata.get("source_folder") == "birac" for chunk in chunks)
    assert all(chunk.metadata.get("page_number") == 2 for chunk in chunks)
    assert all(chunk.metadata.get("original_document_id") == "doc-123" for chunk in chunks)


def test_splitter_extends_chunks_until_sentence_boundary() -> None:
    document = Document(
        id="doc-456",
        content="A" * 140 + " sentence should be preserved until the period.",
        metadata={"filename": "sample.pdf"},
    )

    service = TextSplitterService(
        RecursiveCharacterTextSplitterStrategy(chunk_size=70, chunk_overlap=10)
    )

    chunks = service.split(document)

    assert chunks
    assert any(chunk.page_content.endswith(".") for chunk in chunks)
