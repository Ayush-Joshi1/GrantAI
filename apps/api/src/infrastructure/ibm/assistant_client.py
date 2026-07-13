from __future__ import annotations

import logging
import os
from typing import Any

import requests

from src.core.errors.exceptions import UpstreamError

logger = logging.getLogger("api.infrastructure.ibm.assistant")


class WatsonxAssistantClient:
    """Minimal IBM watsonx Assistant runtime client for chat-style message exchange."""

    def __init__(self, settings: Any | None = None) -> None:
        self.settings = settings
        self._api_key = self._get_env_value("WATSONX_ASSISTANT_API_KEY", "IBM_API_KEY", "WATSONX_API_KEY")
        self._service_url = self._get_env_value("WATSONX_ASSISTANT_URL", "IBM_URL", "WATSONX_URL")
        self._assistant_id = self._get_env_value("WATSONX_ASSISTANT_ID", "ASSISTANT_ID")
        self._timeout_seconds = 30

    def generate_reply(self, message: str, session_id: str | None = None) -> str:
        if not message or not message.strip():
            raise UpstreamError("Assistant message must not be empty.")
        if not self._api_key or not self._service_url or not self._assistant_id:
            raise UpstreamError("IBM watsonx Assistant configuration is incomplete.")

        session = session_id or self._create_session()
        try:
            response = self._send_message(session, message)
            reply = self._extract_reply(response)
        except UpstreamError:
            raise
        except Exception as exc:  # pragma: no cover - network path
            logger.exception("IBM watsonx Assistant runtime call failed")
            raise UpstreamError("IBM watsonx Assistant request failed.") from exc

        if not reply or not reply.strip():
            raise UpstreamError("IBM watsonx Assistant returned an empty response.")
        return reply.strip()

    def _create_session(self) -> str:
        url = self._build_url("/v1/sessions")
        headers = self._build_headers()
        response = requests.post(url, headers=headers, timeout=self._timeout_seconds)
        if response.status_code >= 400:
            raise UpstreamError("IBM watsonx Assistant session creation failed.")
        payload = response.json()
        return str(payload.get("session_id") or payload.get("id") or "")

    def _send_message(self, session_id: str, message: str) -> dict[str, Any]:
        url = self._build_url(f"/v1/sessions/{session_id}/message")
        headers = self._build_headers()
        payload = {
            "assistant_id": self._assistant_id,
            "input": {"text": message},
        }
        response = requests.post(url, headers=headers, json=payload, timeout=self._timeout_seconds)
        if response.status_code >= 400:
            raise UpstreamError("IBM watsonx Assistant message delivery failed.")
        return response.json()

    def _extract_reply(self, response: dict[str, Any]) -> str:
        outputs = response.get("outputs") or []
        if isinstance(outputs, list):
            for item in outputs:
                if isinstance(item, dict):
                    text = item.get("text") or item.get("message") or item.get("content")
                    if isinstance(text, str) and text.strip():
                        return text.strip()
                    if isinstance(text, dict):
                        nested = text.get("text") or text.get("content")
                        if isinstance(nested, str) and nested.strip():
                            return nested.strip()
        for key in ("reply", "output", "response", "text"):
            value = response.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return ""

    def _build_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def _build_url(self, path: str) -> str:
        base = self._service_url.rstrip("/")
        if path.startswith("/"):
            return f"{base}{path}"
        return f"{base}/{path}"

    def _get_env_value(self, *names: str) -> str:
        for name in names:
            value = os.getenv(name)
            if value and value.strip():
                return value.strip()
        return ""
