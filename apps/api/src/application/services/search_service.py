from __future__ import annotations


class SearchService:
    async def search(self, *, query: str, limit: int) -> list[dict]:
        # Placeholder: later combine structured DB filtering + FAISS similarity search.
        return [
            {
                "grant_id": "grant_demo_001",
                "title": "Demo Grant Result",
                "snippet": f"Search placeholder for: {query}",
                "score": 1.0,
            }
        ][:limit]

