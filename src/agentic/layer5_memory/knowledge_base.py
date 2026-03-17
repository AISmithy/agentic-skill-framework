"""Structured knowledge base — entity/fact store for agent reasoning."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Fact:
    subject: str
    predicate: str
    obj: Any
    confidence: float = 1.0
    source: str = "unknown"
    created_at: datetime = field(default_factory=datetime.utcnow)


class KnowledgeBase:
    """
    Simple triple-store (subject, predicate, object) for structured facts.

    Agents use this to store and retrieve domain knowledge used during planning.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._facts: list[Fact] = []

    def assert_fact(
        self,
        subject: str,
        predicate: str,
        obj: Any,
        confidence: float = 1.0,
        source: str = "unknown",
    ) -> Fact:
        fact = Fact(
            subject=subject,
            predicate=predicate,
            obj=obj,
            confidence=confidence,
            source=source,
        )
        with self._lock:
            self._facts.append(fact)
        return fact

    def query(
        self,
        subject: str | None = None,
        predicate: str | None = None,
        min_confidence: float = 0.0,
    ) -> list[Fact]:
        with self._lock:
            results = list(self._facts)

        if subject:
            results = [f for f in results if f.subject == subject]
        if predicate:
            results = [f for f in results if f.predicate == predicate]
        if min_confidence > 0:
            results = [f for f in results if f.confidence >= min_confidence]

        return results

    def retract(self, subject: str, predicate: str) -> int:
        """Remove all facts matching subject+predicate. Returns count removed."""
        with self._lock:
            before = len(self._facts)
            self._facts = [
                f for f in self._facts
                if not (f.subject == subject and f.predicate == predicate)
            ]
            return before - len(self._facts)

    def count(self) -> int:
        with self._lock:
            return len(self._facts)
