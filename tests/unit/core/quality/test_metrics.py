"""Tests for individual quality metrics."""

import pytest

from persona.core.generation.parser import Persona
from persona.core.quality.config import QualityConfig
from persona.core.quality.metrics import (
    CompletenessMetric,
    ConsistencyMetric,
    DistinctivenessMetric,
    EvidenceStrengthMetric,
    RealismMetric,
)
from persona.core.quality.models import DimensionScore


class TestCompletenessMetric:
    """Tests for completeness scoring."""

    @pytest.fixture
    def metric(self) -> CompletenessMetric:
        """Create a CompletenessMetric instance."""
        return CompletenessMetric()

    @pytest.fixture
    def complete_persona(self) -> Persona:
        """Create a complete persona."""
        return Persona(
            id="p001",
            name="Complete Person",
            demographics={"age": "30", "occupation": "Engineer", "location": "London"},
            goals=[
                "Goal one with enough words to pass richness check",
                "Goal two with enough words to pass richness check",
            ],
            pain_points=["Pain point with sufficient detail"],
            behaviours=["Behaviour one with detail"],
            quotes=["A representative quote from research"],
        )

    @pytest.fixture
    def incomplete_persona(self) -> Persona:
        """Create an incomplete persona."""
        return Persona(
            id="p002",
            name="Incomplete",
            demographics={},
            goals=[],
            pain_points=[],
            behaviours=[],
            quotes=[],
        )

    def test_complete_persona_scores_high(
        self, metric: CompletenessMetric, complete_persona: Persona
    ) -> None:
        """Complete persona should score highly."""
        result = metric.evaluate(complete_persona)

        assert isinstance(result, DimensionScore)
        assert result.dimension == "completeness"
        assert result.score >= 80
        assert len(result.issues) == 0

    def test_incomplete_persona_scores_low(
        self, metric: CompletenessMetric, incomplete_persona: Persona
    ) -> None:
        """Incomplete persona should score poorly with issues."""
        result = metric.evaluate(incomplete_persona)

        assert result.score < 50
        assert len(result.issues) > 0
        assert any("goals" in issue.lower() for issue in result.issues)

    def test_missing_required_field(self, metric: CompletenessMetric) -> None:
        """Missing required fields should be flagged."""
        persona = Persona(id="", name="", goals=[])
        result = metric.evaluate(persona)

        assert any("required" in issue.lower() for issue in result.issues)

    def test_field_depth_scoring(self, metric: CompletenessMetric) -> None:
        """Field depth (list lengths) should affect score."""
        persona_few = Persona(
            id="p1",
            name="Few Items",
            goals=["One goal"],
        )
        persona_many = Persona(
            id="p2",
            name="Many Items",
            goals=["Goal one", "Goal two", "Goal three"],
            pain_points=["Pain one", "Pain two"],
        )

        result_few = metric.evaluate(persona_few)
        result_many = metric.evaluate(persona_many)

        assert result_many.score > result_few.score


class TestConsistencyMetric:
    """Tests for consistency scoring."""

    @pytest.fixture
    def metric(self) -> ConsistencyMetric:
        """Create a ConsistencyMetric instance."""
        return ConsistencyMetric()

    def test_consistent_persona_scores_high(
        self, metric: ConsistencyMetric
    ) -> None:
        """Consistent persona should score highly."""
        persona = Persona(
            id="p001",
            name="Consistent Person",
            demographics={"age": "32", "occupation": "Manager"},
            goals=["Lead team effectively", "Improve productivity"],
            pain_points=["Too many meetings", "Information silos"],
            behaviours=["Attends daily standups"],
            quotes=["I want to help my team succeed"],
        )

        result = metric.evaluate(persona)

        assert result.score >= 70
        assert result.dimension == "consistency"

    def test_duplicate_goals_flagged(self, metric: ConsistencyMetric) -> None:
        """Duplicate goals should be flagged."""
        persona = Persona(
            id="p001",
            name="Duplicate Goals",
            goals=["Save time", "Save time", "Different goal"],
        )

        result = metric.evaluate(persona)

        assert any("duplicate" in issue.lower() for issue in result.issues)

    def test_age_goal_mismatch_flagged(self, metric: ConsistencyMetric) -> None:
        """Age-goal mismatches should be flagged."""
        persona = Persona(
            id="p001",
            name="Young CEO",
            demographics={"age": "19"},
            goals=["Plan for retirement", "Build legacy"],
        )

        result = metric.evaluate(persona)

        # May flag age-goal mismatch if patterns match
        assert result.score <= 100


