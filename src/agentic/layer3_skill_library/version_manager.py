"""Semantic version resolution and history for skills."""

from __future__ import annotations

from agentic.core.exceptions import SkillNotFoundError
from agentic.layer3_skill_library.models.skill import SkillDefinition
from agentic.layer3_skill_library.registry import SkillRegistry


def _parse_version(version: str) -> tuple[int, int, int]:
    major, minor, patch = version.split(".")
    return int(major), int(minor), int(patch)


class VersionManager:
    """Resolves version constraints and manages skill version history."""

    def __init__(self, registry: SkillRegistry) -> None:
        self._registry = registry

    def list_versions(self, skill_name: str) -> list[str]:
        """Return all registered versions of a skill, sorted ascending."""
        skills = [s for s in self._registry.list_all() if s.name == skill_name]
        return sorted([s.version for s in skills], key=_parse_version)

    def resolve_latest(self, skill_name: str) -> SkillDefinition:
        """Return the highest-versioned published skill with the given name."""
        from agentic.core.constants import LifecycleStatus

        candidates = [
            s
            for s in self._registry.list_all()
            if s.name == skill_name and s.status == LifecycleStatus.PUBLISHED
        ]
        if not candidates:
            raise SkillNotFoundError(f"No published version of skill '{skill_name}'")
        return max(candidates, key=lambda s: _parse_version(s.version))

    def resolve_compatible(self, skill_name: str, min_version: str) -> SkillDefinition:
        """
        Return the highest published version >= min_version (same major).

        Follows semver compatibility: major version must match.
        """
        from agentic.core.constants import LifecycleStatus

        min_maj, min_min, min_pat = _parse_version(min_version)
        candidates = [
            s
            for s in self._registry.list_all()
            if s.name == skill_name
            and s.status == LifecycleStatus.PUBLISHED
            and _parse_version(s.version)[0] == min_maj
            and _parse_version(s.version) >= (min_maj, min_min, min_pat)
        ]
        if not candidates:
            raise SkillNotFoundError(
                f"No compatible published version of '{skill_name}' >= {min_version}"
            )
        return max(candidates, key=lambda s: _parse_version(s.version))

    def is_upgrade(self, from_version: str, to_version: str) -> bool:
        return _parse_version(to_version) > _parse_version(from_version)

    def is_breaking_change(self, from_version: str, to_version: str) -> bool:
        """Breaking change = major version bump."""
        return _parse_version(to_version)[0] > _parse_version(from_version)[0]
