"""Workflow engine — executes an ExecutionPlan step-by-step."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from agentic.layer2_orchestration.context_manager import ContextManager
from agentic.layer2_orchestration.planner import ExecutionPlan, PlanStep
from agentic.layer2_orchestration.skill_router import SkillRouter
from agentic.layer4_runtime.executor import SkillExecutor, SkillInvocation
from agentic.layer5_memory.artifact_store import ArtifactStore
from agentic.layer5_memory.session_memory import SessionMemory
from agentic.layer6_governance.authn import Identity
from agentic.layer7_observability.logger import get_logger
from agentic.layer7_observability.tracer import start_span

logger = get_logger(__name__)


@dataclass
class WorkflowResult:
    plan_id: str
    success: bool
    step_outputs: dict[str, Any] = field(default_factory=dict)
    final_output: Any = None
    error: str | None = None
    steps_completed: int = 0
    steps_total: int = 0


class WorkflowEngine:
    """
    Executes an ExecutionPlan sequentially, passing outputs between steps.

    Each step:
      1. Router selects the appropriate skill.
      2. Context manager merges session + prior outputs into skill inputs.
      3. Executor runs the skill.
      4. Output is stored in step_outputs and session memory.
    """

    def __init__(
        self,
        router: SkillRouter,
        executor: SkillExecutor,
        context_manager: ContextManager,
        artifact_store: ArtifactStore,
    ) -> None:
        self._router = router
        self._executor = executor
        self._ctx_mgr = context_manager
        self._artifacts = artifact_store

    async def run(
        self,
        plan: ExecutionPlan,
        identity: Identity,
        session: SessionMemory,
        initial_inputs: dict[str, Any] | None = None,
    ) -> WorkflowResult:
        with start_span("workflow.run", plan_id=plan.plan_id) as span:
            plan.status = "running"
            step_outputs: dict[str, Any] = {}
            final_output: Any = None

            if initial_inputs:
                for k, v in initial_inputs.items():
                    session.set(k, v)

            for i, step in enumerate(plan.steps):
                logger.info(
                    "workflow_step_start",
                    plan_id=plan.plan_id,
                    step=step.name,
                    step_num=i + 1,
                    total=len(plan.steps),
                )

                try:
                    output = await self._execute_step(step, identity, session, step_outputs)
                    step_outputs[step.step_id] = output
                    step_outputs[step.name] = output
                    session.set(f"step_{step.name}_output", output)
                    final_output = output

                    # Store as artifact
                    self._artifacts.store(
                        data=output,
                        skill_id=f"workflow.{plan.plan_id}",
                        session_id=session.session_id,
                        tags=[step.name, plan.plan_id],
                    )
                except Exception as exc:
                    logger.error(
                        "workflow_step_failed",
                        plan_id=plan.plan_id,
                        step=step.name,
                        error=str(exc),
                    )
                    plan.status = "failed"
                    return WorkflowResult(
                        plan_id=plan.plan_id,
                        success=False,
                        step_outputs=step_outputs,
                        error=f"Step '{step.name}' failed: {exc}",
                        steps_completed=i,
                        steps_total=len(plan.steps),
                    )

            plan.status = "completed"
            logger.info("workflow_completed", plan_id=plan.plan_id, steps=len(plan.steps))
            return WorkflowResult(
                plan_id=plan.plan_id,
                success=True,
                step_outputs=step_outputs,
                final_output=final_output,
                steps_completed=len(plan.steps),
                steps_total=len(plan.steps),
            )

    async def _execute_step(
        self,
        step: PlanStep,
        identity: Identity,
        session: SessionMemory,
        prior_outputs: dict[str, Any],
    ) -> dict[str, Any]:
        # Route to skill
        skill = self._router.route(step)

        # Build context-aware inputs
        context = self._ctx_mgr.build_step_context(
            step_name=step.name,
            session=session,
            prior_outputs=prior_outputs,
        )

        # Only pass keys declared in input schema
        schema_props = skill.input_schema.get("properties", {})
        inputs = {k: v for k, v in context.items() if k in schema_props}

        # Add required keys with defaults if missing
        for req_key in skill.input_schema.get("required", []):
            if req_key not in inputs:
                inputs[req_key] = ""

        invocation = SkillInvocation(
            skill_id=skill.skill_id,
            inputs=inputs,
            identity=identity,
        )

        result = await self._executor.execute(invocation)
        if not result.success:
            raise RuntimeError(result.error or "Skill execution failed")

        return result.output or {}
