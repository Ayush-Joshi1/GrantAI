from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "apps" / "api") not in sys.path:
    sys.path.insert(0, str(ROOT / "apps" / "api"))

from src.core.errors.exceptions import UpstreamError, ValidationError
from src.infrastructure.ibm.granite_client import GraniteClient


class FakeInferenceClient:
    def __init__(self, response: object | None = None, exception: Exception | None = None) -> None:
        self.response = response
        self.exception = exception
        self.prompts: list[str] = []

    def generate(self, prompt: str) -> object:
        self.prompts.append(prompt)
        if self.exception is not None:
            raise self.exception
        return self.response


class FakeChatInferenceClient(FakeInferenceClient):
    def __init__(self, response: object | None = None, chat_response: object | None = None, exception: Exception | None = None) -> None:
        super().__init__(response=response, exception=exception)
        self.chat_response = chat_response
        self.chat_messages: list[list[dict[str, str]]] = []

    def chat(self, messages: list[dict[str, str]]) -> object:
        self.chat_messages.append(messages)
        if self.chat_response is None:
            raise RuntimeError("chat failed")
        return self.chat_response


def test_generate_passes_prompt_to_inference_dependency() -> None:
    fake_client = FakeInferenceClient(response={"generated_text": "hello"})
    adapter = GraniteClient(inference_client=fake_client, settings={})

    result = adapter.generate("test prompt")

    assert result == "hello"
    assert fake_client.prompts == ["test prompt"]


def test_generate_extracts_generated_text_from_sdk_like_response_shape() -> None:
    adapter = GraniteClient(inference_client=FakeInferenceClient(response={"results": [{"generated_text": "sdk output"}]}), settings={})

    assert adapter.generate("prompt") == "sdk output"


class ResponseWithToDict:
    def __init__(self, payload: dict[str, object]) -> None:
        self._payload = payload

    def to_dict(self) -> dict[str, object]:
        return self._payload


def test_generate_extracts_generated_text_from_to_dict_response() -> None:
    payload = {"results": [{"generated_text": "to_dict output"}]}
    adapter = GraniteClient(inference_client=FakeInferenceClient(response=ResponseWithToDict(payload)), settings={})

    assert adapter.generate("prompt") == "to_dict output"


def test_generate_extracts_generated_text_from_list_response() -> None:
    adapter = GraniteClient(inference_client=FakeInferenceClient(response=[{"generated_text": "list output"}]), settings={})

    assert adapter.generate("prompt") == "list output"


def test_generate_extracts_generated_text_from_live_sdk_like_payload() -> None:
    payload = {
        "model_id": "ibm/granite-8b-code-instruct",
        "results": [{"generated_text": "live sdk output", "generated_token_count": 4, "input_token_count": 3, "stop_reason": "stop"}],
        "system": {"warnings": [{"message": "deprecated model"}]},
    }
    adapter = GraniteClient(inference_client=FakeInferenceClient(response=payload), settings={})

    assert adapter.generate("prompt") == "live sdk output"


def test_generate_falls_back_to_chat_when_generate_raises() -> None:
    chat_payload = {"choices": [{"message": {"content": "chat output"}}]}
    fake_client = FakeChatInferenceClient(response=None, chat_response=chat_payload, exception=RuntimeError("empty generation"))
    adapter = GraniteClient(inference_client=fake_client, settings={})

    assert adapter.generate("prompt") == "chat output"
    assert fake_client.chat_messages == [[{"role": "user", "content": "prompt"}]]
    # chat-first: ensure generate() was not called before chat
    assert fake_client.prompts == []


def test_generate_falls_back_to_chat_when_generate_returns_empty_response() -> None:
    fake_client = FakeChatInferenceClient(response={"generated_text": "   "}, chat_response={"choices": [{"message": {"content": "chat fallback"}}]})
    adapter = GraniteClient(inference_client=fake_client, settings={})

    assert adapter.generate("prompt") == "chat fallback"
    assert fake_client.chat_messages == [[{"role": "user", "content": "prompt"}]]
    # chat-first: ensure generate() was not called before chat
    assert fake_client.prompts == []


