from __future__ import annotations

import uuid


class ProfileService:
    async def upsert(self, payload: dict) -> dict:
        # Placeholder: later persist to Postgres.
        return {"profile_id": str(uuid.uuid4()), **payload}

