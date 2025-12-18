"""
Tests for API configuration.
"""


import pytest
from persona.api.config import APIConfig


def test_api_config_defaults():
    """Test default configuration values."""
    config = APIConfig()

    assert config.host == "127.0.0.1"
    assert config.port == 8000
    assert config.workers == 1
    assert config.reload is False
    assert config.auth_enabled is False
    assert config.rate_limit_enabled is True
    assert config.rate_limit_requests == 100
    assert config.rate_limit_window == 60


def test_api_config_from_env(monkeypatch):
    """Test configuration loading from environment."""
    monkeypatch.setenv("PERSONA_API_HOST", "0.0.0.0")
    monkeypatch.setenv("PERSONA_API_PORT", "9000")
    monkeypatch.setenv("PERSONA_API_AUTH_ENABLED", "true")
    monkeypatch.setenv("PERSONA_API_AUTH_TOKEN", "test-token")

    config = APIConfig()

    assert config.host == "0.0.0.0"
    assert config.port == 9000
    assert config.auth_enabled is True
    assert config.auth_token == "test-token"


def test_api_config_validation():
    """Test configuration validation."""
    # Valid config
    config = APIConfig(port=8080)
    assert config.port == 8080

    # Invalid port (too low)
    with pytest.raises(Exception):
        APIConfig(port=100)

    # Invalid port (too high)
    with pytest.raises(Exception):
        APIConfig(port=70000)


def test_is_auth_required():
    """Test authentication requirement check."""
    # Auth disabled
    config = APIConfig(auth_enabled=False)
    assert config.is_auth_required() is False

    # Auth enabled but no token
    config = APIConfig(auth_enabled=True)
    assert config.is_auth_required() is False

    # Auth enabled with token
    config = APIConfig(auth_enabled=True, auth_token="test")
    assert config.is_auth_required() is True


def test_validate_token():
    """Test token validation."""
    config = APIConfig(auth_enabled=True, auth_token="secret123")

    # Valid token
    assert config.validate_token("secret123") is True

    # Invalid token
    assert config.validate_token("wrong") is False

    # Auth disabled - always valid
    config = APIConfig(auth_enabled=False)
    assert config.validate_token("anything") is True
