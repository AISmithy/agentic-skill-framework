from collections import deque
from typing import TYPE_CHECKING
from ..models import Plan, PlanStep, WorkflowContext, SkillResult
from ..skill_library.registry import SkillRegistry
from .skill_router import SkillRouter

if TYPE_CHECKING:
    from ..runtime.executor import Executor

class WorkflowEngine:
    def __init__(self, registry: SkillRegistry, executor: "Executor"):
        self.registry = registry
        self.executor = executor
        self._router = SkillRouter()

    def _topological_sort(self, steps: list[PlanStep]) -> list[PlanStep]:
        step_map = {s.step_id: s for s in steps}
        in_degree = {s.step_id: 0 for s in steps}
        adj = {s.step_id: [] for s in steps}
        for s in steps:
            for dep in s.depends_on:
                if dep in adj:
                    adj[dep].append(s.step_id)
                    in_degree[s.step_id] += 1
        queue = deque([sid for sid, deg in in_degree.items() if deg == 0])
        result = []
        while queue:
            sid = queue.popleft()
            result.append(step_map[sid])
            for neighbor in adj[sid]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        return result

    def run(self, plan: Plan, context: WorkflowContext) -> WorkflowContext:
        sorted_steps = self._topological_sort(plan.steps)
        for step in sorted_steps:
            result = self.run_step(step, context)
            context.results[step.step_id] = result
        return context

    def run_step(self, step: PlanStep, context: WorkflowContext) -> SkillResult:
        skill = self._router.route(step, self.registry)
        if skill is None:
            return SkillResult(skill_name=step.skill_name, status="error", output=None, error="Skill not found")
        return self.executor.execute(skill, step.inputs)
