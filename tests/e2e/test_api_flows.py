"""End-to-end API tests using FastAPI TestClient."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from agentic.core.constants import LifecycleStatus
from agentic.layer3_skill_library.models.skill import SkillDefinition


@pytest.fixture
def app():
    from skills.summarizer.skill import DocumentSummarizer
    from skills.web_search.skill import WebSearchSkill
    from agentic.layer1_experience.app import create_app

    summarizer = DocumentSummarizer()
    summarizer.manifest.status = LifecycleStatus.PUBLISHED

    web_search = WebSearchSkill()
    web_search.manifest.status = LifecycleStatus.PUBLISHED

    return create_app(
        skill_instances={
            summarizer.manifest.skill_id: summarizer,
            web_search.manifest.skill_id: web_search,
        }
    )


@pytest.fixture
async def client(app):
    # Pre-register skills in the global registry for tests
    from agentic.layer3_skill_library.registry import get_registry
    from skills.summarizer.skill import DocumentSummarizer
    from skills.web_search.skill import WebSearchSkill

    registry = get_registry()
    for skill_cls in [DocumentSummarizer, WebSearchSkill]:
        inst = skill_cls()
        inst.manifest.status = LifecycleStatus.PUBLISHED
        try:
            registry.register(inst.manifest, overwrite=True)
        except Exception:
            pass

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as c:
        yield c


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_list_skills_unauthenticated(client):
    # List endpoint is protected
    response = await client.get("/skills")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_list_skills_authenticated(client):
    response = await client.get(
        "/skills",
        headers={"Authorization": "Bearer dev-token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_execute_summarizer(client):
    response = await client.post(
        "/executions",
        json={
            "skill_id": "doc.summarize.v1",
            "inputs": {"text": "This is a test document with important content."},
        },
        headers={"Authorization": "Bearer dev-token"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "summary" in data["output"]


@pytest.mark.asyncio
async def test_execute_unknown_skill(client):
    response = await client.post(
        "/executions",
        json={"skill_id": "unknown.skill.v99", "inputs": {}},
        headers={"Authorization": "Bearer dev-token"},
    )
    assert response.status_code in (404, 500)


@pytest.mark.asyncio
async def test_metrics_endpoint(client):
    response = await client.get("/metrics")
    assert response.status_code == 200
