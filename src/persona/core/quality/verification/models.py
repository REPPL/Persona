"""
Data models for multi-model verification (F-120).

This module provides data classes for verification configuration,
metrics, and results when comparing persona generation across
multiple LLM models.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class VerificationConfig:
    """
    Configuration for multi-model verification.

    Attributes:
        models: List of model identifiers to use for verification.
            Format: 'provider:model' or just 'model'.
            Example: ['claude-sonnet-4-20250514', 'gpt-4o', 'gemini-2.0-flash']
        samples_per_model: Number of samples to generate per model.
        consistency_threshold: Minimum consistency score to pass verification (0-1).
        voting_strategy: Strategy for consensus ('majority', 'unanimous', 'weighted').
        embedding_model: Model to use for semantic similarity comparison.
        parallel: Whether to run model generation in parallel.
        timeout_seconds: Timeout for each model generation.
    """

    models: list[str] = field(default_factory=list)
    samples_per_model: int = 3
    consistency_threshold: float = 0.7
    voting_strategy: str = "majority"
    embedding_model: str = "text-embedding-3-small"
    parallel: bool = True
    timeout_seconds: int = 300

    def __post_init__(self) -> None:
        """Validate configuration."""
        if not self.models:
            raise ValueError("At least one model must be specified")

        if self.samples_per_model < 1:
            raise ValueError("samples_per_model must be at least 1")

        if not 0 <= self.consistency_threshold <= 1:
            raise ValueError("consistency_threshold must be between 0 and 1")

        valid_strategies = {"majority", "unanimous", "weighted"}
        if self.voting_strategy not in valid_strategies:
            raise ValueError(
                f"voting_strategy must be one of {valid_strategies}, "
                f"got '{self.voting_strategy}'"
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "models": self.models,
            "samples_per_model": self.samples_per_model,
            "consistency_threshold": self.consistency_threshold,
            "voting_strategy": self.voting_strategy,
            "embedding_model": self.embedding_model,
            "parallel": self.parallel,
            "timeout_seconds": self.timeout_seconds,
        }


@dataclass
class ConsistencyMetrics:
    """
    Metrics for measuring consistency across model outputs.

    Attributes:
        attribute_agreement: Percentage of attributes present in all outputs (0-1).
        semantic_consistency: Average embedding similarity across outputs (0-1).
        factual_convergence: Percentage of claims in majority of outputs (0-1).
        confidence_score: Weighted combination of all metrics (0-1).
        weights: Weights used for confidence score calculation.
    """

    attribute_agreement: float = 0.0
    semantic_consistency: float = 0.0
    factual_convergence: float = 0.0
    confidence_score: float = 0.0
    weights: dict[str, float] | None = None

    def __post_init__(self) -> None:
        """Initialize default weights and calculate confidence score."""
        # Set default weights if not provided
        if self.weights is None:
            self.weights = {
                "attribute_agreement": 0.4,
                "semantic_consistency": 0.3,
                "factual_convergence": 0.3,
            }

        # Calculate confidence score if not provided
        if self.confidence_score == 0.0:
            self.confidence_score = self.calculate_confidence()

    def calculate_confidence(self) -> float:
        """
        Calculate weighted confidence score.

        Returns:
            Confidence score between 0 and 1.
        """
        if self.weights is None:
            self.weights = {
                "attribute_agreement": 0.4,
                "semantic_consistency": 0.3,
                "factual_convergence": 0.3,
            }

        return (
            self.attribute_agreement * self.weights["attribute_agreement"]
            + self.semantic_consistency * self.weights["semantic_consistency"]
            + self.factual_convergence * self.weights["factual_convergence"]
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "attribute_agreement": round(self.attribute_agreement, 4),
            "semantic_consistency": round(self.semantic_consistency, 4),
            "factual_convergence": round(self.factual_convergence, 4),
            "confidence_score": round(self.confidence_score, 4),
            "weights": self.weights,
        }


@dataclass
class AttributeAgreement:
    """
    Agreement details for a specific attribute.

    Attributes:
        attribute: The attribute name.
        present_count: Number of models that included this attribute.
        total_count: Total number of models.
        values: List of values from different models.
        agreement_score: Percentage of models agreeing (0-1).
    """

    attribute: str
    present_count: int
    total_count: int
    values: list[Any] = field(default_factory=list)
    agreement_score: float = 0.0

    def __post_init__(self) -> None:
        """Calculate agreement score."""
        if self.total_count > 0:
            self.agreement_score = self.present_count / self.total_count

    @property
    def is_agreed(self) -> bool:
        """Whether attribute is agreed upon (majority)."""
        return self.agreement_score > 0.5

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "attribute": self.attribute,
            "present_count": self.present_count,
            "total_count": self.total_count,
            "agreement_score": round(self.agreement_score, 4),
            "is_agreed": self.is_agreed,
        }


@dataclass
class VerificationReport:
    """
    Report from multi-model verification.

    Attributes:
        persona_id: Identifier for the persona being verified.
        config: Configuration used for verification.
        consistency_score: Overall consistency score (0-1).
        agreed_attributes: Attributes agreed upon by voting strategy.
        disputed_attributes: Attributes with disagreement.
        model_outputs: Optional raw outputs from each model.
        metrics: Detailed consistency metrics.
        consensus_persona: Persona built from agreed attributes.
        timestamp: When verification was performed.
        passed: Whether verification passed threshold.
    """

    persona_id: str
    config: VerificationConfig
    consistency_score: float
    agreed_attributes: list[str] = field(default_factory=list)
    disputed_attributes: list[str] = field(default_factory=list)
    model_outputs: dict[str, Any] = field(default_factory=dict)
    metrics: ConsistencyMetrics = field(default_factory=ConsistencyMetrics)
    consensus_persona: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    passed: bool = False

    def __post_init__(self) -> None:
        """Determine if verification passed."""
        self.passed = self.consistency_score >= self.config.consistency_threshold

    def get_consensus_persona(self) -> dict[str, Any]:
        """
        Get the consensus persona.

        Returns:
            Dictionary with agreed-upon attributes.
        """
        return self.consensus_persona

    def get_agreement_details(self) -> dict[str, AttributeAgreement]:
        """
        Get detailed agreement information for each attribute.

        Returns:
            Dictionary mapping attribute names to agreement details.
        """
        # Extract from model_outputs if available
        if not self.model_outputs:
            return {}

        all_attributes = set()
        for output in self.model_outputs.values():
            if isinstance(output, dict):
                all_attributes.update(output.keys())

        details = {}
        total_count = len(self.model_outputs)

        for attr in all_attributes:
            values = []
            present_count = 0

            for output in self.model_outputs.values():
                if isinstance(output, dict) and attr in output:
                    values.append(output[attr])
                    present_count += 1

            details[attr] = AttributeAgreement(
                attribute=attr,
                present_count=present_count,
                total_count=total_count,
                values=values,
            )

        return details

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "persona_id": self.persona_id,
            "config": self.config.to_dict(),
            "consistency_score": round(self.consistency_score, 4),
            "agreed_attributes": self.agreed_attributes,
            "disputed_attributes": self.disputed_attributes,
            "metrics": self.metrics.to_dict(),
            "consensus_persona": self.consensus_persona,
            "timestamp": self.timestamp.isoformat(),
            "passed": self.passed,
            "model_count": len(self.model_outputs),
        }

    def to_markdown(self) -> str:
        """
        Generate markdown report.

        Returns:
            Formatted markdown string.
        """
        lines = [
            f"# Verification Report: {self.persona_id}",
            "",
            f"**Timestamp**: {self.timestamp.isoformat()}",
            f"**Status**: {'✅ PASSED' if self.passed else '❌ FAILED'}",
            f"**Consistency Score**: {self.consistency_score:.2%}",
            f"**Threshold**: {self.config.consistency_threshold:.2%}",
            "",
            "## Configuration",
            "",
            f"- **Models**: {', '.join(self.config.models)}",
            f"- **Samples per Model**: {self.config.samples_per_model}",
            f"- **Voting Strategy**: {self.config.voting_strategy}",
            "",
            "## Consistency Metrics",
            "",
            f"- **Attribute Agreement**: {self.metrics.attribute_agreement:.2%}",
            f"- **Semantic Consistency**: {self.metrics.semantic_consistency:.2%}",
            f"- **Factual Convergence**: {self.metrics.factual_convergence:.2%}",
            "",
            "## Agreed Attributes",
            "",
        ]

        if self.agreed_attributes:
            for attr in self.agreed_attributes:
                lines.append(f"- {attr}")
        else:
            lines.append("*No attributes met agreement criteria*")

        lines.extend(
            [
                "",
                "## Disputed Attributes",
                "",
            ]
        )

        if self.disputed_attributes:
            for attr in self.disputed_attributes:
                lines.append(f"- {attr}")
        else:
            lines.append("*No disputed attributes*")

        lines.extend(
            [
                "",
                "## Consensus Persona",
                "",
                "```json",
                # Format consensus persona as pretty JSON
                self._format_json(self.consensus_persona, indent=2),
                "```",
            ]
        )

        return "\n".join(lines)

    def _format_json(self, data: Any, indent: int = 2) -> str:
        """Format data as JSON string."""
        import json

        return json.dumps(data, indent=indent, ensure_ascii=False)
