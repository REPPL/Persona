"""
Schema validation for structural fidelity.

This module validates that personas conform to required structural constraints,
including required fields, field types, and schema compliance.
"""

from typing import Any

from persona.core.generation.parser import Persona
from persona.core.quality.fidelity.models import PromptConstraints, Severity, Violation


class SchemaValidator:
    """
    Validate structural schema compliance.

    Checks that personas have required fields populated with correct types.
    """

    def validate(
        self, persona: Persona, constraints: PromptConstraints
    ) -> tuple[float, list[Violation]]:
        """
        Validate structural constraints.

        Args:
            persona: Persona to validate.
            constraints: Structural constraints to check.

        Returns:
            Tuple of (score 0-1, list of violations).
        """
        violations: list[Violation] = []

        # Check required fields
        missing_fields = self._check_required_fields(persona, constraints)
        violations.extend(missing_fields)

        # Check field types
        type_violations = self._check_field_types(persona, constraints)
        violations.extend(type_violations)

        # Calculate score
        if not constraints.required_fields and not constraints.field_types:
            return 1.0, violations

        total_checks = len(constraints.required_fields) + len(constraints.field_types)
        failed_checks = len(violations)
        score = (
            max(0.0, 1.0 - (failed_checks / total_checks)) if total_checks > 0 else 1.0
        )

        return score, violations

    def _check_required_fields(
        self, persona: Persona, constraints: PromptConstraints
    ) -> list[Violation]:
        """Check that required fields are present and non-empty."""
        violations: list[Violation] = []

        for field_name in constraints.required_fields:
            value = self._get_persona_field(persona, field_name)

            if value is None:
                violations.append(
                    Violation(
                        dimension="structure",
                        field=field_name,
                        description=f"Required field '{field_name}' is missing",
                        severity=Severity.CRITICAL,
                        expected="present",
                        actual="missing",
                    )
                )
            elif not self._has_content(value):
                violations.append(
                    Violation(
                        dimension="structure",
                        field=field_name,
                        description=f"Required field '{field_name}' is empty",
                        severity=Severity.HIGH,
                        expected="non-empty",
                        actual="empty",
                    )
                )

        return violations

    def _check_field_types(
        self, persona: Persona, constraints: PromptConstraints
    ) -> list[Violation]:
        """Check that fields have correct types."""
        violations: list[Violation] = []

        for field_name, expected_type in constraints.field_types.items():
            value = self._get_persona_field(persona, field_name)

            if value is None:
                continue  # Missing fields handled by required_fields check

            # Validate type
            if not self._check_type(value, expected_type):
                actual_type = type(value).__name__
                violations.append(
                    Violation(
                        dimension="structure",
                        field=field_name,
                        description=f"Field '{field_name}' has wrong type",
                        severity=Severity.HIGH,
                        expected=expected_type,
                        actual=actual_type,
                    )
                )

        return violations

    def _get_persona_field(self, persona: Persona, field_name: str) -> Any:
        """
        Get a field value from persona, checking both direct attributes and nested paths.

        Supports nested access like "demographics.age".
        """
        if "." in field_name:
            parts = field_name.split(".", 1)
            parent = getattr(persona, parts[0], None)
            if isinstance(parent, dict):
                return parent.get(parts[1])
            return None
        return getattr(persona, field_name, None)

    def _has_content(self, value: Any) -> bool:
        """Check if a value has meaningful content."""
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, (list, dict)):
            return len(value) > 0
        return True

    def _check_type(self, value: Any, expected_type: str) -> bool:
        """
        Check if value matches expected type.

        Supported types: string, integer, float, list, dict, boolean
        """
        type_map = {
            "string": str,
            "str": str,
            "integer": int,
            "int": int,
            "float": float,
            "number": (int, float),
            "list": list,
            "array": list,
            "dict": dict,
            "object": dict,
            "boolean": bool,
            "bool": bool,
        }

        expected_python_type = type_map.get(expected_type.lower())
        if expected_python_type is None:
            # Unknown type, assume valid
            return True

        return isinstance(value, expected_python_type)
