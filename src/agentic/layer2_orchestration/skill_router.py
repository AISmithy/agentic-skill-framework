"""Skill router — selects the best-fit published skill for a plan step."""

from __future__ import annotations

from agentic.core.exceptions import RoutingFailedError
from agentic.layer2_orchestration.planner import PlanStep
from agentic.layer3_skill_library.models.skill import SkillDefinition
from agentic.layer3_skill_library.registry import SkillRegistry
from agentic.layer7_observability.logger import get_logger

logger = get_logger(__name__)


class SkillRouter:
    """
    Routes a PlanStep to the best available published skill.

    Selection criteria (in order):
      1. Tag match on step.skill_hint
      2. Category match on step.skill_hint
      3. Name/description keyword match
    """

    def __init__(self, registry: SkillRegistry) -> None:
        self._registry = registry

    def route(self, step: PlanStep) -> SkillDefinition:
        """Return the best-fit published skill for the given step."""
        candidates = self._registry.list_published()

        if not candidates:
            raise RoutingFailedError(step.name, "No published skills available")

        # Score each candidate
        scored = [(skill, self._score(skill, step)) for skill in candidates]
        scored.sort(key=lambda x: x[1], reverse=True)

        best_skill, best_score = scored[0]
        if best_score == 0:
            raise RoutingFailedError(
                step.name,
                f"No skill matched hint '{step.skill_hint}' or step name '{step.name}'",
            )

        logger.info(
            "skill_routed",
            step=step.name,
            skill_id=best_skill.skill_id,
            score=best_score,
        )
        return best_skill

    def _score(self, skill: SkillDefinition, step: PlanStep) -> float:
        score = 0.0
        hint = (step.skill_hint or "").lower()
        step_name = step.name.lower()

        if hint:
            # Tag exact match
            if hint in [t.lower() for t in skill.tags]:
                score += 3.0
            # Category match
            if hint == skill.category.lower():
                score += 2.0
            # Partial match in name/description
            if hint in skill.name.lower() or hint in skill.description.lower():
                score += 1.0

        # Step name keyword in skill tags
        for tag in skill.tags:
            if tag.lower() in step_name:
                score += 0.5

        return score
