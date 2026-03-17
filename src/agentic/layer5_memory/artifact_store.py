"""Content-addressed artifact store for skill outputs and generated assets."""

from __future__ import annotations

import hashlib
import json
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Artifact:
    content_hash: str
    content_type: str
    data: Any
    skill_id: str
    session_id: str | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    tags: list[str] = field(default_factory=list)


class ArtifactStore:
    """In-memory content-addressed store for reusable execution artifacts."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._artifacts: dict[str, Artifact] = {}

    def store(
        self,
        data: Any,
        skill_id: str,
        content_type: str = "application/json",
        session_id: str | None = None,
        tags: list[str] | None = None,
    ) -> Artifact:
        serialized = json.dumps(data, sort_keys=True, default=str).encode()
        content_hash = hashlib.sha256(serialized).hexdigest()[:16]

        artifact = Artifact(
            content_hash=content_hash,
            content_type=content_type,
            data=data,
            skill_id=skill_id,
            session_id=session_id,
            tags=tags or [],
        )
        with self._lock:
            self._artifacts[content_hash] = artifact
        return artifact

    def retrieve(self, content_hash: str) -> Artifact | None:
        with self._lock:
            return self._artifacts.get(content_hash)

    def list_by_skill(self, skill_id: str) -> list[Artifact]:
        with self._lock:
            return [a for a in self._artifacts.values() if a.skill_id == skill_id]

    def list_by_session(self, session_id: str) -> list[Artifact]:
        with self._lock:
            return [a for a in self._artifacts.values() if a.session_id == session_id]
