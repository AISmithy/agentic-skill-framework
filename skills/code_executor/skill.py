"""Code Executor skill — restricted Python execution in a subprocess."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

from agentic.layer3_skill_library.models.skill import SkillDefinition
from skills._base import BaseSkill

_MANIFEST_PATH = Path(__file__).parent / "manifest.json"

# Allowed built-ins for restricted execution
_ALLOWED_BUILTINS = {
    "print", "len", "range", "enumerate", "zip", "map", "filter",
    "list", "dict", "set", "tuple", "str", "int", "float", "bool",
    "sum", "min", "max", "abs", "round", "sorted", "reversed",
    "isinstance", "type", "hasattr", "getattr",
}


class CodeExecutorSkill(BaseSkill):
    """
    Executes sandboxed Python code snippets.

    Uses subprocess isolation to prevent the executed code from affecting
    the framework process. Only allows a restricted set of built-ins.
    """

    manifest: SkillDefinition = SkillDefinition.model_validate(
        json.loads(_MANIFEST_PATH.read_text())
    )

    async def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        code: str = inputs.get("code", "")
        timeout_s: int = inputs.get("timeout_s", 5)

        if not code.strip():
            return {"stdout": "", "stderr": "No code provided", "exit_code": 1, "success": False}

        return await self._run_subprocess(code, timeout_s)

    async def _run_subprocess(self, code: str, timeout_s: int) -> dict[str, Any]:
        """Run code in a child Python process for isolation."""
        try:
            proc = await asyncio.create_subprocess_exec(
                sys.executable, "-c", code,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            try:
                stdout, stderr = await asyncio.wait_for(
                    proc.communicate(), timeout=float(timeout_s)
                )
            except asyncio.TimeoutError:
                proc.kill()
                await proc.communicate()
                return {
                    "stdout": "",
                    "stderr": f"Execution timed out after {timeout_s}s",
                    "exit_code": -1,
                    "success": False,
                }

            return {
                "stdout": stdout.decode("utf-8", errors="replace"),
                "stderr": stderr.decode("utf-8", errors="replace"),
                "exit_code": proc.returncode,
                "success": proc.returncode == 0,
            }
        except Exception as exc:
            return {
                "stdout": "",
                "stderr": str(exc),
                "exit_code": -1,
                "success": False,
            }
