from __future__ import annotations

from src.api.v1.schemas.common import SelectedGrantInput, StartupProfileInput


class EligibilityPromptBuilder:
    """Build a focused eligibility analysis task from startup and grant context."""

    def build_task(self, *, startup_profile: StartupProfileInput, selected_grant: SelectedGrantInput) -> str:
        grant_name = self._optional_value(selected_grant.grant_name, "selected_grant")
        startup_name = self._optional_value(startup_profile.startup_name, "startup_name")
        description = self._optional_value(startup_profile.startup_description, "startup_description")
        sector = self._optional_value(startup_profile.sector, "sector/domain")
        stage = self._optional_value(startup_profile.startup_stage, "startup_stage")
        location = self._optional_value(startup_profile.location, "location")
        funding = self._optional_value(startup_profile.funding_required, "funding_required")
        founder_profile = self._optional_value(startup_profile.founder_profile, "founder_profile")
        additional_context = self._optional_value(startup_profile.additional_context, "additional_context")

        return f"""ELIGIBILITY ANALYSIS TASK
You are helping a founder assess whether a startup appears to meet the eligibility requirements of a selected Government grant scheme.

Selected grant:
- grant_name: {grant_name}

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
- Compare the startup profile only against the retrieved eligibility requirements for the selected grant.
- Clearly separate confirmed matches from missing information and unmet requirements.
- Do not mark a requirement as met unless the startup profile and retrieved context support it.
- Do not treat missing information as a confirmed match.
- Do not treat missing information as an unmet requirement.
- Avoid inventing grant requirements, eligibility criteria, funding amounts, deadlines, or organization details.
- If the retrieved context is insufficient, clearly say so.

Provide a grounded eligibility analysis based only on the retrieved Government grant context."""

    def _optional_value(self, value: str | None, label: str) -> str:
        if value is None or not value.strip():
            return f"{label}: not provided"
        return value.strip()
