from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "apps" / "api"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from src.application.services.orchestrate_service import OrchestrateExecutionResult, OrchestrateService
from src.infrastructure.ibm.orchestrate_client import WatsonxOrchestrateClient
from src.core.errors.exceptions import UpstreamError, ValidationError


class StubOrchestrateClient:
    def __init__(self, response: dict[str, object] | None = None, error: Exception | None = None) -> None:
        self.response = response or {"execution_id": "exec-123", "status": "completed", "output": {"result": "ok"}}
        self.error = error
        self.calls: list[tuple[str, dict[str, object]]] = []

    def execute_workflow(self, workflow_id: str, inputs: dict[str, object]) -> dict[str, object]:
        self.calls.append((workflow_id, inputs))
        if self.error is not None:
            raise self.error
        return self.response


def test_orchestrate_service_executes_workflow_successfully() -> None:
    client = StubOrchestrateClient()
    service = OrchestrateService(orchestrate_client=client)

    result = service.execute("grant-recommendation", {"query": "AI startup"})

    assert isinstance(result, OrchestrateExecutionResult)
    assert result.execution_id == "exec-123"
    assert result.status == "completed"
    assert result.output == {"result": "ok"}
    assert client.calls == [("grant-recommendation", {"query": "AI startup"})]


def test_orchestrate_service_rejects_empty_workflow_id() -> None:
    service = OrchestrateService(orchestrate_client=StubOrchestrateClient())

    with pytest.raises(ValidationError):
        service.execute("", {})


def test_orchestrate_service_handles_invalid_output() -> None:
    client = StubOrchestrateClient(response={"execution_id": "exec-123", "status": "failed", "output": "not a dict"})
    service = OrchestrateService(orchestrate_client=client)

    with pytest.raises(UpstreamError):
        service.execute("grant-recommendation", {"query": "AI startup"})
