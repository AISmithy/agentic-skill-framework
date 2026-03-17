from typing import Optional
from ..models import PlanStep
from ..skill_library.skill_definition import Skill
from ..skill_library.registry import SkillRegistry

class SkillRouter:
    def route(self, step: PlanStep, registry: SkillRegistry) -> Optional[Skill]:
        return registry.get(step.skill_name)

    def select_best_skill(self, candidates: list[Skill], step: PlanStep) -> Optional[Skill]:
        return candidates[0] if candidates else None
