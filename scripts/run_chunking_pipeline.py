from __future__ import annotations

from backend.rag.chunking_runner import build_chunking_outputs
from backend.rag.metadata_enrichment import MetadataEnricher


def main() -> None:
    build_chunking_outputs()
    MetadataEnricher().enrich()


if __name__ == "__main__":
    main()
