"""
Tests for persona validation functionality (F-019).
"""

import pytest

from persona.core.generation.parser import Persona
from persona.core.validation import PersonaValidator, ValidationResult, ValidationRule
from persona.core.validation.validator import ValidationLevel, ValidationIssue


class TestValidationIssue:
    """Tests for ValidationIssue dataclass."""

    def test_create_issue(self):
        """Test creating a validation issue."""
        issue = ValidationIssue(
            rule="test_rule",
            message="Test message",
            level=ValidationLevel.ERROR,
            field="name",
        )

        assert issue.rule == "test_rule"
        assert issue.message == "Test message"
        assert issue.level == ValidationLevel.ERROR

    def test_to_dict(self):
        """Test converting issue to dictionary."""
        issue = ValidationIssue(
            rule="test",
            message="Test",
            level=ValidationLevel.WARNING,
            field="goals",
            value=["goal1"],
        )

        data = issue.to_dict()

        assert data["rule"] == "test"
        assert data["level"] == "warning"
        assert data["field"] == "goals"


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_empty_result(self):
        """Test result with no issues."""
        result = ValidationResult(persona_id="p001")

        assert result.is_valid
        assert result.score == 100
        assert len(result.issues) == 0

    def test_result_with_errors(self):
        """Test result with error issues."""
        result = ValidationResult(
            persona_id="p001",
            is_valid=False,
            issues=[
                ValidationIssue("rule1", "Error 1", ValidationLevel.ERROR),
                ValidationIssue("rule2", "Warning 1", ValidationLevel.WARNING),
            ],
            score=65,
        )

        assert not result.is_valid
        assert len(result.errors) == 1
        assert len(result.warnings) == 1

    def test_to_dict(self):
        """Test converting result to dictionary."""
        result = ValidationResult(
            persona_id="p001",
            score=80,
        )

        data = result.to_dict()

        assert data["persona_id"] == "p001"
        assert data["score"] == 80
        assert data["is_valid"] is True


