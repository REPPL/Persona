"""Tests for CustomVendorProvider."""

import os
from unittest.mock import Mock, patch

import pytest
from persona.core.config.vendor import AuthType, VendorConfig
from persona.core.providers.base import (
    AuthenticationError,
    ModelNotFoundError,
    RateLimitError,
)
from persona.core.providers.custom import CustomVendorProvider


class TestCustomVendorProviderInit:
    """Tests for CustomVendorProvider initialisation."""

    def test_basic_init(self):
        """Test basic initialisation."""
        config = VendorConfig(
            id="test-vendor",
            name="Test Vendor",
            api_base="https://api.example.com",
        )
        provider = CustomVendorProvider(config)

        assert provider.name == "test-vendor"
        assert provider.display_name == "Test Vendor"

    def test_with_api_key(self):
        """Test initialisation with explicit API key."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            auth_env="TEST_KEY",
        )
        provider = CustomVendorProvider(config, api_key="explicit-key")

        assert provider.is_configured() is True


class TestCustomVendorProviderProperties:
    """Tests for CustomVendorProvider properties."""

    def test_name(self):
        """Test name property returns vendor ID."""
        config = VendorConfig(
            id="my-vendor",
            name="My Vendor",
            api_base="https://api.example.com",
        )
        provider = CustomVendorProvider(config)

        assert provider.name == "my-vendor"

    def test_display_name(self):
        """Test display_name returns human-readable name."""
        config = VendorConfig(
            id="my-vendor",
            name="My Custom Vendor",
            api_base="https://api.example.com",
        )
        provider = CustomVendorProvider(config)

        assert provider.display_name == "My Custom Vendor"

    def test_default_model_from_config(self):
        """Test default_model from config."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            default_model="gpt-4",
        )
        provider = CustomVendorProvider(config)

        assert provider.default_model == "gpt-4"

    def test_default_model_from_models_list(self):
        """Test default_model falls back to first in models list."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            models=["model-a", "model-b"],
        )
        provider = CustomVendorProvider(config)

        assert provider.default_model == "model-a"

    def test_default_model_fallback(self):
        """Test default_model fallback when nothing specified."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
        )
        provider = CustomVendorProvider(config)

        assert provider.default_model == "default"

    def test_available_models(self):
        """Test available_models from config."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            models=["model-a", "model-b", "model-c"],
        )
        provider = CustomVendorProvider(config)

        assert provider.available_models == ["model-a", "model-b", "model-c"]


class TestCustomVendorProviderAuth:
    """Tests for CustomVendorProvider authentication."""

    def test_is_configured_with_explicit_key(self):
        """Test is_configured with explicit API key."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            auth_env="TEST_KEY",
        )
        provider = CustomVendorProvider(config, api_key="my-key")

        assert provider.is_configured() is True

    def test_is_configured_from_env(self):
        """Test is_configured from environment."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            auth_env="TEST_KEY",
        )
        provider = CustomVendorProvider(config)

        with patch.dict(os.environ, {"TEST_KEY": "env-key"}):
            assert provider.is_configured() is True

    def test_is_configured_not_set(self):
        """Test is_configured when not set."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            auth_env="NONEXISTENT_KEY",
        )
        provider = CustomVendorProvider(config)

        assert provider.is_configured() is False

    def test_is_configured_no_auth_required(self):
        """Test is_configured for local vendor."""
        config = VendorConfig(
            id="local",
            name="Local",
            api_base="http://localhost:8080",
            auth_type=AuthType.NONE,
        )
        provider = CustomVendorProvider(config)

        assert provider.is_configured() is True

    def test_build_headers_bearer(self):
        """Test header building with bearer auth."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            auth_type=AuthType.BEARER,
            auth_env="TEST_KEY",
        )
        provider = CustomVendorProvider(config, api_key="my-key")

        headers = provider._build_headers()
        assert headers["Authorization"] == "Bearer my-key"

    def test_build_headers_header_auth(self):
        """Test header building with header auth."""
        config = VendorConfig(
            id="azure",
            name="Azure",
            api_base="https://api.example.com",
            auth_type=AuthType.HEADER,
            auth_env="AZURE_KEY",
            auth_header="api-key",
        )
        provider = CustomVendorProvider(config, api_key="azure-key")

        headers = provider._build_headers()
        assert headers["api-key"] == "azure-key"


class TestCustomVendorProviderRequest:
    """Tests for CustomVendorProvider request building."""

    def test_build_request_openai_format(self):
        """Test request payload in OpenAI format."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            request_format="openai",
        )
        provider = CustomVendorProvider(config)

        payload = provider._build_request_payload(
            prompt="Hello",
            model="gpt-4",
            max_tokens=100,
            temperature=0.7,
        )

        assert payload["model"] == "gpt-4"
        assert payload["messages"] == [{"role": "user", "content": "Hello"}]
        assert payload["max_tokens"] == 100
        assert payload["temperature"] == 0.7

    def test_build_request_anthropic_format(self):
        """Test request payload in Anthropic format."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            request_format="anthropic",
        )
        provider = CustomVendorProvider(config)

        payload = provider._build_request_payload(
            prompt="Hello",
            model="claude-3",
            max_tokens=100,
            temperature=0.7,
        )

        assert payload["model"] == "claude-3"
        assert payload["messages"] == [{"role": "user", "content": "Hello"}]
        assert payload["max_tokens"] == 100
        assert (
            "temperature" not in payload
        )  # Anthropic format doesn't include temp in build

    def test_build_request_o1_model_no_temperature(self):
        """Test temperature is excluded for o1 models."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            request_format="openai",
        )
        provider = CustomVendorProvider(config)

        payload = provider._build_request_payload(
            prompt="Hello",
            model="o1-preview",
            max_tokens=100,
            temperature=0.7,
        )

        assert "temperature" not in payload


