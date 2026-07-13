from __future__ import annotations

import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.rag.logging_config import configure_rag_logging

logger = logging.getLogger("rag.metadata_enrichment")


class MetadataEnricher:
    def __init__(self, chunk_file: str | Path | None = None, output_dir: str | Path | None = None) -> None:
        self.chunk_file = Path(chunk_file or "backend/data/reports/processed_chunks.json")
        self.output_dir = Path(output_dir or "backend/data/reports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def enrich(self) -> dict[str, Any]:
        configure_rag_logging()
        start_time = time.time()
        payload = json.loads(self.chunk_file.read_text(encoding="utf-8")) if self.chunk_file.exists() else []

        enriched_chunks: list[dict[str, Any]] = []
        metadata_fields_added = set()
        missing_fields = set()
        unknown_values_count = 0

        for item in payload:
            metadata = dict(item.get("metadata") or {})
            normalized = self._normalize_metadata(metadata)
            metadata_fields_added.update(normalized.keys())
            for field in [
                "document_id",
                "chunk_id",
                "chunk_number",
                "total_chunks",
                "file_name",
                "document_name",
                "grant_name",
                "organization",
                "document_type",
                "startup_stage",
                "sector",
                "funding_amount",
                "funding_type",
                "eligibility",
                "application_deadline",
                "state",
                "source_folder",
                "source_url",
                "page_number",
                "publication_date",
                "language",
                "keywords",
                "tags",
                "document_source",
                "created_at",
                "updated_at",
            ]:
                if not normalized.get(field):
                    missing_fields.add(field)
                    if field in {"document_id", "chunk_id", "chunk_number", "total_chunks", "file_name", "document_name", "organization", "document_type", "state", "source_folder", "page_number", "language", "document_source", "created_at", "updated_at"}:
                        normalized[field] = "unknown"
                        unknown_values_count += 1

            enriched_chunks.append({"id": item.get("id"), "page_content": item.get("page_content"), "metadata": normalized})

        report = {
            "total_chunks": len(enriched_chunks),
            "metadata_fields_added": sorted(metadata_fields_added),
            "missing_fields": sorted(missing_fields),
            "unknown_values_count": unknown_values_count,
            "processing_time_seconds": round(time.time() - start_time, 3),
        }

        enriched_path = self.output_dir / "enriched_chunks.json"
        enriched_path.write_text(json.dumps(enriched_chunks, indent=2, ensure_ascii=False), encoding="utf-8")
        (self.output_dir / "metadata_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
        logger.info("Metadata enrichment completed: %d chunks", len(enriched_chunks))
        return {"chunks": enriched_chunks, "report": report}

    def _normalize_metadata(self, metadata: dict[str, Any]) -> dict[str, Any]:
        normalized = {
            "document_id": metadata.get("original_document_id") or metadata.get("document_id") or metadata.get("source_id") or "unknown",
            "chunk_id": metadata.get("chunk_id") or "unknown",
            "chunk_number": metadata.get("chunk_number") or metadata.get("chunk_index") or 1,
            "total_chunks": metadata.get("total_chunks") or 0,
            "file_name": metadata.get("file_name") or metadata.get("filename") or "unknown",
            "document_name": metadata.get("document_name") or metadata.get("file_name") or metadata.get("filename") or "unknown",
            "grant_name": metadata.get("grant_name") or metadata.get("grant") or "unknown",
            "organization": metadata.get("organization") or "unknown",
            "document_type": metadata.get("document_type") or "unknown",
            "startup_stage": metadata.get("startup_stage") or "unknown",
            "sector": metadata.get("sector") or [],
            "funding_amount": metadata.get("funding_amount") or metadata.get("funding") or "unknown",
            "funding_type": metadata.get("funding_type") or "unknown",
            "eligibility": metadata.get("eligibility") or "unknown",
            "application_deadline": metadata.get("application_deadline") or "unknown",
            "state": metadata.get("state") or "India",
            "source_folder": metadata.get("source_folder") or metadata.get("folder") or "unknown",
            "source_url": metadata.get("source_url") or "unknown",
            "page_number": metadata.get("page_number") or 1,
            "publication_date": metadata.get("publication_date") or "unknown",
            "language": metadata.get("language") or "English",
            "keywords": metadata.get("keywords") or [],
            "tags": metadata.get("tags") or [],
            "document_source": metadata.get("document_source") or "Government of India",
            "created_at": metadata.get("created_at") or datetime.now(timezone.utc).isoformat(),
            "updated_at": metadata.get("updated_at") or datetime.now(timezone.utc).isoformat(),
        }
        return normalized


if __name__ == "__main__":
    MetadataEnricher().enrich()
