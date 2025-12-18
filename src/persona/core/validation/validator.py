"""
Persona validation functionality.

This module provides the PersonaValidator class for checking
persona quality and consistency.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

from persona.core.generation.parser import Persona


class ValidationLevel(Enum):
    """Severity level for validation issues."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """
    A single validation issue.

    Attributes:
        rule: Name of the rule that was violated.
        message: Human-readable description of the issue.
        level: Severity level.
        field: The persona field with the issue.
        value: The problematic value.
    """

    rule: str
    message: str
    level: ValidationLevel = ValidationLevel.ERROR
    field: str | None = None
    value: Any = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "rule": self.rule,
            "message": self.message,
            "level": self.level.value,
            "field": self.field,
            "value": str(self.value) if self.value else None,
        }


@dataclass
class ValidationResult:
    """
    Result of validating a persona.

    Attributes:
        persona_id: ID of the validated persona.
        is_valid: Whether the persona passed all error-level checks.
        issues: List of validation issues found.
        score: Overall quality score (0-100).
    """

    persona_id: str
    is_valid: bool = True
    issues: list[ValidationIssue] = field(default_factory=list)
    score: int = 100

    @property
    def errors(self) -> list[ValidationIssue]:
        """Return only error-level issues."""
        return [i for i in self.issues if i.level == ValidationLevel.ERROR]

    @property
    def warnings(self) -> list[ValidationIssue]:
        """Return only warning-level issues."""
        return [i for i in self.issues if i.level == ValidationLevel.WARNING]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "persona_id": self.persona_id,
            "is_valid": self.is_valid,
            "score": self.score,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "issues": [i.to_dict() for i in self.issues],
        }


@dataclass
class ValidationRule:
    """
    A validation rule to check personas against.

    Attributes:
        name: Unique rule identifier.
        description: What this rule checks.
        check: Function that takes a Persona and returns issues.
        level: Default severity level for issues from this rule.
        enabled: Whether the rule is active.
    """

    name: str
    description: str
    check: Callable[[Persona], list[ValidationIssue]]
    level: ValidationLevel = ValidationLevel.ERROR
    enabled: bool = True


class PersonaValidator:
    """
    Validates personas against quality and consistency rules.

    Provides built-in rules for common validation needs and allows
    custom rules to be added.

    Example:
        validator = PersonaValidator()
        result = validator.validate(persona)
        if not result.is_valid:
            print(f"Validation failed: {len(result.errors)} errors")
    """

    def __init__(self, strict: bool = False) -> None:
        """
        Initialise the validator.

        Args:
            strict: If True, treat warnings as errors.
        """
        self._strict = strict
        self._rules: list[ValidationRule] = []
        self._register_builtin_rules()

    def _register_builtin_rules(self) -> None:
        """Register built-in validation rules."""
        # Required fields
        self.add_rule(
            ValidationRule(
                name="required_id",
                description="Persona must have an ID",
                check=self._check_required_id,
                level=ValidationLevel.ERROR,
            )
        )

        self.add_rule(
            ValidationRule(
                name="required_name",
                description="Persona must have a name",
                check=self._check_required_name,
                level=ValidationLevel.ERROR,
            )
        )

        # Completeness checks
        self.add_rule(
            ValidationRule(
                name="has_goals",
                description="Persona should have at least one goal",
                check=self._check_has_goals,
                level=ValidationLevel.WARNING,
            )
        )

        self.add_rule(
            ValidationRule(
                name="has_pain_points",
                description="Persona should have at least one pain point",
                check=self._check_has_pain_points,
                level=ValidationLevel.WARNING,
            )
        )

        self.add_rule(
            ValidationRule(
                name="has_demographics",
                description="Persona should have demographics",
                check=self._check_has_demographics,
                level=ValidationLevel.WARNING,
            )
        )

        # Quality checks
        self.add_rule(
            ValidationRule(
                name="name_not_generic",
                description="Persona name should not be generic placeholder",
                check=self._check_name_not_generic,
                level=ValidationLevel.WARNING,
            )
        )

        self.add_rule(
            ValidationRule(
                name="goals_not_empty",
                description="Goals should not be empty strings",
                check=self._check_goals_not_empty,
                level=ValidationLevel.ERROR,
            )
        )

        self.add_rule(
            ValidationRule(
                name="unique_goals",
                description="Goals should be unique",
                check=self._check_unique_goals,
                level=ValidationLevel.WARNING,
            )
        )

        self.add_rule(
            ValidationRule(
                name="minimum_detail",
                description="Persona should have minimum level of detail",
                check=self._check_minimum_detail,
                level=ValidationLevel.INFO,
            )
        )

    def add_rule(self, rule: ValidationRule) -> None:
        """Add a validation rule."""
        self._rules.append(rule)

    def remove_rule(self, name: str) -> bool:
        """Remove a rule by name."""
        for i, rule in enumerate(self._rules):
            if rule.name == name:
                del self._rules[i]
                return True
        return False

    def enable_rule(self, name: str) -> bool:
        """Enable a rule by name."""
        for rule in self._rules:
            if rule.name == name:
                rule.enabled = True
                return True
        return False

    def disable_rule(self, name: str) -> bool:
        """Disable a rule by name."""
        for rule in self._rules:
            if rule.name == name:
                rule.enabled = False
                return True
        return False

    def validate(self, persona: Persona) -> ValidationResult:
        """
        Validate a single persona.

        Args:
            persona: The persona to validate.

        Returns:
            ValidationResult with all issues found.
        """
        issues: list[ValidationIssue] = []

        for rule in self._rules:
            if not rule.enabled:
                continue

            try:
                rule_issues = rule.check(persona)
                issues.extend(rule_issues)
            except Exception as e:
                issues.append(
                    ValidationIssue(
                        rule=rule.name,
                        message=f"Rule check failed: {e}",
                        level=ValidationLevel.ERROR,
                    )
                )

        # Calculate validity
        if self._strict:
            is_valid = len(issues) == 0
        else:
            is_valid = not any(i.level == ValidationLevel.ERROR for i in issues)

        # Calculate score
        score = self._calculate_score(issues)

        return ValidationResult(
            persona_id=persona.id,
            is_valid=is_valid,
            issues=issues,
            score=score,
        )

    def validate_batch(self, personas: list[Persona]) -> list[ValidationResult]:
        """
        Validate multiple personas.

        Args:
            personas: List of personas to validate.

        Returns:
            List of ValidationResult for each persona.
        """
        return [self.validate(p) for p in personas]

    def _calculate_score(self, issues: list[ValidationIssue]) -> int:
        """Calculate quality score based on issues."""
        score = 100

        for issue in issues:
            if issue.level == ValidationLevel.ERROR:
                score -= 25
            elif issue.level == ValidationLevel.WARNING:
                score -= 10
            elif issue.level == ValidationLevel.INFO:
                score -= 2

        return max(0, score)

    # Built-in rule implementations

    def _check_required_id(self, persona: Persona) -> list[ValidationIssue]:
        """Check that persona has an ID."""
        if not persona.id or not persona.id.strip():
            return [
                ValidationIssue(
                    rule="required_id",
                    message="Persona is missing required ID",
                    level=ValidationLevel.ERROR,
                    field="id",
                )
            ]
        return []

    def _check_required_name(self, persona: Persona) -> list[ValidationIssue]:
        """Check that persona has a name."""
        if not persona.name or not persona.name.strip():
            return [
                ValidationIssue(
                    rule="required_name",
                    message="Persona is missing required name",
                    level=ValidationLevel.ERROR,
                    field="name",
                )
            ]
        return []

    def _check_has_goals(self, persona: Persona) -> list[ValidationIssue]:
        """Check that persona has goals."""
        if not persona.goals:
            return [
                ValidationIssue(
                    rule="has_goals",
                    message="Persona has no goals defined",
                    level=ValidationLevel.WARNING,
                    field="goals",
                )
            ]
        return []

    def _check_has_pain_points(self, persona: Persona) -> list[ValidationIssue]:
        """Check that persona has pain points."""
        if not persona.pain_points:
            return [
                ValidationIssue(
                    rule="has_pain_points",
                    message="Persona has no pain points defined",
                    level=ValidationLevel.WARNING,
                    field="pain_points",
                )
            ]
        return []

    def _check_has_demographics(self, persona: Persona) -> list[ValidationIssue]:
        """Check that persona has demographics."""
        if not persona.demographics:
            return [
                ValidationIssue(
                    rule="has_demographics",
                    message="Persona has no demographics defined",
                    level=ValidationLevel.WARNING,
                    field="demographics",
                )
            ]
        return []

    def _check_name_not_generic(self, persona: Persona) -> list[ValidationIssue]:
        """Check that name is not a generic placeholder."""
        generic_names = {
            "user",
            "persona",
            "customer",
            "person",
            "user 1",
            "persona 1",
            "test",
            "example",
            "john doe",
            "jane doe",
            "placeholder",
        }

        if persona.name and persona.name.lower().strip() in generic_names:
            return [
                ValidationIssue(
                    rule="name_not_generic",
                    message=f"Persona name '{persona.name}' appears to be a generic placeholder",
                    level=ValidationLevel.WARNING,
                    field="name",
                    value=persona.name,
                )
            ]
        return []

    def _check_goals_not_empty(self, persona: Persona) -> list[ValidationIssue]:
        """Check that goals are not empty strings."""
        issues = []
        for i, goal in enumerate(persona.goals or []):
            if not goal or not goal.strip():
                issues.append(
                    ValidationIssue(
                        rule="goals_not_empty",
                        message=f"Goal at index {i} is empty",
                        level=ValidationLevel.ERROR,
                        field=f"goals[{i}]",
                    )
                )
        return issues

    def _check_unique_goals(self, persona: Persona) -> list[ValidationIssue]:
        """Check that goals are unique."""
        if not persona.goals:
            return []

        seen = set()
        duplicates = []

        for goal in persona.goals:
            normalised = goal.lower().strip()
            if normalised in seen:
                duplicates.append(goal)
            seen.add(normalised)

        if duplicates:
            return [
                ValidationIssue(
                    rule="unique_goals",
                    message=f"Found {len(duplicates)} duplicate goal(s)",
                    level=ValidationLevel.WARNING,
                    field="goals",
                    value=duplicates,
                )
            ]
        return []

    def _check_minimum_detail(self, persona: Persona) -> list[ValidationIssue]:
        """Check that persona has minimum level of detail."""
        detail_score = 0

        if persona.name:
            detail_score += 1
        if persona.demographics:
            detail_score += len(persona.demographics)
        if persona.goals:
            detail_score += len(persona.goals)
        if persona.pain_points:
            detail_score += len(persona.pain_points)
        if persona.behaviours:
            detail_score += len(persona.behaviours)
        if persona.quotes:
            detail_score += len(persona.quotes)

        if detail_score < 5:
            return [
                ValidationIssue(
                    rule="minimum_detail",
                    message=f"Persona has low detail level (score: {detail_score}/5 minimum)",
                    level=ValidationLevel.INFO,
                    value=detail_score,
                )
            ]
        return []
