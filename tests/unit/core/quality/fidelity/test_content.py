"""
Tests for content checker.

Tests ContentChecker for content requirement validation.
"""

import pytest

from persona.core.generation.parser import Persona
from persona.core.quality.fidelity.content import ContentChecker
from persona.core.quality.fidelity.models import PromptConstraints, Severity


class TestContentChecker:
    """Test ContentChecker."""

    def test_valid_occupation_keywords(self):
        """Test validation with matching occupation keywords."""
        persona = Persona(
            id="p1",
            name="Test User",
            demographics={"occupation": "Software Developer"},
        )

        constraints = PromptConstraints(occupation_keywords=["developer", "software"])

        checker = ContentChecker()
        score, violations = checker.check(persona, constraints)

        assert score == 1.0
        assert len(violations) == 0

    def test_missing_occupation_keywords(self):
        """Test detection of missing occupation keywords."""
        persona = Persona(
            id="p1",
            name="Test User",
            demographics={"occupation": "Manager"},
        )

        constraints = PromptConstraints(occupation_keywords=["developer", "engineer"])

        checker = ContentChecker()
        score, violations = checker.check(persona, constraints)

        assert score < 1.0
        assert len(violations) > 0
        assert any(v.field == "occupation" for v in violations)

    def test_empty_occupation(self):
        """Test handling of empty occupation field."""
        persona = Persona(id="p1", name="Test User")

        constraints = PromptConstraints(occupation_keywords=["developer"])

        checker = ContentChecker()
        score, violations = checker.check(persona, constraints)

        assert len(violations) > 0
        assert any("empty" in v.description.lower() for v in violations)

    def test_valid_goal_themes(self):
        """Test validation with matching goal themes."""
        persona = Persona(
            id="p1",
            name="Test User",
            goals=[
                "Improve productivity at work",
                "Focus on learning new programming skills",
                "Increase efficiency in daily tasks",
            ],
        )

        constraints = PromptConstraints(goal_themes=["productivity", "learning"])

        checker = ContentChecker()
        score, violations = checker.check(persona, constraints)

        assert score == 1.0
        assert len(violations) == 0

    def test_missing_goal_themes(self):
        """Test detection of missing goal themes."""
        persona = Persona(
            id="p1",
            name="Test User",
            goals=["Buy a house", "Travel the world"],
        )

        constraints = PromptConstraints(goal_themes=["productivity", "learning"])

        checker = ContentChecker()
        score, violations = checker.check(persona, constraints)

        assert score < 1.0
        assert len(violations) > 0
        assert any(v.field == "goals" for v in violations)

    def test_empty_goals(self):
        """Test handling of empty goals field."""
        persona = Persona(id="p1", name="Test User", goals=[])

        constraints = PromptConstraints(goal_themes=["productivity"])

        checker = ContentChecker()
        score, violations = checker.check(persona, constraints)

        assert len(violations) > 0
        assert any(v.field == "goals" for v in violations)

    def test_required_keywords_in_field(self):
        """Test required keywords in specific fields."""
        persona = Persona(
            id="p1",
            name="Test User",
            pain_points=[
                "Difficult to manage health appointments",
                "Complex medical care coordination",
            ],
        )

        constraints = PromptConstraints(
            required_keywords={"pain_points": ["health", "care"]}
        )

        checker = ContentChecker()
        score, violations = checker.check(persona, constraints)

        assert score == 1.0
        assert len(violations) == 0

    def test_missing_required_keywords(self):
        """Test detection of missing required keywords."""
        persona = Persona(
            id="p1",
            name="Test User",
            pain_points=["Work is stressful", "Too many meetings"],
        )

        constraints = PromptConstraints(
            required_keywords={"pain_points": ["health", "wellness"]}
        )

        checker = ContentChecker()
        score, violations = checker.check(persona, constraints)

        assert score < 1.0
        assert len(violations) > 0

    def test_no_constraints(self):
        """Test checking with no constraints."""
        persona = Persona(id="p1", name="Test User")
        constraints = PromptConstraints()

        checker = ContentChecker()
        score, violations = checker.check(persona, constraints)

        assert score == 1.0
        assert len(violations) == 0

    def test_case_insensitive_matching(self):
        """Test that keyword matching is case-insensitive."""
        persona = Persona(
            id="p1",
            name="Test User",
            demographics={"occupation": "SOFTWARE DEVELOPER"},
        )

        constraints = PromptConstraints(occupation_keywords=["developer"])

        checker = ContentChecker()
        score, violations = checker.check(persona, constraints)

        assert score == 1.0
        assert len(violations) == 0
