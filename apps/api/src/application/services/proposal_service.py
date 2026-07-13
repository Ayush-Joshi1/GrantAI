from __future__ import annotations

from dataclasses import dataclass, field

from src.api.v1.schemas.common import SelectedGrantInput, StartupProfileInput
from src.application.services.rag_answer_service import RAGAnswerService, RAGAnswerSource
from src.core.errors.exceptions import UpstreamError, ValidationError
from src.prompts.proposal.proposal_prompt_builder import ProposalPromptBuilder


@dataclass(frozen=True)
class ProposalGenerationResult:
    answer: str
    sources: list[RAGAnswerSource] = field(default_factory=list)


class ProposalService:
    """Backward-compatible placeholder service for existing route wiring."""

    def __init__(self) -> None:
        self._proposal_generation_service = ProposalGenerationService()

    def generate(self, *, grant_id: str, startup_profile_id: str, notes: str | None) -> dict:
        return {"proposal_id": "placeholder", "status": "queued"}


class ProposalGenerationService:
    def __init__(self, rag_answer_service: RAGAnswerService | None = None, prompt_builder: ProposalPromptBuilder | None = None) -> None:
        self.rag_answer_service = rag_answer_service or RAGAnswerService()
        self.prompt_builder = prompt_builder or ProposalPromptBuilder()

    def generate(self, *, startup_profile: StartupProfileInput | None = None, selected_grant: SelectedGrantInput | None = None, proposal_context: str | None = None) -> ProposalGenerationResult:
        if startup_profile is None:
            raise ValidationError("Startup profile is required for proposal generation.")
        if selected_grant is None or not self._coerce_text(selected_grant.grant_name):
            raise ValidationError("Selected grant is required for proposal generation.")

        task = self.prompt_builder.build_task(startup_profile=startup_profile, selected_grant=selected_grant, proposal_context=proposal_context)

        try:
            rag_result = self.rag_answer_service.answer(task)
        except ValidationError:
            raise
        except UpstreamError:
            raise
        except Exception as exc:
            raise UpstreamError("Proposal generation could not be completed at the moment.") from exc

        return ProposalGenerationResult(answer=rag_result.answer, sources=rag_result.sources)

    def _coerce_text(self, value: str | None) -> str:
        if value is None:
            return ""
        return value.strip()

