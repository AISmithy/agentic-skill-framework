"""BaseSkill abstract class — all skills must inherit from this."""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from agentic.layer3_skill_library.models.skill import SkillDefinition


class HealthStatus(str, Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"


class BaseSkill(ABC):
    """
    Abstract base class for all skill implementations.

    Every skill must:
      - Declare a class-level `manifest: SkillDefinition`.
      - Implement `async def execute(self, inputs: dict) -> dict`.
      - Optionally override `async def health_check()`.

    The framework calls only this interface — skill internals are never
    imported directly by framework layers.
    """

    manifest: SkillDefinition

    @abstractmethod
    async def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        """
        Execute the skill with validated inputs.

        Returns a dict that must conform to the skill's output_schema.
        Must NOT raise exceptions for expected business errors — encode
        them in the output dict instead.
        """
        ...

    async def health_check(self) -> HealthStatus:
        """Return the operational health of this skill instance."""
        return HealthStatus.HEALTHY
