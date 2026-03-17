"""Auth middleware — extracts and validates JWT from Authorization header."""

from __future__ import annotations

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from agentic.core.exceptions import UnauthorizedError
from agentic.layer6_governance.authn import Identity, verify_token

# Paths that don't require authentication
_PUBLIC_PATHS = {"/", "/health", "/docs", "/openapi.json", "/redoc", "/metrics"}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path in _PUBLIC_PATHS or request.url.path.startswith("/health"):
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid Authorization header"},
            )

        token = auth_header.removeprefix("Bearer ").strip()
        try:
            identity: Identity = verify_token(token)
        except UnauthorizedError as exc:
            return JSONResponse(status_code=401, content={"detail": exc.message})

        request.state.identity = identity
        return await call_next(request)
