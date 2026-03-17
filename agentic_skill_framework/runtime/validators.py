from typing import Any
from ..models import SkillMetadata

TYPE_MAP = {
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
    "list": list,
    "dict": dict,
}

class Validator:
    def validate_inputs(self, inputs: dict, schema: dict) -> tuple[bool, list[str]]:
        errors = []
        for field, type_name in schema.items():
            if field not in inputs:
                errors.append(f"Missing required field: {field}")
                continue
            expected_type = TYPE_MAP.get(type_name)
            if expected_type and not isinstance(inputs[field], expected_type):
                errors.append(f"Field '{field}' expected {type_name}, got {type(inputs[field]).__name__}")
        return (len(errors) == 0, errors)

    def validate_outputs(self, outputs: Any, expected_type: str) -> tuple[bool, str]:
        expected = TYPE_MAP.get(expected_type)
        if expected is None:
            return (False, f"Unknown type: {expected_type}")
        if isinstance(outputs, expected):
            return (True, "")
        return (False, f"Expected {expected_type}, got {type(outputs).__name__}")

    def validate_skill_metadata(self, metadata: SkillMetadata) -> tuple[bool, list[str]]:
        errors = []
        if not metadata.name:
            errors.append("name must be non-empty")
        if not metadata.version:
            errors.append("version must be non-empty")
        if not metadata.description:
            errors.append("description must be non-empty")
        return (len(errors) == 0, errors)
