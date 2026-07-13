from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "apps" / "api"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from src.infrastructure.ibm.granite_client import GraniteClient
from src.prompts.rag.grounded_prompt_builder import GroundedPromptBuilder

QUERY = "What are the eligibility requirements for the Startup India Seed Fund Scheme?"

def main() -> None:
    settings = None
    granite_client = GraniteClient(settings=settings)
    builder = GroundedPromptBuilder()
    prompt = f"{builder._build_system_instruction()}\n\nUSER QUESTION\n{QUERY}"
    print(f"Prompt length: {len(prompt)}")
    print(prompt[:500])
    try:
        client = granite_client._build_inference_client()
        response = client.generate(prompt=prompt)
        print("RESPONSE TYPE", type(response))
        try:
            payload = response.to_dict()
            print("to_dict payload keys", list(payload.keys()))
            print(json.dumps(payload, indent=2, ensure_ascii=False)[:4000])
        except Exception as exc:
            print("to_dict failed", exc)
            try:
                print(repr(response)[:4000])
            except Exception as exc2:
                print("repr failed", exc2)
    except Exception as exc:
        print(type(exc).__name__, exc)


if __name__ == "__main__":
    main()
