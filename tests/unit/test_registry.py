"""Unit tests for SkillRegistry."""

import pytest

from agentic.core.exceptions import SkillNotFoundError, SkillVersionConflictError
from agentic.layer3_skill_library.registry import SkillRegistry


def test_register_and_lookup(sample_skill, fresh_registry):
    fresh_registry.register(sample_skill)
    found = fresh_registry.lookup_by_id(sample_skill.skill_id)
    assert found.skill_id == sample_skill.skill_id


def test_register_duplicate_raises(sample_skill, fresh_registry):
    fresh_registry.register(sample_skill)
    with pytest.raises(SkillVersionConflictError):
        fresh_registry.register(sample_skill)


def test_overwrite_allowed(sample_skill, fresh_registry):
    fresh_registry.register(sample_skill)
    fresh_registry.register(sample_skill, overwrite=True)
    assert len(fresh_registry) == 1


def test_lookup_not_found(fresh_registry):
    with pytest.raises(SkillNotFoundError):
        fresh_registry.lookup_by_id("nonexistent.v1")


def test_list_published(sample_skill, fresh_registry):
    fresh_registry.register(sample_skill)
    published = fresh_registry.list_published()
    assert len(published) == 1
    assert published[0].skill_id == sample_skill.skill_id


def test_search_by_tag(sample_skill, fresh_registry):
    fresh_registry.register(sample_skill)
    results = fresh_registry.search(tags=["test"])
    assert len(results) == 1


def test_search_by_query(sample_skill, fresh_registry):
    fresh_registry.register(sample_skill)
    results = fresh_registry.search(query="test skill")
    assert len(results) == 1


def test_unregister(sample_skill, fresh_registry):
    fresh_registry.register(sample_skill)
    fresh_registry.unregister(sample_skill.skill_id)
    assert len(fresh_registry) == 0
