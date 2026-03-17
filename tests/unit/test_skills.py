"""Unit tests for first-party skill implementations."""

import pytest

from skills.summarizer.skill import DocumentSummarizer
from skills.web_search.skill import WebSearchSkill
from skills.code_executor.skill import CodeExecutorSkill


@pytest.mark.asyncio
async def test_summarizer_basic():
    skill = DocumentSummarizer()
    result = await skill.execute({"text": "This is a test document. It has multiple sentences. Key information is here."})
    assert "summary" in result
    assert "key_points" in result
    assert "word_count" in result
    assert result["word_count"] > 0


@pytest.mark.asyncio
async def test_summarizer_empty_input():
    skill = DocumentSummarizer()
    result = await skill.execute({"text": ""})
    assert result["summary"] == ""
    assert result["key_points"] == []


@pytest.mark.asyncio
async def test_web_search_returns_results():
    skill = WebSearchSkill()
    result = await skill.execute({"query": "machine learning"})
    assert "results" in result
    assert "total_found" in result
    assert result["total_found"] > 0


@pytest.mark.asyncio
async def test_web_search_empty_query():
    skill = WebSearchSkill()
    result = await skill.execute({"query": ""})
    assert result["total_found"] == 0


@pytest.mark.asyncio
async def test_code_executor_success():
    skill = CodeExecutorSkill()
    result = await skill.execute({"code": "print('hello')"})
    assert result["success"] is True
    assert "hello" in result["stdout"]


@pytest.mark.asyncio
async def test_code_executor_syntax_error():
    skill = CodeExecutorSkill()
    result = await skill.execute({"code": "def broken syntax("})
    assert result["success"] is False
    assert result["exit_code"] != 0
