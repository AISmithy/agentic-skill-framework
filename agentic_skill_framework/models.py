from dataclasses import dataclass, field
from typing import Any, Optional

@dataclass
class SkillMetadata:
    name: str
    version: str
    description: str
    tags: list[str] = field(default_factory=list)
    owner: str = ""
    dependencies: list[str] = field(default_factory=list)

@dataclass
class SkillResult:
    skill_name: str
    status: str  # "success" or "error"
    output: Any
    error: Optional[str] = None
    duration_ms: float = 0.0

@dataclass
class Goal:
    id: str
    description: str
    context: dict = field(default_factory=dict)

@dataclass
class PlanStep:
    step_id: str
    skill_name: str
    inputs: dict = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)

@dataclass
class Plan:
    goal_id: str
    steps: list[PlanStep] = field(default_factory=list)

@dataclass
class WorkflowContext:
    session_id: str
    goal: Goal
    plan: Plan
    results: dict = field(default_factory=dict)
    metadata: dict = field(default_factory=dict)

@dataclass
class AuditEvent:
    event_id: str
    timestamp: float
    user_id: str
    action: str
    resource: str
    outcome: str
    details: dict = field(default_factory=dict)

@dataclass
class PolicyDecision:
    allowed: bool
    reason: str
    policy_id: str
