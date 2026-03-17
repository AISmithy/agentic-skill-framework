"""Async timeout context manager for skill executions."""

from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from agentic.core.exceptions import ExecutionTimeoutError


@asynccontextmanager
async def execution_timeout(
    skill_id: str, timeout_ms: int
) -> AsyncGenerator[None, None]:
    """
    Async context manager that enforces a maximum execution duration.

    Raises ExecutionTimeoutError if the block does not complete in time.
    """
    timeout_s = timeout_ms / 1000.0
    try:
        async with asyncio.timeout(timeout_s):
            yield
    except TimeoutError:
        raise ExecutionTimeoutError(skill_id, timeout_ms)
