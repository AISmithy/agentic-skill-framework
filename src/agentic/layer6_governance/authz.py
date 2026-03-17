"""Authorization — RBAC permission checking."""

from __future__ import annotations

from agentic.core.exceptions import UnauthorizedError
from agentic.layer3_skill_library.models.skill import SkillDefinition
from agentic.layer6_governance.authn import Identity


class AuthorizationEngine:
    """Role-based access control for skill invocations."""

    # Built-in role → permissions mapping
    ROLE_PERMISSIONS: dict[str, set[str]] = {
        "admin": {"*"},
        "developer": {"read:skills", "invoke:skills", "publish:skills"},
        "operator": {"read:skills", "invoke:skills"},
        "viewer": {"read:skills"},
    }

    def check_permission(self, identity: Identity, required_permission: str) -> None:
        """Raise UnauthorizedError if identity does not have required_permission."""
        # Wildcard permission grants everything
        if "*" in identity.permissions:
            return

        # Check direct permissions
        if required_permission in identity.permissions:
            return

        # Check role-based permissions
        for role in identity.roles:
            role_perms = self.ROLE_PERMISSIONS.get(role, set())
            if "*" in role_perms or required_permission in role_perms:
                return

        raise UnauthorizedError(identity.actor, required_permission)

    def can_invoke_skill(self, identity: Identity, skill: SkillDefinition) -> None:
        """
        Check whether identity can invoke a specific skill.

        Validates both general invoke permission and skill-specific permission requirements.
        """
        self.check_permission(identity, "invoke:skills")

        # Check skill-specific required permissions
        for perm in skill.permissions:
            if perm not in identity.permissions and not self._has_via_role(identity, perm):
                raise UnauthorizedError(identity.actor, perm)

    def _has_via_role(self, identity: Identity, permission: str) -> bool:
        if "*" in identity.permissions:
            return True
        for role in identity.roles:
            role_perms = self.ROLE_PERMISSIONS.get(role, set())
            if "*" in role_perms or permission in role_perms:
                return True
        return False
