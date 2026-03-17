"""Task planner — decomposes a GoalSpec into an ordered ExecutionPlan."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any

from agentic.layer2_orchestration.goal_interpreter import GoalSpec
from agentic.layer7_observability.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PlanStep:
    """A single step in an execution plan."""

    step_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    name: str = ""
    description: str = ""
    skill_hint: str = ""          # Suggested skill category or tag
    required_inputs: list[str] = field(default_factory=list)
    expected_outputs: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)  # step_ids this step depends on
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionPlan:
    plan_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    goal: GoalSpec = field(default_factory=lambda: GoalSpec("", "", ""))
    steps: list[PlanStep] = field(default_factory=list)
    status: str = "pending"       # pending / running / completed / failed


# Domain-specific plan templates
_PLAN_TEMPLATES: dict[str, list[dict]] = {
    "knowledge-processing": [
        {"name": "retrieve_documents", "skill_hint": "search", "description": "Retrieve relevant documents"},
        {"name": "process_content", "skill_hint": "knowledge-processing", "description": "Process and analyze content"},
    ],
    "search": [
        {"name": "execute_search", "skill_hint": "search", "description": "Execute the search query"},
        {"name": "format_results", "skill_hint": "knowledge-processing", "description": "Format and rank results"},
    ],
    "reporting": [
        {"name": "gather_data", "skill_hint": "search", "description": "Gather required data"},
        {"name": "generate_report", "skill_hint": "reporting", "description": "Generate the report"},
    ],
    "workflow": [
        {"name": "prepare_payload", "skill_hint": "knowledge-processing", "description": "Prepare the workflow payload"},
        {"name": "trigger_workflow", "skill_hint": "workflow", "description": "Trigger the downstream workflow"},
    ],
}


class TaskPlanner:
    """
    Decomposes a GoalSpec into a sequential ExecutionPlan.

    The default implementation uses domain-based templates. A production
    system would use an LLM to dynamically generate plans.
    """

    def plan(self, goal: GoalSpec) -> ExecutionPlan:
        template = _PLAN_TEMPLATES.get(
            goal.domain,
            [{"name": "execute_task", "skill_hint": "general", "description": goal.raw_goal}],
        )

        steps: list[PlanStep] = []
        for i, step_def in enumerate(template):
            step = PlanStep(
                name=step_def["name"],
                description=step_def.get("description", ""),
                skill_hint=step_def.get("skill_hint", ""),
                depends_on=[steps[i - 1].step_id] if i > 0 else [],
            )
            steps.append(step)

        plan = ExecutionPlan(goal=goal, steps=steps)
        logger.info(
            "plan_created",
            plan_id=plan.plan_id,
            steps=len(steps),
            domain=goal.domain,
        )
        return plan
