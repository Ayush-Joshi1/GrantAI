from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.core.errors.exceptions import UpstreamError, ValidationError
from src.infrastructure.ibm.orchestrate_client import WatsonxOrchestrateClient


@dataclass(frozen=True)
class OrchestrateExecutionResult:
    execution_id: str
    status: str
    output: dict[str, Any]


class OrchestrateService:
    def __init__(self, orchestrate_client: WatsonxOrchestrateClient | None = None) -> None:
        self.orchestrate_client = orchestrate_client or WatsonxOrchestrateClient()

    def execute(self, workflow_id: str, inputs: dict[str, Any]) -> OrchestrateExecutionResult:
        if not workflow_id or not workflow_id.strip():
            raise ValidationError("Workflow ID must not be empty.")

        result = self.orchestrate_client.execute_workflow(workflow_id=workflow_id, inputs=inputs)
        execution_id = result.get("execution_id") or result.get("id")
        status = result.get("status") or result.get("state") or "unknown"
        output = result.get("output") or result.get("result") or {}

        if not isinstance(output, dict):
            raise UpstreamError("IBM watsonx Orchestrate returned a malformed output payload.")

        if not execution_id or not isinstance(execution_id, str):
            raise UpstreamError("IBM watsonx Orchestrate returned a malformed execution identifier.")

        return OrchestrateExecutionResult(execution_id=execution_id, status=status, output=output)
