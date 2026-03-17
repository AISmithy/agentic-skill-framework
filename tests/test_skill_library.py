import pytest
from agentic_skill_framework import (SkillMetadata, SkillResult, Skill, SkillRegistry, 
                                      MetadataCatalog, DependencyResolver)

class TestSkill(Skill):
    def __init__(self, name="test_skill", tags=None, deps=None):
        self._metadata = SkillMetadata(
            name=name, version="1.0", description="Test skill",
            tags=tags or [], dependencies=deps or []
        )

    @property
    def metadata(self) -> SkillMetadata:
        return self._metadata

    def execute(self, inputs: dict) -> SkillResult:
        return SkillResult(skill_name=self._metadata.name, status="success", output=inputs)


class TestSkillRegistry:
    def test_register_and_get(self):
        reg = SkillRegistry()
        skill = TestSkill()
        reg.register(skill)
        assert reg.get("test_skill") is skill

    def test_list_skills(self):
        reg = SkillRegistry()
        reg.register(TestSkill("a"))
        reg.register(TestSkill("b"))
        names = [m.name for m in reg.list_skills()]
        assert "a" in names and "b" in names

    def test_find_by_tag(self):
        reg = SkillRegistry()
        reg.register(TestSkill("x", tags=["nlp"]))
        reg.register(TestSkill("y", tags=["ml"]))
        found = reg.find_by_tag("nlp")
        assert len(found) == 1
        assert found[0].metadata.name == "x"

    def test_unregister(self):
        reg = SkillRegistry()
        reg.register(TestSkill())
        assert reg.unregister("test_skill") is True
        assert reg.get("test_skill") is None
        assert reg.unregister("nonexistent") is False


class TestMetadataCatalog:
    def setup_method(self):
        self.catalog = MetadataCatalog()
        self.m1 = SkillMetadata(name="search_skill", version="1.0", description="Search documents", tags=["search", "nlp"], owner="alice")
        self.m2 = SkillMetadata(name="summarize", version="2.0", description="Summarize text", tags=["nlp"], owner="bob")
        self.catalog.add(self.m1)
        self.catalog.add(self.m2)

    def test_get(self):
        assert self.catalog.get("search_skill") is self.m1

    def test_search_by_name(self):
        results = self.catalog.search("search")
        assert any(m.name == "search_skill" for m in results)

    def test_search_by_description(self):
        results = self.catalog.search("Summarize")
        assert any(m.name == "summarize" for m in results)

    def test_search_by_tag(self):
        results = self.catalog.search("nlp")
        assert len(results) == 2

    def test_list_versions(self):
        assert self.catalog.list_versions("summarize") == ["2.0"]
        assert self.catalog.list_versions("missing") == []

    def test_list_by_owner(self):
        result = self.catalog.list_by_owner("alice")
        assert len(result) == 1 and result[0].name == "search_skill"

    def test_list_by_tag(self):
        result = self.catalog.list_by_tag("search")
        assert len(result) == 1


class TestDependencyResolver:
    def test_resolve_no_deps(self):
        reg = SkillRegistry()
        reg.register(TestSkill("standalone"))
        resolver = DependencyResolver()
        result = resolver.resolve("standalone", reg)
        assert "standalone" in result

    def test_resolve_with_deps(self):
        reg = SkillRegistry()
        reg.register(TestSkill("dep_a"))
        reg.register(TestSkill("main_skill", deps=["dep_a"]))
        resolver = DependencyResolver()
        result = resolver.resolve("main_skill", reg)
        assert result.index("dep_a") < result.index("main_skill")

    def test_validate_missing_dep(self):
        reg = SkillRegistry()
        reg.register(TestSkill("skill_with_missing", deps=["missing_dep"]))
        resolver = DependencyResolver()
        assert resolver.validate("skill_with_missing", reg) is False

    def test_validate_valid(self):
        reg = SkillRegistry()
        reg.register(TestSkill("dep"))
        reg.register(TestSkill("parent", deps=["dep"]))
        resolver = DependencyResolver()
        assert resolver.validate("parent", reg) is True

    def test_circular_dep(self):
        reg = SkillRegistry()
        reg.register(TestSkill("a", deps=["b"]))
        reg.register(TestSkill("b", deps=["a"]))
        resolver = DependencyResolver()
        with pytest.raises(ValueError):
            resolver.resolve("a", reg)
