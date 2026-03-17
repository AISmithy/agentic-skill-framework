import uuid
import dataclasses
from typing import Optional
from ..skill_library.registry import SkillRegistry
from ..skill_library.skill_definition import Skill
from ..governance.audit_logger import AuditLogger
from ..governance.observability import ObservabilityManager
from ..governance.auth import AuthManager
from ..runtime.executor import Executor
from ..orchestration.workflow_engine import WorkflowEngine
from ..orchestration.context_manager import ContextManager
from ..orchestration.goal_interpreter import GoalInterpreter
from ..orchestration.planner import Planner
from ..models import WorkflowContext

class AgentAPI:
    def __init__(self, registry: SkillRegistry, audit_logger: AuditLogger = None,
                 observability: ObservabilityManager = None, auth_manager: AuthManager = None):
        self.registry = registry
        self.audit_logger = audit_logger or AuditLogger()
        self.observability = observability or ObservabilityManager()
        self.auth_manager = auth_manager or AuthManager()
        self._executor = Executor()
        self._engine = WorkflowEngine(registry, self._executor)
        self._context_manager = ContextManager()
        self._goal_interpreter = GoalInterpreter()
        self._planner = Planner()
        self._sessions: dict[str, WorkflowContext] = {}

    def submit_goal(self, description: str, session_id: str, user_id: str = "anonymous") -> dict:
        goal = self._goal_interpreter.interpret(description)
        available_skills = self.registry.list_skills()
        plan = self._planner.create_plan(goal, available_skills)
        context = self._context_manager.create_context(session_id, goal, plan)
        context = self._engine.run(plan, context)
        self._sessions[session_id] = context
        self.audit_logger.log(user_id, "submit_goal", description, "success")
        return {"session_id": session_id, "status": "completed", "steps": len(plan.steps)}

    def get_result(self, session_id: str) -> dict:
        context = self._sessions.get(session_id)
        if not context:
            return {"error": "Session not found"}
        return {
            "session_id": session_id,
            "results": {k: dataclasses.asdict(v) for k, v in context.results.items()}
        }

    def list_skills(self) -> list[dict]:
        return [dataclasses.asdict(m) for m in self.registry.list_skills()]

    def register_skill(self, skill: Skill) -> dict:
        self.registry.register(skill)
        return {"status": "registered", "name": skill.metadata.name}

    def health(self) -> dict:
        return {"status": "ok", "skills_registered": self.registry.count()}


class CLI:
    def __init__(self, api: AgentAPI):
        self.api = api

    def run(self, args: list[str]) -> int:
        if not args:
            print("Usage: <command> [args]")
            return 1
        command = args[0]
        if command == "list-skills":
            skills = self.api.list_skills()
            for s in skills:
                print(s)
            return 0
        elif command == "submit-goal":
            if len(args) < 2:
                print("Usage: submit-goal <description>")
                return 1
            description = " ".join(args[1:])
            result = self.api.submit_goal(description, str(uuid.uuid4()))
            print(result)
            return 0
        elif command == "health":
            print(self.api.health())
            return 0
        else:
            print(f"Unknown command: {command}")
            print("Available commands: list-skills, submit-goal, health")
            return 1
