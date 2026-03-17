import json
import time
import uuid
import dataclasses
from ..models import AuditEvent

class AuditLogger:
    def __init__(self):
        self._events: list[AuditEvent] = []

    def log(self, user_id: str, action: str, resource: str, outcome: str, details: dict = None) -> AuditEvent:
        event = AuditEvent(
            event_id=str(uuid.uuid4()),
            timestamp=time.time(),
            user_id=user_id,
            action=action,
            resource=resource,
            outcome=outcome,
            details=details or {}
        )
        self._events.append(event)
        return event

    def get_events(self, user_id: str = None, action: str = None, limit: int = 100) -> list[AuditEvent]:
        events = self._events
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        if action:
            events = [e for e in events if e.action == action]
        return events[:limit]

    def export(self, format: str = "json") -> str:
        return json.dumps([dataclasses.asdict(e) for e in self._events])

    def clear(self) -> None:
        self._events = []
