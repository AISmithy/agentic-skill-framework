import pytest
from agentic_skill_framework import (
    SkillMetadata, SkillResult, Goal, Plan, PlanStep, WorkflowContext,
    Skill, SkillRegistry, GoalInterpreter, Planner, SkillRouter,
    WorkflowEngine, ContextManager, ReflectionManager, Executor
)

class EchoSkill(Skill):
    @property
    def metadata(self):
        return SkillMetadata(name="echo", version="1.0", description="Echo skill", tags=["echo"])

    def execute(self, inputs: dict) -> SkillResult:
        return SkillResult(skill_name="echo", status="success", output=inputs)


class TestGoalInterpreter:
    def test_interpret(self):
        interpreter = GoalInterpreter()
        goal = interpreter.interpret("do something", {"key": "val"})
        assert isinstance(goal, Goal)
        assert goal.description == "do something"
        assert goal.context == {"key": "val"}
        assert goal.id  # non-empty

    def test_interpret_no_context(self):
        interpreter = GoalInterpreter()
        goal = interpreter.interpret("test")
        assert goal.context == {}


class TestPlanner:
    def test_create_plan_match(self):
        planner = Planner()
        skills = [SkillMetadata(name="echo", version="1.0", description="echo skill", tags=["echo"])]
        goal = Goal(id="1", description="echo something")
        plan = planner.create_plan(goal, skills)
        assert isinstance(plan, Plan)
        assert any(s.skill_name == "echo" for s in plan.steps)

    def test_create_plan_no_match(self):
        planner = Planner()
        skills = [SkillMetadata(name="summarize", version="1.0", description="summarize docs", tags=[])]
        goal = Goal(id="1", description="do xyz unrelated")
        plan = planner.create_plan(goal, skills)
        assert plan.steps[0].skill_name == "noop"

    def test_create_plan_by_tag(self):
        planner = Planner()
        skills = [SkillMetadata(name="my_skill", version="1.0", description="does something", tags=["search"])]
        goal = Goal(id="1", description="I need to search documents")
        plan = planner.create_plan(goal, skills)
        assert any(s.skill_name == "my_skill" for s in plan.steps)


class TestSkillRouter:
    def test_route(self):
        reg = SkillRegistry()
        skill = EchoSkill()
        reg.register(skill)
        router = SkillRouter()
        step = PlanStep(step_id="s1", skill_name="echo")
        found = router.route(step, reg)
        assert found is skill

    def test_route_missing(self):
        reg = SkillRegistry()
        router = SkillRouter()
        step = PlanStep(step_id="s1", skill_name="missing")
        assert router.route(step, reg) is None

    def test_select_best_skill(self):
        router = SkillRouter()
        skill = EchoSkill()
        step = PlanStep(step_id="s1", skill_name="echo")
        assert router.select_best_skill([skill], step) is skill
        assert router.select_best_skill([], step) is None


class TestWorkflowEngine:
    def test_run(self):
        reg = SkillRegistry()
        reg.register(EchoSkill())
        executor = Executor()
        engine = WorkflowEngine(reg, executor)
        goal = Goal(id="1", description="test")
        step = PlanStep(step_id="s1", skill_name="echo", inputs={"x": 1})
        plan = Plan(goal_id="1", steps=[step])
        context = WorkflowContext(session_id="sess", goal=goal, plan=plan)
        result_context = engine.run(plan, context)
        assert "s1" in result_context.results
        assert result_context.results["s1"].status == "success"

    def test_run_missing_skill(self):
        reg = SkillRegistry()
        executor = Executor()
        engine = WorkflowEngine(reg, executor)
        goal = Goal(id="1", description="test")
        step = PlanStep(step_id="s1", skill_name="nonexistent")
        plan = Plan(goal_id="1", steps=[step])
        context = WorkflowContext(session_id="sess", goal=goal, plan=plan)
        result_context = engine.run(plan, context)
        assert result_context.results["s1"].status == "error"


class TestContextManager:
    def test_create_context(self):
        cm = ContextManager()
        goal = Goal(id="1", description="test")
        plan = Plan(goal_id="1")
        ctx = cm.create_context("sess1", goal, plan)
        assert ctx.session_id == "sess1"

    def test_update_and_get_result(self):
        cm = ContextManager()
        goal = Goal(id="1", description="test")
        plan = Plan(goal_id="1")
        ctx = cm.create_context("sess1", goal, plan)
        result = SkillResult(skill_name="s", status="success", output=42)
        cm.update_result(ctx, "step_0", result)
        assert cm.get_step_result(ctx, "step_0") is result

    def test_is_complete(self):
        cm = ContextManager()
        goal = Goal(id="1", description="test")
        step = PlanStep(step_id="s1", skill_name="echo")
        plan = Plan(goal_id="1", steps=[step])
        ctx = cm.create_context("sess1", goal, plan)
        assert cm.is_complete(ctx) is False
        cm.update_result(ctx, "s1", SkillResult(skill_name="echo", status="success", output=None))
        assert cm.is_complete(ctx) is True


class TestReflectionManager:
    def test_should_retry(self):
        rm = ReflectionManager()
        result = SkillResult(skill_name="s", status="error", output=None)
        assert rm.should_retry(result, 0, 3) is True
        assert rm.should_retry(result, 3, 3) is False
        ok_result = SkillResult(skill_name="s", status="success", output=None)
        assert rm.should_retry(ok_result, 0, 3) is False

    def test_reflect(self):
        rm = ReflectionManager()
        goal = Goal(id="1", description="test")
        plan = Plan(goal_id="1")
        ctx = WorkflowContext(session_id="sess", goal=goal, plan=plan)
        step = PlanStep(step_id="s1", skill_name="echo")
        msg = rm.reflect(ctx, step)
        assert isinstance(msg, str) and len(msg) > 0

    def test_recover_with_inputs(self):
        rm = ReflectionManager()
        goal = Goal(id="1", description="test")
        plan = Plan(goal_id="1")
        ctx = WorkflowContext(session_id="sess", goal=goal, plan=plan)
        step = PlanStep(step_id="s1", skill_name="echo", inputs={"x": 1})
        recovered = rm.recover(ctx, step)
        assert recovered is not None
        assert recovered.inputs == {}

    def test_recover_no_inputs(self):
        rm = ReflectionManager()
        goal = Goal(id="1", description="test")
        plan = Plan(goal_id="1")
        ctx = WorkflowContext(session_id="sess", goal=goal, plan=plan)
        step = PlanStep(step_id="s1", skill_name="echo", inputs={})
        assert rm.recover(ctx, step) is None
