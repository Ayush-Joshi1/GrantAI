from __future__ import annotations

import json
from pathlib import Path
import sys

WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
APPS_API_ROOT = Path(__file__).resolve().parents[1]
for candidate in (WORKSPACE_ROOT, APPS_API_ROOT, APPS_API_ROOT / "src"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from src.main import create_app


def main() -> None:
    app = create_app()
    openapi = app.openapi()
    filtered_paths = {
        "/api/v1/recommend": openapi["paths"]["/api/v1/recommend"],
        "/api/v1/eligibility/check": openapi["paths"]["/api/v1/eligibility/check"],
        "/api/v1/proposal/generate": openapi["paths"]["/api/v1/proposal/generate"],
        "/api/v1/deadline": openapi["paths"]["/api/v1/deadline"],
        "/api/v1/notifications": openapi["paths"]["/api/v1/notifications"],
    }
    orchestrate_schema = {
        **{k: v for k, v in openapi.items() if k != "paths"},
        "paths": filtered_paths,
    }
    target = APPS_API_ROOT / "openapi_orchestrate.json"
    target.write_text(json.dumps(orchestrate_schema, indent=2), encoding="utf-8")
    print(f"Wrote Orchestrate OpenAPI schema to {target}")


if __name__ == "__main__":
    main()