class TestCustomVendorProviderResponse:
    """Tests for CustomVendorProvider response parsing."""

    def test_parse_response_openai(self):
        """Test parsing OpenAI format response."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            response_format="openai",
        )
        provider = CustomVendorProvider(config)

        data = {
            "choices": [
                {
                    "message": {"content": "Hello there!"},
                    "finish_reason": "stop",
                }
            ],
            "model": "gpt-4",
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
            },
        }

        response = provider._parse_response(data, "gpt-4")

        assert response.content == "Hello there!"
        assert response.model == "gpt-4"
        assert response.input_tokens == 10
        assert response.output_tokens == 5

    def test_parse_response_anthropic(self):
        """Test parsing Anthropic format response."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            response_format="anthropic",
        )
        provider = CustomVendorProvider(config)

        data = {
            "content": [{"type": "text", "text": "Hello there!"}],
            "model": "claude-3",
            "usage": {
                "input_tokens": 10,
                "output_tokens": 5,
            },
            "stop_reason": "end_turn",
        }

        response = provider._parse_response(data, "claude-3")

        assert response.content == "Hello there!"
        assert response.model == "claude-3"
        assert response.input_tokens == 10
        assert response.output_tokens == 5


class TestCustomVendorProviderGenerate:
    """Tests for CustomVendorProvider generate method."""

    def test_generate_not_configured(self):
        """Test generate raises error when not configured."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            auth_env="NONEXISTENT_KEY",
        )
        provider = CustomVendorProvider(config)

        with pytest.raises(AuthenticationError) as exc_info:
            provider.generate("Hello")

        assert "not configured" in str(exc_info.value).lower()

    def test_generate_model_not_found(self):
        """Test generate raises error for unknown model."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            auth_type=AuthType.NONE,
            models=["model-a", "model-b"],
        )
        provider = CustomVendorProvider(config)

        with pytest.raises(ModelNotFoundError):
            provider.generate("Hello", model="unknown-model")

    def test_generate_success(self):
        """Test successful generation."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            auth_type=AuthType.NONE,
        )
        provider = CustomVendorProvider(config)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {"content": "Generated response"},
                    "finish_reason": "stop",
                }
            ],
            "model": "default",
            "usage": {"prompt_tokens": 10, "completion_tokens": 20},
        }

        with patch("httpx.Client") as MockClient:
            mock_client = MockClient.return_value.__enter__.return_value
            mock_client.post.return_value = mock_response

            response = provider.generate("Hello")

            assert response.content == "Generated response"
            assert response.input_tokens == 10
            assert response.output_tokens == 20

    def test_generate_auth_error(self):
        """Test generate handles 401 error."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            auth_type=AuthType.NONE,
        )
        provider = CustomVendorProvider(config)

        mock_response = Mock()
        mock_response.status_code = 401

        with patch("httpx.Client") as MockClient:
            mock_client = MockClient.return_value.__enter__.return_value
            mock_client.post.return_value = mock_response

            with pytest.raises(AuthenticationError):
                provider.generate("Hello")

    def test_generate_rate_limit_error(self):
        """Test generate handles 429 error."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            auth_type=AuthType.NONE,
        )
        provider = CustomVendorProvider(config)

        mock_response = Mock()
        mock_response.status_code = 429

        with patch("httpx.Client") as MockClient:
            mock_client = MockClient.return_value.__enter__.return_value
            mock_client.post.return_value = mock_response

            with pytest.raises(RateLimitError):
                provider.generate("Hello")


class TestCustomVendorProviderTestConnection:
    """Tests for CustomVendorProvider test_connection method."""

    def test_test_connection_not_configured(self):
        """Test test_connection when not configured."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            auth_env="NONEXISTENT_KEY",
        )
        provider = CustomVendorProvider(config)

        result = provider.test_connection()

        assert result["configured"] is False
        assert "error" in result

    def test_test_connection_success(self):
        """Test successful connection test."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            auth_type=AuthType.NONE,
        )
        provider = CustomVendorProvider(config)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {"content": "OK"},
                    "finish_reason": "stop",
                }
            ],
            "model": "test-model",
            "usage": {"prompt_tokens": 5, "completion_tokens": 1},
        }

        with patch("httpx.Client") as MockClient:
            mock_client = MockClient.return_value.__enter__.return_value
            mock_client.post.return_value = mock_response

            result = provider.test_connection()

            assert result["success"] is True
            assert result["response_model"] == "test-model"

    def test_test_connection_failure(self):
        """Test failed connection test."""
        config = VendorConfig(
            id="test",
            name="Test",
            api_base="https://api.example.com",
            auth_type=AuthType.NONE,
        )
        provider = CustomVendorProvider(config)

        with patch("httpx.Client") as MockClient:
            mock_client = MockClient.return_value.__enter__.return_value
            mock_client.post.side_effect = Exception("Connection failed")

            result = provider.test_connection()

            assert result["success"] is False
            assert "Connection failed" in result["error"]
