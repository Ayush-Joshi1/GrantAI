from __future__ import annotations

from src.api.v1.schemas.common import SelectedGrantInput


class NotificationPromptBuilder:
    """Build a focused notification-generation task from grant context and action hints."""

    def build_task(
        self,
        *,
        selected_grant: SelectedGrantInput | None = None,
        grant_context: str | None = None,
        deadline_context: str | None = None,
        action_context: str | None = None,
        notification_preferences: str | None = None,
    ) -> str:
        grant_name = self._optional_value(selected_grant.grant_name if selected_grant else None, "grant_name")

        context_sections: list[str] = [f"Selected grant:\n- grant_name: {grant_name}"]

        if self._has_content(grant_context):
            context_sections.append(f"\nSupplied grant context:\n- grant_context: {grant_context.strip()}")

        if self._has_content(deadline_context):
            context_sections.append(f"\nSupplied deadline context:\n- deadline_context: {deadline_context.strip()}")

        if self._has_content(action_context):
            context_sections.append(f"\nSupplied action context:\n- action_context: {action_context.strip()}")

        if self._has_content(notification_preferences):
            context_sections.append(f"\nNotification preferences:\n- notification_preferences: {notification_preferences.strip()}")

        return f"""NOTIFICATION TASK
You are a Government grant action-reminder and notification assistant.

{"\n\n".join(context_sections)}

Instructions:
- Generate a useful government-grant action notification for the selected grant only.
- Use only the supplied request context and retrieved Government evidence.
- Do not invent a deadline or date.
- Do not invent days remaining.
- Do not claim the application is incomplete unless the supplied action context establishes that fact.
- Do not invent missing documents.
- Do not claim confirmed eligibility.
- Do not invent approval or rejection status.
- Do not create false urgency.
- Match urgency to supported timing or action information only.
- If current deadline information is not established, communicate that clearly and advise the user to verify the official application window.
- If the evidence is insufficient, state that clearly and recommend a cautious next action.
- Do not make unsupported eligibility or application-status claims.
- Do not fabricate funding amounts or application-window status.
- Provide a useful next action.
- If timing is incomplete, handle it cautiously rather than manufacturing urgency.

Provide a grounded, evidence-based notification message based only on the retrieved Government grant context."""

    def _optional_value(self, value: str | None, label: str) -> str:
        if value is None or not value.strip():
            return f"{label}: not provided"
        return value.strip()

    def _has_content(self, value: str | None) -> bool:
        return value is not None and bool(value.strip())
