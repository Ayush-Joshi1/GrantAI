from __future__ import annotations

import json
import logging
import re
import time
from pathlib import Path
from typing import Any

from backend.rag.config import get_rag_settings
from backend.rag.loaders import FileDocumentLoader
from backend.rag.logging_config import configure_rag_logging
from backend.rag.splitter import RecursiveCharacterTextSplitterStrategy, TextSplitterService

logger = logging.getLogger("rag.chunking_runner")


def build_chunking_outputs(source: str | Path | None = None, output_dir: str | Path | None = None) -> dict[str, Any]:
    configure_rag_logging()
    settings = get_rag_settings()

    source_path = Path(source or "backend/data/raw")
    output_path = Path(output_dir or "backend/data/reports")
    output_path.mkdir(parents=True, exist_ok=True)

    loader = FileDocumentLoader()
    splitter = RecursiveCharacterTextSplitterStrategy(chunk_size=settings.chunk_size, chunk_overlap=settings.chunk_overlap)
    service = TextSplitterService(strategy=splitter)

    start_time = time.time()
    documents = loader.load(str(source_path), report_path=output_path / "document_loading_report.json")
    chunks = service.split_many(documents)
    elapsed = time.time() - start_time

    normalized_chunks: list[dict[str, Any]] = []
    for chunk in chunks:
        if not getattr(chunk, "page_content", "") or not getattr(chunk, "page_content", "").strip():
            continue
        normalized_chunks.append(
            {
                "id": chunk.metadata.get("chunk_id") or f"{chunk.metadata.get('source', 'unknown')}:{chunk.metadata.get('chunk_number', 0)}",
                "page_content": chunk.page_content,
                "metadata": dict(chunk.metadata or {}),
            }
        )

    chunk_report = {
        "total_documents": len(documents),
        "total_chunks": len(normalized_chunks),
        "average_chunk_size": round(sum(len(item["page_content"]) for item in normalized_chunks) / len(normalized_chunks), 2) if normalized_chunks else 0,
        "largest_chunk": max((len(item["page_content"]) for item in normalized_chunks), default=0),
        "smallest_chunk": min((len(item["page_content"]) for item in normalized_chunks), default=0),
        "processing_time_seconds": round(elapsed, 3),
    }

    quality_report = self._build_chunk_quality_report(normalized_chunks)

    chunks_path = output_path / "processed_chunks.json"
    chunks_path.write_text(json.dumps(normalized_chunks, indent=2, ensure_ascii=False), encoding="utf-8")
    (output_path / "chunking_report.json").write_text(json.dumps(chunk_report, indent=2), encoding="utf-8")
    (output_path / "chunk_quality_report.json").write_text(json.dumps(quality_report, indent=2), encoding="utf-8")

    logger.info("Chunking completed: %d chunks from %d documents", chunk_report["total_chunks"], chunk_report["total_documents"])
    return {"chunks": normalized_chunks, "report": chunk_report, "quality_report": quality_report}


def _build_chunk_quality_report(chunks: list[dict[str, Any]]) -> dict[str, Any]:
    if not chunks:
        return {
            "total_chunks": 0,
            "average_chunk_size": 0,
            "average_words_per_chunk": 0,
            "chunks_ending_mid_sentence": 0,
            "chunks_beginning_mid_sentence": 0,
            "largest_chunk": 0,
            "smallest_chunk": 0,
        }

    lengths = [len(chunk["page_content"]) for chunk in chunks]
    words = [len(re.findall(r"\b\w+\b", chunk["page_content"])) for chunk in chunks]
    mid_sentence_end = 0
    mid_sentence_begin = 0
    previous_text = ""
    for chunk in chunks:
        text = chunk["page_content"].strip()
        if text and not text.endswith((".", "!", "?", ":", ";")):
            mid_sentence_end += 1

        if previous_text and text and previous_text.strip() and not previous_text.strip().endswith((".", "!", "?", ":", ";")) and text[0].islower():
            mid_sentence_begin += 1

        previous_text = text

    return {
        "total_chunks": len(chunks),
        "average_chunk_size": round(sum(lengths) / len(lengths), 2),
        "average_words_per_chunk": round(sum(words) / len(words), 2),
        "chunks_ending_mid_sentence": mid_sentence_end,
        "chunks_beginning_mid_sentence": mid_sentence_begin,
        "largest_chunk": max(lengths),
        "smallest_chunk": min(lengths),
    }


if __name__ == "__main__":
    build_chunking_outputs()
