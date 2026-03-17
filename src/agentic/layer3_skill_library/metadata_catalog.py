"""SQLite-backed persistent catalog for skill definitions."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import aiosqlite

from agentic.core.constants import LIFECYCLE_TRANSITIONS, LifecycleStatus
from agentic.core.exceptions import SkillLifecycleError, SkillNotFoundError
from agentic.layer3_skill_library.models.lifecycle import LifecycleTransition
from agentic.layer3_skill_library.models.skill import SkillDefinition

_CREATE_SKILLS = """
CREATE TABLE IF NOT EXISTS skills (
    skill_id        TEXT PRIMARY KEY,
    name            TEXT NOT NULL,
    version         TEXT NOT NULL,
    category        TEXT NOT NULL,
    status          TEXT NOT NULL,
    risk_level      TEXT NOT NULL,
    owner           TEXT NOT NULL,
    tags            TEXT NOT NULL DEFAULT '[]',
    definition_json TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    updated_at      TEXT NOT NULL,
    UNIQUE(name, version)
)
"""

_CREATE_TRANSITIONS = """
CREATE TABLE IF NOT EXISTS lifecycle_transitions (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_id    TEXT NOT NULL,
    from_status TEXT NOT NULL,
    to_status   TEXT NOT NULL,
    actor       TEXT NOT NULL,
    reason      TEXT,
    timestamp   TEXT NOT NULL
)
"""


class MetadataCatalog:
    """Async SQLite-backed skill catalog."""

    def __init__(self, db_path: str = "agentic.db") -> None:
        self._db_path = db_path

    async def initialize(self) -> None:
        """Create tables if they don't exist."""
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(_CREATE_SKILLS)
            await db.execute(_CREATE_TRANSITIONS)
            await db.commit()

    async def save(self, skill: SkillDefinition) -> None:
        """Insert or replace a skill definition."""
        now = datetime.utcnow().isoformat()
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                INSERT INTO skills
                    (skill_id, name, version, category, status, risk_level, owner,
                     tags, definition_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(skill_id) DO UPDATE SET
                    name=excluded.name,
                    version=excluded.version,
                    category=excluded.category,
                    status=excluded.status,
                    risk_level=excluded.risk_level,
                    owner=excluded.owner,
                    tags=excluded.tags,
                    definition_json=excluded.definition_json,
                    updated_at=excluded.updated_at
                """,
                (
                    skill.skill_id,
                    skill.name,
                    skill.version,
                    skill.category,
                    skill.status.value,
                    skill.risk_level.value,
                    skill.owner,
                    json.dumps(skill.tags),
                    skill.model_dump_json(),
                    skill.created_at.isoformat(),
                    now,
                ),
            )
            await db.commit()

    async def load(self, skill_id: str) -> SkillDefinition:
        """Load a single skill by ID."""
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                "SELECT definition_json FROM skills WHERE skill_id = ?", (skill_id,)
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    raise SkillNotFoundError(skill_id)
                return SkillDefinition.model_validate_json(row[0])

    async def load_all(self) -> list[SkillDefinition]:
        """Load all skills from the catalog."""
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute("SELECT definition_json FROM skills") as cursor:
                rows = await cursor.fetchall()
                return [SkillDefinition.model_validate_json(row[0]) for row in rows]

    async def delete(self, skill_id: str) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("DELETE FROM skills WHERE skill_id = ?", (skill_id,))
            await db.commit()

    async def transition_lifecycle(
        self,
        skill_id: str,
        to_status: LifecycleStatus,
        actor: str,
        reason: str = "",
    ) -> SkillDefinition:
        """Validate and apply a lifecycle status transition."""
        skill = await self.load(skill_id)
        allowed = LIFECYCLE_TRANSITIONS.get(skill.status, set())
        if to_status not in allowed:
            raise SkillLifecycleError(skill_id, skill.status.value, to_status.value)

        skill.status = to_status
        skill.updated_at = datetime.utcnow()
        await self.save(skill)

        transition = LifecycleTransition(
            skill_id=skill_id,
            from_status=skill.status,
            to_status=to_status,
            actor=actor,
            reason=reason,
        )
        await self._record_transition(transition)
        return skill

    async def _record_transition(self, t: LifecycleTransition) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                INSERT INTO lifecycle_transitions
                    (skill_id, from_status, to_status, actor, reason, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    t.skill_id,
                    t.from_status.value,
                    t.to_status.value,
                    t.actor,
                    t.reason,
                    t.timestamp.isoformat(),
                ),
            )
            await db.commit()

    async def get_transition_history(self, skill_id: str) -> list[dict[str, Any]]:
        """Return lifecycle transition history for a skill."""
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                """
                SELECT skill_id, from_status, to_status, actor, reason, timestamp
                FROM lifecycle_transitions
                WHERE skill_id = ?
                ORDER BY timestamp ASC
                """,
                (skill_id,),
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def search(
        self,
        *,
        category: str | None = None,
        status: LifecycleStatus | None = None,
        risk_level: str | None = None,
    ) -> list[SkillDefinition]:
        """Query the catalog with optional filters."""
        conditions: list[str] = []
        params: list[str] = []

        if category:
            conditions.append("category = ?")
            params.append(category)
        if status:
            conditions.append("status = ?")
            params.append(status.value)
        if risk_level:
            conditions.append("risk_level = ?")
            params.append(risk_level)

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                f"SELECT definition_json FROM skills {where}", params
            ) as cursor:
                rows = await cursor.fetchall()
                return [SkillDefinition.model_validate_json(row[0]) for row in rows]
