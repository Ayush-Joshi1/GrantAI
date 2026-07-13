from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "apps" / "api"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import ModelInference

PROMPT = "Answer this question using only provided context. What are the eligibility requirements for the Startup India Seed Fund Scheme?"


def _normalize_url(raw_url: str | None) -> str:
    if not raw_url:
        return "https://us-south.ml.cloud.ibm.com"
    url = raw_url.strip()
    if url.startswith("https://"):
        return url
    if url.startswith("http://"):
        return f"https://{url[len('http://'):]}"
    return f"https://{url}"


def main() -> None:
    url = _normalize_url(os.getenv("WATSONX_URL") or os.getenv("IBM_URL"))
    api_key = os.getenv("WATSONX_API_KEY") or os.getenv("WATSONX_APIKEY") or os.getenv("IBM_API_KEY")
    project_id = os.getenv("WATSONX_PROJECT_ID") or os.getenv("PROJECT_ID")
    model_id = os.getenv("GRANITE_MODEL_ID") or os.getenv("WATSONX_MODEL_ID") or os.getenv("MODEL_ID") or "ibm/granite-8b-code-instruct"

    print("url", url)
    print("model_id", model_id)
    print("project_id_present", bool(project_id))
    print("api_key_present", bool(api_key))
    print("prompt_len", len(PROMPT))

    credentials = Credentials(url=url, api_key=api_key)
    client = ModelInference(
        model_id=model_id,
        credentials=credentials,
        project_id=project_id,
        params={"temperature": 0.1, "max_new_tokens": 200},
        validate=False,
    )
    response = client.generate(prompt=PROMPT)
    print("response_type", type(response))
    if hasattr(response, "to_dict"):
        try:
            payload = response.to_dict()
            print("payload keys", list(payload.keys()))
            print(payload)
        except Exception as exc:
            print("to_dict error", exc)
            print(response)
    else:
        print(response)


if __name__ == "__main__":
    main()
