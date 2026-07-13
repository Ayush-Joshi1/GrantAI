from __future__ import annotations

import sys
from pathlib import Path

# Ensure repository root and apps/api are on sys.path for imports during pytest collection
ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "apps" / "api"):
    p = str(candidate)
    if p not in sys.path:
        sys.path.insert(0, p)
