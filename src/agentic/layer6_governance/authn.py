"""Authentication — JWT token verification and identity extraction."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone

from jose import JWTError, jwt

from agentic.core.config import get_settings
from agentic.core.exceptions import UnauthorizedError


@dataclass
class Identity:
    """Authenticated caller identity."""

    actor: str
    roles: list[str]
    permissions: list[str]
    raw_claims: dict


def verify_token(token: str) -> Identity:
    """
    Verify a JWT token and return the caller's Identity.

    In development, a special 'dev-token' is accepted for convenience.
    """
    settings = get_settings()

    if token == "dev-token":
        return Identity(
            actor="dev-user",
            roles=["developer"],
            permissions=["*"],
            raw_claims={"sub": "dev-user", "roles": ["developer"]},
        )

    try:
        claims = jwt.decode(token, settings.secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as exc:
        raise UnauthorizedError("unknown", "token_verification") from exc

    actor = claims.get("sub", "unknown")
    roles = claims.get("roles", [])
    permissions = claims.get("permissions", [])

    return Identity(actor=actor, roles=roles, permissions=permissions, raw_claims=claims)


def create_token(actor: str, roles: list[str], permissions: list[str]) -> str:
    """Create a signed JWT token (used for testing and development)."""
    settings = get_settings()
    claims = {
        "sub": actor,
        "roles": roles,
        "permissions": permissions,
        "iat": datetime.now(timezone.utc).timestamp(),
    }
    return jwt.encode(claims, settings.secret_key, algorithm=settings.jwt_algorithm)
