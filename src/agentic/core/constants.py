"""Shared enumerations used across all framework layers."""

from enum import Enum


class LifecycleStatus(str, Enum):
    """Skill lifecycle states: Draft → Tested → Approved → Published → Deprecated → Retired."""

    DRAFT = "draft"
    TESTED = "tested"
    APPROVED = "approved"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


# Valid lifecycle transitions (from → set of allowed to states)
LIFECYCLE_TRANSITIONS: dict[LifecycleStatus, set[LifecycleStatus]] = {
    LifecycleStatus.DRAFT: {LifecycleStatus.TESTED, LifecycleStatus.RETIRED},
    LifecycleStatus.TESTED: {LifecycleStatus.APPROVED, LifecycleStatus.DRAFT},
    LifecycleStatus.APPROVED: {LifecycleStatus.PUBLISHED, LifecycleStatus.TESTED},
    LifecycleStatus.PUBLISHED: {LifecycleStatus.DEPRECATED},
    LifecycleStatus.DEPRECATED: {LifecycleStatus.RETIRED},
    LifecycleStatus.RETIRED: set(),
}


class RiskLevel(str, Enum):
    """Risk classification for governance policy evaluation."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ExecutionMode(str, Enum):
    """How a skill is invoked at runtime."""

    LOCAL = "local"
    CONTAINER = "container"
    SERVERLESS = "serverless"
    REMOTE_API = "remote_api"
    HYBRID = "hybrid"


class AuditClassification(str, Enum):
    """Logging and retention requirements for a skill's executions."""

    STANDARD = "standard"
    ENHANCED = "enhanced"
    STRICT = "strict"


class PolicyDecision(str, Enum):
    """Outcome of a policy engine evaluation."""

    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


class ApprovalStatus(str, Enum):
    """State of a human-in-the-loop approval request."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class CircuitState(str, Enum):
    """Circuit breaker states."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"
