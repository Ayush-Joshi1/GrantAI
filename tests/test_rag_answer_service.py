from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "apps" / "api"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from backend.rag.interfaces import RetrievalResult
from backend.rag.retriever.exceptions import RetrieverError
from src.application.services.rag_answer_service import RAGAnswerService
from src.core.errors.exceptions import UpstreamError, ValidationError


class FakeRetriever:
    def __init__(self, results: list[RetrievalResult] | None = None, error: Exception | None = None) -> None:
        self.results = results or []
        self.error = error
        self.calls: list[dict] = []

    def retrieve(self, *, query: str, top_k: int, similarity_threshold: float | None = None) -> list[RetrievalResult]:
        self.calls.append({"query": query, "top_k": top_k, "similarity_threshold": similarity_threshold})
        if self.error is not None:
            raise self.error
        return self.results


class FakePromptBuilder:
    def __init__(self, prompt: str = "built prompt", error: Exception | None = None) -> None:
        self.prompt = prompt
        self.error = error
        self.calls: list[tuple[str, list[RetrievalResult]]] = []

    def build_prompt(self, query: str, retrieval_results: list[RetrievalResult]) -> str:
        self.calls.append((query, retrieval_results))
        if self.error is not None:
            raise self.error
        return self.prompt


class FakeGraniteClient:
    def __init__(self, response: str = "generated answer", error: Exception | None = None) -> None:
        self.response = response
        self.error = error
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        if self.error is not None:
            raise self.error
        return self.response


@pytest.fixture
def settings() -> SimpleNamespace:
    return SimpleNamespace(top_k=3, similarity_threshold=0.75)


def test_answer_rejects_empty_query(settings: SimpleNamespace) -> None:
    service = RAGAnswerService(
        retrieval_client=FakeRetriever(),
        prompt_builder=FakePromptBuilder(),
        granite_client=FakeGraniteClient(),
        settings=settings,
    )

    with pytest.raises(ValidationError):
        service.answer("   ")


def test_answer_returns_grounded_fallback_for_no_retrieval_results(settings: SimpleNamespace) -> None:
    prompt_builder = FakePromptBuilder()
    granite_client = FakeGraniteClient()
    service = RAGAnswerService(
        retrieval_client=FakeRetriever(results=[]),
        prompt_builder=prompt_builder,
        granite_client=granite_client,
        settings=settings,
    )

    result = service.answer("What grants are available?")

    assert result.answer == "The available Government grant documents do not contain enough relevant information to answer this question confidently."
    assert result.sources == []
    assert prompt_builder.calls == []
    assert granite_client.prompts == []


def test_answer_returns_grounded_fallback_for_unusable_retrieval_content(settings: SimpleNamespace) -> None:
    prompt_builder = FakePromptBuilder()
    granite_client = FakeGraniteClient()
    service = RAGAnswerService(
        retrieval_client=FakeRetriever(
            results=[
                RetrievalResult(chunk_id="chunk-1", content="   ", metadata={"grant_name": "Grant A"}, score=0.9)
            ]
        ),
        prompt_builder=prompt_builder,
        granite_client=granite_client,
        settings=settings,
    )

    result = service.answer("What grants are available?")

    assert result.answer == "The available Government grant documents do not contain enough relevant information to answer this question confidently."
    assert result.sources == []
    assert prompt_builder.calls == []
    assert granite_client.prompts == []


