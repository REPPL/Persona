"""
Configuration for hybrid local/frontier pipeline.

This module provides configuration dataclasses for the hybrid pipeline
that combines local Ollama models with optional frontier APIs.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class HybridConfig:
    """
    Configuration for hybrid local/frontier pipeline.

    The hybrid pipeline uses local models for initial generation and
    optional frontier models for quality refinement based on automated
    quality thresholds.

    Attributes:
        local_provider: Local LLM provider name (default: "ollama").
        local_model: Local model to use for draft generation (default: "qwen2.5:7b").
        frontier_provider: Optional frontier provider (anthropic, openai, gemini).
        frontier_model: Frontier model for quality refinement.
        quality_threshold: Minimum quality score to skip frontier refinement (0.0-1.0).
        max_cost: Optional budget limit in USD.
        batch_size: Number of personas to generate per batch.
        enable_pii_filter: Whether to filter PII from generated personas.
        local_temperature: Temperature for local model generation.
        frontier_temperature: Temperature for frontier model refinement.
        max_refinement_attempts: Maximum attempts to refine low-quality personas.

    Example:
        # Local-only mode (no frontier refinement)
        config = HybridConfig(
            local_model="qwen2.5:7b",
            frontier_provider=None
        )

        # Full hybrid mode with quality threshold
        config = HybridConfig(
            local_model="qwen2.5:7b",
            frontier_provider="anthropic",
            frontier_model="claude-3-5-sonnet-20241022",
            quality_threshold=0.7,
            max_cost=5.0
        )
    """

    # Local model configuration
    local_provider: str = "ollama"
    local_model: str = "qwen2.5:7b"

    # Frontier model configuration
    frontier_provider: Optional[str] = None
    frontier_model: Optional[str] = None

    # Quality and cost controls
    quality_threshold: float = 0.7
    max_cost: Optional[float] = None

    # Generation parameters
    batch_size: int = 10
    enable_pii_filter: bool = True
    local_temperature: float = 0.7
    frontier_temperature: float = 0.7
    max_refinement_attempts: int = 2

    # Judge configuration
    judge_provider: str = "ollama"
    judge_model: str = "qwen2.5:72b"

    def __post_init__(self) -> None:
        """Validate configuration after initialisation."""
        if self.quality_threshold < 0.0 or self.quality_threshold > 1.0:
            raise ValueError("quality_threshold must be between 0.0 and 1.0")

        if self.max_cost is not None and self.max_cost <= 0.0:
            raise ValueError("max_cost must be positive")

        if self.batch_size < 1:
            raise ValueError("batch_size must be at least 1")

        if self.max_refinement_attempts < 1:
            raise ValueError("max_refinement_attempts must be at least 1")

        # Validate frontier configuration
        if self.frontier_provider and not self.frontier_model:
            raise ValueError("frontier_model required when frontier_provider is set")

    @property
    def is_hybrid_mode(self) -> bool:
        """Return True if frontier refinement is enabled."""
        return self.frontier_provider is not None

    @property
    def is_local_only(self) -> bool:
        """Return True if running in local-only mode."""
        return not self.is_hybrid_mode

    def to_dict(self) -> dict:
        """Convert configuration to dictionary."""
        return {
            "local_provider": self.local_provider,
            "local_model": self.local_model,
            "frontier_provider": self.frontier_provider,
            "frontier_model": self.frontier_model,
            "quality_threshold": self.quality_threshold,
            "max_cost": self.max_cost,
            "batch_size": self.batch_size,
            "enable_pii_filter": self.enable_pii_filter,
            "local_temperature": self.local_temperature,
            "frontier_temperature": self.frontier_temperature,
            "max_refinement_attempts": self.max_refinement_attempts,
            "judge_provider": self.judge_provider,
            "judge_model": self.judge_model,
            "is_hybrid_mode": self.is_hybrid_mode,
        }
