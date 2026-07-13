from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "apps" / "api"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from src.api.v1.schemas.common import SelectedGrantInput, StartupProfileInput
from src.application.deps import (
    get_deadline_service,
    get_eligibility_service,
    get_grant_recommendation_service,
    get_notification_service,
    get_proposal_generation_service,
)
from src.application.services.deadline_service import DeadlineResult
from src.application.services.eligibility_service import EligibilityResult
from src.application.services.grant_recommendation_service import GrantRecommendationResult
from src.application.services.notification_service import NotificationResult
from src.application.services.proposal_service import ProposalGenerationResult
from src.application.services.rag_answer_service import RAGAnswerResult, RAGAnswerSource
from src.core.errors.exceptions import UpstreamError, ValidationError
from src.main import app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


class StubGrantRecommendationService:
    def __init__(self, result: GrantRecommendationResult | None = None) -> None:
        self.result = result or GrantRecommendationResult(answer="recommendation", sources=[])
        self.calls: list[dict[str, object]] = []

    def recommend(self, *, startup_profile: StartupProfileInput | None = None, query: str | None = None) -> GrantRecommendationResult:
        self.calls.append({"startup_profile": startup_profile, "query": query})
        return self.result


class StubEligibilityService:
    def __init__(self, result: EligibilityResult | None = None) -> None:
        self.result = result or EligibilityResult(answer="eligibility", sources=[])
        self.calls: list[dict[str, object]] = []

    def check(self, *, startup_profile: StartupProfileInput | None = None, selected_grant: SelectedGrantInput | None = None) -> EligibilityResult:
        self.calls.append({"startup_profile": startup_profile, "selected_grant": selected_grant})
        return self.result


class StubProposalGenerationService:
    def __init__(self, result: ProposalGenerationResult | None = None) -> None:
        self.result = result or ProposalGenerationResult(answer="proposal", sources=[])
        self.calls: list[dict[str, object]] = []

    def generate(self, *, startup_profile: StartupProfileInput | None = None, selected_grant: SelectedGrantInput | None = None, proposal_context: str | None = None) -> ProposalGenerationResult:
        self.calls.append({"startup_profile": startup_profile, "selected_grant": selected_grant, "proposal_context": proposal_context})
        return self.result


class StubDeadlineService:
    def __init__(self, result: DeadlineResult | None = None) -> None:
        self.result = result or DeadlineResult(answer="deadline", sources=[])
        self.calls: list[dict[str, object]] = []

    def analyze(self, *, selected_grant: SelectedGrantInput | None = None, deadline_context: str | None = None) -> DeadlineResult:
        self.calls.append({"selected_grant": selected_grant, "deadline_context": deadline_context})
        return self.result


class StubNotificationService:
    def __init__(self, result: NotificationResult | None = None) -> None:
        self.result = result or NotificationResult(answer="notification", sources=[])
        self.calls: list[dict[str, object]] = []

    def create(
        self,
        *,
        request: object | None = None,
        selected_grant: SelectedGrantInput | None = None,
        grant_context: str | None = None,
        deadline_context: str | None = None,
        action_context: str | None = None,
        notification_preferences: str | None = None,
    ) -> NotificationResult:
        self.calls.append(
            {
                "selected_grant": selected_grant,
                "grant_context": grant_context,
                "deadline_context": deadline_context,
                "action_context": action_context,
                "notification_preferences": notification_preferences,
            }
        )
        return self.result


