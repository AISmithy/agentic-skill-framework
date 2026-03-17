"""Web Search skill implementation (stub — no external search API required)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agentic.layer3_skill_library.models.skill import SkillDefinition
from skills._base import BaseSkill

_MANIFEST_PATH = Path(__file__).parent / "manifest.json"


class WebSearchSkill(BaseSkill):
    """
    Web search skill.

    The default implementation returns simulated results for demonstration.
    Replace _search() with a real search API (SerpAPI, Bing, etc.) in production.
    """

    manifest: SkillDefinition = SkillDefinition.model_validate(
        json.loads(_MANIFEST_PATH.read_text())
    )

    async def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        query: str = inputs.get("query", "")
        max_results: int = inputs.get("max_results", 5)

        if not query.strip():
            return {"results": [], "total_found": 0}

        results = self._search(query, max_results)
        return {"results": results, "total_found": len(results)}

    def _search(self, query: str, max_results: int) -> list[dict[str, str]]:
        """Stub search — returns synthetic results based on query keywords."""
        words = query.lower().split()
        results = []
        for i, word in enumerate(words[:max_results]):
            results.append({
                "title": f"Result {i + 1}: {word.capitalize()} Overview",
                "snippet": f"Comprehensive information about {word} and related topics.",
                "url": f"https://example.com/{word}",
            })
        return results
