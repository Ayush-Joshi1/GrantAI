from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "apps" / "api"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from backend.rag.config import get_rag_settings
from src.application.services.rag_answer_service import RAGAnswerService
from src.prompts.rag.grounded_prompt_builder import GroundedPromptBuilder

QUERY = "What are the eligibility requirements for the Startup India Seed Fund Scheme?"
OUTPUT_FILE = ROOT / "diagnostic_grounded_prompt.txt"


def main() -> None:
    settings = get_rag_settings()
    service = RAGAnswerService(settings=settings)
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
        preview = content[:200].replace("\n", " ").replace("\r", " ")
        source_document = result.metadata.get("file_name") or result.metadata.get("source_document") or result.metadata.get("source_url")
        print(json.dumps({
            "rank": idx,
            "chunk_id": result.chunk_id,
            "score": result.score,
            "grant_name": result.metadata.get("grant_name"),
            "organization": result.metadata.get("organization"),
            "source_document": source_document,
            "page_number": result.metadata.get("page_number"),
            "content_length": len(content),
            "preview": preview,
        }, ensure_ascii=False))

    builder = GroundedPromptBuilder()
    prompt = builder.build_prompt(QUERY, results)
    prompt_type = type(prompt).__name__
    prompt_chars = len(prompt)
    prompt_bytes = len(prompt.encode("utf-8"))
    system_token = "SYSTEM INSTRUCTION"
    context_token = "RETRIEVED GOVERNMENT GRANT CONTEXT"
    user_token = "USER QUESTION"
    print("prompt_type", prompt_type)
    print("prompt_char_length", prompt_chars)
    print("prompt_byte_length", prompt_bytes)
    print("retrieval_context_count", len(results))
    print("system_instruction_present", system_token in prompt)
    print("retrieved_context_present", context_token in prompt)
    print("user_question_present", user_token in prompt)
    print("system_instruction_count", prompt.count(system_token))
    print("retrieved_context_count_marker", prompt.count(context_token))
    print("user_question_count", prompt.count(user_token))
    print("has_null_bytes", "\x00" in prompt)
    print("has_binary_chars", any(ord(ch) > 0x7F for ch in prompt[:500]))
    if "SYSTEM INSTRUCTION:" in prompt and "RETRIEVED GOVERNMENT GRANT CONTEXT:" in prompt:
        system_section = prompt.split("SYSTEM INSTRUCTION:", 1)[1].split("RETRIEVED GOVERNMENT GRANT CONTEXT:", 1)[0]
        print("system_section_length", len(system_section))
    if "RETRIEVED GOVERNMENT GRANT CONTEXT:" in prompt and "USER QUESTION:" in prompt:
        retrieved_section = prompt.split("RETRIEVED GOVERNMENT GRANT CONTEXT:", 1)[1].split("USER QUESTION:", 1)[0]
        print("retrieved_section_length", len(retrieved_section))
    if "USER QUESTION:" in prompt:
        user_section = prompt.split("USER QUESTION:", 1)[1]
        print("user_section_length", len(user_section))

    OUTPUT_FILE.write_text(prompt, encoding="utf-8")
    print("prompt_snapshot", str(OUTPUT_FILE))


if __name__ == "__main__":
    main()
