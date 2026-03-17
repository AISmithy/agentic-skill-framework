"""Skill execution quality evaluator."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agentic.layer7_observability.logger import get_logger

logger = get_logger(__name__)


@dataclass
class EvaluationResult:
    skill_id: str
    execution_id: str
    success: bool
    duration_ms: float
    schema_valid: bool = True
    policy_outcome: str = "allow"
    retry_count: int = 0
    quality_score: float | None = None
    notes: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)


class ExecutionEvaluator:
    """Records and scores skill execution outcomes."""

    def __init__(self) -> None:
        self._records: list[EvaluationResult] = []

    def record(self, result: EvaluationResult) -> None:
        self._records.append(result)
        logger.info(
            "execution_evaluated",
            skill_id=result.skill_id,
            execution_id=result.execution_id,
            success=result.success,
            duration_ms=round(result.duration_ms, 2),
            quality_score=result.quality_score,
        )

    def success_rate(self, skill_id: str | None = None) -> float:
        records = [r for r in self._records if not skill_id or r.skill_id == skill_id]
        if not records:
            return 0.0
        return sum(1 for r in records if r.success) / len(records)

    def avg_duration_ms(self, skill_id: str | None = None) -> float:
        records = [r for r in self._records if not skill_id or r.skill_id == skill_id]
        if not records:
            return 0.0
        return sum(r.duration_ms for r in records) / len(records)

    def get_records(self, skill_id: str | None = None) -> list[EvaluationResult]:
        if skill_id:
            return [r for r in self._records if r.skill_id == skill_id]
        return list(self._records)

    def summary(self) -> dict[str, Any]:
        skill_ids = {r.skill_id for r in self._records}
        return {
            sid: {
                "success_rate": self.success_rate(sid),
                "avg_duration_ms": round(self.avg_duration_ms(sid), 2),
                "total_executions": len(self.get_records(sid)),
            }
            for sid in skill_ids
        }
