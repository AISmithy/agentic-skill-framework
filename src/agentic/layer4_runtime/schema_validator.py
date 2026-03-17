"""JSON Schema validation for skill inputs and outputs."""

from __future__ import annotations

from typing import Any

import jsonschema

from agentic.core.exceptions import SkillValidationError
from agentic.layer3_skill_library.models.skill import SkillDefinition


class SchemaValidator:
    """Validates skill inputs and outputs against their declared JSON Schemas."""

    def validate_input(self, skill: SkillDefinition, payload: dict[str, Any]) -> None:
        """Raise SkillValidationError if payload does not match input_schema."""
        self._validate(skill.skill_id, payload, skill.input_schema, direction="input")

    def validate_output(self, skill: SkillDefinition, payload: dict[str, Any]) -> None:
        """Raise SkillValidationError if payload does not match output_schema."""
        self._validate(skill.skill_id, payload, skill.output_schema, direction="output")

    def _validate(
        self,
        skill_id: str,
        payload: dict[str, Any],
        schema: dict[str, Any],
        direction: str,
    ) -> None:
        try:
            jsonschema.validate(instance=payload, schema=schema)
        except jsonschema.ValidationError as exc:
            raise SkillValidationError(
                f"Skill {skill_id} {direction} validation failed: {exc.message}",
                errors=[
                    {
                        "path": list(exc.absolute_path),
                        "message": exc.message,
                        "schema_path": list(exc.absolute_schema_path),
                    }
                ],
            ) from exc
        except jsonschema.SchemaError as exc:
            raise SkillValidationError(
                f"Skill {skill_id} has an invalid {direction} schema: {exc.message}",
            ) from exc
