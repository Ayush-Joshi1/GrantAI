from __future__ import annotations

import json
import logging
import time
from pathlib import Path
from typing import Any

from backend.rag.config import get_rag_settings
from backend.rag.embeddings.exceptions import EmbeddingError
from backend.rag.embeddings.provider import SentenceTransformerProvider
from backend.rag.embeddings.service import EmbeddingService
from backend.rag.logging_config import configure_rag_logging

logger = logging.getLogger("rag.embedding_runner")


class EmbeddingGenerationService:
    def __init__(self, provider: SentenceTransformerProvider | None = None, settings=None) -> None:
        self.settings = settings or get_rag_settings()
        self.provider = provider or SentenceTransformerProvider(
            model_name=self.settings.embedding_model_name,
            batch_size=self.settings.embedding_batch_size,
            device=self.settings.embedding_device,
        )
        self.service = EmbeddingService(provider=self.provider)

    def generate_embeddings(
        self,
        chunk_file: str | Path | None = None,
        output_dir: str | Path | None = None,
        report_path: str | Path | None = None,
    ) -> dict[str, Any]:
        configure_rag_logging()
        start_time = time.time()
        chunk_path = Path(chunk_file or "backend/data/reports/processed_chunks.json")
        output_path = Path(output_dir or "backend/data/reports")
        output_path.mkdir(parents=True, exist_ok=True)
        report_path = Path(report_path or output_path / "embedding_report.json")

        if not chunk_path.exists():
            raise EmbeddingError(f"Chunk file not found: {chunk_path}")

        payload = json.loads(chunk_path.read_text(encoding="utf-8"))
        documents = payload if isinstance(payload, list) else payload.get("chunks", [])

        unique_chunks: list[dict[str, Any]] = []
        seen_texts: set[str] = set()
        for item in documents:
            page_content = item.get("page_content") or ""
            if not page_content.strip():
                continue
            key = page_content.strip()
            if key in seen_texts:
                logger.info("Skipping duplicate chunk %s", item.get("id"))
                continue
            seen_texts.add(key)
            unique_chunks.append(item)

        successful = 0
        failed = 0
        embeddings_output: list[dict[str, Any]] = []
        for index, item in enumerate(unique_chunks, start=1):
            text = item.get("page_content") or ""
            if not text.strip():
                continue

            try:
                embedding = self.service.embed_single_text(text)
                embeddings_output.append(
                    {
                        "chunk_id": item.get("id") or item.get("metadata", {}).get("chunk_id"),
                        "text": text,
                        "embedding": embedding,
                        "metadata": dict(item.get("metadata") or {}),
                    }
                )
                successful += 1
                logger.info("Embedded chunk %d/%d", index, len(unique_chunks))
            except Exception as exc:
                failed += 1
                logger.exception("Failed to embed chunk %s: %s", item.get("id"), exc)

        report = {
            "total_documents": len({(item.get("metadata") or {}).get("original_document_id") for item in unique_chunks if (item.get("metadata") or {}).get("original_document_id")}),
            "total_chunks": len(unique_chunks),
            "successfully_embedded": successful,
            "failed_embeddings": failed,
            "embedding_model_used": self.settings.embedding_model_name,
            "batch_size": self.settings.embedding_batch_size,
            "processing_time_seconds": round(time.time() - start_time, 3),
        }

        output_path.mkdir(parents=True, exist_ok=True)
        embeddings_path = output_path / "embeddings.json"
        embeddings_path.write_text(json.dumps(embeddings_output, indent=2, ensure_ascii=False), encoding="utf-8")
        report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        logger.info("Embedding generation completed: %d/%d chunks embedded", successful, len(unique_chunks))
        return {"embeddings": embeddings_output, "report": report}


def build_embeddings(output_dir: str | Path | None = None) -> dict[str, Any]:
    service = EmbeddingGenerationService()
    return service.generate_embeddings(output_dir=output_dir)


if __name__ == "__main__":
    build_embeddings()
