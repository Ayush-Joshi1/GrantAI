from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "apps" / "api"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from src.api.v1.schemas.common import SelectedGrantInput
from src.application.container import build_container
from src.application.services.deadline_service import DeadlineResult, DeadlineService
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


def test_deadline_task_includes_selected_grant_and_deadline_cautions() -> None:
    fake_rag = FakeRAGAnswerService(result=RAGAnswerResult(answer="Grounded deadline analysis", sources=[]))
    service = DeadlineService(rag_answer_service=fake_rag)
    selected_grant = SelectedGrantInput(grant_name="Startup India Seed Fund Scheme")

    service.analyze(selected_grant=selected_grant, deadline_context="Applications close on 30 September 2026")

    task = fake_rag.calls[0]
    assert "DEADLINE ANALYSIS TASK" in task
    assert "Startup India Seed Fund Scheme" in task
    assert "Applications close on 30 September 2026" in task
    assert "do not invent dates" in task
    assert "application deadline" in task
    assert "notification date" in task
    assert "publication date" in task
    assert "scheme duration" in task
    assert "historical/current deadline caution" in task
    assert "days remaining" in task


def test_deadline_prompt_contains_explicit_safeguards() -> None:
    service = DeadlineService(rag_answer_service=FakeRAGAnswerService())
    selected_grant = SelectedGrantInput(grant_name="Grant X")

    task = service.prompt_builder.build_task(selected_grant=selected_grant, deadline_context="Applications close on 30 September 2026")

    for phrase in [
        "Do not invent a deadline or date.",
        "Distinguish the application deadline from the notification date.",
        "Distinguish the application deadline from the publication or guideline date.",
        "Distinguish the application deadline from the scheme duration.",
        "Support application-window analysis.",
        "Do not automatically treat a historical deadline as current.",
        "Do not claim that applications are currently open without supporting evidence.",
        "State that the deadline is unknown or not established when the evidence is insufficient.",
        "Do not calculate days remaining from an unsupported date.",
        "Analyze timing only for the explicitly selected grant.",
    ]:
        assert phrase in task


def test_deadline_context_is_omitted_when_not_supplied() -> None:
    service = DeadlineService(rag_answer_service=FakeRAGAnswerService())
    selected_grant = SelectedGrantInput(grant_name="Grant X")

    task = service.prompt_builder.build_task(selected_grant=selected_grant)

    assert "deadline_context:" not in task


def test_deadline_rejects_missing_selected_grant() -> None:
    service = DeadlineService(rag_answer_service=FakeRAGAnswerService())

    with pytest.raises(ValidationError):
        service.analyze(selected_grant=None)


def test_deadline_propagates_answer_and_sources() -> None:
    expected_sources = [RAGAnswerSource(grant_name="Startup India Seed Fund", source_document="deadline.pdf")]
    fake_rag = FakeRAGAnswerService(result=RAGAnswerResult(answer="Deadline analysis", sources=expected_sources))
    service = DeadlineService(rag_answer_service=fake_rag)

    result = service.analyze(selected_grant=SelectedGrantInput(grant_name="Grant X"))

    assert isinstance(result, DeadlineResult)
    assert result.answer == "Deadline analysis"
    assert result.sources == expected_sources


def test_deadline_preserves_partial_source_metadata() -> None:
    expected_sources = [RAGAnswerSource(grant_name=None, organization=None, source_document="doc.pdf", page_number=7)]
    fake_rag = FakeRAGAnswerService(result=RAGAnswerResult(answer="Deadline analysis", sources=expected_sources))
    service = DeadlineService(rag_answer_service=fake_rag)

    result = service.analyze(selected_grant=SelectedGrantInput(grant_name="Grant X"))

    assert result.sources[0].source_document == "doc.pdf"
    assert result.sources[0].page_number == 7


def test_deadline_propagates_upstream_failure() -> None:
    fake_rag = FakeRAGAnswerService(error=UpstreamError("Upstream failure"))
    service = DeadlineService(rag_answer_service=fake_rag)

    with pytest.raises(UpstreamError):
        service.analyze(selected_grant=SelectedGrantInput(grant_name="Grant X"))


def test_container_uses_shared_rag_answer_service_for_deadline_service() -> None:
    container = build_container()

    assert container.deadline_service.rag_answer_service is container.rag_answer_service
