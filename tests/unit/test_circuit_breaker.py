"""Unit tests for CircuitBreaker."""

import pytest

from agentic.core.constants import CircuitState
from agentic.core.exceptions import CircuitOpenError
from agentic.layer4_runtime.resilience.circuit_breaker import CircuitBreaker


def test_initial_state_closed():
    cb = CircuitBreaker(skill_id="test.v1", failure_threshold=3)
    assert cb.state == CircuitState.CLOSED


def test_opens_after_threshold():
    cb = CircuitBreaker(skill_id="test.v1", failure_threshold=3)
    for _ in range(3):
        cb.record_failure()
    assert cb.state == CircuitState.OPEN


def test_check_raises_when_open():
    cb = CircuitBreaker(skill_id="test.v1", failure_threshold=1)
    cb.record_failure()
    with pytest.raises(CircuitOpenError):
        cb.check()


def test_success_resets_count():
    cb = CircuitBreaker(skill_id="test.v1", failure_threshold=3)
    cb.record_failure()
    cb.record_failure()
    cb.record_success()
    assert cb.state == CircuitState.CLOSED
    assert cb._failure_count == 0


def test_half_open_success_closes():
    cb = CircuitBreaker(skill_id="test.v1", failure_threshold=1, recovery_timeout_s=0)
    cb.record_failure()
    # Force to half-open by directly setting state
    cb._state = CircuitState.HALF_OPEN
    cb.record_success()
    assert cb.state == CircuitState.CLOSED
