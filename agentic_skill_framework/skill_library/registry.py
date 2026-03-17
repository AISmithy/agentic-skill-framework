from typing import Optional
from .skill_definition import Skill
from ..models import SkillMetadata

class SkillRegistry:
    def __init__(self):
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        self._skills[skill.metadata.name] = skill

    def get(self, name: str) -> Optional[Skill]:
        return self._skills.get(name)

    def list_skills(self) -> list[SkillMetadata]:
        return [s.metadata for s in self._skills.values()]

    def find_by_tag(self, tag: str) -> list[Skill]:
        return [s for s in self._skills.values() if tag in s.metadata.tags]

    def count(self) -> int:
        return len(self._skills)

    def unregister(self, name: str) -> bool:
        if name in self._skills:
            del self._skills[name]
            return True
        return False
