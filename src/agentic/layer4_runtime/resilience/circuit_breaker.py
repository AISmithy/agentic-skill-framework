"""Per-skill circuit breaker — Closed / Open / Half-Open state machine."""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field

from agentic.core.constants import CircuitState
from agentic.core.exceptions import CircuitOpenError
from agentic.layer7_observability.logger import get_logger
from agentic.layer7_observability.metrics import CIRCUIT_BREAKER_STATE, get_metrics

logger = get_logger(__name__)


@dataclass
class CircuitBreaker:
    """
    Thread-safe circuit breaker for a single skill.

    States:
      CLOSED   — normal operation; failures are counted.
      OPEN     — all calls are rejected immediately.
      HALF_OPEN — one probe call allowed; success → CLOSED, failure → OPEN.
    """

    skill_id: str
    failure_threshold: int = 5
    recovery_timeout_s: int = 60

    _state: CircuitState = field(default=CircuitState.CLOSED, init=False)
    _failure_count: int = field(default=0, init=False)
    _last_failure_time: float = field(default=0.0, init=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False)

    def check(self) -> None:
        """Raise CircuitOpenError if the circuit is open."""
        with self._lock:
            if self._state == CircuitState.CLOSED:
                return

            if self._state == CircuitState.OPEN:
                if time.monotonic() - self._last_failure_time >= self.recovery_timeout_s:
                    self._transition(CircuitState.HALF_OPEN)
                    return
                raise CircuitOpenError(self.skill_id)

            # HALF_OPEN — allow the probe through

    def record_success(self) -> None:
        with self._lock:
            if self._state == CircuitState.HALF_OPEN:
                self._transition(CircuitState.CLOSED)
            self._failure_count = 0

    def record_failure(self) -> None:
        with self._lock:
            self._failure_count += 1
            self._last_failure_time = time.monotonic()
            if self._state == CircuitState.HALF_OPEN:
                self._transition(CircuitState.OPEN)
            elif self._failure_count >= self.failure_threshold:
                self._transition(CircuitState.OPEN)

    def _transition(self, new_state: CircuitState) -> None:
        old_state = self._state
        self._state = new_state
        if new_state == CircuitState.CLOSED:
            self._failure_count = 0
        get_metrics().gauge(f"{CIRCUIT_BREAKER_STATE}_{self.skill_id}").set(
            0 if new_state == CircuitState.CLOSED else 1
        )
        logger.info(
            "circuit_breaker_transition",
            skill_id=self.skill_id,
            from_state=old_state.value,
            to_state=new_state.value,
        )

    @property
    def state(self) -> CircuitState:
        with self._lock:
            return self._state


class CircuitBreakerRegistry:
    """Registry of per-skill circuit breakers."""

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout_s: int = 60,
    ) -> None:
        self._lock = threading.Lock()
        self._breakers: dict[str, CircuitBreaker] = {}
        self._failure_threshold = failure_threshold
        self._recovery_timeout_s = recovery_timeout_s

    def get(self, skill_id: str) -> CircuitBreaker:
        with self._lock:
            if skill_id not in self._breakers:
                self._breakers[skill_id] = CircuitBreaker(
                    skill_id=skill_id,
                    failure_threshold=self._failure_threshold,
                    recovery_timeout_s=self._recovery_timeout_s,
                )
            return self._breakers[skill_id]

    def snapshot(self) -> dict[str, str]:
        with self._lock:
            return {sid: cb.state.value for sid, cb in self._breakers.items()}
