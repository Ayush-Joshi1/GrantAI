from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "apps" / "api"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from src.application.container import Container, build_container
from src.application.deps import get_container, get_rag_answer_service
from src.application.services.rag_answer_service import RAGAnswerService


def test_get_container_returns_cached_container(monkeypatch: Any) -> None:
    monkeypatch.setattr("src.application.deps.build_container", lambda: Container(
        chat=None,  # type: ignore[arg-type]
        recommend=None,  # type: ignore[arg-type]
        proposal=None,  # type: ignore[arg-type]
        profile=None,  # type: ignore[arg-type]
        history=None,  # type: ignore[arg-type]
        eligibility=None,  # type: ignore[arg-type]
        search=None,  # type: ignore[arg-type]
        orchestrate_service=None,  # type: ignore[arg-type]
        rag_answer_service=None,  # type: ignore[arg-type]
        grant_recommendation_service=None,  # type: ignore[arg-type]
        proposal_generation_service=None,  # type: ignore[arg-type]
        deadline_service=None,  # type: ignore[arg-type]
        notification_service=None,  # type: ignore[arg-type]
        workflow_coordinator=None,  # type: ignore[arg-type]
    ))
    get_container.cache_clear()

    container_one = get_container()
    container_two = get_container()

    assert container_one is container_two


def test_container_exposes_rag_answer_service() -> None:
    container = build_container()

    assert isinstance(container.rag_answer_service, RAGAnswerService)


def test_rag_dependency_provider_returns_container_instance() -> None:
    container = build_container()
    service = get_rag_answer_service(container=container)

    assert service is container.rag_answer_service


def test_rag_dependency_provider_does_not_rebuild_service() -> None:
    container = build_container()
    service_one = get_rag_answer_service(container=container)
    service_two = get_rag_answer_service(container=container)

    assert service_one is service_two
    assert service_one is container.rag_answer_service


def test_existing_service_providers_still_resolve() -> None:
    container = build_container()

    assert container.chat is not None
    assert container.recommend is not None
    assert container.proposal is not None
    assert container.profile is not None
    assert container.history is not None
    assert container.eligibility is not None
    assert container.search is not None
    assert container.workflow_coordinator is not None
