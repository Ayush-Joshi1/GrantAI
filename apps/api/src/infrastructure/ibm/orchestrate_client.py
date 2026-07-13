from __future__ import annotations

import os
from typing import Any

import httpx

from src.core.config.settings import Settings, get_settings
from src.core.errors.exceptions import UpstreamError, ValidationError


class WatsonxOrchestrateClient:
    """Minimal IBM watsonx Orchestrate client for workflow execution."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._api_key = self._get_env_value(
            self.settings.orchestrate_api_key,
            "WATSONX_ORCHESTRATE_API_KEY",
            "IBM_ORCHESTRATE_API_KEY",
        )
        self._service_url = self._get_env_value(
            self.settings.orchestrate_url,
            "WATSONX_ORCHESTRATE_URL",
            "IBM_ORCHESTRATE_URL",
        )
        self._timeout_seconds = 30

    def execute_workflow(self, workflow_id: str, inputs: dict[str, Any]) -> dict[str, Any]:
        if not workflow_id or not workflow_id.strip():
            raise ValidationError("Orchestrate workflow ID must not be empty.")

        if not self._api_key or not self._service_url:
            raise UpstreamError("IBM watsonx Orchestrate configuration is incomplete.")

        url = self._build_url(f"/v1/workflows/{workflow_id}/executions")
        headers = self._build_headers()
        payload = {"input": inputs}

        try:
            response = httpx.post(url, headers=headers, json=payload, timeout=self._timeout_seconds)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException as exc:
            raise UpstreamError("IBM watsonx Orchestrate request timed out.") from exc
        except httpx.HTTPStatusError as exc:
            raise UpstreamError("IBM watsonx Orchestrate request failed.") from exc
        except Exception as exc:
            raise UpstreamError("IBM watsonx Orchestrate request failed.") from exc

    def validate_configuration(self) -> None:
        if not self._api_key or not self._service_url:
            raise UpstreamError("IBM watsonx Orchestrate configuration is incomplete.")

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

    def _get_env_value(self, configured_value: str | None, *env_names: str) -> str:
        if configured_value and configured_value.strip():
            return configured_value.strip()
        for name in env_names:
            value = os.getenv(name)
            if value and value.strip():
                return value.strip()
        return ""
