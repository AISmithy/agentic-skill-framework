"""Human-in-the-loop approval state machine."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from agentic.core.constants import ApprovalStatus
from agentic.core.exceptions import ApprovalRequiredError
from agentic.layer7_observability.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ApprovalRequest:
    approval_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    skill_id: str = ""
    actor: str = ""
    inputs: dict[str, Any] = field(default_factory=dict)
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc) + timedelta(hours=24)
    )
    reviewed_by: str | None = None
    review_notes: str = ""
    reviewed_at: datetime | None = None


class ApprovalWorkflow:
    """In-memory approval queue for high-risk skill executions."""

    def __init__(self) -> None:
        self._requests: dict[str, ApprovalRequest] = {}

    def request_approval(
        self, skill_id: str, actor: str, inputs: dict[str, Any]
    ) -> ApprovalRequest:
        """Create a new pending approval request."""
        req = ApprovalRequest(skill_id=skill_id, actor=actor, inputs=inputs)
        self._requests[req.approval_id] = req
        logger.info(
            "approval_requested",
            approval_id=req.approval_id,
            skill_id=skill_id,
            actor=actor,
        )
        return req

    def get(self, approval_id: str) -> ApprovalRequest:
        req = self._requests.get(approval_id)
        if not req:
            raise KeyError(f"Approval request not found: {approval_id}")
        return req

    def approve(self, approval_id: str, reviewer: str, notes: str = "") -> ApprovalRequest:
        req = self.get(approval_id)
        self._check_not_expired(req)
        req.status = ApprovalStatus.APPROVED
        req.reviewed_by = reviewer
        req.review_notes = notes
        req.reviewed_at = datetime.now(timezone.utc)
        logger.info("approval_approved", approval_id=approval_id, reviewer=reviewer)
        return req

    def reject(self, approval_id: str, reviewer: str, notes: str = "") -> ApprovalRequest:
        req = self.get(approval_id)
        req.status = ApprovalStatus.REJECTED
        req.reviewed_by = reviewer
        req.review_notes = notes
        req.reviewed_at = datetime.now(timezone.utc)
        logger.info("approval_rejected", approval_id=approval_id, reviewer=reviewer)
        return req

    def check_approved(self, approval_id: str) -> None:
        """Raise ApprovalRequiredError if the request is not approved."""
        req = self.get(approval_id)
        self._check_not_expired(req)
        if req.status != ApprovalStatus.APPROVED:
            raise ApprovalRequiredError(req.skill_id, approval_id)

    def _check_not_expired(self, req: ApprovalRequest) -> None:
        if datetime.now(timezone.utc) > req.expires_at:
            req.status = ApprovalStatus.EXPIRED
            raise ApprovalRequiredError(req.skill_id, req.approval_id)

    def list_pending(self) -> list[ApprovalRequest]:
        return [r for r in self._requests.values() if r.status == ApprovalStatus.PENDING]
