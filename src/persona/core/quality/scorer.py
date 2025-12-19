"""
Quality scorer for personas.

This module provides the main QualityScorer class that orchestrates
all quality metrics and produces comprehensive quality assessments.
"""

from collections.abc import Callable
from datetime import datetime
from typing import TYPE_CHECKING

from persona.core.generation.parser import Persona
from persona.core.quality.config import QualityConfig
from persona.core.quality.models import (
    BatchQualityResult,
    DimensionScore,
    QualityLevel,
    QualityScore,
)
from persona.core.quality.registry import MetricRegistry, get_registry

if TYPE_CHECKING:
    from persona.core.evidence.linker import EvidenceReport


class QualityScorer:
    """
    Comprehensive quality scorer for personas.

    Evaluates personas across five dimensions:
    - Completeness: Field population and depth
    - Consistency: Internal coherence
    - Evidence Strength: Link to source data
    - Distinctiveness: Uniqueness vs other personas
    - Realism: Plausibility as a real person

    Example:
        scorer = QualityScorer()
        score = scorer.score(persona)
        print(f"Overall: {score.overall_score}/100")
        print(f"Level: {score.level.value}")

        # Batch scoring with cross-comparison
        result = scorer.score_batch(personas)
        print(f"Average: {result.average_score}/100")

        # Use custom registry with additional metrics
        registry = MetricRegistry()
        registry.register("custom", CustomMetric, "Custom metric")
        scorer = QualityScorer(registry=registry)
    """

    def __init__(
        self,
        config: QualityConfig | None = None,
        registry: MetricRegistry | None = None,
        progress_callback: Callable[[str], None] | None = None,
    ) -> None:
        """
        Initialise the quality scorer.

        Args:
            config: Quality configuration. Defaults to standard config.
            registry: Metric registry. Defaults to global registry.
            progress_callback: Optional callback for progress updates.
        """
        self.config = config or QualityConfig()
        self.registry = registry or get_registry()
        self._progress = progress_callback or (lambda x: None)

        # Validate configuration
        errors = self.config.validate()
        if errors:
            raise ValueError(f"Invalid configuration: {', '.join(errors)}")

        # Initialise metrics from registry
        self._metrics = self.registry.get_builtin_metrics(self.config)

        # Create named accessors for backward compatibility
        self._completeness = self._metrics.get("completeness")
        self._consistency = self._metrics.get("consistency")
        self._evidence = self._metrics.get("evidence_strength")
        self._distinctiveness = self._metrics.get("distinctiveness")
        self._realism = self._metrics.get("realism")

    def score(
        self,
        persona: Persona,
        evidence_report: "EvidenceReport | None" = None,
        other_personas: list[Persona] | None = None,
    ) -> QualityScore:
        """
        Calculate comprehensive quality score for a single persona.

        Args:
            persona: Persona to evaluate.
            evidence_report: Optional evidence linking report.
            other_personas: Other personas for distinctiveness comparison.

        Returns:
            QualityScore with overall and dimension scores.
        """
        self._progress(f"Scoring persona: {persona.name}")

        dimensions: dict[str, DimensionScore] = {}

        # Completeness
        self._progress("  Evaluating completeness...")
        dimensions["completeness"] = self._completeness.evaluate(persona)

        # Consistency
        self._progress("  Evaluating consistency...")
        dimensions["consistency"] = self._consistency.evaluate(persona)

        # Evidence Strength
        self._progress("  Evaluating evidence strength...")
        dimensions["evidence_strength"] = self._evidence.evaluate(
            persona, evidence_report
        )

        # Distinctiveness
        self._progress("  Evaluating distinctiveness...")
        dimensions["distinctiveness"] = self._distinctiveness.evaluate(
            persona, other_personas
        )

        # Realism
        self._progress("  Evaluating realism...")
        dimensions["realism"] = self._realism.evaluate(persona)

        # Calculate overall score (weighted sum)
        overall = sum(d.weighted_score for d in dimensions.values())

        # Determine quality level
        level = self._determine_level(overall)

        return QualityScore(
            persona_id=persona.id,
            persona_name=persona.name,
            overall_score=overall,
            level=level,
            dimensions=dimensions,
            generated_at=datetime.now().isoformat(),
        )

    def score_batch(
        self,
        personas: list[Persona],
        evidence_reports: dict[str, "EvidenceReport"] | None = None,
    ) -> BatchQualityResult:
        """
        Score multiple personas with cross-comparison.

        Args:
            personas: List of personas to evaluate.
            evidence_reports: Optional dict mapping persona_id to evidence report.

        Returns:
            BatchQualityResult with individual and aggregate scores.
        """
        self._progress(f"Scoring {len(personas)} personas...")

        evidence_reports = evidence_reports or {}
        scores: list[QualityScore] = []

        for persona in personas:
            other_personas = [p for p in personas if p.id != persona.id]
            evidence = evidence_reports.get(persona.id)

            score = self.score(persona, evidence, other_personas)
            scores.append(score)

        # Calculate averages
        if scores:
            average_score = sum(s.overall_score for s in scores) / len(scores)
        else:
            average_score = 0.0

        # Average by dimension
        dimension_names = [
            "completeness",
            "consistency",
            "evidence_strength",
            "distinctiveness",
            "realism",
        ]
        average_by_dimension: dict[str, float] = {}
        for dim in dimension_names:
            dim_scores = [
                s.dimensions[dim].score for s in scores if dim in s.dimensions
            ]
            average_by_dimension[dim] = (
                sum(dim_scores) / len(dim_scores) if dim_scores else 0
            )

        # Build distinctiveness matrix
        matrix = self._build_similarity_matrix(personas)

        return BatchQualityResult(
            scores=scores,
            average_score=average_score,
            average_by_dimension=average_by_dimension,
            distinctiveness_matrix=matrix,
            generated_at=datetime.now().isoformat(),
        )

    def _determine_level(self, score: float) -> QualityLevel:
        """Determine quality level from score."""
        if score >= self.config.excellent_threshold:
            return QualityLevel.EXCELLENT
        elif score >= self.config.good_threshold:
            return QualityLevel.GOOD
        elif score >= self.config.acceptable_threshold:
            return QualityLevel.ACCEPTABLE
        elif score >= self.config.poor_threshold:
            return QualityLevel.POOR
        else:
            return QualityLevel.FAILING

    def _build_similarity_matrix(self, personas: list[Persona]) -> list[list[float]]:
        """Build NxN similarity matrix for personas."""
        n = len(personas)
        matrix: list[list[float]] = [[0.0] * n for _ in range(n)]

        if n < 2:
            return matrix

        try:
            from persona.core.comparison.comparator import PersonaComparator

            comparator = PersonaComparator()

            for i in range(n):
                for j in range(n):
                    if i == j:
                        matrix[i][j] = 100.0
                    elif j > i:
                        result = comparator.compare(personas[i], personas[j])
                        matrix[i][j] = result.similarity.overall
                        matrix[j][i] = result.similarity.overall
        except Exception:
            # If comparator fails, use simple estimation
            for i in range(n):
                matrix[i][i] = 100.0

        return matrix

    def get_dimension_weights(self) -> dict[str, float]:
        """Get current dimension weights."""
        return self.config.weights.copy()

    def get_thresholds(self) -> dict[str, int]:
        """Get current quality level thresholds."""
        return {
            "excellent": self.config.excellent_threshold,
            "good": self.config.good_threshold,
            "acceptable": self.config.acceptable_threshold,
            "poor": self.config.poor_threshold,
        }