def test_build_chat_messages_separates_system_and_context() -> None:
    prompt = (
        "SYSTEM INSTRUCTION\n"
        "You are GrantAI, an AI assistant for Indian Government grant discovery and funding guidance.\n\n"
        "RETRIEVED GOVERNMENT GRANT CONTEXT\n"
        "[CONTEXT 1]\n"
        "Content: This is retrieved government grant content.\n\n"
        "USER QUESTION\n"
        "What are the eligibility requirements for the Startup India Seed Fund Scheme?"
    )
    fake_client = FakeChatInferenceClient(response={"generated_text": "   "}, chat_response={"choices": [{"message": {"content": "chat output"}}]})
    adapter = GraniteClient(inference_client=fake_client, settings={})

    assert adapter.generate(prompt) == "chat output"
    assert fake_client.chat_messages == [[
        {
            "role": "system",
            "content": "You are GrantAI, an AI assistant for Indian Government grant discovery and funding guidance.",
        },
        {
            "role": "user",
            "content": "RETRIEVED GOVERNMENT GRANT CONTEXT\n[CONTEXT 1]\nContent: This is retrieved government grant content.\n\nUSER QUESTION\nWhat are the eligibility requirements for the Startup India Seed Fund Scheme?",
        },
    ]]
    assert fake_client.prompts == []


def test_generate_rejects_empty_prompt() -> None:
    adapter = GraniteClient(inference_client=FakeInferenceClient(response={"generated_text": "ignored"}), settings={})

    with pytest.raises(ValidationError):
        adapter.generate("   ")


def test_generate_rejects_whitespace_only_prompt() -> None:
    adapter = GraniteClient(inference_client=FakeInferenceClient(response={"generated_text": "ignored"}), settings={})

    with pytest.raises(ValidationError):
        adapter.generate("\n\t")


def test_generate_converts_inference_exception_to_upstream_error() -> None:
    adapter = GraniteClient(inference_client=FakeInferenceClient(exception=RuntimeError("timeout")), settings={})

    with pytest.raises(UpstreamError) as exc_info:
        adapter.generate("prompt")

    assert "timeout" not in str(exc_info.value).lower()


def test_generate_handles_malformed_response() -> None:
    adapter = GraniteClient(inference_client=FakeInferenceClient(response=object()), settings={})

    with pytest.raises(UpstreamError):
        adapter.generate("prompt")


def test_generate_handles_missing_generated_text() -> None:
    adapter = GraniteClient(inference_client=FakeInferenceClient(response={"results": [{}]}), settings={})

    with pytest.raises(UpstreamError):
        adapter.generate("prompt")


def test_generate_handles_empty_generated_text() -> None:
    adapter = GraniteClient(inference_client=FakeInferenceClient(response={"generated_text": "   "}), settings={})

    with pytest.raises(UpstreamError):
        adapter.generate("prompt")


def test_generate_handles_whitespace_generated_text() -> None:
    adapter = GraniteClient(inference_client=FakeInferenceClient(response={"results": [{"generated_text": "   "}]}), settings={})

    with pytest.raises(UpstreamError):
        adapter.generate("prompt")


def test_generate_does_not_include_sensitive_configuration_in_error_message() -> None:
    adapter = GraniteClient(inference_client=FakeInferenceClient(exception=RuntimeError("invalid API key")), settings={})

    with pytest.raises(UpstreamError) as exc_info:
        adapter.generate("prompt")

    assert "api key" not in str(exc_info.value).lower()
    assert "credential" not in str(exc_info.value).lower()


def test_get_env_value_loads_values_from_dotenv_file(tmp_path, monkeypatch) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("WATSONX_API_KEY=dotenv-key\nPROJECT_ID=dotenv-project\n", encoding="utf-8")
    monkeypatch.chdir(tmp_path)

    adapter = GraniteClient(inference_client=FakeInferenceClient(response={"generated_text": "ok"}), settings={})

    assert adapter._get_env_value("WATSONX_API_KEY") == "dotenv-key"
    assert adapter._get_env_value("PROJECT_ID") == "dotenv-project"
