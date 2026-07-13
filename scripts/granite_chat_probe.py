from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "apps" / "api"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from dotenv import load_dotenv
from backend.rag.config import get_rag_settings
from backend.rag.interfaces import RetrievalResult
from src.application.services.rag_answer_service import RAGAnswerService
from src.infrastructure.ibm.granite_client import GraniteClient
from src.prompts.rag.grounded_prompt_builder import GroundedPromptBuilder
from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference


def _load_env() -> None:
    load_dotenv(ROOT / "apps" / "web" / ".env", override=False)
    load_dotenv(ROOT / ".env", override=False)


def _get_env(name: str, fallback: str | None = None) -> str:
    value = os.getenv(name, fallback or "")
    return value.strip() if isinstance(value, str) else ""


def _normalize_url(raw_url: str | None) -> str:
    if not raw_url:
        return "https://us-south.ml.cloud.ibm.com"
    url = raw_url.strip()
    if url.startswith("https:https://"):
        return url.replace("https:https://", "https://", 1)
    if url.startswith("http://"):
        return url.replace("http://", "https://", 1)
    if not url.startswith("https://"):
        return f"https://{url}"
    return url


def _build_prompt(query: str, results: list[RetrievalResult]) -> str:
    builder = GroundedPromptBuilder()
    return builder.build_prompt(query, results)


def _build_chat_messages(prompt: str) -> list[dict[str, str]]:
    system_marker = "SYSTEM INSTRUCTION"
    user_marker = "USER QUESTION"
    if system_marker in prompt and user_marker in prompt:
        system_part = prompt.split(system_marker, 1)[1].split(user_marker, 1)[0].strip()
        user_part = prompt.split(user_marker, 1)[1].strip()
        return [
            {"role": "system", "content": system_part},
            {"role": "user", "content": user_part},
        ]
    return [{"role": "user", "content": prompt}]


def main() -> None:
    _load_env()
    settings = get_rag_settings()
    query = "What are the eligibility requirements for the Startup India Seed Fund Scheme?"
    service = RAGAnswerService(settings=settings)
    results = service.retrieval_client.retrieve(query=query, top_k=settings.top_k, similarity_threshold=settings.similarity_threshold)
    prompt = _build_prompt(query, results[:1])
    print("prompt_length", len(prompt))
    print(prompt[:1200])

    api_key = _get_env("IBM_API_KEY") or _get_env("WATSONX_API_KEY") or _get_env("WATSONX_APIKEY")
    project_id = _get_env("PROJECT_ID") or _get_env("WATSONX_PROJECT_ID")
    url = _normalize_url(_get_env("IBM_URL") or _get_env("WATSONX_URL"))
    model_id = _get_env("MODEL_ID") or _get_env("GRANITE_MODEL_ID") or _get_env("WATSONX_MODEL_ID") or "ibm/granite-8b-code-instruct"

    client = ModelInference(model_id=model_id, credentials=Credentials(api_key=api_key, url=url), project_id=project_id, params={"temperature": 0.1}, validate=False)
    messages = _build_chat_messages(prompt)
    print(json.dumps(messages, indent=2, ensure_ascii=False))
    response = client.chat(messages=messages)
    print("response type", type(response))
    print(json.dumps(_safe_response(response), indent=2, ensure_ascii=False))
    if isinstance(response, dict):
        choices = response.get("choices")
        if isinstance(choices, list) and choices:
            choice = choices[0]
            if isinstance(choice, dict):
                print("assistant content:", choice.get("message", {}).get("content"))
                print("finish_reason:", choice.get("finish_reason"))


def _safe_response(value: Any, depth: int = 0) -> Any:
    if depth > 2:
        return "<MAX_DEPTH>"
    if isinstance(value, dict):
        return {k: _safe_response(v, depth+1) for k, v in list(value.items())[:20]}
    if isinstance(value, list):
        return [_safe_response(v, depth+1) for v in value[:5]]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


if __name__ == "__main__":
    main()
