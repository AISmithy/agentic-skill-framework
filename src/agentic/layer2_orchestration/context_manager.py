"""Context manager — assembles runtime context for each plan step."""

from __future__ import annotations

from typing import Any

from agentic.layer5_memory.session_memory import SessionMemory


class ContextManager:
    """
    Assembles the execution context for a plan step by combining session
    memory, prior step outputs, and workflow state.
    """

    def build_step_context(
        self,
        step_name: str,
        session: SessionMemory,
        prior_outputs: dict[str, Any],
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Return a merged context dict for injecting into skill inputs."""
        ctx: dict[str, Any] = {}
        ctx.update(session.all())
        ctx["_prior_outputs"] = prior_outputs
        ctx["_step"] = step_name
        if extra:
            ctx.update(extra)
        return ctx

    def extract_relevant(
        self,
        context: dict[str, Any],
        required_keys: list[str],
    ) -> dict[str, Any]:
        """Return only the context keys required by a skill's input schema."""
        return {k: v for k, v in context.items() if k in required_keys}
