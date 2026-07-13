#!/usr/bin/env python3
"""Smoke test for IBM Granite connectivity using the existing project environment."""
from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv


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


def main() -> None:
    _load_env()

    api_key = (os.getenv("WATSONX_API_KEY") or os.getenv("WATSONX_APIKEY") or os.getenv("IBM_API_KEY") or "").strip()
    url = _normalize_url(os.getenv("WATSONX_URL") or os.getenv("IBM_URL"))
    project_id = (os.getenv("WATSONX_PROJECT_ID") or os.getenv("PROJECT_ID") or "").strip()
    model_id = (os.getenv("GRANITE_MODEL_ID") or os.getenv("WATSONX_MODEL_ID") or os.getenv("MODEL_ID") or "ibm/granite-8b-code-instruct").strip()

    if not api_key or not project_id:
        raise RuntimeError("Missing IBM watsonx credentials. Set WATSONX_API_KEY/WATSONX_PROJECT_ID or IBM_API_KEY/PROJECT_ID in the environment.")

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

    prompt = "What is Startup India?"
    response = client.generate(prompt=prompt)

    print("Connection successful")
    print(f"Model ID: {model_id}")
    print(f"Question: {prompt}")
    print(f"Granite response: {response}")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
