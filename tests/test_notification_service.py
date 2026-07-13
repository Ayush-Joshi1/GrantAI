from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "apps" / "api"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from src.api.v1.schemas.common import SelectedGrantInput
from src.api.v1.schemas.notifications import NotificationRequest
from src.application.container import build_container
from src.application.services.notification_service import NotificationResult, NotificationService
from src.application.services.rag_answer_service import RAGAnswerResult, RAGAnswerSource
from src.core.errors.exceptions import UpstreamError, ValidationError


class FakeRAGAnswerService:
    def __init__(self, result: RAGAnswerResult | None = None, error: Exception | None = None) -> None:
        self.result = result or RAGAnswerResult(answer="", sources=[])
        self.error = error
        self.calls: list[str] = []

    def answer(self, query: str) -> RAGAnswerResult:
        self.calls.append(query)
        if self.error is not None:
            raise self.error
        return self.result


def test_notification_task_includes_selected_grant_and_context() -> None:
    fake_rag = FakeRAGAnswerService(result=RAGAnswerResult(answer="Grounded notification", sources=[]))
    service = NotificationService(rag_answer_service=fake_rag)
    selected_grant = SelectedGrantInput(grant_name="Startup India Seed Fund Scheme")

    service.create(
        selected_grant=selected_grant,
        grant_context="Grant supports deep-tech startups",
        deadline_context="No verified current application deadline supplied",
        action_context="Founder wants to track the grant and prepare for a future application",
        notification_preferences="Concise and action-oriented",
    )

    task = fake_rag.calls[0]
    assert "NOTIFICATION TASK" in task
    assert "Startup India Seed Fund Scheme" in task
    assert "Grant supports deep-tech startups" in task
    assert "No verified current application deadline supplied" in task
    assert "Founder wants to track the grant and prepare for a future application" in task
    assert "Concise and action-oriented" in task
    assert "Do not invent a deadline or date" in task
    assert "Do not invent days remaining" in task
    assert "Do not create false urgency" in task
    assert "Provide a useful next action" in task


def test_notification_prompt_contains_non_fabrication_safeguards() -> None:
    service = NotificationService(rag_answer_service=FakeRAGAnswerService())
    task = service.prompt_builder.build_task(
        selected_grant=SelectedGrantInput(grant_name="Grant X"),
        grant_context="Grant context",
        deadline_context="No verified current application deadline supplied",
        action_context="Founder wants a reminder",
        notification_preferences="Concise",
    )

    for phrase in [
        "Do not invent a deadline or date.",
        "Do not invent days remaining.",
        "Do not claim the application is incomplete unless the supplied action context establishes that fact.",
        "Do not invent missing documents.",
        "Do not claim confirmed eligibility.",
        "Do not invent approval or rejection status.",
        "Do not create false urgency.",
        "Match urgency to supported timing or action information only.",
        "Provide a useful next action.",
    ]:
        assert phrase in task


def test_notification_context_is_omitted_when_not_supplied() -> None:
    service = NotificationService(rag_answer_service=FakeRAGAnswerService())
    task = service.prompt_builder.build_task(selected_grant=SelectedGrantInput(grant_name="Grant X"))

    assert "deadline_context:" not in task
    assert "action_context:" not in task
    assert "notification_preferences:" not in task


def test_notification_request_is_supported() -> None:
    fake_rag = FakeRAGAnswerService(result=RAGAnswerResult(answer="Notification from request", sources=[]))
    service = NotificationService(rag_answer_service=fake_rag)
    request = NotificationRequest(
        selected_grant=SelectedGrantInput(grant_name="Grant Y"),
        grant_context="Grant Y context",
        deadline_context="No verified deadline",
        action_context="Action context",
        notification_preferences="Concise",
    )

    result = service.create(request=request)

    assert isinstance(result, NotificationResult)
    assert result.answer == "Notification from request"


def test_notification_rejects_missing_selected_grant() -> None:
    service = NotificationService(rag_answer_service=FakeRAGAnswerService())

    with pytest.raises(ValidationError):
        service.create(selected_grant=None, grant_context="Grant context")


def test_notification_rejects_missing_context() -> None:
    service = NotificationService(rag_answer_service=FakeRAGAnswerService())

    with pytest.raises(ValidationError):
        service.create(selected_grant=SelectedGrantInput(grant_name="Grant X"))


def test_notification_propagates_answer_and_sources() -> None:
    expected_sources = [RAGAnswerSource(grant_name="Grant X", source_document="notice.pdf")]
    fake_rag = FakeRAGAnswerService(result=RAGAnswerResult(answer="Notification result", sources=expected_sources))
    service = NotificationService(rag_answer_service=fake_rag)

    result = service.create(selected_grant=SelectedGrantInput(grant_name="Grant X"), grant_context="Context")

    assert result.answer == "Notification result"
    assert result.sources == expected_sources


def test_notification_preserves_partial_source_metadata() -> None:
    expected_sources = [RAGAnswerSource(grant_name=None, organization=None, source_document="doc.pdf", page_number=9)]
    fake_rag = FakeRAGAnswerService(result=RAGAnswerResult(answer="Notification result", sources=expected_sources))
    service = NotificationService(rag_answer_service=fake_rag)

    result = service.create(selected_grant=SelectedGrantInput(grant_name="Grant X"), grant_context="Context")

    assert result.sources[0].source_document == "doc.pdf"
    assert result.sources[0].page_number == 9


def test_notification_propagates_upstream_failure() -> None:
    fake_rag = FakeRAGAnswerService(error=UpstreamError("Upstream failure"))
    service = NotificationService(rag_answer_service=fake_rag)

    with pytest.raises(UpstreamError):
        service.create(selected_grant=SelectedGrantInput(grant_name="Grant X"), grant_context="Context")


def test_container_uses_shared_rag_answer_service_for_notification_service() -> None:
    container = build_container()

    assert container.notification_service.rag_answer_service is container.rag_answer_service
