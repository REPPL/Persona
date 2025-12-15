"""
G-eval (LLM-as-judge) quality metric implementation.

This module provides the GevalMetric class that uses an LLM to evaluate
persona quality across multiple dimensions like coherence, relevance,
fluency, and consistency.
"""

from typing import TYPE_CHECKING, Any

from persona.core.evaluation.criteria import EvaluationCriteria
from persona.core.evaluation.judge import PersonaJudge
from persona.core.generation.parser import Persona
from persona.core.quality.base import MetricCategory, QualityMetric
from persona.core.quality.config import QualityConfig
from persona.core.quality.models import DimensionScore

if TYPE_CHECKING:
    from persona.core.evidence.linker import EvidenceReport


class GevalMetric(QualityMetric):
    """
    G-eval (LLM-as-judge) quality metric.

    G-eval uses a language model to evaluate persona quality across multiple
    dimensions. Unlike automated metrics (ROUGE, BERTScore), G-eval provides
    nuanced human-like evaluation with detailed reasoning.

    Evaluation dimensions:
    - Coherence: Internal logical consistency
    - Relevance: Alignment with source data and context
    - Fluency: Naturalness and readability
    - Consistency: Freedom from contradictions

    Example:
        metric = GevalMetric(provider="ollama", model="qwen2.5:72b")
        score = metric.evaluate(
            persona=my_persona,
            source_data=research_text,
        )
        print(f"G-eval overall: {score.details['overall']:.1f}/100")
    """

    def __init__(
        self,
        config: QualityConfig | None = None,
        provider: str = "ollama",
        model: str | None = None,
        temperature: float = 0.0,
    ) -> None:
        """
        Initialise the G-eval metric.

        Args:
            config: Quality configuration with weights and thresholds.
            provider: LLM provider to use (default: "ollama").
            model: Model name to use (default: provider's default).
            temperature: Sampling temperature (default: 0.0 for consistency).
        """
        super().__init__(config)
        self.judge = PersonaJudge(
            provider=provider,
            model=model,
            temperature=temperature,
        )
        self.provider = provider
        self.model_name = model or self.judge.model

    @property
    def name(self) -> str:
        """Return the unique name of this metric."""
        return "geval"

    @property
    def description(self) -> str:
        """Return a human-readable description."""
        return "G-eval LLM-based quality assessment across multiple dimensions"

    @property
    def requires_source_data(self) -> bool:
        """Indicate that this metric can use source data but doesn't require it."""
        # G-eval can work with or without source data
        # With source: evaluates faithfulness/relevance
        # Without source: evaluates coherence/fluency only
        return False

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
        Evaluate persona using G-eval.

        Args:
            persona: The persona to evaluate.
            source_data: Optional source data for evaluating relevance/faithfulness.
            other_personas: Not used by this metric.
            evidence_report: Not used by this metric.

        Returns:
            DimensionScore with G-eval results across multiple dimensions.

        Raises:
            RuntimeError: If LLM evaluation fails.
        """
        # Convert persona to dict for PersonaJudge
        persona_dict = self._persona_to_dict(persona)

        # Add source data to persona dict if provided
        if source_data:
            persona_dict["_source_data"] = source_data

        # Select evaluation criteria based on whether we have source data
        if source_data:
            # With source: evaluate all dimensions including relevance
            criteria = [
                EvaluationCriteria.COHERENCE,
                EvaluationCriteria.REALISM,
                EvaluationCriteria.USEFULNESS,
            ]
        else:
            # Without source: evaluate intrinsic qualities only
            criteria = [
                EvaluationCriteria.COHERENCE,
                EvaluationCriteria.REALISM,
            ]

        # Evaluate using PersonaJudge
        try:
            result = self.judge.evaluate(persona_dict, criteria=criteria)
        except Exception as e:
            raise RuntimeError(f"G-eval evaluation failed: {e}") from e

        # Extract individual dimension scores
        coherence = result.get_score(EvaluationCriteria.COHERENCE) or 0.0
        realism = result.get_score(EvaluationCriteria.REALISM) or 0.0
        usefulness = result.get_score(EvaluationCriteria.USEFULNESS) or 0.0

        # Map to G-eval dimensions (scale 0-1 to 0-100)
        coherence_score = coherence * 100
        relevance_score = usefulness * 100 if source_data else 0.0
        fluency_score = realism * 100  # Realism includes fluency/naturalness
        consistency_score = coherence_score  # Coherence includes consistency

        # Overall is the average
        overall_score = result.overall_score * 100

        # Extract reasoning
        reasoning = {}
        for criterion in criteria:
            criterion_score = result.scores.get(criterion)
            if criterion_score:
                reasoning[criterion.value] = criterion_score.reasoning

        # Detect issues
        issues = []
        if coherence_score < 50:
            issues.append("Low coherence: persona lacks internal logical consistency")
        if source_data and relevance_score < 50:
            issues.append("Low relevance: persona poorly aligned with source data")
        if fluency_score < 50:
            issues.append("Low fluency: persona text is unnatural or poorly written")
        if overall_score < 60:
            issues.append("Low overall G-eval score: persona needs significant improvement")

        return DimensionScore(
            dimension=self.name,
            score=overall_score,
            weight=self.weight,
            issues=issues,
            details={
                "coherence": coherence_score,
                "relevance": relevance_score,
                "fluency": fluency_score,
                "consistency": consistency_score,
                "overall": overall_score,
                "model": self.model_name,
                "provider": self.provider,
                "reasoning": reasoning,
                "has_source_data": source_data is not None,
            },
        )

    def _persona_to_dict(self, persona: Persona) -> dict[str, Any]:
        """
        Convert persona to dictionary for PersonaJudge.

        Args:
            persona: The persona to convert.

        Returns:
            Dictionary representation of the persona.
        """
        result = {
            "id": persona.id,
            "name": persona.name,
        }

        # Add demographics
        if persona.demographics:
            result["demographics"] = persona.demographics

        # Add goals
        if persona.goals:
            result["goals"] = persona.goals

        # Add pain_points
        if persona.pain_points:
            result["pain_points"] = persona.pain_points

        # Add behaviours
        if persona.behaviours:
            result["behaviours"] = persona.behaviours

        # Add quotes
        if persona.quotes:
            result["quotes"] = persona.quotes

        # Add additional fields
        if persona.additional:
            result.update(persona.additional)

        return result
