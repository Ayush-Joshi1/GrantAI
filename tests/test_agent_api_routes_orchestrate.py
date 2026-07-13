from __future__ import annotations

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
for candidate in (ROOT, ROOT / "apps" / "api"):
    if str(candidate) not in sys.path:
        sys.path.insert(0, str(candidate))

from src.application.deps import get_orchestrate_service
from src.application.services.orchestrate_service import OrchestrateExecutionResult
from src.application.services.orchestrate_service import OrchestrateService
from src.main import app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


class StubOrchestrateService:
    def __init__(self, result: OrchestrateExecutionResult | None = None) -> None:
        self.result = result or OrchestrateExecutionResult(execution_id="exec-123", status="completed", output={"result": "ok"})
        self.calls: list[dict[str, object]] = []

    def execute(self, workflow_id: str, inputs: dict[str, object]) -> OrchestrateExecutionResult:
        self.calls.append({"workflow_id": workflow_id, "inputs": inputs})
        return self.result


def test_orchestrate_endpoint_uses_orchestrate_service(client: TestClient) -> None:
    stub_service = StubOrchestrateService()
    app.dependency_overrides[get_orchestrate_service] = lambda: stub_service

    response = client.post(
        "/api/v1/orchestrate/execute",
        json={"workflow_id": "recommendation", "inputs": {"query": "AI startup"}},
    )

    assert response.status_code == 200
    assert response.json()["execution_id"] == "exec-123"
    assert response.json()["status"] == "completed"
    assert response.json()["output"] == {"result": "ok"}
    assert stub_service.calls == [{"workflow_id": "recommendation", "inputs": {"query": "AI startup"}}]

    app.dependency_overrides.clear()
