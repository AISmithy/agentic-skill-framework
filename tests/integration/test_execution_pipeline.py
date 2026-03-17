"""Integration test — goal → skill execution end-to-end."""

from __future__ import annotations

import pytest

from agentic.core.constants import LifecycleStatus
from agentic.layer3_skill_library.registry import SkillRegistry
from agentic.layer4_runtime.executor import SkillExecutor, SkillInvocation
from agentic.layer4_runtime.resilience.circuit_breaker import CircuitBreakerRegistry
from agentic.layer6_governance.authn import Identity
from skills.summarizer.skill import DocumentSummarizer


@pytest.fixture
def summarizer_skill():
    skill = DocumentSummarizer()
    skill.manifest.status = LifecycleStatus.PUBLISHED
    return skill


@pytest.fixture
def registry_with_summarizer(summarizer_skill):
    registry = SkillRegistry()
    registry.register(summarizer_skill.manifest)
    return registry


@pytest.fixture
def executor(registry_with_summarizer, summarizer_skill):
    return SkillExecutor(
        registry=registry_with_summarizer,
        skill_instances={summarizer_skill.manifest.skill_id: summarizer_skill},
        circuit_registry=CircuitBreakerRegistry(),
        environment="development",
    )


@pytest.fixture
def identity():
    return Identity(
        actor="test-user",
        roles=["admin"],
        permissions=["*"],
        raw_claims={},
    )


@pytest.mark.asyncio
async def test_full_execution_pipeline(executor, identity):
    invocation = SkillInvocation(
        skill_id="doc.summarize.v1",
        inputs={"text": "The quick brown fox jumps over the lazy dog. This is important information. Key points matter."},
        identity=identity,
    )
    result = await executor.execute(invocation)
    assert result.success
    assert result.output is not None
    assert "summary" in result.output
    assert result.duration_ms >= 0


@pytest.mark.asyncio
async def test_execution_with_invalid_inputs(executor, identity):
    invocation = SkillInvocation(
        skill_id="doc.summarize.v1",
        inputs={},  # Missing required 'text' field
        identity=identity,
    )
    result = await executor.execute(invocation)
    assert not result.success
    assert result.error is not None


@pytest.mark.asyncio
async def test_execution_skill_not_found(executor, identity):
    invocation = SkillInvocation(
        skill_id="nonexistent.skill.v1",
        inputs={"text": "hello"},
        identity=identity,
    )
    result = await executor.execute(invocation)
    assert not result.success
