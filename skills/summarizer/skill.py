"""Document Summarizer skill implementation."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from agentic.layer3_skill_library.models.skill import SkillDefinition
from skills._base import BaseSkill

_MANIFEST_PATH = Path(__file__).parent / "manifest.json"


class DocumentSummarizer(BaseSkill):
    """
    Summarizes text content without external API dependencies.

    In production, replace the _summarize method with an LLM API call.
    """

    manifest: SkillDefinition = SkillDefinition.model_validate(
        json.loads(_MANIFEST_PATH.read_text())
    )

    async def execute(self, inputs: dict[str, Any]) -> dict[str, Any]:
        text: str = inputs.get("text", "")
        max_length: int = inputs.get("max_length", 500)

        if not text.strip():
            return {"summary": "", "key_points": [], "word_count": 0}

        summary, key_points = self._summarize(text, max_length)
        word_count = len(text.split())

        return {
            "summary": summary,
            "key_points": key_points,
            "word_count": word_count,
        }

    def _summarize(self, text: str, max_length: int) -> tuple[str, list[str]]:
        """Simple extractive summarization — first N sentences + bullet detection."""
        # Split into sentences
        sentences = re.split(r"(?<=[.!?])\s+", text.strip())

        # Build summary from leading sentences up to max_length
        summary_parts: list[str] = []
        total = 0
        for sent in sentences:
            if total + len(sent) > max_length:
                break
            summary_parts.append(sent)
            total += len(sent) + 1

        summary = " ".join(summary_parts) if summary_parts else sentences[0][:max_length]

        # Extract key points: sentences with action verbs or numbered items
        key_points: list[str] = []
        for sent in sentences[: min(10, len(sentences))]:
            stripped = sent.strip()
            if stripped and (
                re.match(r"^\d+\.", stripped)
                or any(kw in stripped.lower() for kw in ["key", "important", "must", "should", "critical"])
            ):
                key_points.append(stripped)

        # Fallback: use first 3 sentences as key points
        if not key_points:
            key_points = [s.strip() for s in sentences[:3] if s.strip()]

        return summary, key_points[:5]
