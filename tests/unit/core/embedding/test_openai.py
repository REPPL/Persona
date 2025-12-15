"""Tests for OpenAI embedding provider."""

import os
from unittest.mock import MagicMock, patch

import pytest

from persona.core.embedding.openai import (
    OPENAI_EMBEDDING_MODELS,
    OpenAIEmbeddingProvider,
)


class TestOpenAIEmbeddingProvider:
    """Tests for OpenAIEmbeddingProvider class."""

    def test_provider_creation(self):
        """Test provider can be created."""
        provider = OpenAIEmbeddingProvider()
        assert provider.name == "openai"
        assert provider.model == "text-embedding-3-small"

    def test_provider_custom_model(self):
        """Test provider with custom model."""
        provider = OpenAIEmbeddingProvider(model="text-embedding-3-large")
        assert provider.model == "text-embedding-3-large"
        assert provider.dimension == 3072

    def test_provider_dimension_default(self):
        """Test default dimension."""
        provider = OpenAIEmbeddingProvider()
        assert provider.dimension == 1536

    def test_provider_dimension_large(self):
        """Test dimension for large model."""
        provider = OpenAIEmbeddingProvider(model="text-embedding-3-large")
        assert provider.dimension == 3072

    def test_provider_dimension_unknown_model(self):
        """Test dimension for unknown model defaults to 1536."""
        provider = OpenAIEmbeddingProvider(model="unknown-model")
        assert provider.dimension == 1536

    def test_is_configured_with_api_key(self):
        """Test is_configured returns True with API key."""
        provider = OpenAIEmbeddingProvider(api_key="test-key")
        assert provider.is_configured() is True

    def test_is_configured_without_api_key(self):
        """Test is_configured returns False without API key."""
        # Temporarily clear environment variable
        original = os.environ.get("OPENAI_API_KEY")
        if original:
            del os.environ["OPENAI_API_KEY"]

        try:
            provider = OpenAIEmbeddingProvider()
            assert provider.is_configured() is False
        finally:
            if original:
                os.environ["OPENAI_API_KEY"] = original

    def test_is_configured_from_env(self):
        """Test is_configured uses environment variable."""
        original = os.environ.get("OPENAI_API_KEY")

        try:
            os.environ["OPENAI_API_KEY"] = "env-test-key"
            provider = OpenAIEmbeddingProvider()
            assert provider.is_configured() is True
        finally:
            if original:
                os.environ["OPENAI_API_KEY"] = original
            else:
                if "OPENAI_API_KEY" in os.environ:
                    del os.environ["OPENAI_API_KEY"]

    def test_embed_raises_without_config(self):
        """Test embed raises when not configured."""
        original = os.environ.get("OPENAI_API_KEY")
        if original:
            del os.environ["OPENAI_API_KEY"]

        try:
            provider = OpenAIEmbeddingProvider()
            with pytest.raises(RuntimeError, match="not configured"):
                provider.embed("test")
        finally:
            if original:
                os.environ["OPENAI_API_KEY"] = original

    def test_embed_raises_empty_text(self):
        """Test embed raises on empty text."""
        provider = OpenAIEmbeddingProvider(api_key="test-key")
        with pytest.raises(ValueError, match="cannot be empty"):
            provider.embed("")

    def test_embed_raises_whitespace_text(self):
        """Test embed raises on whitespace-only text."""
        provider = OpenAIEmbeddingProvider(api_key="test-key")
        with pytest.raises(ValueError, match="cannot be empty"):
            provider.embed("   ")

    @patch("persona.core.embedding.openai.OpenAIEmbeddingProvider._get_client")
    def test_embed_success(self, mock_get_client):
        """Test successful embedding generation."""
        # Mock OpenAI response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(
                embedding=[0.1] * 1536,
                index=0,
                object="embedding",
            )
        ]
        mock_response.model = "text-embedding-3-small"
        mock_response.usage = MagicMock(total_tokens=5)
        mock_client.embeddings.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        provider = OpenAIEmbeddingProvider(api_key="test-key")
        result = provider.embed("Hello, world!")

        assert len(result.vector) == 1536
        assert result.model == "text-embedding-3-small"
        assert result.input_tokens == 5
        assert result.dimensions == 1536

    @patch("persona.core.embedding.openai.OpenAIEmbeddingProvider._get_client")
    def test_embed_batch_success(self, mock_get_client):
        """Test successful batch embedding."""
        # Mock OpenAI response
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.data = [
            MagicMock(embedding=[0.1] * 1536, index=0),
            MagicMock(embedding=[0.2] * 1536, index=1),
        ]
        mock_response.model = "text-embedding-3-small"
        mock_response.usage = MagicMock(total_tokens=10)
        mock_client.embeddings.create.return_value = mock_response
        mock_get_client.return_value = mock_client

        provider = OpenAIEmbeddingProvider(api_key="test-key")
        result = provider.embed_batch(["Hello", "World"])

        assert len(result.embeddings) == 2
        assert result.total_tokens == 10
        assert result.model == "text-embedding-3-small"

    def test_embed_batch_empty_list(self):
        """Test batch embedding with empty list."""
        provider = OpenAIEmbeddingProvider(api_key="test-key")
        result = provider.embed_batch([])

        assert len(result.embeddings) == 0

    def test_embed_batch_raises_without_config(self):
        """Test batch embed raises when not configured."""
        original = os.environ.get("OPENAI_API_KEY")
        if original:
            del os.environ["OPENAI_API_KEY"]

        try:
            provider = OpenAIEmbeddingProvider()
            with pytest.raises(RuntimeError, match="not configured"):
                provider.embed_batch(["test"])
        finally:
            if original:
                os.environ["OPENAI_API_KEY"] = original

    def test_embed_batch_all_empty_raises(self):
        """Test batch embedding with all empty texts raises."""
        provider = OpenAIEmbeddingProvider(api_key="test-key")
        with pytest.raises(ValueError, match="All texts are empty"):
            provider.embed_batch(["", "   ", ""])

    def test_get_cost_estimate(self):
        """Test cost estimation."""
        provider = OpenAIEmbeddingProvider(model="text-embedding-3-small")
        cost = provider.get_cost_estimate(1000)

        # text-embedding-3-small costs $0.00002 per 1K tokens
        assert abs(cost - 0.00002) < 0.0001

    def test_get_cost_estimate_large_model(self):
        """Test cost estimation for large model."""
        provider = OpenAIEmbeddingProvider(model="text-embedding-3-large")
        cost = provider.get_cost_estimate(1000)

        # text-embedding-3-large costs $0.00013 per 1K tokens
        assert abs(cost - 0.00013) < 0.0001


class TestOpenAIModels:
    """Tests for model configurations."""

    def test_models_have_required_fields(self):
        """Test all models have required configuration."""
        for model_name, config in OPENAI_EMBEDDING_MODELS.items():
            assert "dimension" in config, f"{model_name} missing dimension"
            assert "max_tokens" in config, f"{model_name} missing max_tokens"
            assert "cost_per_1k" in config, f"{model_name} missing cost_per_1k"

    def test_known_models(self):
        """Test known model configurations."""
        assert "text-embedding-3-small" in OPENAI_EMBEDDING_MODELS
        assert "text-embedding-3-large" in OPENAI_EMBEDDING_MODELS
        assert "text-embedding-ada-002" in OPENAI_EMBEDDING_MODELS
