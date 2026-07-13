from __future__ import annotations

from dataclasses import dataclass, field

from src.api.v1.schemas.common import SelectedGrantInput
from src.api.v1.schemas.notifications import NotificationRequest
from src.application.services.rag_answer_service import RAGAnswerService, RAGAnswerSource
from src.core.errors.exceptions import UpstreamError, ValidationError
from src.prompts.notification.notification_prompt_builder import NotificationPromptBuilder


@dataclass(frozen=True)
class NotificationResult:
    answer: str
    sources: list[RAGAnswerSource] = field(default_factory=list)


class NotificationService:
    def __init__(self, rag_answer_service: RAGAnswerService | None = None, prompt_builder: NotificationPromptBuilder | None = None) -> None:
        self.rag_answer_service = rag_answer_service or RAGAnswerService()
        self.prompt_builder = prompt_builder or NotificationPromptBuilder()

    def create(self, *, request: NotificationRequest | None = None, selected_grant: SelectedGrantInput | None = None, grant_context: str | None = None, deadline_context: str | None = None, action_context: str | None = None, notification_preferences: str | None = None) -> NotificationResult:
        if request is not None:
            selected_grant = request.selected_grant or selected_grant
            grant_context = request.grant_context if request.grant_context is not None else grant_context
            deadline_context = request.deadline_context if request.deadline_context is not None else deadline_context
            action_context = request.grant_context if request.grant_context is not None else action_context
            notification_preferences = request.notification_preferences if request.notification_preferences is not None else notification_preferences

        if selected_grant is None or not self._coerce_text(selected_grant.grant_name):
            raise ValidationError("Selected grant is required for notification generation.")

        if not self._has_meaningful_context(grant_context, deadline_context, action_context, notification_preferences):
            raise ValidationError("Notification context is required for notification generation.")

        task = self.prompt_builder.build_task(
            selected_grant=selected_grant,
            grant_context=grant_context,
            deadline_context=deadline_context,
            action_context=action_context,
            notification_preferences=notification_preferences,
        )

        try:
            rag_result = self.rag_answer_service.answer(task)
        except ValidationError:
            raise
        except UpstreamError:
            raise
        except Exception as exc:
            raise UpstreamError("Notification generation could not be completed at the moment.") from exc

        return NotificationResult(answer=rag_result.answer, sources=rag_result.sources)

    def _has_meaningful_context(self, grant_context: str | None, deadline_context: str | None, action_context: str | None, notification_preferences: str | None) -> bool:
        values = [grant_context, deadline_context, action_context, notification_preferences]
        return any(self._coerce_text(value) for value in values)

    def _coerce_text(self, value: str | None) -> str:
        if value is None:
            return ""
        return value.strip()
