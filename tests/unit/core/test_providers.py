"""
Tests for LLM provider functionality (F-002).
"""

import pytest

from persona.core.providers import (
    LLMProvider,
    LLMResponse,
    ProviderFactory,
    OpenAIProvider,
    AnthropicProvider,
    GeminiProvider,
)
from persona.core.providers.base import (
    AuthenticationError,
    ModelNotFoundError,
)


class TestLLMResponse:
    """Tests for LLMResponse dataclass."""

    def test_create_response(self):
        """Test creating an LLM response."""
        response = LLMResponse(
            content="Hello, world!",
            model="test-model",
            input_tokens=10,
            output_tokens=5,
        )

        assert response.content == "Hello, world!"
        assert response.model == "test-model"
        assert response.input_tokens == 10
        assert response.output_tokens == 5

    def test_total_tokens(self):
        """Test total token calculation."""
        response = LLMResponse(
            content="Test",
            model="test-model",
            input_tokens=100,
            output_tokens=50,
        )

        assert response.total_tokens == 150

    def test_default_values(self):
        """Test default values for optional fields."""
        response = LLMResponse(content="Test", model="test-model")

        assert response.input_tokens == 0
        assert response.output_tokens == 0
        assert response.finish_reason == "stop"
        assert response.raw_response == {}


class TestOpenAIProvider:
    """Tests for OpenAI provider."""

    def test_name(self):
        """Test provider name."""
        provider = OpenAIProvider()
        assert provider.name == "openai"

    def test_default_model(self):
        """Test default model."""
        provider = OpenAIProvider()
        assert provider.default_model == "gpt-4o"

    def test_available_models(self):
        """Test available models list."""
        provider = OpenAIProvider()
        models = provider.available_models

        assert "gpt-4o" in models
        assert "gpt-4-turbo" in models
        assert "gpt-3.5-turbo" in models

    def test_is_configured_without_key(self, env_no_api_keys):
        """Test configuration check without API key."""
        provider = OpenAIProvider()
        assert provider.is_configured() is False

    def test_is_configured_with_key(self, env_mock_api_keys):
        """Test configuration check with API key."""
        provider = OpenAIProvider()
        assert provider.is_configured() is True

    def test_validate_model_valid(self):
        """Test model validation with valid model."""
        provider = OpenAIProvider()
        assert provider.validate_model("gpt-4o") is True

    def test_validate_model_invalid(self):
        """Test model validation with invalid model."""
        provider = OpenAIProvider()
        assert provider.validate_model("nonexistent-model") is False

    def test_generate_without_key(self, env_no_api_keys):
        """Test generation without API key raises error."""
        provider = OpenAIProvider()

        with pytest.raises(AuthenticationError):
            provider.generate("Hello")

    def test_generate_invalid_model(self, env_mock_api_keys):
        """Test generation with invalid model raises error."""
        provider = OpenAIProvider()

        with pytest.raises(ModelNotFoundError):
            provider.generate("Hello", model="invalid-model")


class TestAnthropicProvider:
    """Tests for Anthropic provider."""

    def test_name(self):
        """Test provider name."""
        provider = AnthropicProvider()
        assert provider.name == "anthropic"

    def test_default_model(self):
        """Test default model."""
        provider = AnthropicProvider()
        assert "claude" in provider.default_model

    def test_available_models(self):
        """Test available models list."""
        provider = AnthropicProvider()
        models = provider.available_models

        assert any("claude" in m for m in models)

    def test_is_configured_without_key(self, env_no_api_keys):
        """Test configuration check without API key."""
        provider = AnthropicProvider()
        assert provider.is_configured() is False

    def test_is_configured_with_key(self, env_mock_api_keys):
        """Test configuration check with API key."""
        provider = AnthropicProvider()
        assert provider.is_configured() is True


class TestGeminiProvider:
    """Tests for Gemini provider."""

    def test_name(self):
        """Test provider name."""
        provider = GeminiProvider()
        assert provider.name == "gemini"

    def test_default_model(self):
        """Test default model."""
        provider = GeminiProvider()
        assert "gemini" in provider.default_model

    def test_available_models(self):
        """Test available models list."""
        provider = GeminiProvider()
        models = provider.available_models

        assert any("gemini" in m for m in models)

    def test_is_configured_without_key(self, env_no_api_keys):
        """Test configuration check without API key."""
        provider = GeminiProvider()
        assert provider.is_configured() is False


class TestProviderFactory:
    """Tests for ProviderFactory."""

    def test_create_openai(self):
        """Test creating OpenAI provider."""
        provider = ProviderFactory.create("openai")
        assert isinstance(provider, OpenAIProvider)

    def test_create_anthropic(self):
        """Test creating Anthropic provider."""
        provider = ProviderFactory.create("anthropic")
        assert isinstance(provider, AnthropicProvider)

    def test_create_gemini(self):
        """Test creating Gemini provider."""
        provider = ProviderFactory.create("gemini")
        assert isinstance(provider, GeminiProvider)

    def test_create_google_alias(self):
        """Test creating Gemini provider via google alias."""
        provider = ProviderFactory.create("google")
        assert isinstance(provider, GeminiProvider)

    def test_create_case_insensitive(self):
        """Test that provider names are case insensitive."""
        provider = ProviderFactory.create("OpenAI")
        assert isinstance(provider, OpenAIProvider)

    def test_create_unknown_provider(self):
        """Test error for unknown provider."""
        with pytest.raises(ValueError) as excinfo:
            ProviderFactory.create("unknown")

        assert "Unknown provider" in str(excinfo.value)
        assert "Available providers" in str(excinfo.value)

    def test_list_providers(self):
        """Test listing available providers."""
        providers = ProviderFactory.list_providers()

        assert "openai" in providers
        assert "anthropic" in providers
        assert "gemini" in providers

    def test_get_configured_providers_none(self, env_no_api_keys):
        """Test getting configured providers when none are configured."""
        providers = ProviderFactory.get_configured_providers()
        assert providers == []

    def test_get_configured_providers_some(self, env_mock_api_keys):
        """Test getting configured providers when some are configured."""
        providers = ProviderFactory.get_configured_providers()
        assert "openai" in providers
        assert "anthropic" in providers
        assert "gemini" in providers
