"""
Provider factory for creating LLM provider instances.

This module provides a factory pattern for instantiating providers
based on configuration or provider name.
"""

from typing import Any

from persona.core.providers.base import LLMProvider
from persona.core.providers.openai import OpenAIProvider
from persona.core.providers.anthropic import AnthropicProvider
from persona.core.providers.gemini import GeminiProvider


class ProviderFactory:
    """
    Factory for creating LLM provider instances.

    Supports creating providers by name and listing available providers.

    Example:
        factory = ProviderFactory()
        provider = factory.create("anthropic")
        response = provider.generate("Hello, Claude!")
    """

    # Mapping of provider names to classes
    PROVIDERS: dict[str, type[LLMProvider]] = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "gemini": GeminiProvider,
        "google": GeminiProvider,  # Alias
    }

    @classmethod
    def create(
        cls,
        provider_name: str,
        api_key: str | None = None,
        **kwargs: Any,
    ) -> LLMProvider:
        """
        Create a provider instance by name.

        Args:
            provider_name: Name of the provider (openai, anthropic, gemini).
            api_key: Optional API key.
            **kwargs: Additional provider-specific arguments.

        Returns:
            LLMProvider instance.

        Raises:
            ValueError: If the provider name is not recognised.
        """
        provider_name = provider_name.lower()

        if provider_name not in cls.PROVIDERS:
            available = ", ".join(cls.list_providers())
            raise ValueError(
                f"Unknown provider: {provider_name}. "
                f"Available providers: {available}"
            )

        provider_class = cls.PROVIDERS[provider_name]
        return provider_class(api_key=api_key, **kwargs)

    @classmethod
    def list_providers(cls) -> list[str]:
        """
        List available provider names.

        Returns:
            List of provider names (excluding aliases).
        """
        # Return unique providers (exclude aliases)
        seen = set()
        result = []
        for name, provider_class in cls.PROVIDERS.items():
            if provider_class not in seen:
                result.append(name)
                seen.add(provider_class)
        return sorted(result)

    @classmethod
    def get_configured_providers(cls) -> list[str]:
        """
        List providers that are currently configured (have API keys).

        Returns:
            List of configured provider names.
        """
        configured = []
        for name in cls.list_providers():
            provider = cls.create(name)
            if provider.is_configured():
                configured.append(name)
        return configured
