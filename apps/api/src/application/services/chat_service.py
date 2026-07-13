from __future__ import annotations

import uuid
from typing import Any

from src.core.errors.exceptions import UpstreamError
from src.infrastructure.ibm.assistant_client import WatsonxAssistantClient


class ChatService:
    def __init__(self, assistant_client: Any | None = None, fallback_service: Any | None = None, workflow_coordinator: Any | None = None) -> None:
        self.assistant_client = assistant_client or self._build_assistant_client()
        self.fallback_service = fallback_service
        self.workflow_coordinator = workflow_coordinator

    async def turn(self, *, session_id: str | None, message: str) -> dict:
        sid = session_id or str(uuid.uuid4())

        # Detect if the user intends a complete grant workflow. Simple heuristic: if message contains multiple capability keywords.
        if self.workflow_coordinator is not None:
            lowered = (message or "").lower()
            keywords = ["recommend", "eligib", "proposal", "deadline", "notification", "notify", "grant", "next steps", "help draft"]
            matches = sum(1 for k in keywords if k in lowered)
            if matches >= 2:
                try:
                    from src.api.v1.schemas.common import StartupProfileInput

                    profile = StartupProfileInput(startup_name=message)
                    result = self.workflow_coordinator.run_unified_workflow(startup_profile=profile, query=message)
                    # Format a readable reply
                    parts: list[str] = []
                    if result.startup_summary:
                        parts.append(f"Startup summary:\n{result.startup_summary}")
                    if result.recommendation is not None:
                        parts.append(f"Recommendations:\n{result.recommendation.answer}")
                    if result.eligibility is not None:
                        parts.append(f"Eligibility:\n{result.eligibility.answer}")
                    if result.proposal is not None:
                        parts.append(f"Proposal Draft:\n{result.proposal.answer}")
                    if result.deadlines is not None:
                        parts.append(f"Deadlines:\n{result.deadlines.answer}")
                    if result.notification is not None:
                        parts.append(f"Notifications:\n{result.notification.answer}")
                    if result.partial:
                        parts.append("Note: Some stages could not be completed; partial results returned.")

                    from src.application.services.unified_response_builder import UnifiedResponseBuilder

                    reply_text = UnifiedResponseBuilder.build_readable(result)
                    return {"session_id": sid, "reply": reply_text}
                except Exception:
                    pass

        if self.assistant_client is not None:
            try:
                reply = self.assistant_client.generate_reply(message, session_id=sid)
                if isinstance(reply, str) and reply.strip():
                    return {"session_id": sid, "reply": reply.strip()}
            except Exception as exc:
                if not isinstance(exc, UpstreamError):
                    raise

        if self.fallback_service is not None:
            try:
                response = self.fallback_service.answer(message)
                if isinstance(response, dict):
                    reply = response.get("answer") or response.get("reply")
                else:
                    reply = getattr(response, "answer", None)
                if isinstance(reply, str) and reply.strip():
                    return {"session_id": sid, "reply": reply.strip()}
            except Exception:
                pass

        return {"session_id": sid, "reply": "The chat service is currently unavailable. Please try again shortly."}

    def _build_assistant_client(self) -> Any | None:
        try:
            return WatsonxAssistantClient()
        except Exception:
            return None

