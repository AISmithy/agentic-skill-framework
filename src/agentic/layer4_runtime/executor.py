"""Skill Executor — central dispatch combining validation, governance, sandbox, and resilience."""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from agentic.core.constants import PolicyDecision
from agentic.core.exceptions import ApprovalRequiredError, PolicyViolationError
from agentic.layer3_skill_library.models.skill import SkillDefinition
from agentic.layer3_skill_library.registry import SkillRegistry
from agentic.layer4_runtime.resilience.circuit_breaker import CircuitBreakerRegistry
from agentic.layer4_runtime.resilience.timeout import execution_timeout
from agentic.layer4_runtime.sandbox import Sandbox
from agentic.layer4_runtime.schema_validator import SchemaValidator
from agentic.layer6_governance.approval_workflow import ApprovalWorkflow
from agentic.layer6_governance.audit_log import AuditLog
from agentic.layer6_governance.authn import Identity
from agentic.layer6_governance.authz import AuthorizationEngine
from agentic.layer6_governance.policy_engine import PolicyContext, PolicyEngine
from agentic.layer6_governance.safety_filters import SafetyFilter
from agentic.layer7_observability.evaluator import EvaluationResult, ExecutionEvaluator
from agentic.layer7_observability.logger import get_logger
from agentic.layer7_observability.metrics import (
    SKILL_EXECUTION_DURATION_MS,
    SKILL_EXECUTIONS_TOTAL,
    get_metrics,
)
from agentic.layer7_observability.tracer import start_span

logger = get_logger(__name__)


@dataclass
class SkillInvocation:
    """Everything needed to execute a skill."""

    skill_id: str
    inputs: dict[str, Any]
    identity: Identity
    execution_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    environment: str = "development"


@dataclass
class SkillResult:
    execution_id: str
    skill_id: str
    success: bool
    output: dict[str, Any] | None
    error: str | None = None
    duration_ms: float = 0.0
    retry_count: int = 0


