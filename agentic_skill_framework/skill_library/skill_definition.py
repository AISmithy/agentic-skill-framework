from abc import ABC, abstractmethod
from ..models import SkillMetadata, SkillResult

class Skill(ABC):
    @property
    @abstractmethod
    def metadata(self) -> SkillMetadata:
        pass

    @abstractmethod
    def execute(self, inputs: dict) -> SkillResult:
        pass

    def validate_inputs(self, inputs: dict) -> bool:
        return True
