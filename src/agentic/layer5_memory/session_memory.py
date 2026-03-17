"""In-memory session store scoped per agent session."""

from __future__ import annotations

import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from agentic.layer7_observability.metrics import ACTIVE_SESSIONS, get_metrics


@dataclass
class SessionMemory:
    """Scoped key-value store for a single agent session."""

    session_id: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    _data: dict[str, Any] = field(default_factory=dict, repr=False)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def delete(self, key: str) -> None:
        self._data.pop(key, None)

    def all(self) -> dict[str, Any]:
        return dict(self._data)

    def clear(self) -> None:
        self._data.clear()


class SessionStore:
    """Thread-safe registry of active sessions."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._sessions: dict[str, SessionMemory] = {}

    def create(self, session_id: str) -> SessionMemory:
        with self._lock:
            session = SessionMemory(session_id=session_id)
            self._sessions[session_id] = session
            get_metrics().gauge(ACTIVE_SESSIONS).set(len(self._sessions))
            return session

    def get(self, session_id: str) -> SessionMemory | None:
        with self._lock:
            return self._sessions.get(session_id)

    def get_or_create(self, session_id: str) -> SessionMemory:
        with self._lock:
            if session_id not in self._sessions:
                self._sessions[session_id] = SessionMemory(session_id=session_id)
                get_metrics().gauge(ACTIVE_SESSIONS).set(len(self._sessions))
            return self._sessions[session_id]

    def destroy(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)
            get_metrics().gauge(ACTIVE_SESSIONS).set(len(self._sessions))

    def active_count(self) -> int:
        with self._lock:
            return len(self._sessions)
