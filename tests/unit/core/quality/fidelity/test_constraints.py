"""
Tests for constraint validator.

Tests ConstraintValidator for numeric constraint validation.
"""

import pytest

from persona.core.generation.parser import Persona
from persona.core.quality.fidelity.constraints import ConstraintValidator
from persona.core.quality.fidelity.models import PromptConstraints, Severity


class TestConstraintValidator:
    """Test ConstraintValidator."""

    def test_valid_age_range(self):
        """Test validation with age in range."""
        persona = Persona(
            id="p1",
            name="Test User",
            demographics={"age": 35},
        )

        constraints = PromptConstraints(age_range=(25, 45))

        validator = ConstraintValidator()
        score, violations = validator.validate(persona, constraints)

        assert score == 1.0
        assert len(violations) == 0

    def test_age_too_low(self):
        """Test detection of age below minimum."""
        persona = Persona(
            id="p1",
            name="Test User",
            demographics={"age": 20},
        )

        constraints = PromptConstraints(age_range=(25, 45))

        validator = ConstraintValidator()
        score, violations = validator.validate(persona, constraints)

        assert score < 1.0
        assert len(violations) > 0
        assert any(v.field == "age" for v in violations)

    def test_age_too_high(self):
        """Test detection of age above maximum."""
        persona = Persona(
            id="p1",
            name="Test User",
            demographics={"age": 50},
        )

        constraints = PromptConstraints(age_range=(25, 45))

        validator = ConstraintValidator()
        score, violations = validator.validate(persona, constraints)

        assert score < 1.0
        assert len(violations) > 0
        assert any(v.field == "age" for v in violations)

    def test_missing_age(self):
        """Test handling of missing age field."""
        persona = Persona(id="p1", name="Test User")

        constraints = PromptConstraints(age_range=(25, 45))

        validator = ConstraintValidator()
        score, violations = validator.validate(persona, constraints)

        assert len(violations) > 0
        assert any(v.severity == Severity.CRITICAL for v in violations)

    def test_valid_goal_count(self):
        """Test validation with goal count in range."""
        persona = Persona(
            id="p1",
            name="Test User",
            goals=["Goal 1", "Goal 2", "Goal 3", "Goal 4"],
        )

        constraints = PromptConstraints(goal_count=(3, 5))

        validator = ConstraintValidator()
        score, violations = validator.validate(persona, constraints)

        assert score == 1.0
        assert len(violations) == 0

    def test_too_few_goals(self):
        """Test detection of insufficient goals."""
        persona = Persona(
            id="p1",
            name="Test User",
            goals=["Goal 1", "Goal 2"],
        )

        constraints = PromptConstraints(goal_count=(3, 5))

        validator = ConstraintValidator()
        score, violations = validator.validate(persona, constraints)

        assert score < 1.0
        assert len(violations) > 0
        assert any(v.field == "goals" for v in violations)

    def test_too_many_goals(self):
        """Test detection of excessive goals."""
        persona = Persona(
            id="p1",
            name="Test User",
            goals=["Goal 1", "Goal 2", "Goal 3", "Goal 4", "Goal 5", "Goal 6"],
        )

        constraints = PromptConstraints(goal_count=(3, 5))

        validator = ConstraintValidator()
        score, violations = validator.validate(persona, constraints)

        assert score < 1.0
        assert len(violations) > 0

    def test_valid_pain_point_count(self):
        """Test validation with pain point count in range."""
        persona = Persona(
            id="p1",
            name="Test User",
            pain_points=["Pain 1", "Pain 2", "Pain 3"],
        )

        constraints = PromptConstraints(pain_point_count=(2, 4))

        validator = ConstraintValidator()
        score, violations = validator.validate(persona, constraints)

        assert score == 1.0
        assert len(violations) == 0

    def test_valid_behaviour_count(self):
        """Test validation with behaviour count in range."""
        persona = Persona(
            id="p1",
            name="Test User",
            behaviours=["Behaviour 1", "Behaviour 2"],
        )

        constraints = PromptConstraints(behaviour_count=(2, 5))

        validator = ConstraintValidator()
        score, violations = validator.validate(persona, constraints)

        assert score == 1.0
        assert len(violations) == 0

    def test_multiple_constraints(self):
        """Test validation with multiple constraints."""
        persona = Persona(
            id="p1",
            name="Test User",
            demographics={"age": 30},
            goals=["Goal 1", "Goal 2", "Goal 3"],
            pain_points=["Pain 1", "Pain 2"],
        )

        constraints = PromptConstraints(
            age_range=(25, 45),
            goal_count=(3, 5),
            pain_point_count=(2, 4),
        )

        validator = ConstraintValidator()
        score, violations = validator.validate(persona, constraints)

        assert score == 1.0
        assert len(violations) == 0

    def test_no_constraints(self):
        """Test validation with no constraints."""
        persona = Persona(id="p1", name="Test User")
        constraints = PromptConstraints()

        validator = ConstraintValidator()
        score, violations = validator.validate(persona, constraints)

        assert score == 1.0
        assert len(violations) == 0

    def test_age_string_parsing(self):
        """Test parsing age from string like '42 years old'."""
        persona = Persona(
            id="p1",
            name="Test User",
            demographics={"age": "35 years old"},
        )

        constraints = PromptConstraints(age_range=(25, 45))

        validator = ConstraintValidator()
        score, violations = validator.validate(persona, constraints)

        assert score == 1.0
        assert len(violations) == 0
