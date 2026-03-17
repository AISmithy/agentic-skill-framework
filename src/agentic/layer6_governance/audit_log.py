"""Append-only audit log backed by SQLite."""

from __future__ import annotations

import json
import uuid
from datetime import datetime
from typing import Any

import aiosqlite

from agentic.layer7_observability.logger import get_logger
from agentic.layer7_observability.tracer import get_current_trace_id

logger = get_logger(__name__)

_CREATE_AUDIT = """
CREATE TABLE IF NOT EXISTS audit_log (
    event_id        TEXT PRIMARY KEY,
    timestamp       TEXT NOT NULL,
    actor           TEXT NOT NULL,
    skill_id        TEXT,
    event_type      TEXT NOT NULL,
    outcome         TEXT NOT NULL,
    duration_ms     REAL,
    policy_decision TEXT,
    trace_id        TEXT,
    details_json    TEXT
)
"""


class AuditLog:
    """Append-only structured audit trail for all framework events."""

    EVENT_INVOKED = "INVOKED"
    EVENT_APPROVED = "APPROVED"
    EVENT_DENIED = "DENIED"
    EVENT_LIFECYCLE = "LIFECYCLE_TRANSITION"
    EVENT_POLICY = "POLICY_EVALUATED"

    def __init__(self, db_path: str = "agentic.db") -> None:
        self._db_path = db_path

    async def initialize(self) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(_CREATE_AUDIT)
            await db.commit()

    async def record(
        self,
        actor: str,
        event_type: str,
        outcome: str,
        skill_id: str | None = None,
        duration_ms: float | None = None,
        policy_decision: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> str:
        event_id = uuid.uuid4().hex
        timestamp = datetime.utcnow().isoformat()
        trace_id = get_current_trace_id()

        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                INSERT INTO audit_log
                    (event_id, timestamp, actor, skill_id, event_type, outcome,
                     duration_ms, policy_decision, trace_id, details_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event_id,
                    timestamp,
                    actor,
                    skill_id,
                    event_type,
                    outcome,
                    duration_ms,
                    policy_decision,
                    trace_id,
                    json.dumps(details or {}),
                ),
            )
            await db.commit()

        logger.info(
            "audit_event",
            event_id=event_id,
            actor=actor,
            skill_id=skill_id,
            event_type=event_type,
            outcome=outcome,
        )
        return event_id

    async def query(
        self,
        actor: str | None = None,
        skill_id: str | None = None,
        event_type: str | None = None,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        conditions: list[str] = []
        params: list[Any] = []

        if actor:
            conditions.append("actor = ?")
            params.append(actor)
        if skill_id:
            conditions.append("skill_id = ?")
            params.append(skill_id)
        if event_type:
            conditions.append("event_type = ?")
            params.append(event_type)

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        params.append(limit)

        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute(
                f"SELECT * FROM audit_log {where} ORDER BY timestamp DESC LIMIT ?",
                params,
            ) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
