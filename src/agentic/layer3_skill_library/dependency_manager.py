"""Dependency graph resolution and cycle detection for skills."""

from __future__ import annotations

from collections import defaultdict, deque

from agentic.core.exceptions import SkillDependencyError, SkillNotFoundError
from agentic.layer3_skill_library.models.skill import SkillDefinition
from agentic.layer3_skill_library.registry import SkillRegistry


class DependencyManager:
    """
    Builds and validates the skill dependency DAG.

    Detects cycles at registration time and resolves ordered load lists
    for execution (topological sort).
    """

    def __init__(self, registry: SkillRegistry) -> None:
        self._registry = registry

    def validate(self, skill: SkillDefinition) -> None:
        """
        Validate that all declared dependencies exist and are published.

        Raises SkillDependencyError or SkillNotFoundError on failure.
        """
        from agentic.core.constants import LifecycleStatus

        for dep_id in skill.dependencies:
            try:
                dep = self._registry.lookup_by_id(dep_id)
            except SkillNotFoundError:
                raise SkillDependencyError(
                    f"Skill '{skill.skill_id}' depends on '{dep_id}' which is not registered"
                )
            if dep.status != LifecycleStatus.PUBLISHED:
                raise SkillDependencyError(
                    f"Skill '{skill.skill_id}' depends on '{dep_id}' "
                    f"which is not published (status={dep.status.value})"
                )

        # Cycle detection on current registry + this new skill
        self._detect_cycle(skill)

    def _detect_cycle(self, new_skill: SkillDefinition) -> None:
        """DFS cycle detection including the new skill being registered."""
        # Build adjacency from registry + new skill
        graph: dict[str, list[str]] = defaultdict(list)
        for s in self._registry.list_all():
            graph[s.skill_id] = list(s.dependencies)
        graph[new_skill.skill_id] = list(new_skill.dependencies)

        visited: set[str] = set()
        in_stack: set[str] = set()

        def dfs(node: str) -> None:
            visited.add(node)
            in_stack.add(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    dfs(neighbor)
                elif neighbor in in_stack:
                    raise SkillDependencyError(
                        f"Circular dependency detected: '{node}' → '{neighbor}'"
                    )
            in_stack.discard(node)

        for node in list(graph.keys()):
            if node not in visited:
                dfs(node)

    def resolve_order(self, skill_id: str) -> list[str]:
        """
        Return a topologically ordered list of skill_ids that must be
        available before executing skill_id (dependencies first).
        """
        graph: dict[str, list[str]] = {}
        for s in self._registry.list_all():
            graph[s.skill_id] = list(s.dependencies)

        order: list[str] = []
        visited: set[str] = set()

        def visit(node: str) -> None:
            if node in visited:
                return
            visited.add(node)
            for dep in graph.get(node, []):
                visit(dep)
            order.append(node)

        visit(skill_id)
        return order  # skill_id is last; its dependencies come first

    def get_dependents(self, skill_id: str) -> list[str]:
        """Return all skills that directly depend on skill_id."""
        return [
            s.skill_id
            for s in self._registry.list_all()
            if skill_id in s.dependencies
        ]
