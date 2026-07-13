from __future__ import annotations

from functools import lru_cache

from fastapi import Depends

from src.application.container import Container, build_container
from src.application.services.chat_service import ChatService
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
from src.application.services.workflow_coordinator import WorkflowCoordinator


@lru_cache(maxsize=1)
def get_container() -> Container:
    return build_container()


def get_chat_service(container: Container = Depends(get_container)) -> ChatService:
    return container.chat


def get_recommend_service(container: Container = Depends(get_container)) -> RecommendService:
    return container.recommend


def get_proposal_service(container: Container = Depends(get_container)) -> ProposalService:
    return container.proposal


def get_proposal_generation_service(container: Container = Depends(get_container)) -> ProposalGenerationService:
    return container.proposal_generation_service


def get_profile_service(container: Container = Depends(get_container)) -> ProfileService:
    return container.profile


def get_history_service(container: Container = Depends(get_container)) -> HistoryService:
    return container.history


def get_eligibility_service(container: Container = Depends(get_container)) -> EligibilityService:
    return container.eligibility


def get_deadline_service(container: Container = Depends(get_container)) -> DeadlineService:
    return container.deadline_service


def get_notification_service(container: Container = Depends(get_container)) -> NotificationService:
    return container.notification_service


def get_search_service(container: Container = Depends(get_container)) -> SearchService:
    return container.search


def get_orchestrate_service(container: Container = Depends(get_container)) -> OrchestrateService:
    return container.orchestrate_service


def get_workflow_coordinator(container: Container = Depends(get_container)) -> WorkflowCoordinator:
    return container.workflow_coordinator


def get_rag_answer_service(container: Container = Depends(get_container)) -> RAGAnswerService:
    return container.rag_answer_service


def get_grant_recommendation_service(container: Container = Depends(get_container)) -> GrantRecommendationService:
    return container.grant_recommendation_service