def test_answer_builds_prompt_and_returns_answer_with_sources(settings: SimpleNamespace) -> None:
    retrieval_results = [
        RetrievalResult(
            chunk_id="chunk-1",
            content="Grant details.",
            metadata={"grant_name": "Grant A", "organization": "Org A", "file_name": "grant-a.pdf", "page_number": 2},
            score=0.95,
        ),
        RetrievalResult(
            chunk_id="chunk-2",
            content="More grant details.",
            metadata={"grant_name": "Grant A", "organization": "Org A", "file_name": "grant-a.pdf", "page_number": 2},
            score=0.9,
        ),
        RetrievalResult(
            chunk_id="chunk-3",
            content="Third chunk.",
            metadata={"grant_name": "Grant B", "organization": "Org B", "source_document": "grant-b.pdf"},
            score=0.88,
        ),
    ]
    retriever = FakeRetriever(results=retrieval_results)
    prompt_builder = FakePromptBuilder(prompt="formatted prompt")
    granite_client = FakeGraniteClient(response="Generated answer")
    service = RAGAnswerService(
        retrieval_client=retriever,
        prompt_builder=prompt_builder,
        granite_client=granite_client,
        settings=settings,
    )

    result = service.answer("Which grants apply?")

    assert result.answer == "Generated answer"
    assert granite_client.prompts == ["formatted prompt"]
    assert prompt_builder.calls == [("Which grants apply?", retrieval_results)]
    assert retriever.calls == [{"query": "Which grants apply?", "top_k": 3, "similarity_threshold": 0.75}]
    assert [source.grant_name for source in result.sources] == ["Grant A", "Grant B"]
    assert result.sources[0].organization == "Org A"
    assert result.sources[0].source_document == "grant-a.pdf"
    assert result.sources[0].page_number == 2
    assert result.sources[1].source_document == "grant-b.pdf"


def test_answer_raises_when_prompt_builder_produces_empty_prompt(settings: SimpleNamespace) -> None:
    granite_client = FakeGraniteClient()
    service = RAGAnswerService(
        retrieval_client=FakeRetriever(
            results=[RetrievalResult(chunk_id="chunk-1", content="Grant context.", metadata={"grant_name": "Grant A"}, score=0.9)]
        ),
        prompt_builder=FakePromptBuilder(prompt="   "),
        granite_client=granite_client,
        settings=settings,
    )

    with pytest.raises(UpstreamError):
        service.answer("What grants are available?")

    assert granite_client.prompts == []


def test_answer_wraps_retriever_failure_as_upstream_error(settings: SimpleNamespace) -> None:
    prompt_builder = FakePromptBuilder()
    granite_client = FakeGraniteClient()
    service = RAGAnswerService(
        retrieval_client=FakeRetriever(error=RetrieverError("retrieval unavailable")),
        prompt_builder=prompt_builder,
        granite_client=granite_client,
        settings=settings,
    )

    with pytest.raises(UpstreamError) as exc_info:
        service.answer("What grants are available?")

    assert "retrieval unavailable" not in str(exc_info.value).lower()
    assert prompt_builder.calls == []
    assert granite_client.prompts == []


def test_answer_wraps_prompt_builder_failure_as_upstream_error(settings: SimpleNamespace) -> None:
    granite_client = FakeGraniteClient()
    service = RAGAnswerService(
        retrieval_client=FakeRetriever(results=[RetrievalResult(chunk_id="chunk-1", content="Grant context.", metadata={"grant_name": "Grant A"}, score=0.9)]),
        prompt_builder=FakePromptBuilder(error=RuntimeError("builder broke")),
        granite_client=granite_client,
        settings=settings,
    )

    with pytest.raises(UpstreamError):
        service.answer("What grants are available?")

    assert granite_client.prompts == []


def test_answer_raises_upstream_error_when_granite_generation_fails(settings: SimpleNamespace) -> None:
    granite_client = FakeGraniteClient(error=RuntimeError("ibm sdk exploded"))
    service = RAGAnswerService(
        retrieval_client=FakeRetriever(results=[RetrievalResult(chunk_id="chunk-1", content="Grant context.", metadata={"grant_name": "Grant A"}, score=0.9)]),
        prompt_builder=FakePromptBuilder(prompt="formatted prompt"),
        granite_client=granite_client,
        settings=settings,
    )

    with pytest.raises(UpstreamError) as exc_info:
        service.answer("What grants are available?")

    assert "ibm sdk exploded" not in str(exc_info.value).lower()
