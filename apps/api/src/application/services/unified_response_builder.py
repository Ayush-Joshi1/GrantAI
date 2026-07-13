from __future__ import annotations

from typing import Any

from src.application.services.workflow_coordinator import UnifiedWorkflowResult


class UnifiedResponseBuilder:
    @staticmethod
    def build_readable(result: UnifiedWorkflowResult) -> str:
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
        return "\n\n".join(parts) if parts else "No results available."
