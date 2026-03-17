"""Application entry point — wires skills and creates the FastAPI app."""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure src/ and project root are on the path when run directly
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from skills.code_executor.skill import CodeExecutorSkill
from skills.summarizer.skill import DocumentSummarizer
from skills.web_search.skill import WebSearchSkill

from agentic.layer1_experience.app import create_app

# Instantiate all skill implementations
_summarizer = DocumentSummarizer()
_web_search = WebSearchSkill()
_code_executor = CodeExecutorSkill()

# Map skill_id → instance so the executor can dispatch calls
skill_instances = {
    _summarizer.manifest.skill_id: _summarizer,
    _web_search.manifest.skill_id: _web_search,
    _code_executor.manifest.skill_id: _code_executor,
}

app = create_app(skill_instances=skill_instances)
