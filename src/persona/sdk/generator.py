"""
Persona generator SDK class.

This module provides the main PersonaGenerator class for
programmatic persona generation.
"""

from pathlib import Path
from typing import Any, Callable

from persona.sdk.models import (
    PersonaConfig,
    GenerationResultModel,
    ComplexityLevel,
    DetailLevel,
)
from persona.sdk.exceptions import (
    ConfigurationError,
    DataError,
    GenerationError,
    ProviderError,
)


class PersonaGenerator:
    """
    Generate personas from research data.

    This is the main entry point for programmatic persona generation.
    It wraps the core generation pipeline with a clean, typed interface.

    Example:
        from persona.sdk import PersonaGenerator, PersonaConfig

        # Simple usage
        generator = PersonaGenerator(provider="anthropic")
        result = generator.generate("./interviews.csv")

        # With configuration
        generator = PersonaGenerator(
            provider="anthropic",
            model="claude-sonnet-4-5-20250514"
        )
        result = generator.generate(
            "./interviews.csv",
            config=PersonaConfig(count=5, complexity="complex")
        )

        # Access results
        for persona in result.personas:
            print(f"{persona.name}: {persona.goals}")

        # Export
        result.to_json("./output/")
        result.to_markdown("./output/")
    """

    def __init__(
        self,
        provider: str = "anthropic",
        model: str | None = None,
        api_key: str | None = None,
    ) -> None:
        """
        Initialise PersonaGenerator.

        Args:
            provider: LLM provider name (anthropic, openai, gemini).
            model: Model identifier. If None, uses provider default.
            api_key: API key. If None, uses environment variable.

        Raises:
            ConfigurationError: If provider is invalid.
        """
        valid_providers = {"anthropic", "openai", "gemini"}
        if provider not in valid_providers:
            raise ConfigurationError(
                f"Invalid provider: {provider}. Must be one of: {valid_providers}",
                field="provider",
                value=provider,
            )

        self._provider = provider
        self._model = model
        self._api_key = api_key
        self._progress_callback: Callable[[str, int, int], None] | None = None

    @property
    def provider(self) -> str:
        """Return configured provider."""
        return self._provider

    @property
    def model(self) -> str | None:
        """Return configured model."""
        return self._model

    def set_progress_callback(
        self,
        callback: Callable[[str, int, int], None],
    ) -> None:
        """
        Set a callback for progress updates.

        The callback receives (message, current_step, total_steps).

        Args:
            callback: Progress callback function.

        Example:
            def on_progress(message, step, total):
                print(f"[{step}/{total}] {message}")

            generator.set_progress_callback(on_progress)
        """
        self._progress_callback = callback

    def generate(
        self,
        data_path: str | Path,
        config: PersonaConfig | None = None,
    ) -> GenerationResultModel:
        """
        Generate personas from input data.

        Args:
            data_path: Path to input data file or directory.
            config: Generation configuration. If None, uses defaults.

        Returns:
            GenerationResultModel with generated personas.

        Raises:
            DataError: If input data cannot be loaded.
            ProviderError: If LLM provider fails.
            GenerationError: If generation or parsing fails.

        Example:
            result = generator.generate(
                "./interviews.csv",
                config=PersonaConfig(count=3)
            )
        """
        config = config or PersonaConfig()
        data_path = Path(data_path)

        # Validate data path exists
        if not data_path.exists():
            raise DataError(
                f"Data path not found: {data_path}",
                path=str(data_path),
            )

        # Import core modules (lazy import to avoid circular deps)
        from persona.core.generation import GenerationPipeline, GenerationConfig

        # Create core config
        core_config = GenerationConfig(
            data_path=data_path,
            count=config.count,
            provider=self._provider,
            model=self._model,
            workflow=config.workflow,
            complexity=config.complexity,
            detail_level=config.detail_level,
            include_reasoning=config.include_reasoning,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
        )

        # Create pipeline
        pipeline = GenerationPipeline()

        # Set progress callback wrapper
        if self._progress_callback:
            steps = ["Loading data", "Loading workflow", "Rendering prompt",
                     "Generating", "Parsing response", "Complete"]
            step_index = [0]

            def progress_wrapper(message: str) -> None:
                step_index[0] += 1
                if self._progress_callback:
                    self._progress_callback(message, step_index[0], len(steps))

            pipeline.set_progress_callback(progress_wrapper)

        # Generate
        try:
            core_result = pipeline.generate(core_config)
        except FileNotFoundError as e:
            raise DataError(str(e), path=str(data_path)) from e
        except ValueError as e:
            raise DataError(str(e), path=str(data_path)) from e
        except RuntimeError as e:
            error_msg = str(e).lower()
            if "rate limit" in error_msg:
                from persona.sdk.exceptions import RateLimitError
                raise RateLimitError(str(e), provider=self._provider) from e
            if "api" in error_msg or "auth" in error_msg:
                raise ProviderError(str(e), provider=self._provider) from e
            raise GenerationError(str(e), stage="generation") from e
        except Exception as e:
            raise GenerationError(
                f"Generation failed: {e}",
                stage="unknown",
            ) from e

        # Convert to SDK model
        return GenerationResultModel.from_core_result(core_result)

    def estimate_cost(
        self,
        data_path: str | Path,
        config: PersonaConfig | None = None,
    ) -> dict[str, Any]:
        """
        Estimate the cost of generation without running it.

        Args:
            data_path: Path to input data file or directory.
            config: Generation configuration.

        Returns:
            Dictionary with cost estimation details.

        Example:
            estimate = generator.estimate_cost("./interviews.csv")
            print(f"Estimated cost: ${estimate['estimated_cost']:.2f}")
        """
        config = config or PersonaConfig()
        data_path = Path(data_path)

        if not data_path.exists():
            raise DataError(
                f"Data path not found: {data_path}",
                path=str(data_path),
            )

        # Import cost estimation
        from persona.core.cost import CostEstimator
        from persona.core.data import DataLoader

        # Load data to estimate size
        loader = DataLoader()
        try:
            content, files = loader.load_path(data_path)
        except Exception as e:
            raise DataError(str(e), path=str(data_path)) from e

        # Estimate tokens and cost
        estimator = CostEstimator()
        input_tokens = estimator.estimate_input_tokens(content)
        output_tokens = estimator.estimate_output_tokens(config.count)

        # Get pricing
        pricing = estimator.get_pricing(self._provider, self._model)

        estimated_cost = (
            (input_tokens / 1_000_000) * pricing.input_price +
            (output_tokens / 1_000_000) * pricing.output_price
        )

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "model": self._model or pricing.model_id,
            "provider": self._provider,
            "input_price_per_mtok": pricing.input_price,
            "output_price_per_mtok": pricing.output_price,
            "estimated_cost": estimated_cost,
            "source_files": [str(f) for f in files],
        }

    def validate_config(self, config: PersonaConfig) -> list[str]:
        """
        Validate configuration without running generation.

        Args:
            config: Configuration to validate.

        Returns:
            List of validation warnings (empty if valid).
        """
        warnings = []

        if config.count > 10:
            warnings.append(
                f"High persona count ({config.count}) may result in less detailed personas"
            )

        if config.temperature > 1.0:
            warnings.append(
                f"High temperature ({config.temperature}) may produce inconsistent results"
            )

        if config.max_tokens < 1000 and config.count > 1:
            warnings.append(
                f"Low max_tokens ({config.max_tokens}) may truncate output for {config.count} personas"
            )

        return warnings
