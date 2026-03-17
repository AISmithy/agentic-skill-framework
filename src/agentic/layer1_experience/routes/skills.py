"""Skill CRUD and lifecycle endpoints."""

from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from agentic.core.constants import LifecycleStatus
from agentic.core.exceptions import (
    SkillLifecycleError,
    SkillNotFoundError,
    SkillVersionConflictError,
)
from agentic.layer3_skill_library.models.skill import SkillDefinition
from agentic.layer3_skill_library.registry import get_registry

router = APIRouter(prefix="/skills", tags=["skills"])


def get_identity(request: Request):
    identity = getattr(request.state, "identity", None)
    if not identity:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return identity


@router.get("")
async def list_skills(
    category: str | None = None,
    tag: str | None = None,
    published_only: bool = True,
    query: str | None = None,
) -> list[dict]:
    registry = get_registry()
    skills = registry.search(
        category=category,
        tags=[tag] if tag else None,
        published_only=published_only,
        query=query,
    )
    return [s.model_dump(mode="json") for s in skills]


@router.get("/{skill_id}")
async def get_skill(skill_id: str) -> dict:
    registry = get_registry()
    try:
        skill = registry.lookup_by_id(skill_id)
        return skill.model_dump(mode="json")
    except SkillNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message)


@router.post("", status_code=201)
async def register_skill(
    skill: SkillDefinition,
    request: Request,
) -> dict:
    registry = get_registry()
    try:
        registry.register(skill)
        return {"skill_id": skill.skill_id, "status": skill.status.value}
    except SkillVersionConflictError as exc:
        raise HTTPException(status_code=409, detail=exc.message)


@router.delete("/{skill_id}", status_code=204)
async def delete_skill(skill_id: str, request: Request) -> None:
    registry = get_registry()
    try:
        registry.lookup_by_id(skill_id)
        registry.unregister(skill_id)
    except SkillNotFoundError as exc:
        raise HTTPException(status_code=404, detail=exc.message)
