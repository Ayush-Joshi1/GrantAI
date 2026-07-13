import asyncio
from types import SimpleNamespace

from src.application.services.chat_service import ChatService
from src.core.errors.exceptions import UpstreamError


class StubAssistantClient:
    def __init__(self, reply: str | None = None, error: Exception | None = None) -> None:
        self.reply = reply
        self.error = error
        self.calls: list[tuple[str, str | None]] = []

    def generate_reply(self, message: str, session_id: str | None = None) -> str:
        self.calls.append((message, session_id))
        if self.error is not None:
            raise self.error
        if self.reply is None:
            raise UpstreamError("assistant unavailable")
        return self.reply


class StubRAGService:
    def __init__(self, reply: str) -> None:
        self.reply = reply
        self.calls: list[str] = []

    def answer(self, query: str) -> SimpleNamespace:
        self.calls.append(query)
        return SimpleNamespace(answer=self.reply)


def test_chat_service_uses_assistant_reply_when_available() -> None:
    assistant = StubAssistantClient(reply="assistant reply")
    service = ChatService(assistant_client=assistant, fallback_service=StubRAGService("fallback reply"))

    result = asyncio.run(service.turn(session_id="session-1", message="hello"))

    assert result["session_id"] == "session-1"
    assert result["reply"] == "assistant reply"
    assert assistant.calls == [("hello", "session-1")]


def test_chat_service_falls_back_to_rag_when_assistant_fails() -> None:
    assistant = StubAssistantClient(error=UpstreamError("assistant unavailable"))
    fallback = StubRAGService("fallback reply")
    service = ChatService(assistant_client=assistant, fallback_service=fallback)

    result = asyncio.run(service.turn(session_id=None, message="hello"))

    assert result["reply"] == "fallback reply"
    assert result["session_id"]
    assert fallback.calls == ["hello"]
