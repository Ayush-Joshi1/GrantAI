from __future__ import annotations

import logging
import os
from pathlib import Path
from time import perf_counter
from typing import Any, Protocol

from src.core.errors.exceptions import UpstreamError, ValidationError
from src.core.config.settings import get_settings

logger = logging.getLogger("api.infrastructure.ibm.granite")


class GraniteInferenceProtocol(Protocol):
    def generate(self, prompt: str, **kwargs: Any) -> Any:
        ...

    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> Any:
        ...


class GraniteClient:
    """Thin adapter for IBM Granite inference via the verified watsonx SDK path."""

    def __init__(self, inference_client: GraniteInferenceProtocol | None = None, settings: Any | None = None) -> None:
        self.settings = settings or get_settings()
        self._inference_client = inference_client

    def generate(self, prompt: str) -> str:
        if not prompt or not prompt.strip():
            raise ValidationError("Prompt must not be empty.")

        client = self._inference_client or self._build_inference_client()
        logger.info("Granite generation started")
        # Prefer the chat API path for production RAG prompting. Only use
        # text-generation APIs if chat is unavailable. This avoids the
        # observed empty-payloads and extra latency on generation endpoints.
        messages = self._build_chat_messages(prompt)

        # If the client supports chat, use it first and surface any failures
        # as upstream errors rather than silently falling back to generation.
        if hasattr(client, "chat"):
            try:
                start = perf_counter()
                response = client.chat(messages=messages)
                elapsed = perf_counter() - start
                # expose last generation latency for diagnostics
                try:
                    self.last_generation_latency_seconds = elapsed
                except Exception:
                    pass
            except Exception as exc:
                logger.exception("Granite chat failed")
                raise self._wrap_failure(exc) from exc

            logger.info("Granite raw chat response type=%s repr=%r", type(response), response)
            generated_text = self._extract_generated_text(response)
            if not generated_text or not generated_text.strip():
                raise UpstreamError("Granite returned an empty chat response.")

            logger.info("Granite chat generation completed")
            return generated_text

        # Fallback: client does not support chat, use generate() if present
        try:
            response = client.generate(prompt=prompt)
        except Exception as exc:
            logger.exception("Granite generation failed (no chat available)")
            raise self._wrap_failure(exc) from exc

        logger.info("Granite raw response type=%s repr=%r", type(response), response)
        generated_text = self._extract_generated_text(response)
        if not generated_text or not generated_text.strip():
            raise UpstreamError("Granite returned an empty response.")

        logger.info("Granite generation completed (generate path)")
        return generated_text

    def _build_inference_client(self) -> GraniteInferenceProtocol:
        api_key = self._get_env_value("WATSONX_API_KEY", "WATSONX_APIKEY", "IBM_API_KEY")
        project_id = self._get_env_value("WATSONX_PROJECT_ID", "PROJECT_ID")
        url = self._normalize_url(self._get_env_value("WATSONX_URL", "IBM_URL"))
        model_id = self._get_env_value("GRANITE_MODEL_ID", "WATSONX_MODEL_ID", "MODEL_ID") or "ibm/granite-8b-code-instruct"

        if not api_key or not project_id:
            raise UpstreamError("Granite configuration is missing required IBM watsonx credentials.")

        try:
            from ibm_watsonx_ai import Credentials
            from ibm_watsonx_ai.foundation_models import ModelInference
        except Exception as exc:
            logger.exception("Failed to import IBM watsonx SDK")
            raise UpstreamError("Granite SDK is unavailable.") from exc

        credentials = Credentials(url=url, api_key=api_key)
        return ModelInference(
            model_id=model_id,
            credentials=credentials,
            project_id=project_id,
            params={"temperature": 0.1},
            validate=False,
        )

    def _extract_generated_text(self, response: Any) -> str:
        if isinstance(response, str):
            return response.strip()

        candidate_payloads: list[Any] = []
        if isinstance(response, dict):
            candidate_payloads.append(response)
        elif isinstance(response, list):
            candidate_payloads.extend(response)
        elif hasattr(response, "to_dict"):
            try:
                payload = response.to_dict()
            except Exception:
                payload = None
            if isinstance(payload, dict):
                candidate_payloads.append(payload)

        for payload in candidate_payloads:
            if isinstance(payload, dict):
                for key in ("generated_text", "text", "output_text", "completion"):
                    value = payload.get(key)
                    if isinstance(value, str) and value.strip():
                        return value.strip()
                if isinstance(payload.get("results"), list) and payload["results"]:
                    for first in payload["results"]:
                        if isinstance(first, dict):
                            for key in ("generated_text", "text", "output_text", "completion"):
                                value = first.get(key)
                                if isinstance(value, str) and value.strip():
                                    return value.strip()
                        elif hasattr(first, "generated_text") and isinstance(first.generated_text, str) and first.generated_text.strip():
                            return first.generated_text.strip()
                for key in ("output", "choices"):
                    value = payload.get(key)
                    if isinstance(value, list) and value:
                        for item in value:
                            if isinstance(item, dict):
                                for nested_key in ("text", "generated_text", "message"):
                                    nested_value = item.get(nested_key)
                                    if isinstance(nested_value, str) and nested_value.strip():
                                        return nested_value.strip()
                                    if nested_key == "message" and isinstance(nested_value, dict):
                                        message_content = nested_value.get("content")
                                        if isinstance(message_content, str) and message_content.strip():
                                            return message_content.strip()
            elif isinstance(payload, list):
                for item in payload:
                    if isinstance(item, dict):
                        for key in ("generated_text", "text", "output_text", "completion"):
                            value = item.get(key)
                            if isinstance(value, str) and value.strip():
                                return value.strip()

        if hasattr(response, "generated_text") and isinstance(response.generated_text, str) and response.generated_text.strip():
            return response.generated_text.strip()

        if hasattr(response, "result") and isinstance(response.result, str) and response.result.strip():
            return response.result.strip()

        if hasattr(response, "results") and isinstance(response.results, list) and response.results:
            for first in response.results:
                if isinstance(first, dict):
                    for key in ("generated_text", "text", "output_text", "completion"):
                        value = first.get(key)
                        if isinstance(value, str) and value.strip():
                            return value.strip()
                elif hasattr(first, "generated_text") and isinstance(first.generated_text, str) and first.generated_text.strip():
                    return first.generated_text.strip()

        raise UpstreamError("Granite returned an unusable response payload.")

    def _build_chat_messages(self, prompt: str) -> list[dict[str, str]]:
        system_marker = "SYSTEM INSTRUCTION"
        context_marker = "RETRIEVED GOVERNMENT GRANT CONTEXT"
        user_marker = "USER QUESTION"

        if system_marker in prompt and user_marker in prompt:
            system_part = prompt.split(system_marker, 1)[1]
            if context_marker in system_part:
                system_part = system_part.split(context_marker, 1)[0]
            elif user_marker in system_part:
                system_part = system_part.split(user_marker, 1)[0]
            system_part = system_part.strip()

            if context_marker in prompt:
                user_part = context_marker + prompt.split(context_marker, 1)[1]
            else:
                user_part = prompt.split(user_marker, 1)[1]
            user_part = user_part.strip()

            return [
                {"role": "system", "content": system_part},
                {"role": "user", "content": user_part},
            ]

        return [{"role": "user", "content": prompt}]

    def _generate_with_chat(self, prompt: str, client: GraniteInferenceProtocol) -> str:
        messages = self._build_chat_messages(prompt)
        try:
            response = client.chat(messages=messages)
        except Exception as exc:
            logger.exception("Granite chat fallback failed")
            raise self._wrap_failure(exc) from exc

        logger.info("Granite raw chat response type=%s repr=%r", type(response), response)
        generated_text = self._extract_generated_text(response)
        if not generated_text or not generated_text.strip():
            raise UpstreamError("Granite returned an empty chat response.")
        return generated_text

    def _wrap_failure(self, exc: Exception) -> Exception:
        message = str(exc).strip()
        if not message:
            message = "Granite inference failed."
        if any(token in message.lower() for token in ("api key", "project_id", "project id", "credentials", "credential")):
            return UpstreamError("Granite configuration is invalid.")
        if "timeout" in message.lower():
            return UpstreamError("Granite request timed out.")
        return UpstreamError("Granite inference failed.")

    def _get_env_value(self, *names: str) -> str:
        for name in names:
            value = os.getenv(name)
            if value and value.strip():
                return value.strip()

        for env_path in self._candidate_env_paths():
            if not env_path.exists():
                continue
            for line in env_path.read_text(encoding="utf-8").splitlines():
                if not line or line.lstrip().startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                if key in names and value:
                    return value
        return ""

    def _candidate_env_paths(self) -> list[Path]:
        cwd = Path.cwd()
        candidates = [cwd / ".env", cwd / "apps" / "web" / ".env"]
        if cwd != cwd.parent:
            candidates.append(cwd.parent / ".env")
        return candidates

    def _normalize_url(self, raw_url: str | None) -> str:
        if not raw_url:
            return "https://us-south.ml.cloud.ibm.com"

        url = raw_url.strip()
        if url.startswith("https:https://"):
            url = url.replace("https:https://", "https://", 1)
        elif url.startswith("http://"):
            url = url.replace("http://", "https://", 1)
        elif not url.startswith("https://"):
            url = f"https://{url}"
        return url
