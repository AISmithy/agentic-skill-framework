"""Typed exception hierarchy for the agentic framework."""


class AgenticError(Exception):
    """Root exception for all framework errors."""

    def __init__(self, message: str, code: str = "AGENTIC_ERROR") -> None:
        super().__init__(message)
        self.message = message
        self.code = code


# ---------------------------------------------------------------------------
# Skill errors
# ---------------------------------------------------------------------------


class SkillError(AgenticError):
    """Base for skill catalog and definition errors."""


class SkillNotFoundError(SkillError):
    def __init__(self, skill_id: str) -> None:
        super().__init__(f"Skill not found: {skill_id}", code="SKILL_NOT_FOUND")
        self.skill_id = skill_id


class SkillVersionConflictError(SkillError):
    def __init__(self, skill_id: str, version: str) -> None:
        super().__init__(
            f"Version conflict for skill {skill_id}@{version}",
            code="SKILL_VERSION_CONFLICT",
        )


class SkillValidationError(SkillError):
    def __init__(self, message: str, errors: list[dict] | None = None) -> None:
        super().__init__(message, code="SKILL_VALIDATION_ERROR")
        self.errors = errors or []


class SkillLifecycleError(SkillError):
    def __init__(self, skill_id: str, from_status: str, to_status: str) -> None:
        super().__init__(
            f"Invalid lifecycle transition for {skill_id}: {from_status} → {to_status}",
            code="SKILL_LIFECYCLE_ERROR",
        )


class SkillDependencyError(SkillError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="SKILL_DEPENDENCY_ERROR")


# ---------------------------------------------------------------------------
# Execution errors
# ---------------------------------------------------------------------------


class ExecutionError(AgenticError):
    """Base for runtime execution errors."""


class ExecutionTimeoutError(ExecutionError):
    def __init__(self, skill_id: str, timeout_ms: int) -> None:
        super().__init__(
            f"Skill {skill_id} timed out after {timeout_ms}ms",
            code="EXECUTION_TIMEOUT",
        )
        self.skill_id = skill_id
        self.timeout_ms = timeout_ms


class SandboxError(ExecutionError):
    def __init__(self, message: str) -> None:
        super().__init__(message, code="SANDBOX_ERROR")


class CircuitOpenError(ExecutionError):
    def __init__(self, skill_id: str) -> None:
        super().__init__(
            f"Circuit breaker is open for skill {skill_id}",
            code="CIRCUIT_OPEN",
        )
        self.skill_id = skill_id


class ConnectorError(ExecutionError):
    def __init__(self, connector: str, message: str) -> None:
        super().__init__(f"Connector '{connector}' error: {message}", code="CONNECTOR_ERROR")


# ---------------------------------------------------------------------------
# Governance errors
# ---------------------------------------------------------------------------


class GovernanceError(AgenticError):
    """Base for authorization and policy errors."""


class UnauthorizedError(GovernanceError):
    def __init__(self, actor: str, action: str) -> None:
        super().__init__(
            f"Actor '{actor}' is not authorized to perform '{action}'",
            code="UNAUTHORIZED",
        )


class PolicyViolationError(GovernanceError):
    def __init__(self, skill_id: str, reason: str) -> None:
        super().__init__(
            f"Policy violation for skill {skill_id}: {reason}",
            code="POLICY_VIOLATION",
        )
        self.skill_id = skill_id
        self.reason = reason


class ApprovalRequiredError(GovernanceError):
    def __init__(self, skill_id: str, approval_id: str) -> None:
        super().__init__(
            f"Skill {skill_id} requires human approval (approval_id={approval_id})",
            code="APPROVAL_REQUIRED",
        )
        self.skill_id = skill_id
        self.approval_id = approval_id


# ---------------------------------------------------------------------------
# Orchestration errors
# ---------------------------------------------------------------------------


class OrchestrationError(AgenticError):
    """Base for planning and routing errors."""


class PlanningFailedError(OrchestrationError):
    def __init__(self, goal: str, reason: str) -> None:
        super().__init__(f"Failed to plan goal '{goal}': {reason}", code="PLANNING_FAILED")


class RoutingFailedError(OrchestrationError):
    def __init__(self, task: str, reason: str) -> None:
        super().__init__(f"Failed to route task '{task}': {reason}", code="ROUTING_FAILED")
