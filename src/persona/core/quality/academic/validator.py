"""
Academic validation orchestrator.

This module provides the AcademicValidator class that combines multiple
academic validation metrics (ROUGE-L, BERTScore, GPT similarity, G-eval)
into a unified validation report.
"""

from typing import Any

from persona.core.generation.parser import Persona
from persona.core.quality.academic.bertscore import BertScoreMetric
from persona.core.quality.academic.geval import GevalMetric
from persona.core.quality.academic.gpt_similarity import GptSimilarityMetric
from persona.core.quality.academic.models import (
    AcademicValidationReport,
    BatchAcademicValidationReport,
    BertScore,
    GevalScore,
    GptSimilarityScore,
    RougeScore,
)
from persona.core.quality.academic.rouge import RougeLMetric
from persona.core.quality.config import QualityConfig


class AcademicValidator:
    """
    Orchestrator for academic validation metrics.

    Combines ROUGE-L, BERTScore, GPT embedding similarity, and G-eval
    into a unified validation report. Allows selective execution of metrics
    to manage computational cost and API usage.

    Example:
        validator = AcademicValidator()
        report = validator.validate(
            persona=my_persona,
            source_data=research_text,
            metrics=["rouge_l", "bertscore"],  # Selective execution
        )
        print(f"Overall score: {report.overall_score:.2f}")
    """

    def __init__(
        self,
        config: QualityConfig | None = None,
        # ROUGE-L options
        # BERTScore options
        bertscore_model: str = "microsoft/deberta-xlarge-mnli",
        bertscore_device: str | None = None,
        # GPT similarity options
        embedding_provider: str = "openai",
        embedding_model: str | None = None,
        # G-eval options
        geval_provider: str = "ollama",
        geval_model: str | None = None,
        geval_temperature: float = 0.0,
    ) -> None:
        """
        Initialise the academic validator.

        Args:
            config: Quality configuration with weights and thresholds.
            bertscore_model: Model for BERTScore.
            bertscore_device: Device for BERTScore.
            embedding_provider: Provider for GPT similarity.
            embedding_model: Model for GPT similarity.
            geval_provider: LLM provider for G-eval.
            geval_model: Model for G-eval.
            geval_temperature: Temperature for G-eval.
        """
        self.config = config or QualityConfig()

        # Initialise metrics
        self.rouge_metric = RougeLMetric(config=self.config)
        self.bertscore_metric = BertScoreMetric(
            config=self.config,
            model=bertscore_model,
            device=bertscore_device,
        )
        self.gpt_similarity_metric = GptSimilarityMetric(
            config=self.config,
            provider=embedding_provider,
            model=embedding_model,
        )
        self.geval_metric = GevalMetric(
            config=self.config,
            provider=geval_provider,
            model=geval_model,
            temperature=geval_temperature,
        )

        # Store configuration
        self.bertscore_model = bertscore_model
        self.embedding_provider = embedding_provider
        self.embedding_model = embedding_model or self.gpt_similarity_metric.model
        self.geval_provider = geval_provider
        self.geval_model = geval_model or self.geval_metric.model_name

    def validate(
        self,
        persona: Persona,
        source_data: str | None = None,
        metrics: list[str] | None = None,
    ) -> AcademicValidationReport:
        """
        Validate a persona using academic metrics.

        Args:
            persona: The persona to validate.
            source_data: Source data for comparison (required for most metrics).
            metrics: List of metrics to compute. Options: "rouge_l", "bertscore",
                    "gpt_similarity", "geval". If None, computes all available.

        Returns:
            AcademicValidationReport with results from requested metrics.

        Raises:
            ValueError: If required source_data is missing for selected metrics.
        """
        # Default to all metrics if not specified
        if metrics is None:
            metrics = ["rouge_l", "bertscore", "gpt_similarity", "geval"]

        # Validate requirements
        requires_source = {"rouge_l", "bertscore", "gpt_similarity"}
        selected_requiring_source = requires_source & set(metrics)
        if selected_requiring_source and not source_data:
            raise ValueError(f"Metrics {selected_requiring_source} require source_data")

        # Compute requested metrics
        rouge_l = None
        bertscore = None
        gpt_similarity = None
        geval = None

        if "rouge_l" in metrics:
            rouge_l = self._compute_rouge_l(persona, source_data)

        if "bertscore" in metrics:
            bertscore = self._compute_bertscore(persona, source_data)

        if "gpt_similarity" in metrics:
            gpt_similarity = self._compute_gpt_similarity(persona, source_data)

        if "geval" in metrics:
            geval = self._compute_geval(persona, source_data)

        # Create report
        return AcademicValidationReport(
            persona_id=persona.id,
            persona_name=persona.name,
            rouge_l=rouge_l,
            bertscore=bertscore,
            gpt_similarity=gpt_similarity,
            geval=geval,
            metrics_used=metrics,
        )

    def validate_batch(
        self,
        personas: list[Persona],
        source_data: str | None = None,
        metrics: list[str] | None = None,
    ) -> BatchAcademicValidationReport:
        """
        Validate multiple personas using academic metrics.

        Args:
            personas: List of personas to validate.
            source_data: Source data for comparison.
            metrics: List of metrics to compute.

        Returns:
            BatchAcademicValidationReport with individual and aggregate results.

        Raises:
            ValueError: If personas list is empty or source_data requirements not met.
        """
        if not personas:
            raise ValueError("At least one persona is required")

        # Validate each persona
        reports = [self.validate(persona, source_data, metrics) for persona in personas]

        # Create batch report (automatically calculates averages)
        return BatchAcademicValidationReport(reports=reports)

    def _compute_rouge_l(
        self, persona: Persona, source_data: str | None
    ) -> RougeScore | None:
        """Compute ROUGE-L score."""
        if not source_data:
            return None

        try:
            result = self.rouge_metric.evaluate(persona, source_data=source_data)
            return RougeScore(
                precision=result.details["precision"],
                recall=result.details["recall"],
                fmeasure=result.details["fmeasure"],
            )
        except ImportError:
            # Library not installed, skip this metric
            return None

    def _compute_bertscore(
        self, persona: Persona, source_data: str | None
    ) -> BertScore | None:
        """Compute BERTScore."""
        if not source_data:
            return None

        try:
            result = self.bertscore_metric.evaluate(persona, source_data=source_data)
            return BertScore(
                precision=result.details["precision"],
                recall=result.details["recall"],
                f1=result.details["f1"],
                model=self.bertscore_model,
            )
        except ImportError:
            # Library not installed, skip this metric
            return None

    def _compute_gpt_similarity(
        self, persona: Persona, source_data: str | None
    ) -> GptSimilarityScore | None:
        """Compute GPT embedding similarity."""
        if not source_data:
            return None

        try:
            result = self.gpt_similarity_metric.evaluate(
                persona, source_data=source_data
            )
            return GptSimilarityScore(
                similarity=result.details["similarity"],
                embedding_model=result.details["embedding_model"],
                persona_dimensions=result.details["persona_dimensions"],
                source_dimensions=result.details["source_dimensions"],
            )
        except RuntimeError:
            # Provider not configured, skip this metric
            return None

    def _compute_geval(
        self, persona: Persona, source_data: str | None
    ) -> GevalScore | None:
        """Compute G-eval scores."""
        try:
            result = self.geval_metric.evaluate(persona, source_data=source_data)
            return GevalScore(
                coherence=result.details["coherence"],
                relevance=result.details["relevance"],
                fluency=result.details["fluency"],
                consistency=result.details["consistency"],
                overall=result.details["overall"],
                model=result.details["model"],
                reasoning=result.details["reasoning"],
            )
        except RuntimeError:
            # LLM evaluation failed, skip this metric
            return None


def validate_persona(
    persona: Persona,
    source_data: str | None = None,
    metrics: list[str] | None = None,
    **kwargs: Any,
) -> AcademicValidationReport:
    """
    Convenience function to validate a single persona.

    Args:
        persona: The persona to validate.
        source_data: Source data for comparison.
        metrics: List of metrics to compute.
        **kwargs: Additional configuration passed to AcademicValidator.

    Returns:
        AcademicValidationReport with validation results.
    """
    validator = AcademicValidator(**kwargs)
    return validator.validate(persona, source_data, metrics)


def validate_personas(
    personas: list[Persona],
    source_data: str | None = None,
    metrics: list[str] | None = None,
    **kwargs: Any,
) -> BatchAcademicValidationReport:
    """
    Convenience function to validate multiple personas.

    Args:
        personas: List of personas to validate.
        source_data: Source data for comparison.
        metrics: List of metrics to compute.
        **kwargs: Additional configuration passed to AcademicValidator.

    Returns:
        BatchAcademicValidationReport with validation results.
    """
    validator = AcademicValidator(**kwargs)
    return validator.validate_batch(personas, source_data, metrics)
