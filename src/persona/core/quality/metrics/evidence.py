"""
Evidence strength metric for persona quality scoring.

Evaluates how well persona attributes link to source data,
integrating with the existing EvidenceLinker when available.
"""

from typing import TYPE_CHECKING, Any

from persona.core.generation.parser import Persona
from persona.core.quality.base import QualityMetric
from persona.core.quality.models import DimensionScore

if TYPE_CHECKING:
    from persona.core.evidence.linker import EvidenceReport


class EvidenceStrengthMetric(QualityMetric):
    """
    Evaluate how well persona attributes link to source data.

    Scoring breakdown:
    - Coverage: % of attributes with evidence (50%)
    - Strength distribution: quality of evidence (30%)
    - Source diversity: multiple sources used (20%)
    """

    @property
    def name(self) -> str:
        """Return the metric name."""
        return "evidence_strength"

    @property
    def description(self) -> str:
        """Return metric description."""
        return "Evaluate link to source data"

    @property
    def requires_source_data(self) -> bool:
        """This metric does not require source data directly."""
        return False

    @property
    def requires_other_personas(self) -> bool:
        """This metric does not require other personas."""
        return False

    @property
    def requires_evidence_report(self) -> bool:
        """This metric requires an evidence report for full evaluation."""
        return True

    def evaluate(
        self,
        persona: Persona,
        source_data: str | None = None,
        other_personas: list[Persona] | None = None,
        evidence_report: "EvidenceReport | None" = None,
    ) -> DimensionScore:
        """
        Calculate evidence strength score for a persona.

        Args:
            persona: The persona to evaluate.
            evidence_report: Optional evidence linking report.

        Returns:
            DimensionScore with evidence strength assessment.
        """
        issues: list[str] = []
        details: dict[str, Any] = {}

        if evidence_report:
            # Use actual evidence data
            coverage_score = self._calculate_coverage(evidence_report, issues, details)
            strength_score = self._calculate_strength_distribution(
                evidence_report, issues, details
            )
            diversity_score = self._calculate_source_diversity(evidence_report, details)
        else:
            # No evidence available - provide structural baseline
            coverage_score = self._estimate_coverage_potential(persona, details)
            strength_score = 50.0  # Unknown
            diversity_score = 50.0  # Unknown
            issues.append("No evidence linking data available")

        overall = coverage_score * 0.50 + strength_score * 0.30 + diversity_score * 0.20

        return DimensionScore(
            dimension="evidence_strength",
            score=overall,
            weight=self.config.weights["evidence_strength"],
            issues=issues,
            details=details,
        )

    def _calculate_coverage(
        self,
        report: "EvidenceReport",
        issues: list[str],
        details: dict[str, Any],
    ) -> float:
        """Calculate percentage of attributes with evidence."""
        coverage = report.coverage_percentage
        details["evidence_coverage"] = coverage

        if coverage < self.config.min_evidence_coverage * 100:
            issues.append(
                f"Low evidence coverage: {coverage:.1f}% "
                f"(minimum: {self.config.min_evidence_coverage * 100:.0f}%)"
            )

        return coverage

    def _calculate_strength_distribution(
        self,
        report: "EvidenceReport",
        issues: list[str],
        details: dict[str, Any],
    ) -> float:
        """Score based on evidence strength levels."""
        # Import here to avoid circular dependency
        from persona.core.evidence.linker import EvidenceStrength

        if not report.attributes:
            return 50.0

        strength_weights = {
            EvidenceStrength.STRONG: 100,
            EvidenceStrength.MODERATE: 75,
            EvidenceStrength.WEAK: 50,
            EvidenceStrength.INFERRED: 25,
        }

        total_score = 0
        for attr in report.attributes:
            total_score += strength_weights.get(attr.strength, 25)

        avg_strength = total_score / len(report.attributes)

        details["strong_evidence_count"] = report.strong_count
        details["weak_evidence_count"] = report.weak_count
        details["average_strength_score"] = round(avg_strength, 2)

        if report.weak_count > report.strong_count:
            issues.append(
                f"More weak evidence ({report.weak_count}) "
                f"than strong ({report.strong_count})"
            )

        return avg_strength

    def _calculate_source_diversity(
        self,
        report: "EvidenceReport",
        details: dict[str, Any],
    ) -> float:
        """Score based on diversity of sources used."""
        source_count = len(report.source_files)
        details["source_file_count"] = source_count

        # 1 source = 60%, 2 = 80%, 3+ = 100%
        if source_count >= 3:
            return 100.0
        elif source_count == 2:
            return 80.0
        elif source_count == 1:
            return 60.0
        else:
            return 40.0

    def _estimate_coverage_potential(
        self,
        persona: Persona,
        details: dict[str, Any],
    ) -> float:
        """Estimate potential evidence coverage from persona structure."""
        # Based on presence of quotes (direct evidence markers)
        quotes_count = len(persona.quotes or [])

        if quotes_count >= 3:
            details["has_quotes"] = True
            details["quotes_count"] = quotes_count
            return 70.0
        elif quotes_count >= 1:
            details["has_quotes"] = True
            details["quotes_count"] = quotes_count
            return 55.0
        else:
            details["has_quotes"] = False
            details["quotes_count"] = 0
            return 40.0