def test_recommendation_endpoint_uses_application_service(client: TestClient) -> None:
    stub_service = StubGrantRecommendationService(
        result=GrantRecommendationResult(
            answer="Grounded recommendation",
            sources=[RAGAnswerSource(grant_name="Grant X", source_document="grant.pdf", page_number=3)],
        )
    )
    app.dependency_overrides[get_grant_recommendation_service] = lambda: stub_service

    response = client.post(
        "/api/v1/recommend",
        json={
            "query": "Find grants for AI startups",
            "limit": 5,
            "startup_profile": {
                "startup_name": "Aviate AI",
                "startup_description": "AI SaaS",
                "sector": "AI",
            },
        },
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "Grounded recommendation"
    assert response.json()["sources"][0]["source_document"] == "grant.pdf"
    assert response.json()["sources"][0]["page_number"] == 3
    assert stub_service.calls[0]["query"] == "Find grants for AI startups"
    assert stub_service.calls[0]["startup_profile"].startup_name == "Aviate AI"

    app.dependency_overrides.clear()


def test_eligibility_endpoint_uses_application_service(client: TestClient) -> None:
    stub_service = StubEligibilityService(result=EligibilityResult(answer="Grounded eligibility", sources=[]))
    app.dependency_overrides[get_eligibility_service] = lambda: stub_service

    response = client.post(
        "/api/v1/eligibility/check",
        json={
            "selected_grant": {"grant_name": "Grant X"},
            "startup_profile": {"startup_name": "Aviate AI", "sector": "AI"},
        },
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "Grounded eligibility"
    assert stub_service.calls[0]["selected_grant"].grant_name == "Grant X"
    assert stub_service.calls[0]["startup_profile"].startup_name == "Aviate AI"

    app.dependency_overrides.clear()


def test_proposal_endpoint_uses_application_service(client: TestClient) -> None:
    stub_service = StubProposalGenerationService(result=ProposalGenerationResult(answer="Grounded proposal", sources=[]))
    app.dependency_overrides[get_proposal_generation_service] = lambda: stub_service

    response = client.post(
        "/api/v1/proposal/generate",
        json={
            "selected_grant": {"grant_name": "Grant X"},
            "startup_profile": {"startup_name": "Aviate AI", "sector": "AI"},
            "proposal_context": "Need a concise draft",
        },
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "Grounded proposal"
    assert stub_service.calls[0]["selected_grant"].grant_name == "Grant X"
    assert stub_service.calls[0]["proposal_context"] == "Need a concise draft"

    app.dependency_overrides.clear()


def test_deadline_endpoint_uses_application_service(client: TestClient) -> None:
    stub_service = StubDeadlineService(
        result=DeadlineResult(
            answer="Grounded deadline",
            sources=[RAGAnswerSource(grant_name="Grant X", source_document="grant.pdf", page_number=3)],
        )
    )
    app.dependency_overrides[get_deadline_service] = lambda: stub_service

    response = client.post(
        "/api/v1/deadline",
        json={
            "selected_grant": {"grant_name": "Grant X"},
            "grant_context": "Deadline context",
        },
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "Grounded deadline"
    assert response.json()["sources"][0]["source_document"] == "grant.pdf"
    assert response.json()["sources"][0]["page_number"] == 3
    assert stub_service.calls[0]["selected_grant"].grant_name == "Grant X"
    assert stub_service.calls[0]["deadline_context"] == "Deadline context"

    app.dependency_overrides.clear()


def test_notification_endpoint_uses_application_service(client: TestClient) -> None:
    stub_service = StubNotificationService(result=NotificationResult(answer="Grounded notification", sources=[]))
    app.dependency_overrides[get_notification_service] = lambda: stub_service

    response = client.post(
        "/api/v1/notifications",
        json={
            "selected_grant": {"grant_name": "Grant X"},
            "grant_context": "Grant context",
            "deadline_context": "No verified deadline",
            "action_context": "Prepare application",
            "notification_preferences": "Concise",
        },
    )

    assert response.status_code == 200
    assert response.json()["answer"] == "Grounded notification"
    assert stub_service.calls[0]["selected_grant"].grant_name == "Grant X"
    assert stub_service.calls[0]["deadline_context"] == "No verified deadline"
    assert stub_service.calls[0]["action_context"] == "Prepare application"
    assert stub_service.calls[0]["notification_preferences"] == "Concise"

    app.dependency_overrides.clear()


def test_validation_errors_map_to_client_error(client: TestClient) -> None:
    def override() -> object:
        raise ValidationError("Bad request")

    app.dependency_overrides[get_grant_recommendation_service] = override

    response = client.post(
        "/api/v1/recommend",
        json={"query": "Find grants", "limit": 1},
    )

    assert response.status_code == 422
    assert response.json()["error"] == "validation_error"
    assert "Bad request" in response.json()["message"]

    app.dependency_overrides.clear()


def test_upstream_errors_map_to_service_error(client: TestClient) -> None:
    def override() -> object:
        raise UpstreamError("Upstream failed")

    app.dependency_overrides[get_grant_recommendation_service] = override

    response = client.post(
        "/api/v1/recommend",
        json={"query": "Find grants", "limit": 1},
    )

    assert response.status_code == 502
    assert response.json()["error"] == "upstream_error"
    assert response.json()["message"] == "Upstream failed"

    app.dependency_overrides.clear()


def test_openapi_registers_agent_endpoints(client: TestClient) -> None:
    schema = client.get("/api/v1/openapi.json")

    assert schema.status_code == 200
    paths = schema.json()["paths"]
    assert "/api/v1/recommend" in paths
    assert "/api/v1/eligibility/check" in paths
    assert "/api/v1/proposal/generate" in paths
    assert "/api/v1/deadline" in paths
    assert "/api/v1/notifications" in paths
