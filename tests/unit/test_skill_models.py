"""Unit tests for SkillDefinition model."""

import pytest
from pydantic import ValidationError

from agentic.core.constants import LifecycleStatus, RiskLevel
from agentic.layer3_skill_library.models.skill import SkillDefinition


def test_skill_definition_defaults():
    skill = SkillDefinition(
        skill_id="test.v1",
        name="Test",
        description="desc",
        category="cat",
        owner="owner",
        version="1.0.0",
    )
    assert skill.status == LifecycleStatus.DRAFT
    assert skill.risk_level == RiskLevel.LOW
    assert skill.tags == []


def test_skill_id_no_spaces():
    with pytest.raises(ValidationError):
        SkillDefinition(
            skill_id="bad id",
            name="Bad",
            description="d",
            category="c",
            owner="o",
            version="1.0.0",
        )


def test_version_semver():
    with pytest.raises(ValidationError):
        SkillDefinition(
            skill_id="test.v1",
            name="T",
            description="d",
            category="c",
            owner="o",
            version="1.0",  # Invalid: only two parts
        )


def test_is_invocable():
    skill = SkillDefinition(
        skill_id="test.v1",
        name="T",
        description="d",
        category="c",
        owner="o",
        version="1.0.0",
        status=LifecycleStatus.DRAFT,
    )
    assert not skill.is_invocable()
    skill.status = LifecycleStatus.PUBLISHED
    assert skill.is_invocable()


def test_requires_approval():
    skill = SkillDefinition(
        skill_id="test.v1",
        name="T",
        description="d",
        category="c",
        owner="o",
        version="1.0.0",
        risk_level=RiskLevel.HIGH,
    )
    assert skill.requires_approval()
