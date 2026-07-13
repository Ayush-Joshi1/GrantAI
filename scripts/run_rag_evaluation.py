#!/usr/bin/env python3
"""Run the production retrieval evaluation suite and emit reports."""
from __future__ import annotations

import json
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv

from backend.rag.evaluation import RetrievalEvaluator
from backend.rag.rag_service import RAGService


def main() -> None:
    load_dotenv(ROOT / ".env", override=False)
    service = RAGService(settings=None)
    evaluator = RetrievalEvaluator(service=service)
    output = evaluator.evaluate(output_dir=ROOT / "backend" / "data" / "reports")

    summary = output["evaluation_report"]
    print("Evaluation Summary")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
