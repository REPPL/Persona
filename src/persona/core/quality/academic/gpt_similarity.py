"""
GPT embedding similarity metric implementation.

This module provides the GptSimilarityMetric class that uses GPT embeddings
to calculate semantic similarity between persona and source data.
"""

from typing import TYPE_CHECKING

from persona.core.embedding.factory import EmbeddingFactory
from persona.core.generation.parser import Persona
from persona.core.quality.base import MetricCategory, QualityMetric
from persona.core.quality.config import QualityConfig
from persona.core.quality.models import DimensionScore

if TYPE_CHECKING:
    from persona.core.embedding.base import EmbeddingProvider
    from persona.core.evidence.linker import EvidenceReport


class GptSimilarityMetric(QualityMetric):
    """
    GPT embedding similarity metric.

    This metric uses OpenAI's text embedding models to generate vector
    representations of both the persona and source data, then calculates
    cosine similarity between them. This captures high-level semantic
    similarity.

    Unlike BERTScore which compares token-by-token, this metric creates
    a single vector for each text and compares them holistically.

    Example:
        metric = GptSimilarityMetric(provider="openai")
        score = metric.evaluate(
            persona=my_persona,
            source_data=research_text,
        )
        print(f"Similarity: {score.details['similarity']:.3f}")
    """

    def __init__(
        self,
        config: QualityConfig | None = None,
        provider: str = "openai",
        model: str | None = None,
    ) -> None:
        """
        Initialise the GPT similarity metric.

        Args:
            config: Quality configuration with weights and thresholds.
            provider: Embedding provider to use (default: "openai").
            model: Embedding model to use (default: provider's default).
        """
        super().__init__(config)
        self.provider_name = provider
        self.embedding_provider: "EmbeddingProvider" = EmbeddingFactory.create(provider)
        self.model = model or self.embedding_provider.model

    @property
    def name(self) -> str:
        """Return the unique name of this metric."""
        return "gpt_similarity"

    @property
    def description(self) -> str:
        """Return a human-readable description."""
        return "GPT embedding cosine similarity between persona and source"

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
        Evaluate persona using GPT embedding similarity.

        Args:
            persona: The persona to evaluate.
            source_data: Source data text for comparison (required).
            other_personas: Not used by this metric.
            evidence_report: Not used by this metric.

        Returns:
            DimensionScore with similarity results.

        Raises:
            ValueError: If source_data is not provided.
            RuntimeError: If embedding provider is not configured.
        """
        if not source_data:
            raise ValueError("GPT similarity metric requires source_data")

        if not self.embedding_provider.is_configured():
            raise RuntimeError(
                f"Embedding provider '{self.provider_name}' is not configured. "
                "Please set required API keys or configuration."
            )

        # Convert persona to text
        persona_text = self._persona_to_text(persona)

        # Generate embeddings
        persona_embedding = self.embedding_provider.embed(persona_text)
        source_embedding = self.embedding_provider.embed(source_data)

        # Calculate cosine similarity
        similarity = persona_embedding.cosine_similarity(source_embedding)

        # Convert to 0-100 scale
        score = similarity * 100

        # Detect issues
        issues = []
        if similarity < 0.5:
            issues.append(
                "Low embedding similarity: persona semantics differ significantly from source"
            )
        if similarity < 0.3:
            issues.append(
                "Very low embedding similarity: persona may not be grounded in source data"
            )

        return DimensionScore(
            dimension=self.name,
            score=score,
            weight=self.weight,
            issues=issues,
            details={
                "similarity": similarity,
                "embedding_model": self.model,
                "persona_dimensions": persona_embedding.dimensions,
                "source_dimensions": source_embedding.dimensions,
                "persona_length": len(persona_text),
                "source_length": len(source_data),
                "persona_tokens": persona_embedding.input_tokens,
                "source_tokens": source_embedding.input_tokens,
            },
        )

    def _persona_to_text(self, persona: Persona) -> str:
        """
        Convert persona to text for embedding.

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
