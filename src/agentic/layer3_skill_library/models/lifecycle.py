"""Lifecycle transition records for skill governance."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from agentic.core.constants import LifecycleStatus


class LifecycleTransition(BaseModel):
    """Audit record for a single skill lifecycle state change."""

    skill_id: str
    from_status: LifecycleStatus
    to_status: LifecycleStatus
    actor: str
    reason: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ApprovalRecord(BaseModel):
    """Record of an approval gate for publishing a skill."""

    skill_id: str
    approver: str
    approved: bool
    notes: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
