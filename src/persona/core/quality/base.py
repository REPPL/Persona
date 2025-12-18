"""
Abstract base class for quality metrics.

This module provides the QualityMetric abstract base class that all
quality metrics must implement, enabling a pluggable metrics architecture.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from persona.core.generation.parser import Persona
from persona.core.quality.config import QualityConfig
from persona.core.quality.models import DimensionScore

if TYPE_CHECKING:
    from persona.core.evidence.linker import EvidenceReport


class QualityMetric(ABC):
    """
    Abstract base class for persona quality metrics.

    All quality metrics must implement this interface to be registered
    with the MetricRegistry and used by QualityScorer.

    Example:
        class MyCustomMetric(QualityMetric):
            @property
            def name(self) -> str:
                return "custom"

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
                # Implementation here
                return DimensionScore(
                    dimension=self.name,
                    score=100.0,
                    weight=self.weight,
                    issues=[],
                    details={},
                )
    """

    def __init__(self, config: QualityConfig | None = None) -> None:
        """
        Initialise the quality metric.

        Args:
            config: Quality configuration with weights and thresholds.
        """
        self.config = config or QualityConfig()

    @property
    @abstractmethod
    def name(self) -> str:
        """
        Return the unique name of this metric.

        This name is used as the dimension name in DimensionScore
        and as the key in QualityScore.dimensions.

        Returns:
            Unique metric name (e.g., 'completeness', 'rouge_l').
        """
        ...

    @property
    def description(self) -> str:
        """
        Return a human-readable description of this metric.

        Returns:
            Description of what this metric evaluates.
        """
        return f"{self.name.replace('_', ' ').title()} metric"

    @property
    def weight(self) -> float:
        """
        Return the weight for this metric from config.

        Returns:
            Weight factor (0-1) for overall score calculation.
        """
        return self.config.weights.get(self.name, 0.0)

    @property
    @abstractmethod
    def requires_source_data(self) -> bool:
        """
        Indicate whether this metric requires source data.

        Returns:
            True if source_data parameter is required.
        """
        ...

    @property
    @abstractmethod
    def requires_other_personas(self) -> bool:
        """
        Indicate whether this metric requires other personas for comparison.

        Returns:
            True if other_personas parameter is required.
        """
        ...

    @property
    @abstractmethod
    def requires_evidence_report(self) -> bool:
        """
        Indicate whether this metric requires an evidence report.

        Returns:
            True if evidence_report parameter is required.
        """
        ...

    @abstractmethod
    def evaluate(
        self,
        persona: Persona,
        source_data: str | None = None,
        other_personas: list[Persona] | None = None,
        evidence_report: "EvidenceReport | None" = None,
    ) -> DimensionScore:
        """
        Evaluate the quality of a persona.

        Args:
            persona: The persona to evaluate.
            source_data: Optional source data text for comparison.
            other_personas: Optional list of other personas for comparison.
            evidence_report: Optional evidence linking report.

        Returns:
            DimensionScore with evaluation results.
        """
        ...

    def __repr__(self) -> str:
        """Return string representation."""
        return f"<{self.__class__.__name__}(name='{self.name}')>"


class MetricCategory:
    """Categories for organising quality metrics."""

    STRUCTURAL = "structural"  # Completeness, consistency
    SEMANTIC = "semantic"  # Realism, coherence
    COMPARATIVE = "comparative"  # Distinctiveness
    EVIDENTIAL = "evidential"  # Evidence strength, faithfulness
    ACADEMIC = "academic"  # ROUGE-L, BERTScore, G-eval
    COMPLIANCE = "compliance"  # Bias, fidelity


def get_metric_requirements(metric: QualityMetric) -> dict[str, bool]:
    """
    Get the data requirements for a metric.

    Args:
        metric: The metric to check.

    Returns:
        Dict with requirement flags.
    """
    return {
        "requires_source_data": metric.requires_source_data,
        "requires_other_personas": metric.requires_other_personas,
        "requires_evidence_report": metric.requires_evidence_report,
    }
