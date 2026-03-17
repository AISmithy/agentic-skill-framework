"""Agent goal submission endpoints."""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from agentic.layer2_orchestration.goal_interpreter import GoalInterpreter
from agentic.layer2_orchestration.planner import TaskPlanner
from agentic.layer2_orchestration.reflection_manager import ReflectionAction, ReflectionManager
from agentic.layer2_orchestration.workflow_engine import WorkflowEngine
from agentic.layer5_memory.session_memory import SessionStore

router = APIRouter(prefix="/agents", tags=["agents"])

_interpreter = GoalInterpreter()
_planner = TaskPlanner()
_reflection = ReflectionManager()
_sessions = SessionStore()


class GoalRequest(BaseModel):
    goal: str
    session_id: str | None = None
    initial_inputs: dict[str, Any] = {}


@router.post("/goal")
async def submit_goal(body: GoalRequest, request: Request) -> dict:
    engine: WorkflowEngine | None = getattr(request.app.state, "workflow_engine", None)
    if not engine:
        raise HTTPException(status_code=503, detail="Workflow engine not initialized")

    identity = getattr(request.state, "identity", None)
    if not identity:
        raise HTTPException(status_code=401, detail="Not authenticated")

    session_id = body.session_id or uuid.uuid4().hex
    session = _sessions.get_or_create(session_id)

    # Interpret → Plan → Execute
    goal_spec = _interpreter.interpret(body.goal, session_context=session.all())
    plan = _planner.plan(goal_spec)

    result = await engine.run(
        plan=plan,
        identity=identity,
        session=session,
        initial_inputs=body.initial_inputs,
    )

    reflection = _reflection.reflect(result)

    return {
        "session_id": session_id,
        "plan_id": result.plan_id,
        "success": result.success,
        "steps_completed": result.steps_completed,
        "steps_total": result.steps_total,
        "final_output": result.final_output,
        "reflection_action": reflection.action.value,
        "reflection_reason": reflection.reason,
        "error": result.error,
    }
