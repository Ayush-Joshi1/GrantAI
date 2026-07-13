#!/usr/bin/env python3
"""List all foundation models available for the configured IBM watsonx.ai account and region."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from ibm_watsonx_ai import APIClient, Credentials


ROOT = Path(__file__).resolve().parent


def _load_env() -> None:
    load_dotenv(ROOT / ".env", override=False)
    load_dotenv(ROOT / "apps" / "web" / ".env", override=False)


def _get_env(name: str, fallback: str | None = None) -> str:
    value = os.getenv(name, fallback or "")
    return value.strip() if isinstance(value, str) else ""


def _extract_model_ids(payload: dict[str, Any]) -> list[str]:
    resources = payload.get("resources")
    if not isinstance(resources, list):
        raise RuntimeError("Unexpected IBM watsonx response format: missing resources list")

    ids: list[str] = []
    for item in resources:
        if isinstance(item, dict):
            model_id = item.get("model_id")
            if isinstance(model_id, str) and model_id:
                ids.append(model_id)
    return ids


def main() -> None:
    _load_env()

    api_key = _get_env("IBM_API_KEY") or _get_env("WATSONX_API_KEY") or _get_env("WATSONX_APIKEY")
    project_id = _get_env("PROJECT_ID") or _get_env("WATSONX_PROJECT_ID")
    url = _get_env("IBM_URL") or _get_env("WATSONX_URL") or "https://us-south.ml.cloud.ibm.com"

    if not api_key or not project_id:
        raise RuntimeError("IBM_API_KEY/PROJECT_ID must be set in the environment or .env file")

    credentials = Credentials(api_key=api_key, url=url)
    client = APIClient(credentials=credentials, project_id=project_id)

    response = client.foundation_models.get_model_specs()
    model_ids = _extract_model_ids(response)

    print(f"Discovered {len(model_ids)} model(s) for project {project_id} at {url}")
    print("=" * 80)
    for model_id in sorted(model_ids):
        is_granite = "granite" in model_id.lower()
        marker = "[GRANITE]" if is_granite else ""
        print(f"{model_id} {marker}".rstrip())


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
