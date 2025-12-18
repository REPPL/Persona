"""
Tests for async provider functionality.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from persona.core.providers.anthropic import AnthropicProvider
from persona.core.providers.base import (
    AuthenticationError,
    ModelNotFoundError,
    RateLimitError,
)
from persona.core.providers.gemini import GeminiProvider
from persona.core.providers.ollama import OllamaProvider
from persona.core.providers.openai import OpenAIProvider


@pytest.mark.asyncio
class TestOpenAIProviderAsync:
    """Test OpenAI provider async functionality."""

    async def test_generate_async_success(self):
        """Test successful async generation."""
        provider = OpenAIProvider(api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "gpt-4o",
            "choices": [
                {
                    "message": {"content": "Test response"},
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
            },
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_instance

            response = await provider.generate_async("Test prompt")

            assert response.content == "Test response"
            assert response.model == "gpt-4o"
            assert response.input_tokens == 10
            assert response.output_tokens == 20

    async def test_generate_async_authentication_error(self):
        """Test async generation with authentication error."""
        provider = OpenAIProvider(api_key="invalid-key")

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": {"message": "Invalid API key"}}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_instance

            with pytest.raises(AuthenticationError):
                await provider.generate_async("Test prompt")

    async def test_generate_async_rate_limit_error(self):
        """Test async generation with rate limit error."""
        provider = OpenAIProvider(api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.json.return_value = {"error": {"message": "Rate limit exceeded"}}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_instance

            with pytest.raises(RateLimitError):
                await provider.generate_async("Test prompt")

    async def test_generate_async_invalid_model(self):
        """Test async generation with invalid model."""
        provider = OpenAIProvider(api_key="test-key")

        with pytest.raises(ModelNotFoundError):
            await provider.generate_async("Test prompt", model="invalid-model")


@pytest.mark.asyncio
class TestAnthropicProviderAsync:
    """Test Anthropic provider async functionality."""

    async def test_generate_async_success(self):
        """Test successful async generation."""
        provider = AnthropicProvider(api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "model": "claude-sonnet-4-5-20250929",
            "content": [{"type": "text", "text": "Test response"}],
            "stop_reason": "end_turn",
            "usage": {
                "input_tokens": 10,
                "output_tokens": 20,
            },
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_instance

            response = await provider.generate_async("Test prompt")

            assert response.content == "Test response"
            assert response.model == "claude-sonnet-4-5-20250929"
            assert response.input_tokens == 10
            assert response.output_tokens == 20

    async def test_generate_async_authentication_error(self):
        """Test async generation with authentication error."""
        provider = AnthropicProvider(api_key="invalid-key")

        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": {"message": "Invalid API key"}}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_instance

            with pytest.raises(AuthenticationError):
                await provider.generate_async("Test prompt")


@pytest.mark.asyncio
class TestGeminiProviderAsync:
    """Test Gemini provider async functionality."""

    async def test_generate_async_success(self):
        """Test successful async generation."""
        provider = GeminiProvider(api_key="test-key")

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "candidates": [
                {
                    "content": {"parts": [{"text": "Test response"}]},
                    "finishReason": "STOP",
                }
            ],
            "usageMetadata": {
                "promptTokenCount": 10,
                "candidatesTokenCount": 20,
            },
        }

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_instance

            response = await provider.generate_async("Test prompt")

            assert response.content == "Test response"
            assert response.model == "gemini-1.5-pro"
            assert response.input_tokens == 10
            assert response.output_tokens == 20

    async def test_generate_async_authentication_error(self):
        """Test async generation with authentication error."""
        provider = GeminiProvider(api_key="invalid-key")

        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"error": {"message": "Invalid API key"}}

        with patch("httpx.AsyncClient") as mock_client:
            mock_instance = MagicMock()
            mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
            mock_instance.__aexit__ = AsyncMock(return_value=None)
            mock_instance.post = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_instance

            with pytest.raises(AuthenticationError):
                await provider.generate_async("Test prompt")


@pytest.mark.asyncio
class TestBaseProviderAsyncFallback:
    """Test base provider async fallback for providers without native async."""

    async def test_generate_async_uses_sync_fallback(self):
        """Test that base provider falls back to sync method in thread pool."""
        provider = OpenAIProvider(api_key="test-key")

        # Mock the sync generate method
        with patch.object(provider, "generate") as mock_generate:
            mock_generate.return_value = MagicMock(
                content="Test response",
                model="gpt-4o",
                input_tokens=10,
                output_tokens=20,
            )

            # Call the base class async method (would be used by providers without native async)
            from persona.core.providers.base import LLMProvider

            response = await LLMProvider.generate_async(
                provider, "Test prompt", model="gpt-4o"
            )

            # Verify sync method was called
            mock_generate.assert_called_once()


@pytest.mark.asyncio
class TestOllamaProviderAsync:
    """Test Ollama provider async functionality."""

    async def test_generate_async_success(self):
        """Test successful async generation."""
        provider = OllamaProvider(model="llama3:8b")

        # Mock is_configured to return True
        with patch.object(provider, "is_configured", return_value=True):
            # Set the cache directly to mock available models
            provider._available_models_cache = ["llama3:8b"]

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "model": "llama3:8b",
                "message": {"content": "Test async response"},
                "done": True,
                "prompt_eval_count": 12,
                "eval_count": 28,
            }

            with patch("httpx.AsyncClient") as mock_client:
                mock_instance = MagicMock()
                mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
                mock_instance.__aexit__ = AsyncMock(return_value=None)
                mock_instance.post = AsyncMock(return_value=mock_response)
                mock_client.return_value = mock_instance

                response = await provider.generate_async("Test prompt")

                assert response.content == "Test async response"
                assert response.model == "llama3:8b"
                assert response.input_tokens == 12
                assert response.output_tokens == 28
                assert response.finish_reason == "stop"

    async def test_generate_async_with_system_prompt(self):
        """Test async generation with system prompt."""
        provider = OllamaProvider(model="llama3:8b")

        with patch.object(provider, "is_configured", return_value=True):
            provider._available_models_cache = ["llama3:8b"]

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "model": "llama3:8b",
                "message": {"content": "Test response"},
                "done": True,
                "prompt_eval_count": 20,
                "eval_count": 30,
            }

            with patch("httpx.AsyncClient") as mock_client:
                mock_instance = MagicMock()
                mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
                mock_instance.__aexit__ = AsyncMock(return_value=None)
                mock_instance.post = AsyncMock(return_value=mock_response)
                mock_client.return_value = mock_instance

                response = await provider.generate_async(
                    "Test prompt", system_prompt="You are helpful"
                )

                # Verify messages structure
                call_args = mock_instance.post.call_args
                payload = call_args[1]["json"]
                assert len(payload["messages"]) == 2
                assert payload["messages"][0]["role"] == "system"
                assert payload["messages"][1]["role"] == "user"

    async def test_generate_async_not_configured(self):
        """Test async generation when Ollama is not running."""
        provider = OllamaProvider()

        with patch.object(provider, "is_configured", return_value=False):
            with pytest.raises(AuthenticationError, match="Ollama is not running"):
                await provider.generate_async("Test prompt")

    async def test_generate_async_model_not_found(self):
        """Test async generation with unavailable model."""
        provider = OllamaProvider()

        with patch.object(provider, "is_configured", return_value=True):
            provider._available_models_cache = ["llama3:8b"]
            with pytest.raises(
                ModelNotFoundError, match="Model 'invalid' not available"
            ):
                await provider.generate_async("Test prompt", model="invalid")

    async def test_generate_async_timeout_error(self):
        """Test async generation with timeout."""
        provider = OllamaProvider(model="llama3:8b", timeout=5.0)

        with patch.object(provider, "is_configured", return_value=True):
            provider._available_models_cache = ["llama3:8b"]

            with patch("httpx.AsyncClient") as mock_client:
                mock_instance = MagicMock()
                mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
                mock_instance.__aexit__ = AsyncMock(return_value=None)
                mock_instance.post = AsyncMock(
                    side_effect=httpx.TimeoutException("Timeout")
                )
                mock_client.return_value = mock_instance

                with pytest.raises(RuntimeError, match="Ollama request timed out"):
                    await provider.generate_async("Test prompt")

    async def test_generate_async_custom_parameters(self):
        """Test async generation with custom parameters."""
        provider = OllamaProvider(model="llama3:8b")

        with patch.object(provider, "is_configured", return_value=True):
            provider._available_models_cache = ["llama3:8b"]

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "model": "llama3:8b",
                "message": {"content": "Response"},
                "done": True,
                "prompt_eval_count": 10,
                "eval_count": 20,
            }

            with patch("httpx.AsyncClient") as mock_client:
                mock_instance = MagicMock()
                mock_instance.__aenter__ = AsyncMock(return_value=mock_instance)
                mock_instance.__aexit__ = AsyncMock(return_value=None)
                mock_instance.post = AsyncMock(return_value=mock_response)
                mock_client.return_value = mock_instance

                await provider.generate_async(
                    "Test prompt", temperature=0.9, max_tokens=2048
                )

                # Verify custom parameters
                call_args = mock_instance.post.call_args
                payload = call_args[1]["json"]
                assert payload["options"]["temperature"] == 0.9
                assert payload["options"]["num_predict"] == 2048
