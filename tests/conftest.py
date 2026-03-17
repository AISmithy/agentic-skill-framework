"""Shared pytest fixtures."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

# Ensure src/ and project root are importable in tests
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from agentic.core.constants import LifecycleStatus, RiskLevel
from agentic.layer3_skill_library.models.skill import SkillDefinition, SLATargets
from agentic.layer3_skill_library.registry import SkillRegistry
from agentic.layer6_governance.authn import Identity


@pytest.fixture
def sample_skill() -> SkillDefinition:
    return SkillDefinition(
        skill_id="test.skill.v1",
        name="Test Skill",
        description="A skill used in tests",
        category="testing",
        owner="test-team",
        version="1.0.0",
        input_schema={
            "type": "object",
            "properties": {"text": {"type": "string"}},
            "required": ["text"],
        },
        output_schema={
            "type": "object",
            "properties": {"result": {"type": "string"}},
        },
        permissions=[],
        risk_level=RiskLevel.LOW,
        tags=["test"],
        status=LifecycleStatus.PUBLISHED,
        sla_targets=SLATargets(timeout_ms=5000),
    )


@pytest.fixture
def published_skill(sample_skill: SkillDefinition) -> SkillDefinition:
    sample_skill.status = LifecycleStatus.PUBLISHED
    return sample_skill


@pytest.fixture
def admin_identity() -> Identity:
    return Identity(
        actor="admin-user",
        roles=["admin"],
        permissions=["*"],
        raw_claims={"sub": "admin-user"},
    )


@pytest.fixture
def dev_identity() -> Identity:
    return Identity(
        actor="dev-user",
        roles=["developer"],
        permissions=[],
        raw_claims={"sub": "dev-user"},
    )


@pytest.fixture
def fresh_registry() -> SkillRegistry:
    return SkillRegistry()
