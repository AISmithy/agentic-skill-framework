"""Skill execution endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from agentic.core.exceptions import (
    AgenticError,
    ApprovalRequiredError,
    CircuitOpenError,
    PolicyViolationError,
    SkillNotFoundError,
    UnauthorizedError,
)
from agentic.layer4_runtime.executor import SkillExecutor, SkillInvocation

router = APIRouter(prefix="/executions", tags=["executions"])


class ExecuteRequest(BaseModel):
    skill_id: str
    inputs: dict[str, Any] = {}
    environment: str = "development"


@router.post("")
async def execute_skill(body: ExecuteRequest, request: Request) -> dict:
    executor: SkillExecutor | None = getattr(request.app.state, "executor", None)
    if not executor:
        raise HTTPException(status_code=503, detail="Executor not initialized")

    identity = getattr(request.state, "identity", None)
    if not identity:
        raise HTTPException(status_code=401, detail="Not authenticated")

    invocation = SkillInvocation(
        skill_id=body.skill_id,
        inputs=body.inputs,
        identity=identity,
        environment=body.environment,
    )

    result = await executor.execute(invocation)

    if not result.success:
        # Surface specific error types as appropriate HTTP codes
        error = result.error or "Execution failed"
        if "not authorized" in error.lower() or "unauthorized" in error.lower():
            raise HTTPException(status_code=403, detail=error)
        if "policy violation" in error.lower():
            raise HTTPException(status_code=403, detail=error)
        if "approval required" in error.lower():
            raise HTTPException(status_code=202, detail=error)
        if "circuit" in error.lower():
            raise HTTPException(status_code=503, detail=error)
        raise HTTPException(status_code=500, detail=error)

    return {
        "execution_id": result.execution_id,
        "skill_id": result.skill_id,
        "success": result.success,
        "output": result.output,
        "duration_ms": round(result.duration_ms, 2),
    }
