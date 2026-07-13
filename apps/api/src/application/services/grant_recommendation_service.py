from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.api.v1.schemas.common import StartupProfileInput
from src.application.services.rag_answer_service import RAGAnswerService, RAGAnswerSource
from src.core.errors.exceptions import UpstreamError, ValidationError
from src.prompts.recommendation.grant_recommendation_prompt_builder import GrantRecommendationPromptBuilder


@dataclass(frozen=True)
class GrantRecommendationResult:
    answer: str
    sources: list[RAGAnswerSource] = field(default_factory=list)


class GrantRecommendationService:
    """Application service for grounded grant recommendation guidance."""

    def __init__(self, rag_answer_service: RAGAnswerService | None = None, prompt_builder: GrantRecommendationPromptBuilder | None = None) -> None:
        self.rag_answer_service = rag_answer_service or RAGAnswerService()
        self.prompt_builder = prompt_builder or GrantRecommendationPromptBuilder()

    def recommend(self, *, startup_profile: StartupProfileInput | None = None, query: str | None = None) -> GrantRecommendationResult:
        if startup_profile is None:
            raise ValidationError("Startup profile is required for grant recommendations.")

        normalized_query = (query or "").strip()
        if not normalized_query:
            normalized_query = self._build_default_query(startup_profile)

        task = self.prompt_builder.build_task(startup_profile=startup_profile, query=normalized_query)

        try:
            rag_result = self.rag_answer_service.answer(task)
        except ValidationError:
            raise
        except UpstreamError:
            raise
        except Exception as exc:
            raise UpstreamError("Grant recommendation could not be completed at the moment.") from exc

        return GrantRecommendationResult(answer=rag_result.answer, sources=rag_result.sources)

    def _build_default_query(self, startup_profile: StartupProfileInput) -> str:
        return f"Recommend relevant Government grants for {self._optional_text(startup_profile.startup_name, 'this startup')} based on the startup profile."

    def _optional_text(self, value: str | None, fallback: str) -> str:
        if value is None or not value.strip():
            return f"{fallback}: not provided"
        return value.strip()
