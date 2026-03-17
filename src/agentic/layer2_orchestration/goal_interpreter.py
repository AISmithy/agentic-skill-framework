"""Goal interpreter — converts a user goal string into a structured GoalSpec."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from agentic.core.exceptions import PlanningFailedError
from agentic.layer7_observability.logger import get_logger

logger = get_logger(__name__)


@dataclass
class GoalSpec:
    """Structured representation of a user or system goal."""

    raw_goal: str
    intent: str
    domain: str
    constraints: dict[str, Any] = field(default_factory=dict)
    expected_outputs: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)


# Simple keyword-to-domain mapping for the default interpreter
_DOMAIN_KEYWORDS: dict[str, list[str]] = {
    "knowledge-processing": ["summarize", "summary", "extract", "classify", "analyze", "review"],
    "search": ["search", "find", "lookup", "retrieve", "query", "fetch"],
    "reporting": ["report", "generate", "create", "draft", "produce"],
    "workflow": ["send", "notify", "trigger", "approve", "route", "forward"],
    "code": ["code", "program", "script", "execute", "run", "debug"],
}


class GoalInterpreter:
    """
    Parses a natural-language goal into a GoalSpec.

    The default implementation uses keyword heuristics. In production this
    would be replaced by an LLM call or a fine-tuned classifier.
    """

    def interpret(self, goal: str, session_context: dict[str, Any] | None = None) -> GoalSpec:
        if not goal or not goal.strip():
            raise PlanningFailedError(goal, "Empty goal provided")

        intent = self._extract_intent(goal)
        domain = self._detect_domain(goal)

        spec = GoalSpec(
            raw_goal=goal,
            intent=intent,
            domain=domain,
            context=session_context or {},
        )

        logger.info(
            "goal_interpreted",
            intent=intent,
            domain=domain,
            raw_goal=goal[:80],
        )
        return spec

    def _extract_intent(self, goal: str) -> str:
        """Return a normalized intent verb from the goal text."""
        goal_lower = goal.lower()
        for intent in ["summarize", "search", "generate", "classify", "send", "execute", "analyze"]:
            if intent in goal_lower:
                return intent
        return "process"

    def _detect_domain(self, goal: str) -> str:
        goal_lower = goal.lower()
        for domain, keywords in _DOMAIN_KEYWORDS.items():
            if any(kw in goal_lower for kw in keywords):
                return domain
        return "general"
