"""OpenTelemetry-compatible span context using contextvars."""

from __future__ import annotations

import time
import uuid
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Generator

from agentic.layer7_observability.logger import get_logger

logger = get_logger(__name__)

# Active span stored in context
_current_span: ContextVar[Span | None] = ContextVar("current_span", default=None)


@dataclass
class Span:
    name: str
    trace_id: str = field(default_factory=lambda: uuid.uuid4().hex)
    span_id: str = field(default_factory=lambda: uuid.uuid4().hex[:16])
    parent_span_id: str | None = None
    start_time: float = field(default_factory=time.monotonic)
    end_time: float | None = None
    attributes: dict[str, Any] = field(default_factory=dict)
    status: str = "ok"

    def set_attribute(self, key: str, value: Any) -> None:
        self.attributes[key] = value

    def set_error(self, error: Exception) -> None:
        self.status = "error"
        self.attributes["error.type"] = type(error).__name__
        self.attributes["error.message"] = str(error)

    def duration_ms(self) -> float:
        end = self.end_time or time.monotonic()
        return (end - self.start_time) * 1000

    def to_dict(self) -> dict[str, Any]:
        return {
            "trace_id": self.trace_id,
            "span_id": self.span_id,
            "parent_span_id": self.parent_span_id,
            "name": self.name,
            "duration_ms": round(self.duration_ms(), 2),
            "status": self.status,
            "attributes": self.attributes,
        }


@contextmanager
def start_span(name: str, **attributes: Any) -> Generator[Span, None, None]:
    """Context manager that creates a child span under the current active span."""
    parent = _current_span.get()
    span = Span(
        name=name,
        trace_id=parent.trace_id if parent else uuid.uuid4().hex,
        parent_span_id=parent.span_id if parent else None,
    )
    span.attributes.update(attributes)
    token = _current_span.set(span)
    try:
        yield span
    except Exception as exc:
        span.set_error(exc)
        raise
    finally:
        span.end_time = time.monotonic()
        _current_span.reset(token)
        logger.debug(
            "span_finished",
            **span.to_dict(),
        )


def get_current_trace_id() -> str | None:
    span = _current_span.get()
    return span.trace_id if span else None


def get_current_span() -> Span | None:
    return _current_span.get()
