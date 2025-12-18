"""
BERTScore quality metric implementation.

This module provides the BertScoreMetric class that calculates BERTScore
for evaluating semantic similarity between persona and source data.
"""

from typing import TYPE_CHECKING

from persona.core.generation.parser import Persona
from persona.core.quality.base import QualityMetric
from persona.core.quality.config import QualityConfig
from persona.core.quality.models import DimensionScore

if TYPE_CHECKING:
    from persona.core.evidence.linker import EvidenceReport


class BertScoreMetric(QualityMetric):
    """
    BERTScore semantic similarity metric.

    BERTScore uses contextual embeddings from BERT-like models to evaluate
    semantic similarity between generated persona text and source data.
    Unlike ROUGE-L which focuses on surface-level overlap, BERTScore captures
    meaning similarity.

    This metric requires source data and returns:
    - Precision: Semantic alignment of persona with source
    - Recall: Coverage of source semantics in persona
    - F1: Harmonic mean of precision and recall

    Example:
        metric = BertScoreMetric(model="microsoft/deberta-xlarge-mnli")
        score = metric.evaluate(
            persona=my_persona,
            source_data=research_text,
        )
        print(f"BERTScore F1: {score.details['f1']:.3f}")
    """

    def __init__(
        self,
        config: QualityConfig | None = None,
        model: str = "microsoft/deberta-xlarge-mnli",
        device: str | None = None,
    ) -> None:
        """
        Initialise the BERTScore metric.

        Args:
            config: Quality configuration with weights and thresholds.
            model: Model to use for BERTScore (default: deberta-xlarge-mnli).
            device: Device to run model on (default: auto-detect).
        """
        super().__init__(config)
        self.model_name = model
        self.device = device

    @property
    def name(self) -> str:
        """Return the unique name of this metric."""
        return "bertscore"

    @property
    def description(self) -> str:
        """Return a human-readable description."""
        return "BERTScore semantic similarity using contextual embeddings"

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
        Evaluate persona using BERTScore.

        Args:
            persona: The persona to evaluate.
            source_data: Source data text for comparison (required).
            other_personas: Not used by this metric.
            evidence_report: Not used by this metric.

        Returns:
            DimensionScore with BERTScore results.

        Raises:
            ValueError: If source_data is not provided.
            ImportError: If bert-score library is not installed.
        """
        if not source_data:
            raise ValueError("BERTScore metric requires source_data")

        try:
            from bert_score import score as bert_score
        except ImportError as e:
            raise ImportError(
                "bert-score library is required for BERTScore metric. "
                "Install with: pip install 'persona[academic]'"
            ) from e

        # Convert persona to text
        persona_text = self._persona_to_text(persona)

        # Calculate BERTScore
        # Returns tensors of shape (batch_size,) for P, R, F1
        P, R, F1 = bert_score(
            cands=[persona_text],
            refs=[source_data],
            model_type=self.model_name,
            device=self.device,
            verbose=False,
        )

        # Extract scalar values
        precision = float(P[0].item())
        recall = float(R[0].item())
        f1 = float(F1[0].item())

        # Convert to 0-100 scale (F1 is the primary metric)
        score = f1 * 100

        # Detect issues
        issues = []
        if precision < 0.5:
            issues.append(
                "Low BERTScore precision: persona semantics diverge from source"
            )
        if recall < 0.5:
            issues.append(
                "Low BERTScore recall: persona does not capture source semantics well"
            )
        if f1 < 0.45:
            issues.append(
                "Low BERTScore F1: weak semantic alignment between persona and source"
            )

        return DimensionScore(
            dimension=self.name,
            score=score,
            weight=self.weight,
            issues=issues,
            details={
                "precision": precision,
                "recall": recall,
                "f1": f1,
                "model": self.model_name,
                "persona_length": len(persona_text),
                "source_length": len(source_data),
            },
        )

    def _persona_to_text(self, persona: Persona) -> str:
        """
        Convert persona to text for BERTScore calculation.

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
