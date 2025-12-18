"""
ROUGE-L quality metric implementation.

This module provides the RougeLMetric class that calculates ROUGE-L
scores for evaluating persona text quality against source data.
"""

from typing import TYPE_CHECKING

from persona.core.generation.parser import Persona
from persona.core.quality.base import QualityMetric
from persona.core.quality.models import DimensionScore

if TYPE_CHECKING:
    from persona.core.evidence.linker import EvidenceReport


class RougeLMetric(QualityMetric):
    """
    ROUGE-L (Recall-Oriented Understudy for Gisting Evaluation - Longest) metric.

    ROUGE-L measures the longest common subsequence (LCS) between the generated
    persona text and the source data. It evaluates how well the persona content
    captures information from the source while allowing for paraphrasing.

    This metric requires source data and returns scores for:
    - Precision: How much of the persona text comes from the source
    - Recall: How much of the source is covered by the persona
    - F-measure: Harmonic mean of precision and recall

    Example:
        metric = RougeLMetric()
        score = metric.evaluate(
            persona=my_persona,
            source_data=research_text,
        )
        print(f"ROUGE-L F-score: {score.details['fmeasure']:.3f}")
    """

    @property
    def name(self) -> str:
        """Return the unique name of this metric."""
        return "rouge_l"

    @property
    def description(self) -> str:
        """Return a human-readable description."""
        return "ROUGE-L longest common subsequence similarity"

    @property
    def requires_source_data(self) -> bool:
        """Indicate that this metric requires source data."""
        return True

    @property
    def requires_other_personas(self) -> bool:
        """Indicate that this metric does not require other personas."""
        return False

    @property
    def requires_evidence_report(self) -> bool:
        """Indicate that this metric does not require evidence report."""
        return False

    def evaluate(
        self,
        persona: Persona,
        source_data: str | None = None,
        other_personas: list[Persona] | None = None,
        evidence_report: "EvidenceReport | None" = None,
    ) -> DimensionScore:
        """
        Evaluate persona using ROUGE-L.

        Args:
            persona: The persona to evaluate.
            source_data: Source data text for comparison (required).
            other_personas: Not used by this metric.
            evidence_report: Not used by this metric.

        Returns:
            DimensionScore with ROUGE-L results.

        Raises:
            ValueError: If source_data is not provided.
            ImportError: If rouge-score library is not installed.
        """
        if not source_data:
            raise ValueError("ROUGE-L metric requires source_data")

        try:
            from rouge_score import rouge_scorer
        except ImportError as e:
            raise ImportError(
                "rouge-score library is required for ROUGE-L metric. "
                "Install with: pip install 'persona[academic]'"
            ) from e

        # Convert persona to text
        persona_text = self._persona_to_text(persona)

        # Initialise ROUGE scorer
        scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)

        # Calculate ROUGE-L scores
        scores = scorer.score(source_data, persona_text)
        rouge_l = scores["rougeL"]

        # Convert to 0-100 scale (F-measure is the primary metric)
        score = rouge_l.fmeasure * 100

        # Detect issues
        issues = []
        if rouge_l.precision < 0.3:
            issues.append(
                "Low precision: persona contains content not well-grounded in source"
            )
        if rouge_l.recall < 0.3:
            issues.append(
                "Low recall: persona does not capture much information from source"
            )
        if rouge_l.fmeasure < 0.25:
            issues.append(
                "Low overall ROUGE-L: weak alignment between persona and source data"
            )

        return DimensionScore(
            dimension=self.name,
            score=score,
            weight=self.weight,
            issues=issues,
            details={
                "precision": rouge_l.precision,
                "recall": rouge_l.recall,
                "fmeasure": rouge_l.fmeasure,
                "persona_length": len(persona_text),
                "source_length": len(source_data),
            },
        )

    def _persona_to_text(self, persona: Persona) -> str:
        """
        Convert persona to text for ROUGE calculation.

        Args:
            persona: The persona to convert.

        Returns:
            Text representation of the persona.
        """
        parts = []

        # Add name
        if persona.name:
            parts.append(persona.name)

        # Add demographics
        if persona.demographics:
            for key, value in persona.demographics.items():
                if value:
                    parts.append(f"{key}: {value}")

        # Add goals
        if persona.goals:
            parts.extend(persona.goals)

        # Add pain points
        if persona.pain_points:
            parts.extend(persona.pain_points)

        # Add behaviours
        if persona.behaviours:
            parts.extend(persona.behaviours)

        # Add quotes
        if persona.quotes:
            parts.extend(persona.quotes)

        # Add additional fields
        if persona.additional:
            for key, value in persona.additional.items():
                if isinstance(value, list):
                    parts.extend(str(v) for v in value)
                elif isinstance(value, dict):
                    for k, v in value.items():
                        if v:
                            parts.append(f"{k}: {v}")
                else:
                    parts.append(str(value))

        return " ".join(str(p) for p in parts if p)
