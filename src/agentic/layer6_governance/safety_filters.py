"""Safety filters — input/output content gates."""

from __future__ import annotations

import re
from typing import Any

from agentic.core.exceptions import PolicyViolationError
from agentic.layer7_observability.logger import get_logger

logger = get_logger(__name__)

# Patterns that should be blocked in inputs (simplified examples)
_BLOCKED_INPUT_PATTERNS: list[re.Pattern] = [
    re.compile(r"(?i)(drop\s+table|delete\s+from|insert\s+into)"),  # SQL injection
    re.compile(r"<script.*?>.*?</script>", re.DOTALL),              # XSS
]


class SafetyFilter:
    """Inspects inputs and outputs for unsafe content."""

    def check_input(self, skill_id: str, inputs: dict[str, Any]) -> None:
        """Raise PolicyViolationError if inputs contain unsafe content."""
        serialized = str(inputs)
        for pattern in _BLOCKED_INPUT_PATTERNS:
            if pattern.search(serialized):
                logger.warning(
                    "safety_filter_blocked",
                    skill_id=skill_id,
                    pattern=pattern.pattern,
                )
                raise PolicyViolationError(
                    skill_id, f"Input blocked by safety filter: {pattern.pattern}"
                )

    def check_output(self, skill_id: str, output: dict[str, Any]) -> None:
        """Apply output safety gates (extensible)."""
        # Placeholder for PII detection, sensitive data masking, etc.
        pass
