from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPO_ROOT = ROOT.parents[1]
API_ROOT = ROOT
BACKEND_ROOT = REPO_ROOT / "backend"

for path in (API_ROOT, BACKEND_ROOT, REPO_ROOT):
    resolved = str(path)
    if resolved not in sys.path:
        sys.path.insert(0, resolved)

os.chdir(REPO_ROOT)
from src.main import app  # noqa: E402


if __name__ == "__main__":
    import argparse
    from uvicorn import run

    parser = argparse.ArgumentParser(description="Run the GrantAI backend API.")
    parser.add_argument("--host", default=os.getenv("API_HOST", "0.0.0.0"), help="Host address to bind.")
    parser.add_argument("--port", type=int, default=int(os.getenv("API_PORT", "8000")), help="Port to bind.")
    parser.add_argument("--log-level", default=os.getenv("LOG_LEVEL", "info"), help="Uvicorn log level.")
    args = parser.parse_args()

    run(app, host=args.host, port=args.port, log_level=args.log_level)
