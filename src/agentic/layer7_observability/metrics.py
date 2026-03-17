"""In-process metrics registry — counters, gauges, histograms."""

from __future__ import annotations

import threading
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Counter:
    name: str
    _value: float = 0.0
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def inc(self, amount: float = 1.0, labels: dict[str, str] | None = None) -> None:
        with self._lock:
            self._value += amount

    @property
    def value(self) -> float:
        with self._lock:
            return self._value


@dataclass
class Gauge:
    name: str
    _value: float = 0.0
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def set(self, value: float) -> None:
        with self._lock:
            self._value = value

    def inc(self, amount: float = 1.0) -> None:
        with self._lock:
            self._value += amount

    def dec(self, amount: float = 1.0) -> None:
        with self._lock:
            self._value -= amount

    @property
    def value(self) -> float:
        with self._lock:
            return self._value


@dataclass
class Histogram:
    name: str
    _observations: list[float] = field(default_factory=list)
    _lock: threading.Lock = field(default_factory=threading.Lock)

    def observe(self, value: float) -> None:
        with self._lock:
            self._observations.append(value)

    def percentile(self, p: float) -> float:
        with self._lock:
            if not self._observations:
                return 0.0
            sorted_obs = sorted(self._observations)
            idx = int(len(sorted_obs) * p / 100)
            return sorted_obs[min(idx, len(sorted_obs) - 1)]

    def count(self) -> int:
        with self._lock:
            return len(self._observations)

    def sum(self) -> float:
        with self._lock:
            return sum(self._observations)


class MetricsRegistry:
    """Global registry of all framework metrics."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._counters: dict[str, Counter] = {}
        self._gauges: dict[str, Gauge] = {}
        self._histograms: dict[str, Histogram] = {}

    def counter(self, name: str) -> Counter:
        with self._lock:
            if name not in self._counters:
                self._counters[name] = Counter(name=name)
            return self._counters[name]

    def gauge(self, name: str) -> Gauge:
        with self._lock:
            if name not in self._gauges:
                self._gauges[name] = Gauge(name=name)
            return self._gauges[name]

    def histogram(self, name: str) -> Histogram:
        with self._lock:
            if name not in self._histograms:
                self._histograms[name] = Histogram(name=name)
            return self._histograms[name]

    def to_prometheus_text(self) -> str:
        """Export metrics in Prometheus text format."""
        lines: list[str] = []
        for name, c in self._counters.items():
            lines.append(f"# TYPE {name} counter")
            lines.append(f"{name} {c.value}")
        for name, g in self._gauges.items():
            lines.append(f"# TYPE {name} gauge")
            lines.append(f"{name} {g.value}")
        for name, h in self._histograms.items():
            lines.append(f"# TYPE {name} histogram")
            lines.append(f"{name}_count {h.count()}")
            lines.append(f"{name}_sum {h.sum()}")
        return "\n".join(lines)

    def snapshot(self) -> dict[str, Any]:
        return {
            "counters": {n: c.value for n, c in self._counters.items()},
            "gauges": {n: g.value for n, g in self._gauges.items()},
            "histograms": {
                n: {"count": h.count(), "sum": h.sum(), "p99": h.percentile(99)}
                for n, h in self._histograms.items()
            },
        }


# Module-level singleton
_metrics = MetricsRegistry()


def get_metrics() -> MetricsRegistry:
    return _metrics


# Pre-defined framework metrics
SKILL_EXECUTIONS_TOTAL = "skill_executions_total"
SKILL_EXECUTION_DURATION_MS = "skill_execution_duration_ms"
CIRCUIT_BREAKER_STATE = "circuit_breaker_state"
ACTIVE_SESSIONS = "active_sessions"
POLICY_DECISIONS_TOTAL = "policy_decisions_total"
