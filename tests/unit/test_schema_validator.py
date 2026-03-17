"""Unit tests for SchemaValidator."""

import pytest

from agentic.core.exceptions import SkillValidationError
from agentic.layer4_runtime.schema_validator import SchemaValidator


def test_valid_input_passes(sample_skill):
    validator = SchemaValidator()
    validator.validate_input(sample_skill, {"text": "hello world"})


def test_missing_required_field_fails(sample_skill):
    validator = SchemaValidator()
    with pytest.raises(SkillValidationError) as exc_info:
        validator.validate_input(sample_skill, {})
    assert "input" in exc_info.value.message


def test_wrong_type_fails(sample_skill):
    validator = SchemaValidator()
    with pytest.raises(SkillValidationError):
        validator.validate_input(sample_skill, {"text": 123})


def test_valid_output_passes(sample_skill):
    validator = SchemaValidator()
    validator.validate_output(sample_skill, {"result": "output text"})
