from __future__ import annotations

from src.api.v1.schemas.common import StartupProfileInput


class GrantRecommendationPromptBuilder:
    """Build a focused recommendation task from startup profile context."""

    def build_task(self, *, startup_profile: StartupProfileInput, query: str) -> str:
        startup_name = self._optional_value(startup_profile.startup_name, "startup_name")
        description = self._optional_value(startup_profile.startup_description, "startup_description")
        sector = self._optional_value(startup_profile.sector, "sector/domain")
        stage = self._optional_value(startup_profile.startup_stage, "startup_stage")
        location = self._optional_value(startup_profile.location, "location")
        funding = self._optional_value(startup_profile.funding_required, "funding_required")
        founder_profile = self._optional_value(startup_profile.founder_profile, "founder_profile")
        additional_context = self._optional_value(startup_profile.additional_context, "additional_context")

        return f"""GRANT RECOMMENDATION TASK
You are helping a founder identify relevant Government grant schemes from the available trusted grant context.

Analyze the startup profile below and create a grounded recommendation response.

Startup profile:
- startup_name: {startup_name}
- startup_description: {description}
- sector/domain: {sector}
- startup_stage: {stage}
- location: {location}
- funding_required: {funding}
- founder_profile: {founder_profile}
- additional_context: {additional_context}

Instructions:
- Identify relevant Government grant schemes from the retrieved evidence.
- Explain why each recommendation is relevant to the startup profile.
- Distinguish recommendations from confirmed eligibility.
- Describe practical founder next actions based on the retrieved evidence.
- Avoid inventing grant information, funding amounts, deadlines, eligibility criteria, or organizations.
- If the retrieved context is insufficient, clearly say so.

User request:
{query}"""

    def _optional_value(self, value: str | None, label: str) -> str:
        if value is None or not value.strip():
            return f"{label}: not provided"
        return value.strip()
