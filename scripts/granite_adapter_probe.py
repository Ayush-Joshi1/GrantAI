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

from src.infrastructure.ibm.granite_client import GraniteClient

PROMPT = "Reply with exactly: GRANITE_OK"


def _load_env() -> None:
    load_dotenv(ROOT / ".env", override=False)
    load_dotenv(ROOT / "apps" / "web" / ".env", override=False)


def _normalize_url(raw_url: str | None) -> str:
    if not raw_url:
        return "https://us-south.ml.cloud.ibm.com"

    url = raw_url.strip()
    if url.startswith("https:https://"):
        url = url.replace("https:https://", "https://", 1)
    elif url.startswith("http://"):
        url = url.replace("http://", "https://", 1)
    elif not url.startswith("https://"):
        url = f"https://{url}"
    return url


def _safe_shape(value: Any, *, depth: int = 0) -> Any:
    if depth > 3:
        return "<MAX_DEPTH>"
    if isinstance(value, str):
        return "<REDACTED>" if "key" in value.lower() or "token" in value.lower() else value
    if isinstance(value, bytes):
        return f"<BYTES:{len(value)}>"
    if isinstance(value, dict):
        return {k: _safe_shape(v, depth=depth + 1) for k, v in list(value.items())[:10]}
    if isinstance(value, list):
        return [_safe_shape(item, depth=depth + 1) for item in value[:5]]
    if hasattr(value, "to_dict"):
        try:
            return _safe_shape(value.to_dict(), depth=depth + 1)
        except Exception:
            return f"<{value.__class__.__module__}.{value.__class__.__name__}>"
    if hasattr(value, "__dict__"):
        return f"<{value.__class__.__module__}.{value.__class__.__name__}>"
    return value


def _run_direct_sdk() -> dict[str, Any]:
    _load_env()

    api_key = (os.getenv("WATSONX_API_KEY") or os.getenv("WATSONX_APIKEY") or os.getenv("IBM_API_KEY") or "").strip()
    url = _normalize_url(os.getenv("WATSONX_URL") or os.getenv("IBM_URL"))
    project_id = (os.getenv("WATSONX_PROJECT_ID") or os.getenv("PROJECT_ID") or "").strip()
    model_id = (os.getenv("GRANITE_MODEL_ID") or os.getenv("WATSONX_MODEL_ID") or os.getenv("MODEL_ID") or "ibm/granite-8b-code-instruct").strip()

    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference

    credentials = Credentials(url=url, api_key=api_key)
    client = ModelInference(
        model_id=model_id,
        credentials=credentials,
        project_id=project_id,
        params={"temperature": 0.1},
        validate=False,
    )
    response = client.generate(prompt=PROMPT)
    return {
        "model_id": model_id,
        "url": url,
        "project_id_present": bool(project_id),
        "params": {"temperature": 0.1},
        "response_type": type(response).__name__,
        "response_shape": _safe_shape(response),
    }


def _run_adapter() -> dict[str, Any]:
    _load_env()
    client = GraniteClient(settings={})

    resolved_model_id = client._get_env_value("GRANITE_MODEL_ID", "WATSONX_MODEL_ID", "MODEL_ID") or "ibm/granite-8b-code-instruct"
    resolved_url = client._normalize_url(client._get_env_value("WATSONX_URL", "IBM_URL"))
    resolved_project_id = client._get_env_value("WATSONX_PROJECT_ID", "PROJECT_ID")
    resolved_api_key = client._get_env_value("WATSONX_API_KEY", "WATSONX_APIKEY", "IBM_API_KEY")
    try:
        response = client.generate(PROMPT)
        extraction = response
        status = "PASS"
    except Exception as exc:
        response = None
        extraction = f"{type(exc).__name__}: {exc}"
        status = "FAIL"

    return {
        "model_id": resolved_model_id,
        "url": resolved_url,
        "project_id_present": bool(resolved_project_id),
        "api_key_present": bool(resolved_api_key),
        "status": status,
        "response_type": type(response).__name__ if response is not None else None,
        "response_shape": _safe_shape(response) if response is not None else None,
        "extraction_result": extraction,
    }


if __name__ == "__main__":
    direct = _run_direct_sdk()
    adapter = _run_adapter()
    print("DIRECT_SDK")
    print(json.dumps(direct, indent=2, ensure_ascii=False))
    print("PRODUCTION_ADAPTER")
    print(json.dumps(adapter, indent=2, ensure_ascii=False))
