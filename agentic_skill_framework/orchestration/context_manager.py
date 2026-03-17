from typing import Optional
from ..models import Goal, Plan, WorkflowContext, SkillResult

class ContextManager:
    def create_context(self, session_id: str, goal: Goal, plan: Plan) -> WorkflowContext:
        return WorkflowContext(session_id=session_id, goal=goal, plan=plan)

    def update_result(self, context: WorkflowContext, step_id: str, result: SkillResult) -> None:
        context.results[step_id] = result

    def get_step_result(self, context: WorkflowContext, step_id: str) -> Optional[SkillResult]:
        return context.results.get(step_id)

    def is_complete(self, context: WorkflowContext) -> bool:
        return all(s.step_id in context.results for s in context.plan.steps)
