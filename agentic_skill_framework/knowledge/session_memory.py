from typing import Any, Optional

class SessionMemory:
    def __init__(self):
        self._store: dict = {}
        self._history: dict = {}

    def store(self, session_id: str, key: str, value: Any) -> None:
        if session_id not in self._store:
            self._store[session_id] = {}
        self._store[session_id][key] = value

    def retrieve(self, session_id: str, key: str) -> Optional[Any]:
        return self._store.get(session_id, {}).get(key)

    def get_history(self, session_id: str) -> list[dict]:
        return self._history.get(session_id, [])

    def clear(self, session_id: str) -> None:
        self._store.pop(session_id, None)
        self._history.pop(session_id, None)

    def append_history(self, session_id: str, entry: dict) -> None:
        if session_id not in self._history:
            self._history[session_id] = []
        self._history[session_id].append(entry)
