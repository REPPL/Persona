"""
PersonaClient - Convenient SDK interface for persona generation.

This module provides the PersonaClient class, a high-level wrapper
around the SDK that simplifies common use cases.
"""

from collections.abc import Callable
from pathlib import Path
from typing import Any

from persona.sdk.config import SDKConfig
from persona.sdk.generator import PersonaGenerator
from persona.sdk.models import GenerationResultModel, PersonaConfig


class PersonaClient:
    """
    High-level client for persona generation.

    This is a convenience wrapper around PersonaGenerator that
    provides a simplified interface with integrated configuration
    management.

    Example:
        from persona.sdk import PersonaClient

        # Simple usage with defaults
        client = PersonaClient()
        personas = client.generate(data="./interviews.csv", count=5)

        # With configuration
        client = PersonaClient(
            provider="openai",
            model="gpt-4o",
        )
        personas = client.generate(
            data="./interviews.csv",
            config={
                "complexity": "detailed",
                "detail_level": "comprehensive",
            }
        )

        # Access results
        for persona in personas.personas:
            print(f"{persona.name}: {persona.goals}")
    """

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
        api_key: str | None = None,
        config: SDKConfig | None = None,
    ) -> None:
        """
        Initialise PersonaClient.

        Args:
            provider: LLM provider (anthropic, openai, gemini).
                If None, loads from config or defaults to anthropic.
            model: Model identifier. If None, uses provider default.
            api_key: API key. If None, uses environment variable.
            config: SDK configuration. If None, loads from defaults.

        Raises:
            ConfigurationError: If configuration is invalid.
        """
        # Load SDK configuration
        self._config = config or SDKConfig.from_defaults()

        # Override with constructor arguments
        if provider is not None:
            self._config.default_provider = provider
        if model is not None:
            self._config.default_model = model

        # Create generator
        self._generator = PersonaGenerator(
            provider=self._config.default_provider,
            model=self._config.default_model or model,
            api_key=api_key,
        )

    @property
    def provider(self) -> str:
        """Return configured provider."""
        return self._generator.provider

    @property
    def model(self) -> str | None:
        """Return configured model."""
        return self._generator.model

    @property
    def config(self) -> SDKConfig:
        """Return SDK configuration."""
        return self._config

    def generate(
        self,
        data: str | Path,
        count: int | None = None,
        provider: str | None = None,
        model: str | None = None,
        config: dict[str, Any] | PersonaConfig | None = None,
    ) -> GenerationResultModel:
        """
        Generate personas from data.

        This is a convenience method that handles configuration
        merging and generator creation automatically.

        Args:
            data: Path to data file or directory.
            count: Number of personas to generate. Defaults to config.
            provider: Override provider for this generation.
            model: Override model for this generation.
            config: Generation configuration (dict or PersonaConfig).

        Returns:
            GenerationResultModel with generated personas.

        Raises:
            DataError: If data cannot be loaded.
            ProviderError: If LLM provider fails.
            GenerationError: If generation fails.

        Example:
            client = PersonaClient()

            # Simple usage
            result = client.generate("./data.csv", count=3)

            # With detailed config
            result = client.generate(
                data="./interviews/",
                count=5,
                config={
                    "complexity": "complex",
                    "detail_level": "detailed",
                    "include_reasoning": True,
                }
            )
        """
        # Handle provider/model override
        if provider is not None or model is not None:
            generator = PersonaGenerator(
                provider=provider or self._config.default_provider,
                model=model or self._config.default_model,
            )
        else:
            generator = self._generator

        # Build PersonaConfig
        if isinstance(config, PersonaConfig):
            persona_config = config
        elif isinstance(config, dict):
            persona_config = PersonaConfig(**config)
        else:
            persona_config = PersonaConfig()

        # Override count if provided
        if count is not None:
            persona_config = PersonaConfig(
                count=count,
                complexity=persona_config.complexity,
                detail_level=persona_config.detail_level,
                include_reasoning=persona_config.include_reasoning,
                temperature=persona_config.temperature,
                max_tokens=persona_config.max_tokens,
                workflow=persona_config.workflow,
            )

        # Generate
        return generator.generate(data_path=data, config=persona_config)

    def estimate_cost(
        self,
        data: str | Path,
        count: int | None = None,
    ) -> dict[str, Any]:
        """
        Estimate cost before generation.

        Args:
            data: Path to data file or directory.
            count: Number of personas. Defaults to config.

        Returns:
            Dictionary with cost estimation.

        Example:
            client = PersonaClient()
            estimate = client.estimate_cost("./data.csv", count=5)
            print(f"Estimated: ${estimate['estimated_cost']:.2f}")
        """
        config = PersonaConfig(count=count or self._config.default_count)
        return self._generator.estimate_cost(data_path=data, config=config)

    def set_progress_callback(
        self,
        callback: Callable[[str, int, int], None],
    ) -> None:
        """
        Set progress callback for generation updates.

        Args:
            callback: Function that receives (message, current_step, total_steps).

        Example:
            def on_progress(msg, step, total):
                print(f"[{step}/{total}] {msg}")

            client = PersonaClient()
            client.set_progress_callback(on_progress)
        """
        self._generator.set_progress_callback(callback)

    def validate_config(self, config: PersonaConfig) -> list[str]:
        """
        Validate configuration without running generation.

        Args:
            config: Configuration to validate.

        Returns:
            List of validation warnings (empty if valid).
        """
        return self._generator.validate_config(config)

    @classmethod
    def from_config_file(cls, path: str | Path) -> "PersonaClient":
        """
        Create client from configuration file.

        Args:
            path: Path to YAML configuration file.

        Returns:
            PersonaClient configured from file.

        Raises:
            ConfigurationError: If config file is invalid.

        Example:
            client = PersonaClient.from_config_file("~/.persona/config.yaml")
        """
        config = SDKConfig.from_file(path)
        return cls(config=config)

    @classmethod
    def from_environment(cls) -> "PersonaClient":
        """
        Create client from environment variables.

        Reads configuration from PERSONA_* environment variables.

        Returns:
            PersonaClient configured from environment.

        Example:
            # With PERSONA_PROVIDER=anthropic set
            client = PersonaClient.from_environment()
        """
        config = SDKConfig.from_environment()
        return cls(config=config)