class TestPersonaValidator:
    """Tests for PersonaValidator class."""

    def test_validate_valid_persona(self):
        """Test validating a complete persona."""
        persona = Persona(
            id="p001",
            name="Alice Smith",
            demographics={"age_range": "25-34"},
            goals=["Learn new skills"],
            pain_points=["Not enough time"],
        )

        validator = PersonaValidator()
        result = validator.validate(persona)

        assert result.is_valid
        assert result.score >= 80

    def test_validate_missing_id(self):
        """Test validation catches missing ID."""
        persona = Persona(id="", name="Alice")

        validator = PersonaValidator()
        result = validator.validate(persona)

        assert not result.is_valid
        assert any(i.rule == "required_id" for i in result.errors)

    def test_validate_missing_name(self):
        """Test validation catches missing name."""
        persona = Persona(id="p001", name="")

        validator = PersonaValidator()
        result = validator.validate(persona)

        assert not result.is_valid
        assert any(i.rule == "required_name" for i in result.errors)

    def test_validate_missing_goals_warning(self):
        """Test validation warns about missing goals."""
        persona = Persona(
            id="p001",
            name="Alice",
            goals=[],
        )

        validator = PersonaValidator()
        result = validator.validate(persona)

        assert result.is_valid  # Warnings don't fail
        assert any(i.rule == "has_goals" for i in result.warnings)

    def test_validate_generic_name_warning(self):
        """Test validation warns about generic names."""
        persona = Persona(
            id="p001",
            name="User",
            goals=["Goal 1"],
        )

        validator = PersonaValidator()
        result = validator.validate(persona)

        assert any(i.rule == "name_not_generic" for i in result.warnings)

    def test_validate_duplicate_goals(self):
        """Test validation warns about duplicate goals."""
        persona = Persona(
            id="p001",
            name="Alice",
            goals=["Learn Python", "learn python", "Other goal"],
        )

        validator = PersonaValidator()
        result = validator.validate(persona)

        assert any(i.rule == "unique_goals" for i in result.warnings)

    def test_validate_empty_goal_error(self):
        """Test validation errors on empty goals."""
        persona = Persona(
            id="p001",
            name="Alice",
            goals=["Valid goal", "", "Another goal"],
        )

        validator = PersonaValidator()
        result = validator.validate(persona)

        assert not result.is_valid
        assert any(i.rule == "goals_not_empty" for i in result.errors)

    def test_strict_mode(self):
        """Test strict mode treats warnings as errors."""
        persona = Persona(
            id="p001",
            name="Alice",
            goals=[],  # Missing goals is a warning
        )

        validator = PersonaValidator(strict=True)
        result = validator.validate(persona)

        assert not result.is_valid  # Warning becomes error in strict mode

    def test_validate_batch(self):
        """Test batch validation."""
        personas = [
            Persona(id="p001", name="Alice", goals=["Goal"]),
            Persona(id="p002", name="Bob", goals=["Goal"]),
            Persona(id="", name="Invalid"),  # Invalid
        ]

        validator = PersonaValidator()
        results = validator.validate_batch(personas)

        assert len(results) == 3
        assert results[0].is_valid
        assert results[1].is_valid
        assert not results[2].is_valid

    def test_disable_rule(self):
        """Test disabling a validation rule."""
        persona = Persona(id="p001", name="User")  # Generic name

        validator = PersonaValidator()
        validator.disable_rule("name_not_generic")
        result = validator.validate(persona)

        assert not any(i.rule == "name_not_generic" for i in result.issues)

    def test_enable_rule(self):
        """Test re-enabling a disabled rule."""
        validator = PersonaValidator()
        validator.disable_rule("has_goals")
        validator.enable_rule("has_goals")

        persona = Persona(id="p001", name="Alice", goals=[])
        result = validator.validate(persona)

        assert any(i.rule == "has_goals" for i in result.warnings)

    def test_add_custom_rule(self):
        """Test adding a custom validation rule."""
        def check_name_length(persona: Persona) -> list[ValidationIssue]:
            if persona.name and len(persona.name) < 3:
                return [ValidationIssue(
                    rule="name_length",
                    message="Name too short",
                    level=ValidationLevel.WARNING,
                )]
            return []

        validator = PersonaValidator()
        validator.add_rule(ValidationRule(
            name="name_length",
            description="Name must be at least 3 characters",
            check=check_name_length,
        ))

        persona = Persona(id="p001", name="Al")
        result = validator.validate(persona)

        assert any(i.rule == "name_length" for i in result.issues)

    def test_remove_rule(self):
        """Test removing a validation rule."""
        validator = PersonaValidator()
        removed = validator.remove_rule("has_goals")

        assert removed is True

        persona = Persona(id="p001", name="Alice", goals=[])
        result = validator.validate(persona)

        assert not any(i.rule == "has_goals" for i in result.issues)

    def test_remove_nonexistent_rule(self):
        """Test removing a rule that doesn't exist."""
        validator = PersonaValidator()
        removed = validator.remove_rule("nonexistent")

        assert removed is False

    def test_score_calculation(self):
        """Test quality score calculation."""
        # Perfect persona
        perfect = Persona(
            id="p001",
            name="Alice Smith",
            demographics={"age": "30"},
            goals=["Goal 1", "Goal 2"],
            pain_points=["Pain 1"],
            behaviours=["Behaviour 1"],
        )

        validator = PersonaValidator()
        result = validator.validate(perfect)

        assert result.score == 100

    def test_score_decreases_with_issues(self):
        """Test score decreases based on issue severity."""
        # Persona with issues
        persona = Persona(
            id="p001",
            name="User",  # Generic name (warning)
            goals=[],  # No goals (warning)
        )

        validator = PersonaValidator()
        result = validator.validate(persona)

        assert result.score < 100

    def test_minimum_detail_info(self):
        """Test minimum detail check."""
        minimal = Persona(
            id="p001",
            name="Alice",
        )

        validator = PersonaValidator()
        result = validator.validate(minimal)

        info_issues = [i for i in result.issues if i.level == ValidationLevel.INFO]
        assert any(i.rule == "minimum_detail" for i in info_issues)
