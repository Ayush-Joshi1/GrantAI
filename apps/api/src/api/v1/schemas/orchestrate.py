from __future__ import annotations

from pydantic import BaseModel, Field


class OrchestrateExecuteRequest(BaseModel):
    workflow_id: str = Field(..., description="IBM watsonx Orchestrate workflow identifier")
    inputs: dict[str, object] | None = Field(default_factory=dict, description="Workflow inputs mapped to the Orchestrate definition")


class OrchestrateExecuteResponse(BaseModel):
    execution_id: str = Field(..., description="Orchestrate execution identifier")
    status: str = Field(..., description="Orchestrate execution status")
    output: dict[str, object] = Field(default_factory=dict, description="Workflow execution output payload")
