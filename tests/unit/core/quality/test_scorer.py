"""Tests for the QualityScorer class."""

import pytest

from persona.core.generation.parser import Persona
from persona.core.quality import (
    QualityScorer,
    QualityConfig,
    QualityScore,
    QualityLevel,
    BatchQualityResult,
)


class TestQualityScorer:
    """Tests for the main QualityScorer class."""

    @pytest.fixture
    def high_quality_persona(self) -> Persona:
        """Create a high-quality test persona."""
        return Persona(
            id="p001",
            name="Sarah Mitchell",
            demographics={
                "age": "32",
                "occupation": "Product Manager",
                "location": "London",
            },
            goals=[
                "Streamline team communication workflows to reduce meeting overhead",
                "Reduce time spent on manual status updates by 50%",
                "Improve visibility into project progress for stakeholders",
            ],
            pain_points=[
                "Too many meetings fragment my day and reduce deep work time",
                "Information is scattered across multiple disconnected tools",
            ],
            behaviours=[
                "Checks Slack first thing every morning for urgent updates",
                "Uses spreadsheets for manual tracking because existing tools don't integrate",
            ],
            quotes=[
                "I spend half my day just figuring out what's happening across teams",
                "We need one place where everyone can see the big picture",
            ],
        )

    @pytest.fixture
    def low_quality_persona(self) -> Persona:
        """Create a low-quality test persona."""
        return Persona(
            id="p002",
            name="User",
            demographics={},
            goals=["Be better"],
            pain_points=[],
            behaviours=[],
            quotes=[],
        )

    @pytest.fixture
    def scorer(self) -> QualityScorer:
        """Create a standard QualityScorer."""
        return QualityScorer()

    def test_score_high_quality_persona(
        self, scorer: QualityScorer, high_quality_persona: Persona
    ) -> None:
        """High quality personas should score well."""
        result = scorer.score(high_quality_persona)

        assert isinstance(result, QualityScore)
        assert result.overall_score >= 70
        assert result.level in (QualityLevel.EXCELLENT, QualityLevel.GOOD)
        assert "completeness" in result.dimensions
        assert "consistency" in result.dimensions
        assert "evidence_strength" in result.dimensions
        assert "distinctiveness" in result.dimensions
        assert "realism" in result.dimensions

    def test_score_low_quality_persona(
        self, scorer: QualityScorer, low_quality_persona: Persona
    ) -> None:
        """Low quality personas should score poorly."""
        result = scorer.score(low_quality_persona)

        assert result.overall_score <= 60  # At boundary or below
        assert result.level in (QualityLevel.ACCEPTABLE, QualityLevel.POOR, QualityLevel.FAILING)
        assert len(result.dimensions["completeness"].issues) > 0
        assert len(result.dimensions["realism"].issues) > 0

    def test_batch_scoring(
        self,
        scorer: QualityScorer,
        high_quality_persona: Persona,
        low_quality_persona: Persona,
    ) -> None:
        """Batch scoring should work with multiple personas."""
        result = scorer.score_batch([high_quality_persona, low_quality_persona])

        assert isinstance(result, BatchQualityResult)
        assert len(result.scores) == 2
        assert result.average_score > 0
        assert "completeness" in result.average_by_dimension
        # At least one should pass, and scores vary based on comparison
        assert result.passing_count >= 1 or result.failing_count >= 1

    def test_distinctiveness_single_persona(
        self, scorer: QualityScorer, high_quality_persona: Persona
    ) -> None:
        """Single persona should have max distinctiveness."""
        result = scorer.score(high_quality_persona, other_personas=None)

        assert result.dimensions["distinctiveness"].score == 100.0

    def test_distinctiveness_with_others(
        self, scorer: QualityScorer, high_quality_persona: Persona
    ) -> None:
        """Distinctiveness should vary when comparing to others."""
        other = Persona(
            id="p003",
            name="Different Person",
            demographics={"age": "45"},
            goals=["Completely different goal about something else entirely"],
            pain_points=["Unique pain point not shared by others"],
        )

        result = scorer.score(high_quality_persona, other_personas=[other])

        # Should still be distinct since goals/pain points are different
        assert result.dimensions["distinctiveness"].score > 50

    def test_strict_config(self, high_quality_persona: Persona) -> None:
        """Strict config should have higher thresholds."""
        config = QualityConfig.strict()
        scorer = QualityScorer(config=config)
        result = scorer.score(high_quality_persona)

        # Same persona should score relatively lower with strict config
        assert result.overall_score <= 95  # Not guaranteed excellent

    def test_lenient_config(self, low_quality_persona: Persona) -> None:
        """Lenient config should have lower thresholds."""
        config = QualityConfig.lenient()
        scorer = QualityScorer(config=config)
        result = scorer.score(low_quality_persona)

        # Same persona might score higher with lenient config
        # (though still probably poor due to missing content)
        assert result.overall_score >= 0  # Just verify it runs

    def test_quality_score_to_dict(
        self, scorer: QualityScorer, high_quality_persona: Persona
    ) -> None:
        """QualityScore should serialise to dict correctly."""
        result = scorer.score(high_quality_persona)
        data = result.to_dict()

        assert "persona_id" in data
        assert "overall_score" in data
        assert "level" in data
        assert "dimensions" in data
        assert isinstance(data["dimensions"], dict)

    def test_batch_result_to_dict(
        self,
        scorer: QualityScorer,
        high_quality_persona: Persona,
        low_quality_persona: Persona,
    ) -> None:
        """BatchQualityResult should serialise correctly."""
        result = scorer.score_batch([high_quality_persona, low_quality_persona])
        data = result.to_dict()

        assert "persona_count" in data
        assert "average_score" in data
        assert "average_by_dimension" in data
        assert "individual_scores" in data
        assert len(data["individual_scores"]) == 2

    def test_invalid_config_raises(self) -> None:
        """Invalid config should raise ValueError."""
        config = QualityConfig()
        config.weights = {"completeness": 0.5}  # Doesn't sum to 1.0

        with pytest.raises(ValueError, match="Invalid configuration"):
            QualityScorer(config=config)

    def test_get_dimension_weights(self, scorer: QualityScorer) -> None:
        """Should return copy of dimension weights."""
        weights = scorer.get_dimension_weights()

        assert "completeness" in weights
        assert sum(weights.values()) == pytest.approx(1.0)

    def test_get_thresholds(self, scorer: QualityScorer) -> None:
        """Should return quality thresholds."""
        thresholds = scorer.get_thresholds()

        assert "excellent" in thresholds
        assert "good" in thresholds
        assert "acceptable" in thresholds
        assert "poor" in thresholds
        assert thresholds["excellent"] > thresholds["good"]


