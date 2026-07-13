from __future__ import annotations

import inspect
import json
import os
import sys
from pathlib import Path

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


def main() -> None:
    _load_env()
    api_key = _get_env("IBM_API_KEY") or _get_env("WATSONX_API_KEY") or _get_env("WATSONX_APIKEY")
    project_id = _get_env("PROJECT_ID") or _get_env("WATSONX_PROJECT_ID")
    url = _normalize_url(_get_env("IBM_URL") or _get_env("WATSONX_URL"))
    model_id = _get_env("MODEL_ID") or _get_env("GRANITE_MODEL_ID") or _get_env("WATSONX_MODEL_ID") or "ibm/granite-8b-code-instruct"

    print(json.dumps({
        "current_model_id": model_id,
        "project_id_present": bool(project_id),
        "api_key_present": bool(api_key),
        "url": url,
    }, indent=2))

    print("\n--- SDK CAPABILITIES ---")
    print("ibm_watsonx_ai version", getattr(sys.modules.get('ibm_watsonx_ai'), '__version__', 'unknown'))
    print("ModelInference source", inspect.getsourcefile(ModelInference))
    for name in ["generate", "generate_text", "chat", "chat_stream", "chat_completion", "complete"]:
        if hasattr(ModelInference, name):
            print(name, inspect.signature(getattr(ModelInference, name)))

    print("\n--- CURRENT MODEL METADATA ---")
    credentials = Credentials(api_key=api_key, url=url)
    client = APIClient(credentials=credentials, project_id=project_id)
    response = client.foundation_models.get_model_specs()
    model_infos = []
    for item in response.get("resources", []):
        if isinstance(item, dict) and item.get("model_id") == model_id:
            model_infos.append(item)
    print(json.dumps(model_infos, indent=2, ensure_ascii=False))

    print("\n--- RELEVANT GRANITE MODELS ---")
    granite_models = []
    for item in response.get("resources", []):
        if isinstance(item, dict) and "granite" in item.get("model_id", "").lower():
            granite_models.append({
                "model_id": item.get("model_id"),
                "name": item.get("name"),
                "family": item.get("family"),
                "lifecycle": item.get("lifecycle"),
                "type": item.get("type"),
                "support": item.get("support"),
                "capabilities": item.get("capabilities"),
                "task": item.get("task"),
                "description": item.get("description"),
            })
    print(json.dumps(granite_models, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
