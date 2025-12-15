"""
Tests for Ollama provider functionality.
"""

import pytest
import httpx
from unittest.mock import patch, MagicMock

from persona.core.providers.ollama import OllamaProvider
from persona.core.providers.base import (
    AuthenticationError,
    ModelNotFoundError,
)


class TestOllamaProvider:
    """Test Ollama provider basic functionality."""

    def test_init_default_values(self):
        """Test provider initialisation with defaults."""
        provider = OllamaProvider()
        assert provider.name == "ollama"
        assert provider._base_url == "http://localhost:11434"
        assert provider._timeout == 300.0

    def test_init_custom_values(self):
        """Test provider initialisation with custom values."""
        provider = OllamaProvider(
            base_url="http://custom:8080",
            model="llama3:8b",
            timeout=600.0,
        )
        assert provider._base_url == "http://custom:8080"
        assert provider._default_model == "llama3:8b"
        assert provider._timeout == 600.0

    def test_init_removes_trailing_slash(self):
        """Test that trailing slash is removed from base URL."""
        provider = OllamaProvider(base_url="http://localhost:11434/")
        assert provider._base_url == "http://localhost:11434"

    def test_default_model_with_explicit_model(self):
        """Test default model when explicitly set."""
        provider = OllamaProvider(model="qwen2.5:72b")
        assert provider.default_model == "qwen2.5:72b"

    def test_default_model_auto_detection(self):
        """Test default model auto-detection from available models."""
        provider = OllamaProvider()

        # Mock list_available_models
        with patch.object(provider, "list_available_models") as mock_list:
            mock_list.return_value = ["llama3:8b", "qwen2.5:72b", "mistral:7b"]
            # Should prefer qwen2.5:72b (high quality)
            assert provider.default_model == "qwen2.5:72b"

    def test_default_model_fallback(self):
        """Test default model fallback when Ollama not running."""
        provider = OllamaProvider()

        # Mock list_available_models to raise exception
        with patch.object(provider, "list_available_models") as mock_list:
            mock_list.side_effect = RuntimeError("Ollama not running")
            # Should fall back to first common model (qwen2.5:72b in COMMON_MODELS)
            # Actually it should return the first in COMMON_MODELS.keys()
            # But available_models returns sorted list of common models
            default = provider.default_model
            # Should be one of the common models
            assert default in provider.COMMON_MODELS.keys()

    def test_list_available_models_success(self):
        """Test listing available models from Ollama."""
        provider = OllamaProvider()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [
                {"name": "llama3:8b"},
                {"name": "mistral:7b"},
                {"name": "qwen2.5:7b"},
            ]
        }

        with patch("httpx.Client") as mock_client:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.get = MagicMock(return_value=mock_response)
            mock_client.return_value = mock_instance

            models = provider.list_available_models()

            assert models == ["llama3:8b", "mistral:7b", "qwen2.5:7b"]
            mock_instance.get.assert_called_once_with(
                "http://localhost:11434/api/tags"
            )

    def test_list_available_models_connection_error(self):
        """Test listing models when Ollama is not running."""
        provider = OllamaProvider()

        with patch("httpx.Client") as mock_client:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.get = MagicMock(side_effect=httpx.ConnectError("Connection refused"))
            mock_client.return_value = mock_instance

            with pytest.raises(RuntimeError, match="Cannot connect to Ollama"):
                provider.list_available_models()

    def test_is_configured_true(self):
        """Test is_configured when Ollama is running."""
        provider = OllamaProvider()

        mock_response = MagicMock()
        mock_response.status_code = 200

        with patch("httpx.Client") as mock_client:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.get = MagicMock(return_value=mock_response)
            mock_client.return_value = mock_instance

            assert provider.is_configured() is True

    def test_is_configured_false(self):
        """Test is_configured when Ollama is not running."""
        provider = OllamaProvider()

        with patch("httpx.Client") as mock_client:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.get = MagicMock(side_effect=httpx.ConnectError("Connection refused"))
            mock_client.return_value = mock_instance

            assert provider.is_configured() is False

    def test_health_check_success(self):
        """Test health check when Ollama is running."""
        provider = OllamaProvider()

        with patch.object(provider, "list_available_models") as mock_list:
            mock_list.return_value = ["llama3:8b", "mistral:7b"]

            health = provider.health_check()

            assert health["is_running"] is True
            assert health["base_url"] == "http://localhost:11434"
            assert health["available_models"] == ["llama3:8b", "mistral:7b"]
            assert health["model_count"] == 2

    def test_health_check_failure(self):
        """Test health check when Ollama is not running."""
        provider = OllamaProvider()

        with patch.object(provider, "list_available_models") as mock_list:
            mock_list.side_effect = RuntimeError("Ollama not running")

            health = provider.health_check()

            assert health["is_running"] is False
            assert health["base_url"] == "http://localhost:11434"
            assert health["available_models"] == []
            assert health["model_count"] == 0
            assert "error" in health

    def test_generate_success(self):
        """Test successful generation."""
        provider = OllamaProvider(model="llama3:8b")

        # Mock is_configured to return True
        with patch.object(provider, "is_configured", return_value=True):
            # Set the cache directly to mock available models
            provider._available_models_cache = ["llama3:8b"]

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "model": "llama3:8b",
                "message": {"content": "Test response from Ollama"},
                "done": True,
                "prompt_eval_count": 15,
                "eval_count": 25,
            }

            with patch("httpx.Client") as mock_client:
                mock_instance = MagicMock()
                mock_instance.__enter__ = MagicMock(return_value=mock_instance)
                mock_instance.__exit__ = MagicMock(return_value=None)
                mock_instance.post = MagicMock(return_value=mock_response)
                mock_client.return_value = mock_instance

                response = provider.generate("Test prompt")

                assert response.content == "Test response from Ollama"
                assert response.model == "llama3:8b"
                assert response.input_tokens == 15
                assert response.output_tokens == 25
                assert response.finish_reason == "stop"

    def test_generate_with_system_prompt(self):
        """Test generation with system prompt."""
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

            with patch("httpx.Client") as mock_client:
                mock_instance = MagicMock()
                mock_instance.__enter__ = MagicMock(return_value=mock_instance)
                mock_instance.__exit__ = MagicMock(return_value=None)
                mock_instance.post = MagicMock(return_value=mock_response)
                mock_client.return_value = mock_instance

                response = provider.generate(
                    "Test prompt",
                    system_prompt="You are a helpful assistant"
                )

                # Verify the request included system message
                call_args = mock_instance.post.call_args
                payload = call_args[1]["json"]
                assert len(payload["messages"]) == 2
                assert payload["messages"][0]["role"] == "system"
                assert payload["messages"][0]["content"] == "You are a helpful assistant"
                assert payload["messages"][1]["role"] == "user"
                assert payload["messages"][1]["content"] == "Test prompt"

    def test_generate_not_configured(self):
        """Test generation when Ollama is not running."""
        provider = OllamaProvider()

        with patch.object(provider, "is_configured", return_value=False):
            with pytest.raises(AuthenticationError, match="Ollama is not running"):
                provider.generate("Test prompt")

    def test_generate_model_not_found(self):
        """Test generation with unavailable model."""
        provider = OllamaProvider()

        with patch.object(provider, "is_configured", return_value=True):
            provider._available_models_cache = ["llama3:8b"]
            with pytest.raises(ModelNotFoundError, match="Model 'invalid-model' not available"):
                provider.generate("Test prompt", model="invalid-model")

    def test_generate_custom_parameters(self):
        """Test generation with custom temperature and max_tokens."""
        provider = OllamaProvider(model="llama3:8b")

        with patch.object(provider, "is_configured", return_value=True):
            provider._available_models_cache = ["llama3:8b"]

            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "model": "llama3:8b",
                "message": {"content": "Test response"},
                "done": True,
                "prompt_eval_count": 10,
                "eval_count": 20,
            }

            with patch("httpx.Client") as mock_client:
                mock_instance = MagicMock()
                mock_instance.__enter__ = MagicMock(return_value=mock_instance)
                mock_instance.__exit__ = MagicMock(return_value=None)
                mock_instance.post = MagicMock(return_value=mock_response)
                mock_client.return_value = mock_instance

                response = provider.generate(
                    "Test prompt",
                    temperature=0.9,
                    max_tokens=2048
                )

                # Verify custom parameters were used
                call_args = mock_instance.post.call_args
                payload = call_args[1]["json"]
                assert payload["options"]["temperature"] == 0.9
                assert payload["options"]["num_predict"] == 2048

    def test_generate_timeout_error(self):
        """Test generation with timeout error."""
        provider = OllamaProvider(model="llama3:8b", timeout=5.0)

        with patch.object(provider, "is_configured", return_value=True):
            provider._available_models_cache = ["llama3:8b"]

            with patch("httpx.Client") as mock_client:
                mock_instance = MagicMock()
                mock_instance.__enter__ = MagicMock(return_value=mock_instance)
                mock_instance.__exit__ = MagicMock(return_value=None)
                mock_instance.post = MagicMock(side_effect=httpx.TimeoutException("Timeout"))
                mock_client.return_value = mock_instance

                with pytest.raises(RuntimeError, match="Ollama request timed out"):
                    provider.generate("Test prompt")

    def test_generate_api_error(self):
        """Test generation with API error."""
        provider = OllamaProvider(model="llama3:8b")

        with patch.object(provider, "is_configured", return_value=True):
            provider._available_models_cache = ["llama3:8b"]

            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal server error"
            mock_response.json.return_value = {"error": "Model loading failed"}

            with patch("httpx.Client") as mock_client:
                mock_instance = MagicMock()
                mock_instance.__enter__ = MagicMock(return_value=mock_instance)
                mock_instance.__exit__ = MagicMock(return_value=None)
                mock_instance.post = MagicMock(return_value=mock_response)
                mock_client.return_value = mock_instance

                with pytest.raises(RuntimeError, match="Ollama API error"):
                    provider.generate("Test prompt")

    def test_available_models_caching(self):
        """Test that available models are cached."""
        provider = OllamaProvider()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "models": [{"name": "llama3:8b"}]
        }

        with patch("httpx.Client") as mock_client:
            mock_instance = MagicMock()
            mock_instance.__enter__ = MagicMock(return_value=mock_instance)
            mock_instance.__exit__ = MagicMock(return_value=None)
            mock_instance.get = MagicMock(return_value=mock_response)
            mock_client.return_value = mock_instance

            # First call should hit the API
            models1 = provider.available_models
            assert models1 == ["llama3:8b"]

            # Second call should use cache
            models2 = provider.available_models
            assert models2 == ["llama3:8b"]

            # Should only have called the API once
            assert mock_instance.get.call_count == 1


