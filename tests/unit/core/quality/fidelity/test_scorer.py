"""
Tests for fidelity scorer.

Tests FidelityScorer orchestrator.
"""


from persona.core.generation.parser import Persona
from persona.core.quality.fidelity import (
    FidelityConfig,
    FidelityScorer,
    PromptConstraints,
)


class TestFidelityScorer:
    """Test FidelityScorer."""

    def test_perfect_persona(self):
        """Test scoring perfect persona."""
        persona = Persona(
            id="p1",
            name="Test User",
            demographics={"age": 30, "occupation": "Software Developer"},
            goals=["Improve productivity", "Learn new skills", "Advance career"],
            pain_points=["Too many meetings", "Legacy code"],
        )

        constraints = PromptConstraints(
            required_fields=["name", "goals"],
            age_range=(25, 45),
            goal_count=(3, 5),
            occupation_keywords=["developer"],
        )

        config = FidelityConfig(use_llm_judge=False)
        scorer = FidelityScorer(config)
        report = scorer.score(persona, constraints)

        assert report.overall_score >= 0.9
        assert report.passed is True
        assert len(report.violations) == 0

    def test_persona_with_violations(self):
        """Test scoring persona with violations."""
        persona = Persona(
            id="p1",
            name="Test User",
            demographics={"age": 20},  # Too young
            goals=["Goal 1"],  # Too few goals
        )

        constraints = PromptConstraints(
            required_fields=["name", "goals", "pain_points"],  # Missing pain_points
            age_range=(25, 45),
            goal_count=(3, 5),
        )

        config = FidelityConfig(use_llm_judge=False)
        scorer = FidelityScorer(config)
        report = scorer.score(persona, constraints)

        assert report.overall_score < 0.9
        assert len(report.violations) > 0

    def test_selective_checking(self):
        """Test disabling specific check dimensions."""
        persona = Persona(
            id="p1",
            name="Test User",
            goals=["Goal"],  # Would violate if checked
        )

        constraints = PromptConstraints(goal_count=(3, 5))

        # Disable constraint checking
        config = FidelityConfig(check_constraints=False, use_llm_judge=False)
        scorer = FidelityScorer(config)
        report = scorer.score(persona, constraints)

        # Should pass because constraint checking is disabled
        assert report.constraint_score == 1.0

    def test_dimension_scores(self):
        """Test individual dimension scores."""
        persona = Persona(
            id="p1",
            name="Test User",
            demographics={"age": 30},
            goals=["Goal 1", "Goal 2", "Goal 3"],
        )

        constraints = PromptConstraints(
            required_fields=["name"],
            age_range=(25, 45),
            goal_count=(3, 5),
        )

        config = FidelityConfig(use_llm_judge=False)
        scorer = FidelityScorer(config)
        report = scorer.score(persona, constraints)

        assert 0.0 <= report.structure_score <= 1.0
        assert 0.0 <= report.content_score <= 1.0
        assert 0.0 <= report.constraint_score <= 1.0
        assert 0.0 <= report.style_score <= 1.0

    def test_overall_score_calculation(self):
        """Test overall score is weighted average."""
        persona = Persona(
            id="p1",
            name="Test User",
            demographics={"age": 30},
            goals=["Goal 1", "Goal 2", "Goal 3"],
        )

        constraints = PromptConstraints(
            required_fields=["name"],
            age_range=(25, 45),
            goal_count=(3, 5),
        )

        config = FidelityConfig(use_llm_judge=False)
        scorer = FidelityScorer(config)
        report = scorer.score(persona, constraints)

        # Verify overall score is reasonable weighted average
        # Weights: structure=35%, content=25%, constraint=25%, style=15%
        expected_min = min(
            report.structure_score,
            report.content_score,
            report.constraint_score,
            report.style_score,
        )
        expected_max = max(
            report.structure_score,
            report.content_score,
            report.constraint_score,
            report.style_score,
        )

        assert expected_min <= report.overall_score <= expected_max

    def test_pass_threshold(self):
        """Test pass/fail threshold."""
        # Create persona with borderline score
        persona = Persona(
            id="p1",
            name="Test User",
            demographics={"age": 30},
            goals=["Goal 1", "Goal 2", "Goal 3"],
        )

        constraints = PromptConstraints(
            required_fields=["name", "goals"],
            age_range=(25, 45),
            goal_count=(3, 5),
        )

        config = FidelityConfig(use_llm_judge=False)
        scorer = FidelityScorer(config)
        report = scorer.score(persona, constraints)

        # Should pass with score >= 0.6 and no critical violations
        if report.overall_score >= 0.6 and len(report.critical_violations) == 0:
            assert report.passed is True
        else:
            assert report.passed is False

    def test_empty_constraints(self):
        """Test scoring with no constraints."""
        persona = Persona(id="p1", name="Test User")
        constraints = PromptConstraints()

        config = FidelityConfig(use_llm_judge=False)
        scorer = FidelityScorer(config)
        report = scorer.score(persona, constraints)

        assert report.overall_score >= 0.9
        assert report.passed is True

    def test_report_details(self):
        """Test report contains detailed information."""
        persona = Persona(
            id="p1",
            name="Test User",
            demographics={"age": 30},
        )

        constraints = PromptConstraints(required_fields=["name"])

        config = FidelityConfig(use_llm_judge=False)
        scorer = FidelityScorer(config)
        report = scorer.score(persona, constraints)

        assert report.persona_id == "p1"
        assert report.persona_name == "Test User"
        assert "structure" in report.details
        assert "content" in report.details
        assert "constraint" in report.details
        assert "style" in report.details
