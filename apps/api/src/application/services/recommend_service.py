from __future__ import annotations


class RecommendService:
    async def recommend(self, *, query: str | None, limit: int) -> list[dict]:
        # Placeholder: later use profile signals + RAG + ML ranking model.
        return [
            {
                "grant_id": "grant_demo_001",
                "title": "DST Seed Support (Demo)",
                "score": 0.86,
                "reason": "Placeholder recommendation result.",
            }
        ][:limit]

