"""Tests for quality metric base classes."""

from typing import TYPE_CHECKING

from persona.core.generation.parser import Persona
from persona.core.quality.base import (
    MetricCategory,
    QualityMetric,
    get_metric_requirements,
)
from persona.core.quality.config import QualityConfig
from persona.core.quality.models import DimensionScore

if TYPE_CHECKING:
    from persona.core.evidence.linker import EvidenceReport


class ConcreteMetric(QualityMetric):
    """Concrete implementation for testing."""

    @property
    def name(self) -> str:
        return "test_metric"

    @property
    def requires_source_data(self) -> bool:
        return False

    @property
    def requires_other_personas(self) -> bool:
        return False

    @property
    def requires_evidence_report(self) -> bool:
        return False

    def evaluate(
        self,
        persona: Persona,
        source_data: str | None = None,
        other_personas: list[Persona] | None = None,
        evidence_report: "EvidenceReport | None" = None,
    ) -> DimensionScore:
        return DimensionScore(
            dimension=self.name,
            score=100.0,
            weight=0.2,
            issues=[],
            details={"test": True},
        )


class SourceRequiringMetric(QualityMetric):
    """Metric that requires source data."""

    @property
    def name(self) -> str:
        return "source_metric"

    @property
    def requires_source_data(self) -> bool:
        return True

    @property
    def requires_other_personas(self) -> bool:
        return False

    @property
    def requires_evidence_report(self) -> bool:
        return False

    def evaluate(
        self,
        persona: Persona,
        source_data: str | None = None,
        other_personas: list[Persona] | None = None,
        evidence_report: "EvidenceReport | None" = None,
    ) -> DimensionScore:
        score = 100.0 if source_data else 50.0
        return DimensionScore(
            dimension=self.name,
            score=score,
            weight=0.2,
            issues=[] if source_data else ["No source data"],
            details={"has_source": source_data is not None},
        )


class TestQualityMetricABC:
    """Tests for the QualityMetric abstract base class."""

    def test_concrete_metric_instantiation(self):
        """Test that concrete metric can be instantiated."""
        metric = ConcreteMetric()
        assert metric.name == "test_metric"
        assert metric.config is not None

    def test_concrete_metric_with_config(self):
        """Test that concrete metric accepts config."""
        config = QualityConfig()
        metric = ConcreteMetric(config=config)
        assert metric.config is config

    def test_metric_name_property(self):
        """Test the name property."""
        metric = ConcreteMetric()
        assert metric.name == "test_metric"

    def test_metric_description_default(self):
        """Test default description generation."""
        metric = ConcreteMetric()
        assert metric.description == "Test Metric metric"

    def test_metric_weight_from_config(self):
        """Test weight property reads from config."""
        config = QualityConfig()
        config.weights["test_metric"] = 0.15
        metric = ConcreteMetric(config=config)
        assert metric.weight == 0.15

    def test_metric_weight_default_zero(self):
        """Test weight defaults to 0 if not in config."""
        metric = ConcreteMetric()
        assert metric.weight == 0.0

    def test_requires_source_data(self):
        """Test requires_source_data property."""
        metric = ConcreteMetric()
        assert metric.requires_source_data is False

        source_metric = SourceRequiringMetric()
        assert source_metric.requires_source_data is True

    def test_requires_other_personas(self):
        """Test requires_other_personas property."""
        metric = ConcreteMetric()
        assert metric.requires_other_personas is False

    def test_requires_evidence_report(self):
        """Test requires_evidence_report property."""
        metric = ConcreteMetric()
        assert metric.requires_evidence_report is False

    def test_evaluate_returns_dimension_score(self):
        """Test that evaluate returns DimensionScore."""
        metric = ConcreteMetric()
        persona = Persona(
            id="test-1",
            name="Test Person",
            goals=["Goal 1"],
            pain_points=["Pain 1"],
        )
        result = metric.evaluate(persona)

        assert isinstance(result, DimensionScore)
        assert result.dimension == "test_metric"
        assert result.score == 100.0

    def test_metric_repr(self):
        """Test string representation."""
        metric = ConcreteMetric()
        assert repr(metric) == "<ConcreteMetric(name='test_metric')>"


class TestMetricCategory:
    """Tests for MetricCategory constants."""

    def test_category_values(self):
        """Test category constant values."""
        assert MetricCategory.STRUCTURAL == "structural"
        assert MetricCategory.SEMANTIC == "semantic"
        assert MetricCategory.COMPARATIVE == "comparative"
        assert MetricCategory.EVIDENTIAL == "evidential"
        assert MetricCategory.ACADEMIC == "academic"
        assert MetricCategory.COMPLIANCE == "compliance"


class TestGetMetricRequirements:
    """Tests for get_metric_requirements helper."""

    def test_get_requirements_basic_metric(self):
        """Test requirements for basic metric."""
        metric = ConcreteMetric()
        reqs = get_metric_requirements(metric)

        assert reqs == {
            "requires_source_data": False,
            "requires_other_personas": False,
            "requires_evidence_report": False,
        }

    def test_get_requirements_source_metric(self):
        """Test requirements for source-requiring metric."""
        metric = SourceRequiringMetric()
        reqs = get_metric_requirements(metric)

        assert reqs == {
            "requires_source_data": True,
            "requires_other_personas": False,
            "requires_evidence_report": False,
        }


class TestBuiltinMetricsInterface:
    """Tests that builtin metrics implement the interface correctly."""

    def test_completeness_metric_interface(self):
        """Test CompletenessMetric implements interface."""
        from persona.core.quality.metrics.completeness import CompletenessMetric

        metric = CompletenessMetric()
        assert metric.name == "completeness"
        assert metric.requires_source_data is False
        assert metric.requires_other_personas is False
        assert metric.requires_evidence_report is False

    def test_consistency_metric_interface(self):
        """Test ConsistencyMetric implements interface."""
        from persona.core.quality.metrics.consistency import ConsistencyMetric

        metric = ConsistencyMetric()
        assert metric.name == "consistency"
        assert metric.requires_source_data is False
        assert metric.requires_other_personas is False
        assert metric.requires_evidence_report is False

    def test_realism_metric_interface(self):
        """Test RealismMetric implements interface."""
        from persona.core.quality.metrics.realism import RealismMetric

        metric = RealismMetric()
        assert metric.name == "realism"
        assert metric.requires_source_data is False
        assert metric.requires_other_personas is False
        assert metric.requires_evidence_report is False

    def test_evidence_metric_interface(self):
        """Test EvidenceStrengthMetric implements interface."""
        from persona.core.quality.metrics.evidence import EvidenceStrengthMetric

        metric = EvidenceStrengthMetric()
        assert metric.name == "evidence_strength"
        assert metric.requires_source_data is False
        assert metric.requires_other_personas is False
        assert metric.requires_evidence_report is True

    def test_distinctiveness_metric_interface(self):
        """Test DistinctivenessMetric implements interface."""
        from persona.core.quality.metrics.distinctiveness import DistinctivenessMetric

        metric = DistinctivenessMetric()
        assert metric.name == "distinctiveness"
        assert metric.requires_source_data is False
        assert metric.requires_other_personas is True
        assert metric.requires_evidence_report is False
