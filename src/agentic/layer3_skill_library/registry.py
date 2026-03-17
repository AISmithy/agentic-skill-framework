"""In-process skill registry — the runtime source of truth for available skills."""

from __future__ import annotations

import threading
from typing import Iterator

from agentic.core.exceptions import SkillNotFoundError, SkillVersionConflictError
from agentic.layer3_skill_library.models.skill import SkillDefinition


class SkillRegistry:
    """
    Thread-safe in-memory registry of skill definitions.

    Backed by the metadata_catalog at startup; serves low-latency lookups
    at runtime without hitting the database on every invocation.
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._by_id: dict[str, SkillDefinition] = {}
        # (name, version) → skill_id
        self._by_name_version: dict[tuple[str, str], str] = {}
        # name → latest published skill_id
        self._latest_published: dict[str, str] = {}

    def register(self, skill: SkillDefinition, *, overwrite: bool = False) -> None:
        """Register a skill definition. Raises SkillVersionConflictError if duplicate."""
        with self._lock:
            if skill.skill_id in self._by_id and not overwrite:
                raise SkillVersionConflictError(skill.skill_id, skill.version)
            self._by_id[skill.skill_id] = skill
            self._by_name_version[(skill.name, skill.version)] = skill.skill_id

    def unregister(self, skill_id: str) -> None:
        """Remove a skill from the in-memory registry (does not affect DB)."""
        with self._lock:
            skill = self._by_id.pop(skill_id, None)
            if skill:
                self._by_name_version.pop((skill.name, skill.version), None)
                if self._latest_published.get(skill.name) == skill_id:
                    del self._latest_published[skill.name]

    def lookup_by_id(self, skill_id: str) -> SkillDefinition:
        """Return skill by ID or raise SkillNotFoundError."""
        with self._lock:
            try:
                return self._by_id[skill_id]
            except KeyError:
                raise SkillNotFoundError(skill_id)

    def lookup_by_name_version(self, name: str, version: str) -> SkillDefinition:
        """Return skill by (name, version) tuple."""
        with self._lock:
            skill_id = self._by_name_version.get((name, version))
            if not skill_id:
                raise SkillNotFoundError(f"{name}@{version}")
            return self._by_id[skill_id]

    def list_all(self) -> list[SkillDefinition]:
        """Return all registered skills."""
        with self._lock:
            return list(self._by_id.values())

    def list_by_category(self, category: str) -> list[SkillDefinition]:
        with self._lock:
            return [s for s in self._by_id.values() if s.category == category]

    def list_by_tag(self, tag: str) -> list[SkillDefinition]:
        with self._lock:
            return [s for s in self._by_id.values() if tag in s.tags]

    def list_published(self) -> list[SkillDefinition]:
        from agentic.core.constants import LifecycleStatus

        with self._lock:
            return [s for s in self._by_id.values() if s.status == LifecycleStatus.PUBLISHED]

    def search(
        self,
        *,
        category: str | None = None,
        tags: list[str] | None = None,
        published_only: bool = True,
        query: str | None = None,
    ) -> list[SkillDefinition]:
        """Multi-criteria skill search."""
        from agentic.core.constants import LifecycleStatus

        with self._lock:
            results: Iterator[SkillDefinition] = iter(self._by_id.values())

        candidates = list(results)
        if published_only:
            candidates = [s for s in candidates if s.status == LifecycleStatus.PUBLISHED]
        if category:
            candidates = [s for s in candidates if s.category == category]
        if tags:
            candidates = [s for s in candidates if any(t in s.tags for t in tags)]
        if query:
            q = query.lower()
            candidates = [
                s
                for s in candidates
                if q in s.name.lower()
                or q in s.description.lower()
                or any(q in t.lower() for t in s.tags)
            ]
        return candidates

    def __len__(self) -> int:
        with self._lock:
            return len(self._by_id)


# Module-level singleton
_registry = SkillRegistry()


def get_registry() -> SkillRegistry:
    """Return the global skill registry singleton."""
    return _registry