@pytest.mark.real_api
class TestOllamaProviderIntegration:
    """
    Integration tests requiring a real Ollama instance.

    These tests are marked with @pytest.mark.real_api and should be
    run separately with: pytest -m real_api

    Prerequisites:
    - Ollama must be running (ollama serve)
    - At least one model must be pulled (e.g., ollama pull llama3:8b)
    """

    def test_real_health_check(self):
        """Test health check with real Ollama instance."""
        provider = OllamaProvider()
        health = provider.health_check()

        # Should have at least some fields
        assert "is_running" in health
        assert "base_url" in health

        # If running, should have models
        if health["is_running"]:
            assert health["model_count"] > 0
            assert len(health["available_models"]) > 0

    def test_real_list_models(self):
        """Test listing models from real Ollama instance."""
        provider = OllamaProvider()

        if not provider.is_configured():
            pytest.skip("Ollama not running")

        models = provider.list_available_models()
        assert isinstance(models, list)
        assert len(models) > 0

    def test_real_generation(self):
        """Test generation with real Ollama instance."""
        provider = OllamaProvider()

        if not provider.is_configured():
            pytest.skip("Ollama not running")

        # Use a small model for faster testing
        available = provider.available_models
        if not available:
            pytest.skip("No models available")

        # Try to use a small model if available
        model = None
        for preferred in ["llama3.2:3b", "llama3:8b", "mistral:7b"]:
            if preferred in available:
                model = preferred
                break

        if model is None:
            model = available[0]

        response = provider.generate(
            "Say hello in exactly 3 words",
            model=model,
            max_tokens=20,
            temperature=0.7
        )

        assert response.content
        assert isinstance(response.content, str)
        assert len(response.content) > 0
        assert response.model == model
