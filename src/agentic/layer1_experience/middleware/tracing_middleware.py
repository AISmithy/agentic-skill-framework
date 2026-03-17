"""Tracing middleware — injects trace/span IDs into each request."""

from __future__ import annotations

import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class TracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("X-Trace-Id", uuid.uuid4().hex)
        request.state.trace_id = trace_id
        response = await call_next(request)
        response.headers["X-Trace-Id"] = trace_id
        return response
