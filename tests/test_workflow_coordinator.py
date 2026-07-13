from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "apps" / "api"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from src.application.services.workflow_coordinator import WorkflowCoordinator, UnifiedWorkflowResult
from src.api.v1.schemas.common import StartupProfileInput, SelectedGrantInput


class FakeRecommend:
    def recommend(self, *, startup_profile: StartupProfileInput | None = None, query: str | None = None):
        class Src:
            def __init__(self, grant_name: str, organization: str):
                self.grant_name = grant_name
                self.organization = organization

        class Rec:
            answer = "We recommend Grant A and Grant B"
            sources = [Src(grant_name="Grant A", organization="Gov A")]

        return Rec()


class FakeEligibility:
    def check(self, *, startup_profile: StartupProfileInput | None = None, selected_grant: SelectedGrantInput | None = None):
        class E:
            answer = "You appear eligible based on provided profile."
            sources = []

        return E()


class FakeProposal:
    def generate(self, *, startup_profile: StartupProfileInput | None = None, selected_grant: SelectedGrantInput | None = None):
        class P:
            answer = "Draft proposal content"
            sources = []

        return P()


class FakeDeadline:
    def analyze(self, *, selected_grant: SelectedGrantInput | None = None):
        class D:
            answer = "Deadline is 30 days from now"
            sources = []

        return D()


class FakeNotification:
    def create(self, *, selected_grant: SelectedGrantInput | None = None, grant_context: str | None = None):
        class N:
            answer = "Notify team and set reminders"
            sources = []

        return N()


def test_workflow_coordinator_sequence() -> None:
    coord = WorkflowCoordinator(
        recommend_service=FakeRecommend(),
        eligibility_service=FakeEligibility(),
        proposal_service=FakeProposal(),
        deadline_service=FakeDeadline(),
        notification_service=FakeNotification(),
    )

    result = coord.run_unified_workflow(startup_profile=StartupProfileInput(startup_name="My Startup"), query="healthcare Pune")

    assert isinstance(result, UnifiedWorkflowResult)
    assert result.startup_summary is not None
    assert result.recommendation is not None
    assert result.eligibility is not None
    assert result.proposal is not None
    assert result.deadlines is not None
    assert result.notification is not None