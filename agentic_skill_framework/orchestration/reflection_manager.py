from typing import Optional
from ..models import SkillResult, WorkflowContext, PlanStep

class ReflectionManager:
    def should_retry(self, result: SkillResult, attempt: int, max_attempts: int) -> bool:
        return result.status == "error" and attempt < max_attempts

    def reflect(self, context: WorkflowContext, failed_step: PlanStep) -> str:
        return (f"Step '{failed_step.step_id}' with skill '{failed_step.skill_name}' "
                f"failed in session '{context.session_id}'. "
                f"Reflecting on failure and considering alternatives.")

    def recover(self, context: WorkflowContext, failed_step: PlanStep) -> Optional[PlanStep]:
        if not failed_step.inputs:
            return None
        return PlanStep(
            step_id=failed_step.step_id,
            skill_name=failed_step.skill_name,
            inputs={},
            depends_on=failed_step.depends_on
        )
