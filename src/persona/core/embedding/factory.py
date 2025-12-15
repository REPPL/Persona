"""
Embedding provider factory.

This module provides factory functions for creating embedding providers.
"""

from typing import Any

from persona.core.embedding.base import EmbeddingProvider


# Registry of available providers
_PROVIDER_REGISTRY: dict[str, type[EmbeddingProvider]] = {}


def _register_builtin_providers() -> None:
    """Register built-in embedding providers."""
    global _PROVIDER_REGISTRY

    # Only register if not already done
    if _PROVIDER_REGISTRY:
        return

    from persona.core.embedding.openai import OpenAIEmbeddingProvider

    _PROVIDER_REGISTRY["openai"] = OpenAIEmbeddingProvider


class EmbeddingFactory:
    """
    Factory for creating embedding providers.

    Example:
        # Get OpenAI provider
        provider = EmbeddingFactory.create("openai")

        # Get OpenAI with specific model
        provider = EmbeddingFactory.create(
            "openai",
            model="text-embedding-3-large"
        )

        # List available providers
        providers = EmbeddingFactory.list_providers()
    """

    @staticmethod
    def create(
        provider_name: str = "openai",
        **kwargs: Any,
    ) -> EmbeddingProvider:
        """
        Create an embedding provider instance.

        Args:
            provider_name: Name of the provider to create.
            **kwargs: Additional arguments passed to the provider.

        Returns:
            EmbeddingProvider instance.

        Raises:
            ValueError: If provider is not found.
        """
        _register_builtin_providers()

        if provider_name not in _PROVIDER_REGISTRY:
            available = list(_PROVIDER_REGISTRY.keys())
            raise ValueError(
                f"Unknown embedding provider: '{provider_name}'. "
                f"Available: {available}"
            )

        provider_class = _PROVIDER_REGISTRY[provider_name]
        return provider_class(**kwargs)

    @staticmethod
    def list_providers() -> list[str]:
        """
        List available embedding provider names.

        Returns:
            List of provider names.
        """
        _register_builtin_providers()
        return list(_PROVIDER_REGISTRY.keys())

    @staticmethod
    def register(name: str, provider_class: type[EmbeddingProvider]) -> None:
        """
        Register a custom embedding provider.

        Args:
            name: Unique name for the provider.
            provider_class: The provider class.

        Raises:
            ValueError: If name is already registered.
            TypeError: If class doesn't inherit from EmbeddingProvider.
        """
        _register_builtin_providers()

        if name in _PROVIDER_REGISTRY:
            raise ValueError(f"Provider '{name}' is already registered")

        if not issubclass(provider_class, EmbeddingProvider):
            raise TypeError(
                f"Provider class must inherit from EmbeddingProvider, "
                f"got {provider_class.__name__}"
            )

        _PROVIDER_REGISTRY[name] = provider_class

    @staticmethod
    def is_available(provider_name: str) -> bool:
        """
        Check if a provider is available and configured.

        Args:
            provider_name: Name of the provider.

        Returns:
            True if provider exists and is configured.
        """
        _register_builtin_providers()

        if provider_name not in _PROVIDER_REGISTRY:
            return False

        try:
            provider = EmbeddingFactory.create(provider_name)
            return provider.is_configured()
        except Exception:
            return False


def get_embedding_provider(
    provider_name: str = "openai",
    **kwargs: Any,
) -> EmbeddingProvider:
    """
    Convenience function to get an embedding provider.

    Args:
        provider_name: Name of the provider.
        **kwargs: Additional arguments for the provider.

    Returns:
        EmbeddingProvider instance.
    """
    return EmbeddingFactory.create(provider_name, **kwargs)
