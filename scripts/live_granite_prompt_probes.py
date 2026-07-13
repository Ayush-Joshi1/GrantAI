from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "apps" / "api"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from backend.rag.config import get_rag_settings
from src.application.services.rag_answer_service import RAGAnswerService
from src.infrastructure.ibm.granite_client import GraniteClient
from src.prompts.rag.grounded_prompt_builder import GroundedPromptBuilder

QUERY = "What are the eligibility requirements for the Startup India Seed Fund Scheme?"


def _safe_shape(value: Any, depth: int = 0) -> Any:
    if depth > 3:
        return "<MAX_DEPTH>"
    if isinstance(value, str):
        return "<STR>"
    if isinstance(value, dict):
        return {k: _safe_shape(v, depth + 1) for k, v in list(value.items())[:10]}
    if isinstance(value, list):
        return [_safe_shape(v, depth + 1) for v in value[:5]]
    if hasattr(value, "to_dict"):
        try:
            return _safe_shape(value.to_dict(), depth + 1)
        except Exception:
            return f"<{value.__class__.__module__}.{value.__class__.__name__}>"
    return f"<{value.__class__.__module__}.{value.__class__.__name__}>"


def _probe(client: GraniteClient, prompt: str, label: str, capture_raw: bool = False) -> dict[str, Any]:
    result: dict[str, Any] = {
        "label": label,
        "prompt_length": len(prompt),
        "prompt_bytes": len(prompt.encode("utf-8")),
    }

    original_extract = GraniteClient._extract_generated_text
    raw_info: dict[str, Any] = {}

    def instrumented_extract(self, response: Any) -> str:
        raw_info["raw_type"] = type(response).__name__
        if isinstance(response, dict):
            raw_info["top_keys"] = list(response.keys())
            if "results" in response and isinstance(response["results"], list):
                raw_info["results_len"] = len(response["results"])
                if response["results"]:
                    first = response["results"][0]
                    raw_info["first_result_type"] = type(first).__name__
                    if isinstance(first, dict):
                        raw_info["first_result_keys"] = list(first.keys())
                        raw_info["generated_text_exists"] = "generated_text" in first
                        raw_info["generated_text_len"] = len(first.get("generated_text", "")) if isinstance(first.get("generated_text"), str) else None
                        raw_info["stop_reason"] = first.get("stop_reason")
        elif hasattr(response, "to_dict"):
            raw_info["to_dict_exists"] = True
        raw_info["shape"] = _safe_shape(response)
        return original_extract(self, response)

    if capture_raw:
        GraniteClient._extract_generated_text = instrumented_extract

    try:
        generated = client.generate(prompt)
        result["status"] = "PASS"
        result["generated_text_length"] = len(generated)
        result["generated_text_preview"] = generated[:120].replace("\n", " ").replace("\r", " ")
    except Exception as exc:
        result["status"] = "FAIL"
        result["exception"] = f"{type(exc).__name__}: {exc}"
    finally:
        if capture_raw:
            GraniteClient._extract_generated_text = original_extract
            result["raw_response"] = raw_info

    return result


def main() -> None:
    settings = get_rag_settings()
    service = RAGAnswerService(settings=settings)
    builder = GroundedPromptBuilder()
    granite_client = GraniteClient(settings=settings)

    print("QUERY", QUERY)
    print(f"top_k={settings.top_k}")
    print(f"similarity_threshold={settings.similarity_threshold}")

    results = service.retrieval_client.retrieve(
        query=QUERY,
        top_k=settings.top_k,
        similarity_threshold=settings.similarity_threshold,
    )

    print("retrieval_count", len(results))
    for idx, result in enumerate(results, start=1):
        content = result.content or ""
        print(json.dumps({
            "rank": idx,
            "chunk_id": result.chunk_id,
            "score": result.score,
            "grant_name": result.metadata.get("grant_name"),
            "organization": result.metadata.get("organization"),
            "source_document": result.metadata.get("file_name") or result.metadata.get("source_document") or result.metadata.get("source_url"),
            "page_number": result.metadata.get("page_number"),
            "content_length": len(content),
            "preview": content[:200].replace("\n", " ").replace("\r", " "),
        }, ensure_ascii=False))

    probe_prompts: dict[str, str] = {}
    probe_prompts["A - tiny"] = "Reply with exactly: GRANITE_OK"
    probe_prompts["B - instruction+question"] = f"{builder._build_system_instruction()}\n\nUSER QUESTION\n{QUERY}"
    probe_prompts["C - top1"] = builder.build_prompt(QUERY, results[:1])
    probe_prompts["D - top2"] = builder.build_prompt(QUERY, results[:2])
    probe_prompts["E - top3"] = builder.build_prompt(QUERY, results[:3])
    probe_prompts["F - top5"] = builder.build_prompt(QUERY, results)

    first_failing_label = None
    outcomes = []
    for label, prompt in probe_prompts.items():
        capture_raw = False
        if label == "B - instruction+question":
            capture_raw = True
        outcome = _probe(granite_client, prompt, label, capture_raw=capture_raw)
        outcomes.append(outcome)
        print(json.dumps(outcome, indent=2, ensure_ascii=False))
        if outcome["status"] == "FAIL" and first_failing_label is None:
            first_failing_label = label

    if first_failing_label:
        print("first_failing_probe", first_failing_label)


if __name__ == "__main__":
    main()