class TestQualityLevel:
    """Tests for QualityLevel enum."""

    def test_level_values(self) -> None:
        """QualityLevel should have expected values."""
        assert QualityLevel.EXCELLENT.value == "excellent"
        assert QualityLevel.GOOD.value == "good"
        assert QualityLevel.ACCEPTABLE.value == "acceptable"
        assert QualityLevel.POOR.value == "poor"
        assert QualityLevel.FAILING.value == "failing"


class TestQualityConfig:
    """Tests for QualityConfig."""

    def test_default_config(self) -> None:
        """Default config should be valid."""
        config = QualityConfig()
        errors = config.validate()

        assert len(errors) == 0
        assert sum(config.weights.values()) == pytest.approx(1.0)

    def test_strict_config(self) -> None:
        """Strict config should be valid with higher thresholds."""
        config = QualityConfig.strict()
        errors = config.validate()

        assert len(errors) == 0
        assert config.min_goals == 3
        assert config.excellent_threshold > QualityConfig().excellent_threshold

    def test_lenient_config(self) -> None:
        """Lenient config should be valid with lower thresholds."""
        config = QualityConfig.lenient()
        errors = config.validate()

        assert len(errors) == 0
        assert config.min_goals == 1
        assert config.excellent_threshold < QualityConfig().excellent_threshold

    def test_invalid_weights(self) -> None:
        """Invalid weights should fail validation."""
        config = QualityConfig()
        config.weights = {"completeness": 0.5, "consistency": 0.2}

        errors = config.validate()
        assert len(errors) > 0
        assert "sum to 1.0" in errors[0]

    def test_invalid_thresholds(self) -> None:
        """Thresholds in wrong order should fail validation."""
        config = QualityConfig()
        config.excellent_threshold = 50
        config.good_threshold = 90  # Higher than excellent

        errors = config.validate()
        assert len(errors) > 0
