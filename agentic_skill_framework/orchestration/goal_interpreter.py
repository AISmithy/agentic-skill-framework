import uuid
from ..models import Goal

class GoalInterpreter:
    def interpret(self, description: str, context: dict = None) -> Goal:
        return Goal(
            id=str(uuid.uuid4()),
            description=description,
            context=context or {}
        )
