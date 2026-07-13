from __future__ import annotations

from fastapi import APIRouter, Depends

from src.api.v1.schemas.orchestrate import OrchestrateExecuteRequest, OrchestrateExecuteResponse
from src.application.deps import get_orchestrate_service
from src.application.services.orchestrate_service import OrchestrateService

router = APIRouter()


@router.post("/execute", response_model=OrchestrateExecuteResponse)
async def execute_orchestrate(
    payload: OrchestrateExecuteRequest,
    svc: OrchestrateService = Depends(get_orchestrate_service),
) -> OrchestrateExecuteResponse:
    result = svc.execute(workflow_id=payload.workflow_id, inputs=payload.inputs or {})
    return OrchestrateExecuteResponse(
        execution_id=result.execution_id,
        status=result.status,
        output=result.output,
    )
