"""Canonical SkillDefinition model — the lingua franca of the framework."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator

from agentic.core.constants import AuditClassification, ExecutionMode, LifecycleStatus, RiskLevel


class SLATargets(BaseModel):
    """Latency and availability expectations for a skill."""

    p50_ms: int = 1_000
    p99_ms: int = 5_000
    timeout_ms: int = 30_000
    availability_pct: float = 99.0


class SkillDefinition(BaseModel):
    """
    Standard skill contract as defined in architecture section 10.

    Every skill registered in the framework must conform to this schema.
    """

    # Identity
    skill_id: str = Field(
        description="Globally unique identifier, e.g. doc.summarize.v1"
    )
    name: str = Field(description="Human-readable skill name")
    description: str = Field(description="Short explanation of the skill purpose")

    # Classification
    category: str = Field(description="Domain grouping, e.g. search, reporting, workflow")
    owner: str = Field(description="Team or individual responsible for maintenance")
    version: str = Field(description="Semantic version, e.g. 1.0.0")

    # Contracts
    input_schema: dict[str, Any] = Field(
        default_factory=lambda: {"type": "object", "properties": {}},
        description="JSON Schema for accepted inputs",
    )
    output_schema: dict[str, Any] = Field(
        default_factory=lambda: {"type": "object", "properties": {}},
        description="JSON Schema for emitted outputs",
    )

    # Governance
    permissions: list[str] = Field(
        default_factory=list,
        description="Required scopes or roles to invoke this skill",
    )
    risk_level: RiskLevel = Field(
        default=RiskLevel.LOW,
        description="Policy risk classification",
    )
    audit_classification: AuditClassification = Field(
        default=AuditClassification.STANDARD,
        description="Level of logging and retention required",
    )

    # Runtime
    execution_mode: ExecutionMode = Field(
        default=ExecutionMode.LOCAL,
        description="How the skill is invoked at runtime",
    )
    dependencies: list[str] = Field(
        default_factory=list,
        description="Other skill_ids this skill depends on",
    )

    # Discovery
    tags: list[str] = Field(default_factory=list, description="Discovery attributes")

    # Lifecycle
    status: LifecycleStatus = Field(default=LifecycleStatus.DRAFT)
    health_status: str = Field(default="unknown", description="Operational readiness")

    # SLA
    sla_targets: SLATargets = Field(default_factory=SLATargets)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    @field_validator("skill_id")
    @classmethod
    def skill_id_no_spaces(cls, v: str) -> str:
        if " " in v:
            raise ValueError("skill_id must not contain spaces")
        return v

    @field_validator("version")
    @classmethod
    def version_semver_format(cls, v: str) -> str:
        parts = v.split(".")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            raise ValueError("version must be in semver format: MAJOR.MINOR.PATCH")
        return v

    def is_invocable(self) -> bool:
        """Return True only if this skill is in Published status."""
        return self.status == LifecycleStatus.PUBLISHED

    def requires_approval(self) -> bool:
        return self.risk_level == RiskLevel.HIGH

    class Config:
        use_enum_values = False
