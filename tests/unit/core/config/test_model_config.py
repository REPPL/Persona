"""Tests for model configuration loader."""

from pathlib import Path

import yaml
from persona.core.config.model_config import (
    ModelParams,
    get_default_model,
    get_model_params,
    list_configured_models,
    load_model_config,
)


class TestModelParams:
    """Tests for ModelParams dataclass."""

    def test_default_values(self):
        """Test default parameter values."""
        params = ModelParams()

        assert params.name == ""
        assert params.provider == ""
        assert params.description == ""
        assert params.max_tokens == 4096
        assert params.temperature == 0.7
        assert params.top_p == 1.0
        assert params.context_window == 128000

    def test_custom_values(self):
        """Test custom parameter values."""
        params = ModelParams(
            name="gpt-4o",
            provider="openai",
            description="Test model",
            max_tokens=8192,
            temperature=0.5,
        )

        assert params.name == "gpt-4o"
        assert params.provider == "openai"
        assert params.description == "Test model"
        assert params.max_tokens == 8192
        assert params.temperature == 0.5


class TestLoadModelConfig:
    """Tests for load_model_config function."""

    def test_returns_defaults_when_no_config_dir(self):
        """Test returns defaults when config directory doesn't exist."""
        # Use a non-existent provider
        params = load_model_config("nonexistent", "test-model")

        assert params.name == "test-model"
        assert params.provider == "nonexistent"
        assert params.max_tokens == 4096
        assert params.temperature == 0.7

    def test_loads_from_yaml_file(self, tmp_path: Path):
        """Test loading from YAML config file."""
        # Create temp config structure
        config_dir = tmp_path / "config" / "models" / "openai"
        config_dir.mkdir(parents=True)

        config_file = config_dir / "gpt-4o.yaml"
        config_file.write_text(
            yaml.dump(
                {
                    "name": "gpt-4o",
                    "provider": "openai",
                    "description": "Test GPT-4o",
                    "parameters": {
                        "max_tokens": 8192,
                        "temperature": 0.5,
                    },
                }
            )
        )

        # Temporarily patch get_config_dir
        import persona.core.config.model_config as mc

        original_get_config_dir = mc.get_config_dir

        try:
            mc.get_config_dir = lambda: tmp_path / "config"
            params = load_model_config("openai", "gpt-4o")

            assert params.name == "gpt-4o"
            assert params.provider == "openai"
            assert params.description == "Test GPT-4o"
            assert params.max_tokens == 8192
            assert params.temperature == 0.5
        finally:
            mc.get_config_dir = original_get_config_dir


class TestGetModelParams:
    """Tests for get_model_params convenience function."""

    def test_wrapper_returns_model_params(self):
        """Test that get_model_params returns ModelParams."""
        params = get_model_params("openai", "gpt-4o")

        assert isinstance(params, ModelParams)
        assert params.name == "gpt-4o"
        assert params.provider == "openai"


class TestGetDefaultModel:
    """Tests for get_default_model function."""

    def test_fallback_defaults(self):
        """Test fallback default models."""
        assert get_default_model("openai") == "gpt-4o"
        assert get_default_model("anthropic") == "claude-sonnet-4-20250514"
        assert get_default_model("gemini") == "gemini-2.5-flash"
        assert get_default_model("ollama") == "llama3:8b"

    def test_unknown_provider_returns_empty(self):
        """Test unknown provider returns empty string."""
        assert get_default_model("unknown") == ""


class TestListConfiguredModels:
    """Tests for list_configured_models function."""

    def test_returns_empty_when_no_config(self):
        """Test returns empty list when no config directory."""
        import persona.core.config.model_config as mc

        original_get_config_dir = mc.get_config_dir

        try:
            mc.get_config_dir = lambda: Path("/nonexistent/path")
            models = list_configured_models()
            assert models == []
        finally:
            mc.get_config_dir = original_get_config_dir
