"""Tests for embedding provider factory."""

import pytest
from persona.core.embedding.base import EmbeddingProvider, EmbeddingResponse
from persona.core.embedding.factory import (
    _PROVIDER_REGISTRY,
    EmbeddingFactory,
    get_embedding_provider,
)
from persona.core.embedding.openai import OpenAIEmbeddingProvider


class TestEmbeddingFactory:
    """Tests for EmbeddingFactory class."""

    def test_create_default_provider(self):
        """Test creating default provider (OpenAI)."""
        provider = EmbeddingFactory.create()

        assert isinstance(provider, OpenAIEmbeddingProvider)
        assert provider.name == "openai"

    def test_create_openai_provider(self):
        """Test creating OpenAI provider explicitly."""
        provider = EmbeddingFactory.create("openai")

        assert isinstance(provider, OpenAIEmbeddingProvider)
        assert provider.model == "text-embedding-3-small"

    def test_create_with_kwargs(self):
        """Test creating provider with custom arguments."""
        provider = EmbeddingFactory.create(
            "openai",
            model="text-embedding-3-large",
            api_key="test-key",
        )

        assert provider.model == "text-embedding-3-large"
        assert provider.is_configured() is True

    def test_create_unknown_provider_raises(self):
        """Test that unknown provider raises ValueError."""
        with pytest.raises(ValueError, match="Unknown embedding provider"):
            EmbeddingFactory.create("nonexistent")

    def test_create_unknown_provider_lists_available(self):
        """Test error message includes available providers."""
        with pytest.raises(ValueError, match="openai"):
            EmbeddingFactory.create("nonexistent")

    def test_list_providers(self):
        """Test listing available providers."""
        providers = EmbeddingFactory.list_providers()

        assert isinstance(providers, list)
        assert "openai" in providers

    def test_is_available_known_provider(self):
        """Test is_available for known provider without API key."""
        # This will return False if no API key is configured
        # The important thing is it doesn't raise
        result = EmbeddingFactory.is_available("openai")

        assert isinstance(result, bool)

    def test_is_available_unknown_provider(self):
        """Test is_available for unknown provider."""
        result = EmbeddingFactory.is_available("nonexistent")

        assert result is False


class TestEmbeddingFactoryRegistration:
    """Tests for custom provider registration."""

    def setup_method(self):
        """Store original registry state."""
        self._original_keys = set(_PROVIDER_REGISTRY.keys())

    def teardown_method(self):
        """Restore original registry state."""
        # Remove any providers added during test
        keys_to_remove = set(_PROVIDER_REGISTRY.keys()) - self._original_keys
        for key in keys_to_remove:
            del _PROVIDER_REGISTRY[key]

    def test_register_custom_provider(self):
        """Test registering a custom provider."""

        class CustomProvider(EmbeddingProvider):
            @property
            def name(self) -> str:
                return "custom"

            @property
            def model(self) -> str:
                return "custom-v1"

            @property
            def dimension(self) -> int:
                return 256

            def is_configured(self) -> bool:
                return True

            def embed(self, text: str) -> EmbeddingResponse:
                return EmbeddingResponse(
                    vector=[0.1] * 256,
                    model="custom-v1",
                    input_tokens=1,
                )

        EmbeddingFactory.register("custom", CustomProvider)

        assert "custom" in EmbeddingFactory.list_providers()

        provider = EmbeddingFactory.create("custom")
        assert provider.name == "custom"
        assert provider.dimension == 256

    def test_register_duplicate_raises(self):
        """Test that registering duplicate name raises."""

        class DummyProvider(EmbeddingProvider):
            @property
            def name(self) -> str:
                return "dummy"

            @property
            def model(self) -> str:
                return "dummy"

            @property
            def dimension(self) -> int:
                return 128

            def is_configured(self) -> bool:
                return True

            def embed(self, text: str) -> EmbeddingResponse:
                return EmbeddingResponse(vector=[0.1], model="dummy")

        EmbeddingFactory.register("dummy", DummyProvider)

        with pytest.raises(ValueError, match="already registered"):
            EmbeddingFactory.register("dummy", DummyProvider)

    def test_register_non_provider_raises(self):
        """Test that registering non-provider class raises."""

        class NotAProvider:
            pass

        with pytest.raises(TypeError, match="must inherit from EmbeddingProvider"):
            EmbeddingFactory.register("invalid", NotAProvider)  # type: ignore


class TestGetEmbeddingProviderFunction:
    """Tests for convenience function."""

    def test_get_embedding_provider_default(self):
        """Test convenience function with defaults."""
        provider = get_embedding_provider()

        assert isinstance(provider, OpenAIEmbeddingProvider)
        assert provider.model == "text-embedding-3-small"

    def test_get_embedding_provider_with_args(self):
        """Test convenience function with arguments."""
        provider = get_embedding_provider(
            "openai",
            model="text-embedding-3-large",
        )

        assert provider.model == "text-embedding-3-large"

    def test_get_embedding_provider_unknown_raises(self):
        """Test convenience function with unknown provider."""
        with pytest.raises(ValueError, match="Unknown embedding provider"):
            get_embedding_provider("nonexistent")
