from __future__ import annotations

from src.api.v1.schemas.common import SelectedGrantInput, StartupProfileInput


class ProposalPromptBuilder:
    """Build a focused proposal generation task from startup and grant context."""

    def build_task(self, *, startup_profile: StartupProfileInput, selected_grant: SelectedGrantInput, proposal_context: str | None = None) -> str:
        grant_name = self._optional_value(selected_grant.grant_name, "selected_grant")
        startup_name = self._optional_value(startup_profile.startup_name, "startup_name")
        description = self._optional_value(startup_profile.startup_description, "startup_description")
        sector = self._optional_value(startup_profile.sector, "sector/domain")
        stage = self._optional_value(startup_profile.startup_stage, "startup_stage")
        location = self._optional_value(startup_profile.location, "location")
        funding = self._optional_value(startup_profile.funding_required, "funding_required")
        founder_profile = self._optional_value(startup_profile.founder_profile, "founder_profile")
        additional_context = self._optional_value(startup_profile.additional_context, "additional_context")
        proposal_context_value = self._optional_value(proposal_context, "proposal_context")

        return f"""PROPOSAL GENERATION TASK
You are helping a founder prepare a grounded grant proposal draft for a selected Government grant scheme.

Selected grant:
- grant_name: {grant_name}

Startup information:
- startup_name: {startup_name}
- startup_description: {description}
- sector/domain: {sector}
- startup_stage: {stage}
- location: {location}
- funding_required: {funding}
- founder_profile: {founder_profile}
- additional_context: {additional_context}

Proposal-specific context:
- proposal_context: {proposal_context_value}

Instructions:
- Use the supplied startup information exactly as provided for startup-specific facts.
- Use retrieved Government evidence for grant-specific facts such as scheme objectives, funding purpose, and program fit.
- use retrieved Government evidence
- Do not invent startup achievements, revenue, customer counts, founder credentials, partnerships, patents, pilot results, or financial history.
- Do not invent startup metrics or founder details.
- do not invent startup achievements
- If founder information is missing, say that more founder input is needed rather than fabricating details.
- Create a clear proposal draft with sections such as Executive Summary, Problem Statement, Proposed Solution, Grant Alignment, Implementation Plan, Funding Use / Budget Rationale, Timeline, Expected Impact, and Information Needed From Founder.
- Use retrieved Government evidence to support grant-specific claims and keep the proposal grounded in the available context."""

    def _optional_value(self, value: str | None, label: str) -> str:
        if value is None or not value.strip():
            return f"{label}: not provided"
        return value.strip()
