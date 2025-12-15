"""
Constraint validation for numeric and range limits.

This module validates that personas adhere to numeric constraints
such as age ranges, item counts, and other quantitative requirements.
"""

from typing import Any

from persona.core.generation.parser import Persona
from persona.core.quality.fidelity.models import PromptConstraints, Severity, Violation


class ConstraintValidator:
    """
    Validate numeric and range constraints.

    Checks that personas adhere to quantitative requirements like
    age ranges, minimum/maximum list lengths, etc.
    """

    def validate(
        self, persona: Persona, constraints: PromptConstraints
    ) -> tuple[float, list[Violation]]:
        """
        Validate numeric constraints.

        Args:
            persona: Persona to validate.
            constraints: Numeric constraints to check.

        Returns:
            Tuple of (score 0-1, list of violations).
        """
        violations: list[Violation] = []

        # Check age range
        if constraints.age_range:
            age_violations = self._check_age_range(persona, constraints)
            violations.extend(age_violations)

        # Check goal count
        if constraints.goal_count:
            goal_violations = self._check_list_count(
                persona.goals, "goals", constraints.goal_count
            )
            violations.extend(goal_violations)

        # Check pain point count
        if constraints.pain_point_count:
            pain_violations = self._check_list_count(
                persona.pain_points, "pain_points", constraints.pain_point_count
            )
            violations.extend(pain_violations)

        # Check behaviour count
        if constraints.behaviour_count:
            behaviour_violations = self._check_list_count(
                persona.behaviours, "behaviours", constraints.behaviour_count
            )
            violations.extend(behaviour_violations)

        # Calculate score
        total_checks = sum(
            1
            for c in [
                constraints.age_range,
                constraints.goal_count,
                constraints.pain_point_count,
                constraints.behaviour_count,
            ]
            if c is not None
        )

        if total_checks == 0:
            return 1.0, violations

        failed_checks = len(violations)
        score = max(0.0, 1.0 - (failed_checks / total_checks))

        return score, violations

    def _check_age_range(
        self, persona: Persona, constraints: PromptConstraints
    ) -> list[Violation]:
        """Check that age is within specified range."""
        violations: list[Violation] = []

        if not constraints.age_range:
            return violations

        min_age, max_age = constraints.age_range

        # Get age from persona
        age = self._get_age(persona)

        if age is None:
            violations.append(
                Violation(
                    dimension="constraint",
                    field="age",
                    description="Age field is missing or invalid",
                    severity=Severity.CRITICAL,
                    expected=f"Age between {min_age} and {max_age}",
                    actual="missing",
                )
            )
            return violations

        # Check range
        if age < min_age or age > max_age:
            violations.append(
                Violation(
                    dimension="constraint",
                    field="age",
                    description=f"Age {age} is outside allowed range",
                    severity=Severity.HIGH,
                    expected=f"Between {min_age} and {max_age}",
                    actual=str(age),
                )
            )

        return violations

    def _check_list_count(
        self, items: list[Any] | None, field_name: str, count_range: tuple[int, int]
    ) -> list[Violation]:
        """Check that a list has the required number of items."""
        violations: list[Violation] = []

        min_count, max_count = count_range
        actual_count = len(items) if items else 0

        if actual_count < min_count:
            violations.append(
                Violation(
                    dimension="constraint",
                    field=field_name,
                    description=f"Field '{field_name}' has too few items",
                    severity=Severity.HIGH,
                    expected=f"At least {min_count} items",
                    actual=f"{actual_count} items",
                )
            )
        elif actual_count > max_count:
            violations.append(
                Violation(
                    dimension="constraint",
                    field=field_name,
                    description=f"Field '{field_name}' has too many items",
                    severity=Severity.MEDIUM,
                    expected=f"At most {max_count} items",
                    actual=f"{actual_count} items",
                )
            )

        return violations

    def _get_age(self, persona: Persona) -> int | None:
        """Extract age from persona, checking multiple possible locations."""
        # Check demographics.age
        if persona.demographics and "age" in persona.demographics:
            age_value = persona.demographics["age"]
            return self._parse_age(age_value)

        # Check additional.age
        if "age" in persona.additional:
            age_value = persona.additional["age"]
            return self._parse_age(age_value)

        return None

    def _parse_age(self, value: Any) -> int | None:
        """Parse age value to integer."""
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            # Try to extract number from string like "42" or "42 years old"
            import re

            match = re.search(r"\b(\d+)\b", value)
            if match:
                return int(match.group(1))
        return None
