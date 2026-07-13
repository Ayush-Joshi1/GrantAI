from __future__ import annotations

from datetime import datetime, timezone


class HistoryService:
    async def list(self) -> list[dict]:
        # Placeholder: later read from audit log store.
        now = datetime.now(timezone.utc)
        return [
            {
                "type": "proposal",
                "title": "Generated proposal draft",
                "detail": "Placeholder history item.",
                "time": now,
            }
        ]

