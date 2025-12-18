"""Multi-model persona generation (F-066).

Enables generation using multiple LLM models simultaneously,
supporting same-provider and cross-provider configurations.
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class ModelSpec:
    """Specification for a model in multi-model generation.

    Attributes:
        provider: The LLM provider (anthropic, openai, gemini).
        model: The model identifier.
        weight: Relative weight for consensus (default 1.0).
        temperature: Optional temperature override.
        max_tokens: Optional max tokens override.
    """

    provider: str
    model: str
    weight: float = 1.0
    temperature: float | None = None
    max_tokens: int | None = None

    @classmethod
    def parse(cls, spec_string: str) -> "ModelSpec":
        """Parse a model spec string like 'anthropic:claude-sonnet-4'.

        Args:
            spec_string: Model specification in format 'provider:model' or just 'model'.

        Returns:
            ModelSpec instance.

        Raises:
            ValueError: If the spec string is invalid.
        """
        if ":" in spec_string:
            parts = spec_string.split(":", 1)
            return cls(provider=parts[0], model=parts[1])
        else:
            # Infer provider from model name
            provider = cls._infer_provider(spec_string)
            return cls(provider=provider, model=spec_string)

    @staticmethod
    def _infer_provider(model: str) -> str:
        """Infer provider from model name."""
        model_lower = model.lower()
        if "claude" in model_lower:
            return "anthropic"
        elif "gpt" in model_lower or "o1" in model_lower or "o3" in model_lower:
            return "openai"
        elif "gemini" in model_lower:
            return "gemini"
        else:
            raise ValueError(f"Cannot infer provider from model name: {model}")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "provider": self.provider,
            "model": self.model,
            "weight": self.weight,
        }
        if self.temperature is not None:
            result["temperature"] = self.temperature
        if self.max_tokens is not None:
            result["max_tokens"] = self.max_tokens
        return result


@dataclass
class ModelOutput:
    """Output from a single model in multi-model generation.

    Attributes:
        model_spec: The model specification used.
        personas: List of generated personas.
        tokens_input: Input tokens used.
        tokens_output: Output tokens generated.
        latency_ms: Generation latency in milliseconds.
        cost: Estimated cost in USD.
        raw_response: Optional raw LLM response.
        error: Optional error message if generation failed.
    """

    model_spec: ModelSpec
    personas: list[dict[str, Any]] = field(default_factory=list)
    tokens_input: int = 0
    tokens_output: int = 0
    latency_ms: float = 0.0
    cost: float = 0.0
    raw_response: str | None = None
    error: str | None = None

    @property
    def success(self) -> bool:
        """Whether generation succeeded."""
        return self.error is None and len(self.personas) > 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model": self.model_spec.to_dict(),
            "personas": self.personas,
            "tokens_input": self.tokens_input,
            "tokens_output": self.tokens_output,
            "latency_ms": self.latency_ms,
            "cost": self.cost,
            "success": self.success,
            "error": self.error,
        }


@dataclass
class MultiModelResult:
    """Result of multi-model generation.

    Attributes:
        model_outputs: Outputs from each model.
        execution_mode: The execution mode used.
        total_tokens_input: Total input tokens across all models.
        total_tokens_output: Total output tokens across all models.
        total_cost: Total cost across all models.
        total_latency_ms: Total latency (for sequential) or max latency (for parallel).
        consolidated_personas: Personas after consolidation (for consensus mode).
        timestamp: When generation completed.
    """

    model_outputs: list[ModelOutput] = field(default_factory=list)
    execution_mode: str = "parallel"
    total_tokens_input: int = 0
    total_tokens_output: int = 0
    total_cost: float = 0.0
    total_latency_ms: float = 0.0
    consolidated_personas: list[dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def all_personas(self) -> list[dict[str, Any]]:
        """Get all personas from all models."""
        personas = []
        for output in self.model_outputs:
            personas.extend(output.personas)
        return personas

    @property
    def successful_models(self) -> list[ModelOutput]:
        """Get outputs from models that succeeded."""
        return [o for o in self.model_outputs if o.success]

    @property
    def failed_models(self) -> list[ModelOutput]:
        """Get outputs from models that failed."""
        return [o for o in self.model_outputs if not o.success]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model_outputs": [o.to_dict() for o in self.model_outputs],
            "execution_mode": self.execution_mode,
            "total_tokens_input": self.total_tokens_input,
            "total_tokens_output": self.total_tokens_output,
            "total_cost": self.total_cost,
            "total_latency_ms": self.total_latency_ms,
            "consolidated_personas": self.consolidated_personas,
            "timestamp": self.timestamp.isoformat(),
            "successful_models": len(self.successful_models),
            "failed_models": len(self.failed_models),
        }


class MultiModelGenerator:
    """Generator for multi-model persona generation.

    Supports generating personas using multiple LLM models simultaneously,
    with different execution strategies (parallel, sequential, consensus).

    Example:
        >>> generator = MultiModelGenerator()
        >>> result = generator.generate(
        ...     data="interview transcripts...",
        ...     models=[
        ...         ModelSpec("anthropic", "claude-sonnet-4"),
        ...         ModelSpec("openai", "gpt-4o"),
        ...     ],
        ...     count=3,
        ...     mode="parallel"
        ... )
    """

    def __init__(
        self,
        default_temperature: float = 0.7,
        default_max_tokens: int = 4096,
        timeout_seconds: int = 300,
    ):
        """Initialise the multi-model generator.

        Args:
            default_temperature: Default temperature for generation.
            default_max_tokens: Default max tokens for generation.
            timeout_seconds: Timeout for each model.
        """
        self.default_temperature = default_temperature
        self.default_max_tokens = default_max_tokens
        self.timeout_seconds = timeout_seconds

    def generate(
        self,
        data: str | Path,
        models: list[ModelSpec],
        count: int = 3,
        mode: str = "parallel",
    ) -> MultiModelResult:
        """Generate personas using multiple models.

        Args:
            data: Source data for persona generation.
            models: List of model specifications.
            count: Number of personas to generate per model.
            mode: Execution mode (parallel, sequential, consensus).

        Returns:
            MultiModelResult with outputs from all models.

        Raises:
            ValueError: If models list is empty or mode is invalid.
        """
        if not models:
            raise ValueError("At least one model must be specified")

        valid_modes = {"parallel", "sequential", "consensus"}
        if mode not in valid_modes:
            raise ValueError(f"Invalid mode: {mode}. Must be one of {valid_modes}")

        # Import strategy classes here to avoid circular imports
        from persona.core.multimodel.strategies import (
            ConsensusStrategy,
            ParallelStrategy,
            SequentialStrategy,
        )

        # Select execution strategy
        strategy_map = {
            "parallel": ParallelStrategy,
            "sequential": SequentialStrategy,
            "consensus": ConsensusStrategy,
        }
        strategy_class = strategy_map[mode]
        strategy = strategy_class(timeout_seconds=self.timeout_seconds)

        # Execute generation
        result = strategy.execute(
            data=data,
            models=models,
            count=count,
            temperature=self.default_temperature,
            max_tokens=self.default_max_tokens,
        )

        return result

    def generate_single(
        self,
        data: str | Path,
        model: ModelSpec,
        count: int = 3,
    ) -> ModelOutput:
        """Generate personas using a single model.

        Args:
            data: Source data for persona generation.
            model: Model specification.
            count: Number of personas to generate.

        Returns:
            ModelOutput with generation results.
        """
        import time

        start_time = time.time()

        # Simulate generation for now (actual LLM call would go here)
        # In production, this would call the provider's API
        personas = self._mock_generate(data, model, count)

        latency_ms = (time.time() - start_time) * 1000

        # Estimate tokens (simplified)
        data_str = str(data) if isinstance(data, Path) else data
        tokens_input = len(data_str.split()) * 2  # Rough estimate
        tokens_output = count * 500  # Rough estimate per persona

        # Estimate cost (simplified)
        cost = self._estimate_cost(model, tokens_input, tokens_output)

        return ModelOutput(
            model_spec=model,
            personas=personas,
            tokens_input=tokens_input,
            tokens_output=tokens_output,
            latency_ms=latency_ms,
            cost=cost,
        )

    def _mock_generate(
        self,
        data: str | Path,
        model: ModelSpec,
        count: int,
    ) -> list[dict[str, Any]]:
        """Mock persona generation for testing."""
        personas = []
        for i in range(count):
            personas.append(
                {
                    "id": f"persona-{i+1}",
                    "name": f"Persona {i+1} ({model.model})",
                    "role": "User",
                    "goals": ["Goal 1", "Goal 2"],
                    "frustrations": ["Frustration 1"],
                    "model_source": f"{model.provider}:{model.model}",
                }
            )
        return personas

    def _estimate_cost(
        self,
        model: ModelSpec,
        tokens_input: int,
        tokens_output: int,
    ) -> float:
        """Estimate cost for a model call."""
        # Simplified pricing (per 1M tokens)
        pricing = {
            "anthropic": {"input": 3.0, "output": 15.0},
            "openai": {"input": 5.0, "output": 15.0},
            "gemini": {"input": 0.5, "output": 1.5},
        }

        rates = pricing.get(model.provider, {"input": 3.0, "output": 15.0})
        input_cost = (tokens_input / 1_000_000) * rates["input"]
        output_cost = (tokens_output / 1_000_000) * rates["output"]

        return round(input_cost + output_cost, 6)


def generate_multi_model(
    data: str | Path,
    models: list[str | ModelSpec],
    count: int = 3,
    mode: str = "parallel",
) -> MultiModelResult:
    """Convenience function for multi-model generation.

    Args:
        data: Source data for persona generation.
        models: List of model specs (strings or ModelSpec objects).
        count: Number of personas to generate per model.
        mode: Execution mode (parallel, sequential, consensus).

    Returns:
        MultiModelResult with outputs from all models.
    """
    # Convert strings to ModelSpec
    model_specs = []
    for m in models:
        if isinstance(m, str):
            model_specs.append(ModelSpec.parse(m))
        else:
            model_specs.append(m)

    generator = MultiModelGenerator()
    return generator.generate(data, model_specs, count, mode)
