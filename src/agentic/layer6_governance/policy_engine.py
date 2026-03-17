"""Policy engine — evaluates rules against skill risk and execution context."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from agentic.core.constants import PolicyDecision, RiskLevel
from agentic.layer3_skill_library.models.skill import SkillDefinition
from agentic.layer6_governance.authn import Identity
from agentic.layer7_observability.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PolicyContext:
    """All data available to policy rules during evaluation."""

    identity: Identity
    skill: SkillDefinition
    inputs: dict[str, Any]
    environment: str = "development"
    extra: dict[str, Any] | None = None


@dataclass
class PolicyResult:
    decision: PolicyDecision
    reason: str
    matched_rule: str | None = None


class PolicyRule:
    """A single evaluable policy rule."""

    def __init__(self, name: str, condition: Any, decision: PolicyDecision, reason: str) -> None:
        self.name = name
        self._condition = condition  # callable: (PolicyContext) -> bool
        self.decision = decision
        self.reason = reason

    def matches(self, ctx: PolicyContext) -> bool:
        try:
            return bool(self._condition(ctx))
        except Exception:
            return False


class PolicyEngine:
    """
    Evaluates an ordered list of policy rules against a PolicyContext.

    Rules are evaluated in priority order; first match wins.
    If no rule matches, the default decision is ALLOW.
    """

    def __init__(self) -> None:
        self._rules: list[PolicyRule] = []
        self._load_default_rules()

    def _load_default_rules(self) -> None:
        """Load the built-in governance rules."""
        self._rules = [
            # Retired skills cannot be invoked
            PolicyRule(
                name="deny_retired_skills",
                condition=lambda ctx: ctx.skill.status.value == "retired",
                decision=PolicyDecision.DENY,
                reason="Skill is retired",
            ),
            # Draft/tested/approved skills cannot be invoked in production
            PolicyRule(
                name="deny_unpublished_in_production",
                condition=lambda ctx: (
                    ctx.environment == "production"
                    and ctx.skill.status.value not in ("published",)
                ),
                decision=PolicyDecision.DENY,
                reason="Only published skills may be invoked in production",
            ),
            # High-risk skills require approval unless caller is admin
            PolicyRule(
                name="require_approval_high_risk",
                condition=lambda ctx: (
                    ctx.skill.risk_level == RiskLevel.HIGH
                    and "admin" not in ctx.identity.roles
                    and "*" not in ctx.identity.permissions
                ),
                decision=PolicyDecision.REQUIRE_APPROVAL,
                reason="High-risk skill requires human approval",
            ),
        ]

    def add_rule(self, rule: PolicyRule) -> None:
        """Add a custom policy rule (evaluated after built-ins)."""
        self._rules.append(rule)

    def evaluate(self, ctx: PolicyContext) -> PolicyResult:
        """Evaluate all rules and return the first matching decision."""
        for rule in self._rules:
            if rule.matches(ctx):
                result = PolicyResult(
                    decision=rule.decision,
                    reason=rule.reason,
                    matched_rule=rule.name,
                )
                logger.info(
                    "policy_evaluated",
                    skill_id=ctx.skill.skill_id,
                    actor=ctx.identity.actor,
                    decision=rule.decision.value,
                    matched_rule=rule.name,
                )
                return result

        # Default: allow
        return PolicyResult(
            decision=PolicyDecision.ALLOW,
            reason="No matching deny or approval rule",
            matched_rule=None,
        )
