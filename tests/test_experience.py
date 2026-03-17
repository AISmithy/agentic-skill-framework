import pytest
from agentic_skill_framework import (
    SkillMetadata, SkillResult, Skill, SkillRegistry, AgentAPI, CLI, ChatInterface
)

class EchoSkill(Skill):
    @property
    def metadata(self):
        return SkillMetadata(name="echo", version="1.0", description="Echoes input", tags=["echo"])

    def execute(self, inputs: dict) -> SkillResult:
        return SkillResult(skill_name="echo", status="success", output=inputs)


def make_api():
    reg = SkillRegistry()
    reg.register(EchoSkill())
    return AgentAPI(reg)


class TestAgentAPI:
    def test_health(self):
        api = make_api()
        h = api.health()
        assert h["status"] == "ok"
        assert h["skills_registered"] == 1

    def test_list_skills(self):
        api = make_api()
        skills = api.list_skills()
        assert len(skills) == 1
        assert skills[0]["name"] == "echo"

    def test_register_skill(self):
        api = make_api()
        
        class NewSkill(Skill):
            @property
            def metadata(self):
                return SkillMetadata(name="new_skill", version="1.0", description="New")
            def execute(self, inputs):
                return SkillResult(skill_name="new_skill", status="success", output=None)
        
        result = api.register_skill(NewSkill())
        assert result["status"] == "registered"
        assert result["name"] == "new_skill"

    def test_submit_goal(self):
        api = make_api()
        result = api.submit_goal("echo something", "session1")
        assert result["session_id"] == "session1"
        assert result["status"] == "completed"

    def test_get_result(self):
        api = make_api()
        api.submit_goal("echo test", "session2")
        result = api.get_result("session2")
        assert result["session_id"] == "session2"
        assert "results" in result

    def test_get_result_not_found(self):
        api = make_api()
        result = api.get_result("nonexistent")
        assert "error" in result


class TestCLI:
    def test_list_skills(self, capsys):
        api = make_api()
        cli = CLI(api)
        ret = cli.run(["list-skills"])
        assert ret == 0

    def test_health(self, capsys):
        api = make_api()
        cli = CLI(api)
        ret = cli.run(["health"])
        assert ret == 0
        captured = capsys.readouterr()
        assert "ok" in captured.out

    def test_unknown_command(self, capsys):
        api = make_api()
        cli = CLI(api)
        ret = cli.run(["unknown-command"])
        assert ret == 1

    def test_submit_goal(self, capsys):
        api = make_api()
        cli = CLI(api)
        ret = cli.run(["submit-goal", "echo", "hello"])
        assert ret == 0


class TestChatInterface:
    def test_send_message(self):
        api = make_api()
        chat = ChatInterface(api)
        response = chat.send_message("session1", "echo hello")
        assert isinstance(response, str)
        assert len(response) > 0

    def test_get_history(self):
        api = make_api()
        chat = ChatInterface(api)
        chat.send_message("session1", "first message")
        chat.send_message("session1", "second message")
        history = chat.get_history("session1")
        assert len(history) >= 2

    def test_reset_session(self):
        api = make_api()
        chat = ChatInterface(api)
        chat.send_message("session1", "hello")
        chat.reset_session("session1")
        assert chat.get_history("session1") == []

    def test_empty_history(self):
        api = make_api()
        chat = ChatInterface(api)
        assert chat.get_history("new_session") == []
