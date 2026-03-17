import os
import time
import tempfile
import pytest
from agentic_skill_framework import (
    CircuitBreaker, CircuitBreakerOpenError, Executor, Sandbox,
    HttpConnector, DatabaseConnector, FileConnector, ConnectorRegistry,
    Validator, SkillMetadata, SkillResult, Skill
)

class SuccessSkill(Skill):
    @property
    def metadata(self):
        return SkillMetadata(name="success_skill", version="1.0", description="Always succeeds")

    def execute(self, inputs: dict) -> SkillResult:
        return SkillResult(skill_name="success_skill", status="success", output={"result": "ok"})


class FailSkill(Skill):
    def __init__(self):
        self._count = 0

    @property
    def metadata(self):
        return SkillMetadata(name="fail_skill", version="1.0", description="Always fails")

    def execute(self, inputs: dict) -> SkillResult:
        self._count += 1
        raise RuntimeError("Intentional failure")


class SucceedOnThirdAttemptSkill(Skill):
    def __init__(self):
        self._count = 0

    @property
    def metadata(self):
        return SkillMetadata(name="flaky_skill", version="1.0", description="Flaky skill")

    def execute(self, inputs: dict) -> SkillResult:
        self._count += 1
        if self._count < 3:
            raise RuntimeError("Not yet")
        return SkillResult(skill_name="flaky_skill", status="success", output="done")


class TestCircuitBreaker:
    def test_normal_success(self):
        cb = CircuitBreaker()
        result = cb.call(lambda: 42)
        assert result == 42
        assert cb.get_state() == CircuitBreaker.CLOSED

    def test_failure_counting(self):
        cb = CircuitBreaker(failure_threshold=3)
        def fail():
            raise RuntimeError("fail")
        for _ in range(2):
            with pytest.raises(RuntimeError):
                cb.call(fail)
        assert cb.get_state() == CircuitBreaker.CLOSED

    def test_circuit_opens(self):
        cb = CircuitBreaker(failure_threshold=3)
        def fail():
            raise RuntimeError("fail")
        for _ in range(3):
            try:
                cb.call(fail)
            except RuntimeError:
                pass
        assert cb.get_state() == CircuitBreaker.OPEN
        with pytest.raises(CircuitBreakerOpenError):
            cb.call(lambda: 1)

    def test_recovery(self):
        cb = CircuitBreaker(failure_threshold=1, recovery_timeout=0.01)
        def fail():
            raise RuntimeError("fail")
        try:
            cb.call(fail)
        except RuntimeError:
            pass
        assert cb.get_state() == CircuitBreaker.OPEN
        time.sleep(0.05)
        result = cb.call(lambda: "recovered")
        assert result == "recovered"
        assert cb.get_state() == CircuitBreaker.CLOSED

    def test_reset(self):
        cb = CircuitBreaker(failure_threshold=1)
        def fail():
            raise RuntimeError("fail")
        try:
            cb.call(fail)
        except RuntimeError:
            pass
        cb.reset()
        assert cb.get_state() == CircuitBreaker.CLOSED


class TestExecutor:
    def test_successful_execution(self):
        executor = Executor()
        skill = SuccessSkill()
        result = executor.execute(skill, {})
        assert result.status == "success"
        assert result.duration_ms >= 0

    def test_retry_on_failure(self):
        executor = Executor(default_max_retries=3)
        skill = SucceedOnThirdAttemptSkill()
        result = executor.execute(skill, {})
        assert result.status == "success"

    def test_failure_after_retries(self):
        executor = Executor(default_max_retries=2)
        skill = FailSkill()
        result = executor.execute(skill, {})
        assert result.status == "error"


class TestSandbox:
    def test_execute(self):
        sb = Sandbox()
        result = sb.execute(lambda: 42)
        assert result == 42

    def test_is_allowed_module(self):
        sb = Sandbox()
        assert sb.is_allowed_module("os") is True
        assert sb.is_allowed_module("subprocess") is False

    def test_custom_allowed_modules(self):
        sb = Sandbox(allowed_modules=["json", "math"])
        assert sb.is_allowed_module("json") is True
        assert sb.is_allowed_module("os") is False


class TestConnectors:
    def test_http_get(self):
        http = HttpConnector("http://example.com")
        resp = http.get("/api/test")
        assert resp["status"] == 200
        assert "GET" in resp["body"]

    def test_http_post(self):
        http = HttpConnector()
        resp = http.post("/api/data", {"key": "value"})
        assert resp["status"] == 200
        assert resp["data"] == {"key": "value"}

    def test_database_connector(self):
        db = DatabaseConnector()
        db.connect()
        db.execute("CREATE TABLE test (id INTEGER, name TEXT)")
        db.execute("INSERT INTO test VALUES (?, ?)", (1, "Alice"))
        rows = db.query("SELECT * FROM test")
        assert len(rows) == 1
        assert rows[0]["name"] == "Alice"
        db.disconnect()

    def test_file_connector(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fc = FileConnector(tmpdir)
            fc.write("test.txt", "hello world")
            content = fc.read("test.txt")
            assert content == "hello world"
            files = fc.list(".")
            assert "test.txt" in files

    def test_connector_registry(self):
        reg = ConnectorRegistry()
        http = HttpConnector()
        reg.register("http", http)
        assert reg.get("http") is http
        assert "http" in reg.list_connectors()


class TestValidator:
    def test_validate_inputs_happy(self):
        v = Validator()
        schema = {"name": "str", "age": "int"}
        valid, errors = v.validate_inputs({"name": "Alice", "age": 30}, schema)
        assert valid is True
        assert errors == []

    def test_validate_inputs_missing(self):
        v = Validator()
        schema = {"name": "str"}
        valid, errors = v.validate_inputs({}, schema)
        assert valid is False
        assert any("name" in e for e in errors)

    def test_validate_inputs_wrong_type(self):
        v = Validator()
        schema = {"age": "int"}
        valid, errors = v.validate_inputs({"age": "not_an_int"}, schema)
        assert valid is False

    def test_validate_skill_metadata_valid(self):
        v = Validator()
        m = SkillMetadata(name="test", version="1.0", description="desc")
        valid, errors = v.validate_skill_metadata(m)
        assert valid is True

    def test_validate_skill_metadata_invalid(self):
        v = Validator()
        m = SkillMetadata(name="", version="", description="")
        valid, errors = v.validate_skill_metadata(m)
        assert valid is False
        assert len(errors) >= 2
