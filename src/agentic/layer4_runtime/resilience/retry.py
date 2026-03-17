"""Exponential backoff retry decorator for async skill executions."""

from __future__ import annotations

import asyncio
import functools
import logging
from typing import Any, Callable, Type

from agentic.layer7_observability.logger import get_logger

logger = get_logger(__name__)


def async_retry(
    max_attempts: int = 3,
    base_delay_s: float = 0.5,
    max_delay_s: float = 30.0,
    backoff_factor: float = 2.0,
    retryable_exceptions: tuple[Type[Exception], ...] = (Exception,),
    non_retryable_exceptions: tuple[Type[Exception], ...] = (),
) -> Callable:
    """
    Decorator that retries an async function with exponential backoff.

    Args:
        max_attempts: Maximum number of total attempts (including first).
        base_delay_s: Initial delay between retries in seconds.
        max_delay_s: Maximum delay cap.
        backoff_factor: Multiplier applied to delay on each retry.
        retryable_exceptions: Only retry on these exception types.
        non_retryable_exceptions: Never retry on these (overrides retryable).
    """

    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = base_delay_s
            last_exc: Exception | None = None

            for attempt in range(1, max_attempts + 1):
                try:
                    return await fn(*args, **kwargs)
                except non_retryable_exceptions as exc:
                    raise
                except retryable_exceptions as exc:
                    last_exc = exc
                    if attempt == max_attempts:
                        break
                    logger.warning(
                        "retry_attempt",
                        function=fn.__name__,
                        attempt=attempt,
                        max_attempts=max_attempts,
                        delay_s=round(delay, 2),
                        error=str(exc),
                    )
                    await asyncio.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay_s)

            raise last_exc  # type: ignore[misc]

        return wrapper

    return decorator
