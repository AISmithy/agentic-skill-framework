"""SQLite-backed long-term key-value memory for agents."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any

import aiosqlite

_CREATE = """
CREATE TABLE IF NOT EXISTS long_term_memory (
    key         TEXT PRIMARY KEY,
    value_json  TEXT NOT NULL,
    namespace   TEXT NOT NULL DEFAULT 'default',
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL
)
"""


class LongTermMemory:
    """Persistent key-value store for agent knowledge that survives sessions."""

    def __init__(self, db_path: str = "agentic.db") -> None:
        self._db_path = db_path

    async def initialize(self) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(_CREATE)
            await db.commit()

    async def set(self, key: str, value: Any, namespace: str = "default") -> None:
        now = datetime.utcnow().isoformat()
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute(
                """
                INSERT INTO long_term_memory (key, value_json, namespace, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value_json=excluded.value_json,
                    updated_at=excluded.updated_at
                """,
                (key, json.dumps(value), namespace, now, now),
            )
            await db.commit()

    async def get(self, key: str, default: Any = None) -> Any:
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                "SELECT value_json FROM long_term_memory WHERE key = ?", (key,)
            ) as cursor:
                row = await cursor.fetchone()
                if not row:
                    return default
                return json.loads(row[0])

    async def delete(self, key: str) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await db.execute("DELETE FROM long_term_memory WHERE key = ?", (key,))
            await db.commit()

    async def list_keys(self, namespace: str = "default") -> list[str]:
        async with aiosqlite.connect(self._db_path) as db:
            async with db.execute(
                "SELECT key FROM long_term_memory WHERE namespace = ?", (namespace,)
            ) as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]
