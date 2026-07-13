from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "apps" / "api"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from src.api.v1.schemas.common import StartupProfileInput
from src.application.container import build_container
from src.application.services.grant_recommendation_service import GrantRecommendationService, GrantRecommendationResult
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


def test_recommendation_task_includes_startup_profile_and_prompt_instructions() -> None:
    fake_rag = FakeRAGAnswerService(result=RAGAnswerResult(answer="recommendation", sources=[]))
    service = GrantRecommendationService(rag_answer_service=fake_rag)
    startup_profile = StartupProfileInput(
        startup_name="AgriVision AI",
        startup_description="AI crop monitoring platform",
        sector="Agritech",
        startup_stage="MVP",
        location="Pune",
        funding_required="₹25 lakh",
        founder_profile="Founder with agri-tech experience",
        additional_context="Need support for pilots",
    )

    service.recommend(startup_profile=startup_profile, query="Recommend grants for my startup")

    task = fake_rag.calls[0]
    assert "GRANT RECOMMENDATION TASK" in task
    assert "AgriVision AI" in task
    assert "Agritech" in task
    assert "MVP" in task
    assert "Pune" in task
    assert "₹25 lakh" in task
    assert "Founder with agri-tech experience" in task
    assert "Need support for pilots" in task
    assert "Identify relevant Government grant schemes" in task
    assert "Distinguish recommendations from confirmed eligibility" in task


def test_recommendation_task_handles_missing_optional_fields_without_inventing_values() -> None:
    fake_rag = FakeRAGAnswerService(result=RAGAnswerResult(answer="recommendation", sources=[]))
    service = GrantRecommendationService(rag_answer_service=fake_rag)

    service.recommend(startup_profile=StartupProfileInput(), query="Recommend grants")

    task = fake_rag.calls[0]
    assert "startup_name" in task
    assert "not provided" in task
    assert "sector/domain" in task


def test_recommendation_calls_rag_answer_service_once() -> None:
    fake_rag = FakeRAGAnswerService(result=RAGAnswerResult(answer="recommendation", sources=[]))
    service = GrantRecommendationService(rag_answer_service=fake_rag)

    service.recommend(startup_profile=StartupProfileInput(sector="AI"))

    assert len(fake_rag.calls) == 1


def test_recommendation_propagates_answer_and_sources() -> None:
    expected_sources = [RAGAnswerSource(grant_name="Startup India Seed Fund", source_document="seed-fund.pdf")]
    fake_rag = FakeRAGAnswerService(result=RAGAnswerResult(answer="Grounded recommendation", sources=expected_sources))
    service = GrantRecommendationService(rag_answer_service=fake_rag)

    result = service.recommend(startup_profile=StartupProfileInput(sector="AI"))

    assert isinstance(result, GrantRecommendationResult)
    assert result.answer == "Grounded recommendation"
    assert result.sources == expected_sources


def test_recommendation_preserves_partial_source_metadata() -> None:
    expected_sources = [RAGAnswerSource(grant_name=None, organization=None, source_document="doc.pdf", page_number=3)]
    fake_rag = FakeRAGAnswerService(result=RAGAnswerResult(answer="answer", sources=expected_sources))
    service = GrantRecommendationService(rag_answer_service=fake_rag)

    result = service.recommend(startup_profile=StartupProfileInput(sector="AI"))

    assert result.sources[0].source_document == "doc.pdf"
    assert result.sources[0].page_number == 3


def test_recommendation_preserves_insufficient_context_result() -> None:
    fake_rag = FakeRAGAnswerService(result=RAGAnswerResult(answer="The available Government grant documents do not contain enough relevant information to answer this question confidently.", sources=[]))
    service = GrantRecommendationService(rag_answer_service=fake_rag)

    result = service.recommend(startup_profile=StartupProfileInput(sector="AI"))

    assert result.answer.startswith("The available Government grant documents")
    assert result.sources == []


def test_recommendation_propagates_upstream_failure() -> None:
    fake_rag = FakeRAGAnswerService(error=UpstreamError("Upstream failure"))
    service = GrantRecommendationService(rag_answer_service=fake_rag)

    with pytest.raises(UpstreamError):
        service.recommend(startup_profile=StartupProfileInput(sector="AI"))


def test_recommendation_rejects_empty_startup_context() -> None:
    service = GrantRecommendationService(rag_answer_service=FakeRAGAnswerService())

    with pytest.raises(ValidationError):
        service.recommend(startup_profile=None, query="   ")


def test_container_uses_shared_rag_answer_service_for_grant_recommendation_service() -> None:
    container = build_container()

    assert container.grant_recommendation_service.rag_answer_service is container.rag_answer_service
