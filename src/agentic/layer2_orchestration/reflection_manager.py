"""Reflection manager — evaluates outcomes and decides on retry or replan."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from agentic.layer2_orchestration.workflow_engine import WorkflowResult
from agentic.layer7_observability.logger import get_logger

logger = get_logger(__name__)


class ReflectionAction(str, Enum):
    ACCEPT = "accept"
    RETRY = "retry"
    REPLAN = "replan"
    ESCALATE = "escalate"


@dataclass
class ReflectionOutcome:
    action: ReflectionAction
    reason: str
    retry_step: str | None = None


class ReflectionManager:
    """
    Evaluates a WorkflowResult and decides what to do next.

    Actions:
      ACCEPT   — result is good, return to caller.
      RETRY    — transient error; retry the failed step.
      REPLAN   — structural failure; request a new plan.
      ESCALATE — unrecoverable; surface to human.
    """

    def __init__(self, max_retries: int = 2) -> None:
        self._max_retries = max_retries
        self._retry_counts: dict[str, int] = {}

    def reflect(self, result: WorkflowResult) -> ReflectionOutcome:
        if result.success:
            logger.info("reflection_accept", plan_id=result.plan_id)
            return ReflectionOutcome(
                action=ReflectionAction.ACCEPT,
                reason="Workflow completed successfully",
            )

        error = result.error or ""
        plan_id = result.plan_id

        # Determine retry vs replan vs escalate
        retries = self._retry_counts.get(plan_id, 0)

        if retries < self._max_retries and self._is_transient(error):
            self._retry_counts[plan_id] = retries + 1
            logger.warning(
                "reflection_retry",
                plan_id=plan_id,
                attempt=retries + 1,
                max=self._max_retries,
            )
            return ReflectionOutcome(
                action=ReflectionAction.RETRY,
                reason=f"Transient error, retry {retries + 1}/{self._max_retries}",
            )

        if self._is_replanning_viable(error):
            logger.warning("reflection_replan", plan_id=plan_id)
            return ReflectionOutcome(
                action=ReflectionAction.REPLAN,
                reason="Structural failure; requesting new plan",
            )

        logger.error("reflection_escalate", plan_id=plan_id, error=error)
        return ReflectionOutcome(
            action=ReflectionAction.ESCALATE,
            reason=f"Unrecoverable failure: {error}",
        )

    def _is_transient(self, error: str) -> bool:
        transient_keywords = ["timeout", "connection", "temporary", "unavailable", "retry"]
        return any(kw in error.lower() for kw in transient_keywords)

    def _is_replanning_viable(self, error: str) -> bool:
        replan_keywords = ["not found", "no skill", "routing failed"]
        return any(kw in error.lower() for kw in replan_keywords)