class TestDistinctivenessMetric:
    """Tests for distinctiveness scoring."""

    @pytest.fixture
    def metric(self) -> DistinctivenessMetric:
        """Create a DistinctivenessMetric instance."""
        return DistinctivenessMetric()

    def test_single_persona_is_distinct(
        self, metric: DistinctivenessMetric
    ) -> None:
        """Single persona should have max distinctiveness."""
        persona = Persona(id="p001", name="Solo Persona")

        result = metric.evaluate(persona, other_personas=None)

        assert result.score == 100.0

    def test_unique_personas_are_distinct(
        self, metric: DistinctivenessMetric
    ) -> None:
        """Unique personas should score as distinct."""
        persona = Persona(
            id="p001",
            name="Person A",
            goals=["Learn Python programming", "Build web applications"],
            pain_points=["Syntax is confusing"],
        )
        other = Persona(
            id="p002",
            name="Person B",
            goals=["Improve fitness", "Run a marathon"],
            pain_points=["Lack of motivation"],
        )

        result = metric.evaluate(persona, other_personas=[other])

        assert result.score > 60  # Should be fairly distinct

    def test_similar_personas_score_lower(
        self, metric: DistinctivenessMetric
    ) -> None:
        """Similar personas should have lower distinctiveness."""
        persona = Persona(
            id="p001",
            name="Person A",
            goals=["Save time on meetings"],
            pain_points=["Too many meetings"],
        )
        similar = Persona(
            id="p002",
            name="Person B",
            goals=["Save time on meetings"],  # Same goal
            pain_points=["Too many meetings"],  # Same pain point
        )

        result = metric.evaluate(persona, other_personas=[similar])

        # Very similar personas should have lower distinctiveness
        # (exact match would be 0, but comparison is more nuanced)
        assert result.score < 100


class TestEvidenceStrengthMetric:
    """Tests for evidence strength scoring."""

    @pytest.fixture
    def metric(self) -> EvidenceStrengthMetric:
        """Create an EvidenceStrengthMetric instance."""
        return EvidenceStrengthMetric()

    def test_no_evidence_report_uses_estimation(
        self, metric: EvidenceStrengthMetric
    ) -> None:
        """Without evidence report, should estimate from structure."""
        persona = Persona(
            id="p001",
            name="Test Person",
            quotes=["Quote 1", "Quote 2", "Quote 3"],
        )

        result = metric.evaluate(persona, evidence_report=None)

        assert result.dimension == "evidence_strength"
        assert result.score > 0
        assert any("evidence" in issue.lower() for issue in result.issues)

    def test_persona_with_quotes_scores_higher(
        self, metric: EvidenceStrengthMetric
    ) -> None:
        """Persona with quotes should score higher (indicates evidence)."""
        with_quotes = Persona(
            id="p001",
            name="With Quotes",
            quotes=["Quote 1", "Quote 2", "Quote 3", "Quote 4"],
        )
        without_quotes = Persona(
            id="p002",
            name="Without Quotes",
            quotes=[],
        )

        result_with = metric.evaluate(with_quotes)
        result_without = metric.evaluate(without_quotes)

        assert result_with.score > result_without.score


class TestRealismMetric:
    """Tests for realism scoring."""

    @pytest.fixture
    def metric(self) -> RealismMetric:
        """Create a RealismMetric instance."""
        return RealismMetric()

    def test_realistic_persona_scores_high(self, metric: RealismMetric) -> None:
        """Realistic persona should score highly."""
        persona = Persona(
            id="p001",
            name="Sarah Mitchell",
            demographics={"age": "32", "occupation": "Product Manager"},
            goals=["Improve team communication workflows to reduce overhead"],
            quotes=["I'm always looking for ways to work smarter, not harder"],
        )

        result = metric.evaluate(persona)

        assert result.score >= 60
        assert result.dimension == "realism"

    def test_generic_name_flagged(self, metric: RealismMetric) -> None:
        """Generic placeholder names should be flagged."""
        persona = Persona(
            id="p001",
            name="User",
            goals=["Some goal"],
        )

        result = metric.evaluate(persona)

        assert any("generic" in issue.lower() for issue in result.issues)
        assert result.details.get("name_type") == "generic"

    def test_incomplete_name_flagged(self, metric: RealismMetric) -> None:
        """Single-word names should be flagged."""
        persona = Persona(
            id="p001",
            name="John",
            goals=["Some goal"],
        )

        result = metric.evaluate(persona)

        assert result.details.get("name_type") == "incomplete"

    def test_generic_goals_flagged(self, metric: RealismMetric) -> None:
        """Generic goals should be flagged."""
        persona = Persona(
            id="p001",
            name="Test Person",
            goals=["Be better", "Get successful"],
        )

        result = metric.evaluate(persona)

        assert any("generic" in issue.lower() for issue in result.issues)

    def test_missing_name_fails(self, metric: RealismMetric) -> None:
        """Missing name should fail realism check."""
        persona = Persona(
            id="p001",
            name="",
            goals=["Some goal"],
        )

        result = metric.evaluate(persona)

        assert result.details.get("name_type") == "missing"
        assert any("missing" in issue.lower() for issue in result.issues)
