"""Sandbox — isolated skill execution wrapper."""

from __future__ import annotations

import traceback
from typing import Any

from agentic.core.exceptions import SandboxError
from agentic.layer7_observability.logger import get_logger

logger = get_logger(__name__)


class Sandbox:
    """
    Executes a skill's execute() method in a controlled context.

    In the current implementation this is an in-process execution with
    structured error capture. It can be replaced with subprocess or
    container-based isolation for higher-risk skills.
    """

    async def run(
        self,
        skill_instance: Any,
        inputs: dict[str, Any],
        skill_id: str,
    ) -> dict[str, Any]:
        """
        Call skill_instance.execute(inputs) and return its output.

        Captures all exceptions and re-raises as SandboxError with context.
        """
        try:
            result = await skill_instance.execute(inputs)
            if not isinstance(result, dict):
                raise SandboxError(
                    f"Skill {skill_id} execute() must return a dict, got {type(result).__name__}"
                )
            return result
        except SandboxError:
            raise
        except Exception as exc:
            tb = traceback.format_exc()
            logger.error(
                "sandbox_execution_error",
                skill_id=skill_id,
                error=str(exc),
                traceback=tb,
            )
            raise SandboxError(f"Skill {skill_id} raised an unhandled exception: {exc}") from exc
