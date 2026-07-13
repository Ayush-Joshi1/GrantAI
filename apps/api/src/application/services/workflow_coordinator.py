from __future__ import annotations

from dataclasses import dataclass
import logging
from typing import Any

from src.api.v1.schemas.common import SelectedGrantInput, StartupProfileInput
from src.core.errors.exceptions import UpstreamError, ValidationError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.application.services.grant_recommendation_service import GrantRecommendationService, GrantRecommendationResult
    from src.application.services.eligibility_service import EligibilityService, EligibilityResult
    from src.application.services.proposal_service import ProposalGenerationService, ProposalGenerationResult
    from src.application.services.deadline_service import DeadlineService, DeadlineResult
    from src.application.services.notification_service import NotificationService, NotificationResult


@dataclass(frozen=True)
class UnifiedWorkflowResult:
    startup_summary: str | None
    recommendation: GrantRecommendationResult | None
    eligibility: EligibilityResult | None
    proposal: ProposalGenerationResult | None
    deadlines: DeadlineResult | None
    notification: NotificationResult | None
    partial: bool = False
    errors: dict[str, str] = None


class WorkflowCoordinator:
    """Coordinate existing GrantAI services into a sequential unified workflow."""

    def __init__(
        self,
        recommend_service: Any | None = None,
        eligibility_service: Any | None = None,
        proposal_service: Any | None = None,
        deadline_service: Any | None = None,
        notification_service: Any | None = None,
    ) -> None:
        # Import and instantiate heavy services lazily to avoid import-time dependency failures in test collection
        if recommend_service is None:
            from src.application.services.grant_recommendation_service import GrantRecommendationService

            recommend_service = GrantRecommendationService()
        if eligibility_service is None:
            from src.application.services.eligibility_service import EligibilityService

            eligibility_service = EligibilityService()
        if proposal_service is None:
            from src.application.services.proposal_service import ProposalGenerationService

            proposal_service = ProposalGenerationService()
        if deadline_service is None:
            from src.application.services.deadline_service import DeadlineService

            deadline_service = DeadlineService()
        if notification_service is None:
            from src.application.services.notification_service import NotificationService

            notification_service = NotificationService()

        self.recommend_service = recommend_service
        self.eligibility_service = eligibility_service
        self.proposal_service = proposal_service
        self.deadline_service = deadline_service
        self.notification_service = notification_service

    def run_unified_workflow(self, *, startup_profile: StartupProfileInput | None = None, query: str | None = None) -> UnifiedWorkflowResult:
        logger = logging.getLogger("api.application.workflow")
        logger.info("Unified workflow started", extra={"query": (query or '')[:200]})
        errors: dict[str, str] = {}
        partial = False

        # Stage 1: Recommendation
        try:
            rec = self.recommend_service.recommend(startup_profile=startup_profile or StartupProfileInput(), query=query)
            startup_summary = rec.answer
        except Exception as exc:  # pragma: no cover - orchestration error handling
            errors["recommendation"] = str(exc)
            rec = None
            startup_summary = None
            partial = True

        # Determine a selected grant for downstream stages
        selected_grant = None
        if rec and rec.sources:
            first = rec.sources[0]
            if first and first.grant_name:
                selected_grant = SelectedGrantInput(grant_name=first.grant_name, organization=first.organization, grant_context=None)

        # Stage 2: Eligibility
        try:
            elig = None
            if selected_grant is not None:
                elig = self.eligibility_service.check(startup_profile=startup_profile or StartupProfileInput(), selected_grant=selected_grant)
            else:
                elig = None
        except Exception as exc:  # pragma: no cover - orchestration error handling
            errors["eligibility"] = str(exc)
            elig = None
            partial = True

        # Stage 3: Proposal
        try:
            proposal = None
            if selected_grant is not None:
                proposal = self.proposal_service.generate(startup_profile=startup_profile or StartupProfileInput(), selected_grant=selected_grant)
            else:
                proposal = None
        except Exception as exc:  # pragma: no cover - orchestration error handling
            errors["proposal"] = str(exc)
            proposal = None
            partial = True

        # Stage 4: Deadlines
        try:
            deadlines = None
            if selected_grant is not None:
                deadlines = self.deadline_service.analyze(selected_grant=selected_grant)
            else:
                deadlines = None
        except Exception as exc:  # pragma: no cover - orchestration error handling
            errors["deadlines"] = str(exc)
            deadlines = None
            partial = True

        # Stage 5: Notifications
        try:
            notification = None
            if selected_grant is not None:
                notification = self.notification_service.create(selected_grant=selected_grant, grant_context=startup_summary)
            else:
                notification = None
        except Exception as exc:  # pragma: no cover - orchestration error handling
            errors["notification"] = str(exc)
            notification = None
            partial = True

        result = UnifiedWorkflowResult(
            startup_summary=startup_summary,
            recommendation=rec,
            eligibility=elig,
            proposal=proposal,
            deadlines=deadlines,
            notification=notification,
            partial=partial,
            errors=errors or None,
        )
        logger.info("Unified workflow completed", extra={"partial": result.partial, "errors": result.errors or {}})
        return result
