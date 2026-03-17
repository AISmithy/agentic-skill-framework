import pytest
from agentic_skill_framework import (SkillMetadata, SkillResult, Goal, Plan, PlanStep, 
                                      WorkflowContext, AuditEvent, PolicyDecision)

def test_skill_metadata_defaults():
    m = SkillMetadata(name="test", version="1.0", description="desc")
    assert m.name == "test"
    assert m.version == "1.0"
    assert m.description == "desc"
    assert m.tags == []
    assert m.owner == ""
    assert m.dependencies == []

def test_skill_metadata_custom():
    m = SkillMetadata(name="test", version="1.0", description="desc", tags=["a", "b"], owner="me", dependencies=["dep1"])
    assert m.tags == ["a", "b"]
    assert m.owner == "me"
    assert m.dependencies == ["dep1"]

def test_skill_result():
    r = SkillResult(skill_name="s", status="success", output=42)
    assert r.skill_name == "s"
    assert r.status == "success"
    assert r.output == 42
    assert r.error is None
    assert r.duration_ms == 0.0

def test_goal():
    g = Goal(id="1", description="do something")
    assert g.id == "1"
    assert g.context == {}

def test_plan_step():
    s = PlanStep(step_id="s1", skill_name="my_skill")
    assert s.inputs == {}
    assert s.depends_on == []

def test_plan():
    p = Plan(goal_id="g1")
    assert p.steps == []

def test_workflow_context():
    g = Goal(id="1", description="test")
    p = Plan(goal_id="1")
    wc = WorkflowContext(session_id="sess", goal=g, plan=p)
    assert wc.results == {}
    assert wc.metadata == {}

def test_audit_event():
    e = AuditEvent(event_id="e1", timestamp=1.0, user_id="u1", action="act", resource="res", outcome="ok")
    assert e.details == {}

def test_policy_decision():
    d = PolicyDecision(allowed=True, reason="ok", policy_id="p1")
    assert d.allowed is True
