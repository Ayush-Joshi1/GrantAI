from __future__ import annotations

from dataclasses import dataclass, field

from src.api.v1.schemas.common import SelectedGrantInput, StartupProfileInput
from src.application.services.rag_answer_service import RAGAnswerService, RAGAnswerSource
from src.core.errors.exceptions import UpstreamError, ValidationError
from src.prompts.eligibility.eligibility_prompt_builder import EligibilityPromptBuilder


@dataclass(frozen=True)
class EligibilityResult:
    answer: str
    sources: list[RAGAnswerSource] = field(default_factory=list)


class EligibilityService:
    def __init__(self, rag_answer_service: RAGAnswerService | None = None, prompt_builder: EligibilityPromptBuilder | None = None) -> None:
        self.rag_answer_service = rag_answer_service or RAGAnswerService()
        self.prompt_builder = prompt_builder or EligibilityPromptBuilder()

    def check(self, *, startup_profile: StartupProfileInput | None = None, selected_grant: SelectedGrantInput | None = None) -> EligibilityResult:
        if startup_profile is None:
            raise ValidationError("Startup profile is required for eligibility analysis.")
        if selected_grant is None or not self._coerce_text(selected_grant.grant_name):
            raise ValidationError("Selected grant is required for eligibility analysis.")

        task = self.prompt_builder.build_task(startup_profile=startup_profile, selected_grant=selected_grant)

        try:
            rag_result = self.rag_answer_service.answer(task)
        except ValidationError:
            raise
        except UpstreamError:
            raise
        except Exception as exc:
            raise UpstreamError("Eligibility analysis could not be completed at the moment.") from exc

        return EligibilityResult(answer=rag_result.answer, sources=rag_result.sources)

    def _coerce_text(self, value: str | None) -> str:
        if value is None:
            return ""
        value = value.strip()
        return value

