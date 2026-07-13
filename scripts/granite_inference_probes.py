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

from dotenv import load_dotenv
from ibm_watsonx_ai import APIClient, Credentials
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


def _safe_shape(value: Any, depth: int = 0) -> Any:
    if depth > 3:
        return "<MAX_DEPTH>"
    if isinstance(value, (str, int, float, bool)) or value is None:
        return type(value).__name__
    if isinstance(value, dict):
        return {k: _safe_shape(v, depth + 1) for k, v in list(value.items())[:20]}
    if isinstance(value, list):
        return [_safe_shape(v, depth + 1) for v in value[:5]]
    if hasattr(value, "to_dict"):
        try:
            return _safe_shape(value.to_dict(), depth + 1)
        except Exception:
            return f"<{value.__class__.__module__}.{value.__class__.__name__}>"
    return f"<{value.__class__.__module__}.{value.__class__.__name__}>"


def _print_section(title: str) -> None:
    print("\n" + "=" * 10 + f" {title} " + "=" * 10)


def _print_json(value: Any) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False))


def _capture_response(response: Any) -> dict[str, Any]:
    return {
        "type": type(response).__name__,
        "shape": _safe_shape(response),
        "repr": repr(response)[:2000],
    }


def _probe_generate(model_id: str, prompt: str) -> dict[str, Any]:
    client = ModelInference(
        model_id=model_id,
        credentials=Credentials(api_key=API_KEY, url=URL),
        project_id=PROJECT_ID,
        params={"temperature": 0.1},
        validate=False,
    )
    response = client.generate(prompt=prompt)
    result = {
        "method": "generate",
        "response": _capture_response(response),
    }
    if isinstance(response, dict):
        results = response.get("results")
        if isinstance(results, list) and results:
            first = results[0]
            if isinstance(first, dict):
                result["generated_text"] = first.get("generated_text")
                result["text"] = first.get("text")
                result["stop_reason"] = first.get("stop_reason")
                result["generated_text_len"] = len(first.get("generated_text") or "")
    return result


def _probe_generate_text(model_id: str, prompt: str) -> dict[str, Any]:
    client = ModelInference(
        model_id=model_id,
        credentials=Credentials(api_key=API_KEY, url=URL),
        project_id=PROJECT_ID,
        params={"temperature": 0.1},
        validate=False,
    )
    response = client.generate_text(prompt=prompt, params={"temperature": 0.1})
    result = {
        "method": "generate_text",
        "response": _capture_response(response),
    }
    if isinstance(response, str):
        result["generated_text"] = response
        result["generated_text_len"] = len(response)
    elif isinstance(response, dict):
        result["generated_text_len"] = len(response.get("generated_text", "") or "")
    return result


def _probe_chat(model_id: str, messages: list[dict[str, str]]) -> dict[str, Any]:
    client = ModelInference(
        model_id=model_id,
        credentials=Credentials(api_key=API_KEY, url=URL),
        project_id=PROJECT_ID,
        params={"temperature": 0.1},
        validate=False,
    )
    response = client.chat(messages=messages)
    result = {
        "method": "chat",
        "response": _capture_response(response),
    }
    if isinstance(response, dict):
        if "output" in response:
            result["output"] = _safe_shape(response["output"])
        if "messages" in response:
            result["messages"] = _safe_shape(response["messages"])
    return result


def main() -> None:
    global API_KEY, PROJECT_ID, URL
    _load_env()
    API_KEY = _get_env("IBM_API_KEY") or _get_env("WATSONX_API_KEY") or _get_env("WATSONX_APIKEY")
    PROJECT_ID = _get_env("PROJECT_ID") or _get_env("WATSONX_PROJECT_ID")
    URL = _normalize_url(_get_env("IBM_URL") or _get_env("WATSONX_URL"))
    MODEL_ID = _get_env("MODEL_ID") or _get_env("GRANITE_MODEL_ID") or _get_env("WATSONX_MODEL_ID") or "ibm/granite-8b-code-instruct"

    print("current_model_id", MODEL_ID)
    print("project_id_present", bool(PROJECT_ID))
    print("api_key_present", bool(API_KEY))
    print("url", URL)

    _print_section("SDK CAPABILITIES")
    import ibm_watsonx_ai
    print("ibm_watsonx_ai version", getattr(ibm_watsonx_ai, "__version__", "unknown"))
    print("ModelInference generate", sys.modules['ibm_watsonx_ai.foundation_models.inference.model_inference'].ModelInference.generate)
    print("ModelInference generate_text", sys.modules['ibm_watsonx_ai.foundation_models.inference.model_inference'].ModelInference.generate_text)
    print("ModelInference chat", sys.modules['ibm_watsonx_ai.foundation_models.inference.model_inference'].ModelInference.chat)
    print("ModelInference chat_stream", sys.modules['ibm_watsonx_ai.foundation_models.inference.model_inference'].ModelInference.chat_stream)

    _print_section("AVAILABLE GRANITE MODELS")
    creds = Credentials(api_key=API_KEY, url=URL)
    api_client = APIClient(credentials=creds, project_id=PROJECT_ID)
    specs = api_client.foundation_models.get_model_specs()
    granite_models = []
    for item in specs.get("resources", []):
        if isinstance(item, dict) and "granite" in item.get("model_id", "").lower():
            granite_models.append({
                "model_id": item.get("model_id"),
                "label": item.get("label"),
                "lifecycle": item.get("lifecycle"),
                "functions": item.get("functions"),
                "tasks": item.get("tasks"),
                "task_ids": item.get("task_ids"),
                "type": item.get("type"),
                "support": item.get("support"),
                "short_description": item.get("short_description"),
                "long_description": item.get("long_description"),
            })
    _print_json(granite_models)

    current_model_info = [item for item in granite_models if item["model_id"] == MODEL_ID]
    _print_section("CURRENT MODEL INFO")
    _print_json(current_model_info)

    prompt = (
        "SYSTEM INSTRUCTION\n"
        "You are GrantAI, an AI assistant for Indian Government grant discovery and funding guidance.\n"
        "Answer the user's question only using supplied Government grant context.\n"
        "Do not invent grant facts.\n\n"
        "USER QUESTION\nWhat are the eligibility requirements for the Startup India Seed Fund Scheme?"
    )

    _print_section("PROBE 1 - generate")
    try:
        result = _probe_generate(MODEL_ID, prompt)
        _print_json(result)
    except Exception as exc:
        print("PROBE 1 ERROR", type(exc).__name__, exc)

    _print_section("PROBE 2 - generate_text")
    try:
        result = _probe_generate_text(MODEL_ID, prompt)
        _print_json(result)
    except Exception as exc:
        print("PROBE 2 ERROR", type(exc).__name__, exc)

    _print_section("PROBE 3 - chat")
    try:
        messages = [
            {"role": "system", "content": "You are GrantAI, an AI assistant for Indian Government grant discovery and funding guidance. Answer only using supplied Government grant context. Do not invent grant facts."},
            {"role": "user", "content": "What are the eligibility requirements for the Startup India Seed Fund Scheme?"},
        ]
        result = _probe_chat(MODEL_ID, messages)
        _print_json(result)
    except Exception as exc:
        print("PROBE 3 ERROR", type(exc).__name__, exc)


if __name__ == "__main__":
    main()
