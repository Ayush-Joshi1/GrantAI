from __future__ import annotations

from dataclasses import dataclass, field

from src.api.v1.schemas.common import SelectedGrantInput
from src.application.services.rag_answer_service import RAGAnswerService, RAGAnswerSource
from src.core.errors.exceptions import UpstreamError, ValidationError
from src.prompts.deadline.deadline_prompt_builder import DeadlinePromptBuilder


@dataclass(frozen=True)
class DeadlineResult:
    answer: str
    sources: list[RAGAnswerSource] = field(default_factory=list)


class DeadlineService:
    def __init__(self, rag_answer_service: RAGAnswerService | None = None, prompt_builder: DeadlinePromptBuilder | None = None) -> None:
        self.rag_answer_service = rag_answer_service or RAGAnswerService()
        self.prompt_builder = prompt_builder or DeadlinePromptBuilder()

    def analyze(self, *, selected_grant: SelectedGrantInput | None = None, deadline_context: str | None = None) -> DeadlineResult:
        if selected_grant is None or not self._coerce_text(selected_grant.grant_name):
            raise ValidationError("Selected grant is required for deadline analysis.")

        task = self.prompt_builder.build_task(selected_grant=selected_grant, deadline_context=deadline_context)

        try:
            rag_result = self.rag_answer_service.answer(task)
        except ValidationError:
            raise
        except UpstreamError:
            raise
        except Exception as exc:
            raise UpstreamError("Deadline analysis could not be completed at the moment.") from exc

        return DeadlineResult(answer=rag_result.answer, sources=rag_result.sources)

    def _coerce_text(self, value: str | None) -> str:
        if value is None:
            return ""
        value = value.strip()
        return value
