from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "apps" / "api"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from src.api.v1.schemas.common import SelectedGrantInput, StartupProfileInput
from src.application.container import build_container
from src.application.services.eligibility_service import EligibilityService, EligibilityResult
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


def test_eligibility_task_includes_selected_grant_and_startup_profile() -> None:
    fake_rag = FakeRAGAnswerService(result=RAGAnswerResult(answer="Grounded eligibility analysis", sources=[]))
    service = EligibilityService(rag_answer_service=fake_rag)
    startup_profile = StartupProfileInput(
        startup_name="AgriVision AI",
        startup_description="AI crop monitoring platform",
        sector="Agritech",
        startup_stage="MVP",
        location="Pune",
        funding_required="₹25 lakh",
        founder_profile="Founder with agri-tech experience",
        additional_context="Needs support for pilots",
    )
    selected_grant = SelectedGrantInput(grant_name="Startup India Seed Fund Scheme")

    service.check(startup_profile=startup_profile, selected_grant=selected_grant)

    task = fake_rag.calls[0]
    assert "ELIGIBILITY ANALYSIS TASK" in task
    assert "Startup India Seed Fund Scheme" in task
    assert "AgriVision AI" in task
    assert "Agritech" in task
    assert "MVP" in task
    assert "Pune" in task
    assert "₹25 lakh" in task
    assert "confirmed matches" in task
    assert "missing information" in task
    assert "unmet requirements" in task


def test_eligibility_rejects_empty_selected_grant() -> None:
    service = EligibilityService(rag_answer_service=FakeRAGAnswerService())

    with pytest.raises(ValidationError):
        service.check(startup_profile=StartupProfileInput(sector="AI"), selected_grant=None)


def test_eligibility_rejects_empty_startup_profile() -> None:
    service = EligibilityService(rag_answer_service=FakeRAGAnswerService())

    with pytest.raises(ValidationError):
        service.check(startup_profile=None, selected_grant=SelectedGrantInput(grant_name="Grant X"))


def test_eligibility_propagates_answer_and_sources() -> None:
    expected_sources = [RAGAnswerSource(grant_name="Startup India Seed Fund", source_document="grant.pdf")]
    fake_rag = FakeRAGAnswerService(result=RAGAnswerResult(answer="Eligibility result", sources=expected_sources))
    service = EligibilityService(rag_answer_service=fake_rag)

    result = service.check(startup_profile=StartupProfileInput(sector="AI"), selected_grant=SelectedGrantInput(grant_name="Grant X"))

    assert isinstance(result, EligibilityResult)
    assert result.answer == "Eligibility result"
    assert result.sources == expected_sources


def test_eligibility_preserves_partial_source_metadata() -> None:
    expected_sources = [RAGAnswerSource(grant_name=None, organization=None, source_document="doc.pdf", page_number=4)]
    fake_rag = FakeRAGAnswerService(result=RAGAnswerResult(answer="Eligibility result", sources=expected_sources))
    service = EligibilityService(rag_answer_service=fake_rag)

    result = service.check(startup_profile=StartupProfileInput(sector="AI"), selected_grant=SelectedGrantInput(grant_name="Grant X"))

    assert result.sources[0].source_document == "doc.pdf"
    assert result.sources[0].page_number == 4


def test_eligibility_propagates_upstream_failure() -> None:
    fake_rag = FakeRAGAnswerService(error=UpstreamError("Upstream failure"))
    service = EligibilityService(rag_answer_service=fake_rag)

    with pytest.raises(UpstreamError):
        service.check(startup_profile=StartupProfileInput(sector="AI"), selected_grant=SelectedGrantInput(grant_name="Grant X"))


def test_container_uses_shared_rag_answer_service_for_eligibility_service() -> None:
    container = build_container()

    assert container.eligibility.rag_answer_service is container.rag_answer_service