class SkillExecutor:
    """
    Orchestrates the full execution lifecycle of a single skill invocation.

    Call sequence:
      1. Resolve skill definition from registry
      2. Authorization check (RBAC)
      3. Input safety filter
      4. Input schema validation
      5. Policy engine evaluation (ALLOW / DENY / REQUIRE_APPROVAL)
      6. Circuit breaker check
      7. Sandbox execution with timeout
      8. Output schema validation
      9. Metrics, audit, and evaluation recording
    """

    def __init__(
        self,
        registry: SkillRegistry,
        skill_instances: dict[str, Any],
        *,
        policy_engine: PolicyEngine | None = None,
        authz: AuthorizationEngine | None = None,
        safety_filter: SafetyFilter | None = None,
        schema_validator: SchemaValidator | None = None,
        approval_workflow: ApprovalWorkflow | None = None,
        audit_log: AuditLog | None = None,
        evaluator: ExecutionEvaluator | None = None,
        circuit_registry: CircuitBreakerRegistry | None = None,
        sandbox: Sandbox | None = None,
        environment: str = "development",
    ) -> None:
        self._registry = registry
        self._skill_instances = skill_instances
        self._policy_engine = policy_engine or PolicyEngine()
        self._authz = authz or AuthorizationEngine()
        self._safety = safety_filter or SafetyFilter()
        self._validator = schema_validator or SchemaValidator()
        self._approval = approval_workflow or ApprovalWorkflow()
        self._audit = audit_log
        self._evaluator = evaluator or ExecutionEvaluator()
        self._circuit = circuit_registry or CircuitBreakerRegistry()
        self._sandbox = sandbox or Sandbox()
        self._environment = environment

    async def execute(self, invocation: SkillInvocation) -> SkillResult:
        start = time.monotonic()

        with start_span("skill.execute", skill_id=invocation.skill_id) as span:
            try:
                result = await self._do_execute(invocation, span)
            except Exception as exc:
                span.set_error(exc)
                duration_ms = (time.monotonic() - start) * 1000
                self._record_metrics(invocation.skill_id, success=False, duration_ms=duration_ms)
                if self._audit:
                    await self._audit.record(
                        actor=invocation.identity.actor,
                        event_type=AuditLog.EVENT_INVOKED,
                        outcome="error",
                        skill_id=invocation.skill_id,
                        duration_ms=duration_ms,
                        details={"error": str(exc)},
                    )
                return SkillResult(
                    execution_id=invocation.execution_id,
                    skill_id=invocation.skill_id,
                    success=False,
                    output=None,
                    error=str(exc),
                    duration_ms=duration_ms,
                )

        return result

    async def _do_execute(self, inv: SkillInvocation, span: Any) -> SkillResult:
        start = time.monotonic()

        # 1. Resolve skill
        skill = self._registry.lookup_by_id(inv.skill_id)
        span.set_attribute("skill.version", skill.version)
        span.set_attribute("skill.risk_level", skill.risk_level.value)

        # 2. Authorization
        self._authz.can_invoke_skill(inv.identity, skill)

        # 3. Safety filter on inputs
        self._safety.check_input(inv.skill_id, inv.inputs)

        # 4. Input schema validation
        self._validator.validate_input(skill, inv.inputs)

        # 5. Policy evaluation
        ctx = PolicyContext(
            identity=inv.identity,
            skill=skill,
            inputs=inv.inputs,
            environment=self._environment,
        )
        policy_result = self._policy_engine.evaluate(ctx)
        span.set_attribute("policy.decision", policy_result.decision.value)

        if policy_result.decision == PolicyDecision.DENY:
            raise PolicyViolationError(inv.skill_id, policy_result.reason)

        if policy_result.decision == PolicyDecision.REQUIRE_APPROVAL:
            approval = self._approval.request_approval(
                inv.skill_id, inv.identity.actor, inv.inputs
            )
            raise ApprovalRequiredError(inv.skill_id, approval.approval_id)

        # 6. Circuit breaker
        breaker = self._circuit.get(inv.skill_id)
        breaker.check()

        # 7. Sandbox execution with timeout
        instance = self._skill_instances.get(inv.skill_id)
        if not instance:
            raise ValueError(f"No executable instance registered for skill '{inv.skill_id}'")

        timeout_ms = skill.sla_targets.timeout_ms
        try:
            async with execution_timeout(inv.skill_id, timeout_ms):
                output = await self._sandbox.run(instance, inv.inputs, inv.skill_id)
            breaker.record_success()
        except Exception:
            breaker.record_failure()
            raise

        # 8. Output validation and safety
        self._validator.validate_output(skill, output)
        self._safety.check_output(inv.skill_id, output)

        duration_ms = (time.monotonic() - start) * 1000

        # 9. Record metrics and audit
        self._record_metrics(inv.skill_id, success=True, duration_ms=duration_ms)
        if self._audit:
            await self._audit.record(
                actor=inv.identity.actor,
                event_type=AuditLog.EVENT_INVOKED,
                outcome="success",
                skill_id=inv.skill_id,
                duration_ms=duration_ms,
                policy_decision=policy_result.decision.value,
            )

        self._evaluator.record(
            EvaluationResult(
                skill_id=inv.skill_id,
                execution_id=inv.execution_id,
                success=True,
                duration_ms=duration_ms,
                schema_valid=True,
                policy_outcome=policy_result.decision.value,
            )
        )

        logger.info(
            "skill_executed",
            skill_id=inv.skill_id,
            execution_id=inv.execution_id,
            actor=inv.identity.actor,
            duration_ms=round(duration_ms, 2),
        )

        return SkillResult(
            execution_id=inv.execution_id,
            skill_id=inv.skill_id,
            success=True,
            output=output,
            duration_ms=duration_ms,
        )

    def _record_metrics(self, skill_id: str, success: bool, duration_ms: float) -> None:
        m = get_metrics()
        m.counter(SKILL_EXECUTIONS_TOTAL).inc()
        m.histogram(SKILL_EXECUTION_DURATION_MS).observe(duration_ms)
