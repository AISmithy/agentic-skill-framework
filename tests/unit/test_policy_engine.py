"""Unit tests for PolicyEngine."""

from agentic.core.constants import LifecycleStatus, PolicyDecision, RiskLevel
from agentic.layer6_governance.policy_engine import PolicyContext, PolicyEngine


def test_allow_low_risk_published(sample_skill, admin_identity):
    engine = PolicyEngine()
    ctx = PolicyContext(
        identity=admin_identity,
        skill=sample_skill,
        inputs={},
        environment="production",
    )
    result = engine.evaluate(ctx)
    assert result.decision == PolicyDecision.ALLOW


def test_deny_retired_skill(sample_skill, admin_identity):
    sample_skill.status = LifecycleStatus.RETIRED
    engine = PolicyEngine()
    ctx = PolicyContext(identity=admin_identity, skill=sample_skill, inputs={})
    result = engine.evaluate(ctx)
    assert result.decision == PolicyDecision.DENY


def test_deny_unpublished_in_production(sample_skill, admin_identity):
    sample_skill.status = LifecycleStatus.DRAFT
    engine = PolicyEngine()
    ctx = PolicyContext(
        identity=admin_identity,
        skill=sample_skill,
        inputs={},
        environment="production",
    )
    result = engine.evaluate(ctx)
    assert result.decision == PolicyDecision.DENY


def test_require_approval_high_risk_non_admin(sample_skill, dev_identity):
    sample_skill.risk_level = RiskLevel.HIGH
    engine = PolicyEngine()
    ctx = PolicyContext(identity=dev_identity, skill=sample_skill, inputs={})
    result = engine.evaluate(ctx)
    assert result.decision == PolicyDecision.REQUIRE_APPROVAL


def test_allow_high_risk_admin(sample_skill, admin_identity):
    sample_skill.risk_level = RiskLevel.HIGH
    engine = PolicyEngine()
    ctx = PolicyContext(identity=admin_identity, skill=sample_skill, inputs={})
    result = engine.evaluate(ctx)
    assert result.decision == PolicyDecision.ALLOW
