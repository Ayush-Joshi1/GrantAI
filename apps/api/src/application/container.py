from __future__ import annotations

"""
Dependency Injection container (minimal).

This stays framework-light: FastAPI uses dependency providers in `src/application/deps.py`,
and those dependencies can be swapped for tests.
"""

from dataclasses import dataclass

from src.application.services.chat_service import ChatService
from src.application.services.workflow_coordinator import WorkflowCoordinator
from src.application.services.deadline_service import DeadlineService
from src.application.services.eligibility_service import EligibilityService
from src.application.services.grant_recommendation_service import GrantRecommendationService
from src.application.services.history_service import HistoryService
from src.application.services.notification_service import NotificationService
from src.application.services.profile_service import ProfileService
from src.application.services.proposal_service import ProposalGenerationService, ProposalService
from src.application.services.orchestrate_service import OrchestrateService
from src.application.services.rag_answer_service import RAGAnswerService
from src.application.services.recommend_service import RecommendService
from src.application.services.search_service import SearchService


@dataclass(frozen=True)
class Container:
    chat: ChatService
    recommend: RecommendService
    proposal: ProposalService
    proposal_generation_service: ProposalGenerationService
    profile: ProfileService
    history: HistoryService
    eligibility: EligibilityService
    deadline_service: DeadlineService
    notification_service: NotificationService
    search: SearchService
    orchestrate_service: OrchestrateService
    rag_answer_service: RAGAnswerService
    grant_recommendation_service: GrantRecommendationService
    workflow_coordinator: WorkflowCoordinator


def build_container() -> Container:
    # Placeholder implementations; swap with real adapters later.
    rag_answer_service = RAGAnswerService()
    return Container(
        workflow_coordinator=WorkflowCoordinator(),
        chat=ChatService(workflow_coordinator=WorkflowCoordinator()),
        recommend=RecommendService(),
        proposal=ProposalService(),
        proposal_generation_service=ProposalGenerationService(rag_answer_service=rag_answer_service),
        profile=ProfileService(),
        history=HistoryService(),
        eligibility=EligibilityService(rag_answer_service=rag_answer_service),
        deadline_service=DeadlineService(rag_answer_service=rag_answer_service),
        notification_service=NotificationService(rag_answer_service=rag_answer_service),
        search=SearchService(),
        orchestrate_service=OrchestrateService(),
        rag_answer_service=rag_answer_service,
        grant_recommendation_service=GrantRecommendationService(rag_answer_service=rag_answer_service),
    )

