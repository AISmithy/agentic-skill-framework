import json
import pytest
from agentic_skill_framework import (
    AuthManager, PolicyEngine, AuditLogger, ObservabilityManager, PolicyDecision
)

class TestAuthManager:
    def test_create_user(self):
        auth = AuthManager()
        user = auth.create_user("user1", roles=["admin"], permissions=["*:*"])
        assert user["user_id"] == "user1"

    def test_generate_and_authenticate(self):
        auth = AuthManager()
        auth.create_user("user1", roles=[], permissions=[])
        token = auth.generate_token("user1")
        assert auth.authenticate("user1", token) is True
        assert auth.authenticate("user1", "wrong_token") is False
        assert auth.authenticate("other", token) is False

    def test_authorize(self):
        auth = AuthManager()
        auth.create_user("admin", roles=["admin"], permissions=["*:*"])
        auth.create_user("reader", roles=["reader"], permissions=["docs:read"])
        auth.create_user("limited", roles=[], permissions=["docs:*"])
        assert auth.authorize("admin", "anything", "do") is True
        assert auth.authorize("reader", "docs", "read") is True
        assert auth.authorize("reader", "docs", "write") is False
        assert auth.authorize("limited", "docs", "read") is True
        assert auth.authorize("limited", "docs", "write") is True
        assert auth.authorize("limited", "admin", "access") is False

    def test_revoke_token(self):
        auth = AuthManager()
        auth.create_user("user1", roles=[], permissions=[])
        token = auth.generate_token("user1")
        assert auth.revoke_token(token) is True
        assert auth.authenticate("user1", token) is False
        assert auth.revoke_token("nonexistent") is False


class TestPolicyEngine:
    def test_add_and_evaluate_allow(self):
        engine = PolicyEngine()
        engine.add_policy("p1", {"docs/*": ["read", "write"]})
        decision = engine.evaluate("user1", "docs/file1", "read")
        assert decision.allowed is True
        assert decision.policy_id == "p1"

    def test_evaluate_deny(self):
        engine = PolicyEngine()
        engine.add_policy("p1", {"docs/*": ["read"]})
        decision = engine.evaluate("user1", "docs/file1", "delete")
        assert decision.allowed is False

    def test_no_policy(self):
        engine = PolicyEngine()
        decision = engine.evaluate("user1", "resource", "action")
        assert decision.allowed is False

    def test_list_policies(self):
        engine = PolicyEngine()
        engine.add_policy("p1", {"*": ["read"]})
        engine.add_policy("p2", {"admin/*": ["*"]})
        assert len(engine.list_policies()) == 2

    def test_remove_policy(self):
        engine = PolicyEngine()
        engine.add_policy("p1", {"*": ["read"]})
        assert engine.remove_policy("p1") is True
        assert engine.remove_policy("nonexistent") is False
        assert len(engine.list_policies()) == 0


class TestAuditLogger:
    def test_log_and_get(self):
        logger = AuditLogger()
        event = logger.log("user1", "read", "docs/file1", "success", {"size": 100})
        assert event.user_id == "user1"
        assert event.action == "read"
        events = logger.get_events()
        assert len(events) == 1

    def test_get_events_filter(self):
        logger = AuditLogger()
        logger.log("user1", "read", "res1", "success")
        logger.log("user2", "write", "res2", "success")
        logger.log("user1", "delete", "res3", "failure")
        assert len(logger.get_events(user_id="user1")) == 2
        assert len(logger.get_events(action="write")) == 1

    def test_export_json(self):
        logger = AuditLogger()
        logger.log("user1", "act", "res", "ok")
        exported = logger.export("json")
        data = json.loads(exported)
        assert len(data) == 1
        assert data[0]["user_id"] == "user1"

    def test_clear(self):
        logger = AuditLogger()
        logger.log("u1", "a", "r", "ok")
        logger.clear()
        assert logger.get_events() == []


class TestObservabilityManager:
    def test_record_and_get_metrics(self):
        obs = ObservabilityManager()
        obs.record_metric("latency", 100.0, {"service": "api"})
        obs.record_metric("latency", 150.0)
        metrics = obs.get_metrics("latency")
        assert len(metrics["latency"]) == 2

    def test_get_all_metrics(self):
        obs = ObservabilityManager()
        obs.record_metric("m1", 1.0)
        obs.record_metric("m2", 2.0)
        all_m = obs.get_metrics()
        assert "m1" in all_m and "m2" in all_m

    def test_trace(self):
        import time
        obs = ObservabilityManager()
        trace = obs.start_trace("t1", "operation_x")
        assert trace["status"] == "running"
        time.sleep(0.01)
        ended = obs.end_trace("t1", "ok")
        assert ended["status"] == "ok"
        assert ended["duration_ms"] > 0

    def test_record_eval(self):
        obs = ObservabilityManager()
        obs.record_eval("eval1", "accuracy", 0.95, {"dataset": "test"})
        evals = obs.get_evals("eval1")
        assert len(evals) == 1
        assert evals[0]["score"] == 0.95

    def test_summary(self):
        obs = ObservabilityManager()
        obs.record_metric("m1", 1.0)
        obs.start_trace("t1", "op")
        obs.record_eval("e1", "acc", 0.9)
        s = obs.summary()
        assert s["total_metrics"] == 1
        assert s["total_traces"] == 1
        assert s["total_evals"] == 1
        assert "m1" in s["metric_names"]
        assert "t1" in s["trace_ids"]
