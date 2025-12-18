"""
Provider factory for creating LLM provider instances.

This module provides a factory pattern for instantiating providers
based on configuration or provider name. Supports both built-in
providers and custom vendors loaded from YAML configuration.
"""

from typing import Any

from persona.core.providers.anthropic import AnthropicProvider
from persona.core.providers.base import LLMProvider
from persona.core.providers.gemini import GeminiProvider
from persona.core.providers.ollama import OllamaProvider
from persona.core.providers.openai import OpenAIProvider


class ProviderFactory:
    """
    Factory for creating LLM provider instances.

    Supports creating providers by name and listing available providers.
    Includes support for custom vendors loaded from YAML configuration.

    Example:
        factory = ProviderFactory()
        provider = factory.create("anthropic")
        response = provider.generate("Hello, Claude!")

        # Custom vendor
        provider = factory.create("azure-openai")
    """

    # Mapping of built-in provider names to classes
    BUILTIN_PROVIDERS: dict[str, type[LLMProvider]] = {
        "openai": OpenAIProvider,
        "anthropic": AnthropicProvider,
        "gemini": GeminiProvider,
        "google": GeminiProvider,  # Alias
        "ollama": OllamaProvider,
    }

    # Legacy alias for backward compatibility
    PROVIDERS = BUILTIN_PROVIDERS

    # Cache for vendor loader instance
    _vendor_loader = None

    @classmethod
    def _get_vendor_loader(cls):
        """Lazy-load the vendor loader."""
        if cls._vendor_loader is None:
            from persona.core.config.vendor import VendorLoader

            cls._vendor_loader = VendorLoader()
        return cls._vendor_loader

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
            provider_name: Name of the provider (openai, anthropic, gemini,
                          or a custom vendor ID).
            api_key: Optional API key.
            **kwargs: Additional provider-specific arguments.

        Returns:
            LLMProvider instance.

        Raises:
            ValueError: If the provider name is not recognised.
        """
        provider_name = provider_name.lower()

        # Check built-in providers first
        if provider_name in cls.BUILTIN_PROVIDERS:
            provider_class = cls.BUILTIN_PROVIDERS[provider_name]
            return provider_class(api_key=api_key, **kwargs)

        # Check custom vendors
        vendor_loader = cls._get_vendor_loader()
        if vendor_loader.exists(provider_name):
            from persona.core.providers.custom import CustomVendorProvider

            config = vendor_loader.load(provider_name)
            return CustomVendorProvider(config, api_key=api_key)

        # Provider not found
        available = ", ".join(cls.list_providers())
        raise ValueError(
            f"Unknown provider: {provider_name}. " f"Available providers: {available}"
        )

    @classmethod
    def list_providers(cls, include_custom: bool = True) -> list[str]:
        """
        List available provider names.

        Args:
            include_custom: If True, include custom vendors.

        Returns:
            List of provider names (excluding aliases).
        """
        # Built-in providers (excluding aliases)
        seen = set()
        result = []
        for name, provider_class in cls.BUILTIN_PROVIDERS.items():
            if provider_class not in seen:
                result.append(name)
                seen.add(provider_class)

        # Add custom vendors
        if include_custom:
            vendor_loader = cls._get_vendor_loader()
            for vendor_id in vendor_loader.list_vendors():
                if vendor_id not in result:
                    result.append(vendor_id)

        return sorted(result)

    @classmethod
    def list_builtin_providers(cls) -> list[str]:
        """
        List only built-in provider names.

        Returns:
            List of built-in provider names.
        """
        return cls.list_providers(include_custom=False)

    @classmethod
    def list_custom_vendors(cls) -> list[str]:
        """
        List only custom vendor names.

        Returns:
            List of custom vendor IDs.
        """
        vendor_loader = cls._get_vendor_loader()
        return vendor_loader.list_vendors()

    @classmethod
    def get_configured_providers(cls, include_custom: bool = True) -> list[str]:
        """
        List providers that are currently configured (have API keys).

        Args:
            include_custom: If True, include custom vendors.

        Returns:
            List of configured provider names.
        """
        configured = []
        for name in cls.list_providers(include_custom=include_custom):
            try:
                provider = cls.create(name)
                if provider.is_configured():
                    configured.append(name)
            except Exception:
                continue
        return configured

    @classmethod
    def is_builtin(cls, provider_name: str) -> bool:
        """
        Check if a provider is built-in.

        Args:
            provider_name: Provider name to check.

        Returns:
            True if provider is built-in.
        """
        return provider_name.lower() in cls.BUILTIN_PROVIDERS

    @classmethod
    def is_custom(cls, provider_name: str) -> bool:
        """
        Check if a provider is a custom vendor.

        Args:
            provider_name: Provider name to check.

        Returns:
            True if provider is a custom vendor.
        """
        vendor_loader = cls._get_vendor_loader()
        return vendor_loader.exists(provider_name.lower())

    @classmethod
    def clear_vendor_cache(cls) -> None:
        """Clear the vendor loader cache."""
        if cls._vendor_loader is not None:
            cls._vendor_loader.clear_cache()
        cls._vendor_loader = None
