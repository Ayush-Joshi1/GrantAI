from __future__ import annotations

from src.api.v1.schemas.common import SelectedGrantInput


class DeadlinePromptBuilder:
    """Build a focused deadline-analysis task from grant context and any deadline hints."""

    def build_task(self, *, selected_grant: SelectedGrantInput, deadline_context: str | None = None) -> str:
        grant_name = self._optional_value(selected_grant.grant_name, "grant_name")
        grant_context_block = f"Selected grant:\n- grant_name: {grant_name}"

        if deadline_context and deadline_context.strip():
            deadline_hint = self._optional_value(deadline_context, "deadline_context")
            grant_context_block += f"\n- deadline_context: {deadline_hint}"

        return f"""DEADLINE ANALYSIS TASK
You are helping a founder understand the application deadlines for a selected Government grant scheme.

{grant_context_block}

Instructions:
- Focus on the application deadline for the selected grant.
- Distinguish the application deadline from the notification date.
- Distinguish the application deadline from the publication or guideline date.
- Distinguish the application deadline from the scheme duration.
- Support application-window analysis.
- Do not invent a deadline or date.
- do not invent dates
- Do not automatically treat a historical deadline as current.
- Do not claim that applications are currently open without supporting evidence.
- State that the deadline is unknown or not established when the evidence is insufficient.
- Do not calculate days remaining from an unsupported date.
- Analyze timing only for the explicitly selected grant.
- If a concrete deadline is not clearly present in the retrieved context, say so clearly.
- If the query includes a deadline hint, treat it as a clue only and verify it against the retrieved evidence.
- Use a careful, evidence-first tone and explicitly flag when the retrieved context is insufficient.
- Highlight the difference between application deadlines and other dates such as notification date, publication date, scheme duration, historical/current deadline caution, and other dates that may be mentioned.
- When possible, mention how many days remain until the deadline if the retrieved evidence supports a precise date.
- If the retrieved context does not support a precise day count, clearly state that days remaining cannot be determined.
- Do not infer deadlines from prior knowledge or from unrelated grant schemes.

Provide a grounded deadline analysis based only on the retrieved Government grant context."""

    def _optional_value(self, value: str | None, label: str) -> str:
        if value is None or not value.strip():
            return f"{label}: not provided"
        return value.strip()
