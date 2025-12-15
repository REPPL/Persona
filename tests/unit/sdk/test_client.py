"""Tests for PersonaClient SDK wrapper."""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from persona.sdk.client import PersonaClient
from persona.sdk.config import SDKConfig
from persona.sdk.models import PersonaConfig, GenerationResultModel, PersonaModel
from persona.sdk.exceptions import ConfigurationError, DataError


class TestPersonaClientInit:
    """Test PersonaClient initialisation."""

    def test_default_init(self):
        """Test client with defaults."""
        client = PersonaClient()
        assert client.provider == "anthropic"
        assert client.model is None

    def test_with_provider(self):
        """Test client with custom provider."""
        client = PersonaClient(provider="openai")
        assert client.provider == "openai"

    def test_with_model(self):
        """Test client with custom model."""
        client = PersonaClient(provider="openai", model="gpt-4o")
        assert client.provider == "openai"
        assert client.model == "gpt-4o"

    def test_with_config(self):
        """Test client with SDKConfig."""
        config = SDKConfig(default_provider="gemini", default_count=5)
        client = PersonaClient(config=config)
        assert client.provider == "gemini"
        assert client.config.default_count == 5

    def test_provider_override_config(self):
        """Test that constructor args override config."""
        config = SDKConfig(default_provider="gemini")
        client = PersonaClient(provider="openai", config=config)
        assert client.provider == "openai"


class TestPersonaClientGenerate:
    """Test PersonaClient.generate() method."""

    @patch("persona.sdk.generator.PersonaGenerator.generate")
    def test_simple_generate(self, mock_generate):
        """Test simple generation with defaults."""
        # Mock the response
        mock_result = GenerationResultModel(
            personas=[PersonaModel(id="p1", name="Test")],
            model="claude-sonnet-4-5-20250929",
            provider="anthropic",
        )
        mock_generate.return_value = mock_result

        client = PersonaClient()
        result = client.generate(data="./test.csv", count=3)

        assert result is mock_result
        mock_generate.assert_called_once()
        # Check that count was applied
        call_args = mock_generate.call_args
        assert call_args[1]["config"].count == 3

    @patch("persona.sdk.generator.PersonaGenerator.generate")
    def test_generate_with_dict_config(self, mock_generate):
        """Test generation with dictionary config."""
        mock_result = GenerationResultModel(personas=[])
        mock_generate.return_value = mock_result

        client = PersonaClient()
        result = client.generate(
            data="./test.csv",
            config={"complexity": "complex", "detail_level": "detailed"}
        )

        call_args = mock_generate.call_args
        config = call_args[1]["config"]
        assert config.complexity == "complex"
        assert config.detail_level == "detailed"

    @patch("persona.sdk.generator.PersonaGenerator.generate")
    def test_generate_with_persona_config(self, mock_generate):
        """Test generation with PersonaConfig object."""
        mock_result = GenerationResultModel(personas=[])
        mock_generate.return_value = mock_result

        config = PersonaConfig(count=5, complexity="simple")
        client = PersonaClient()
        result = client.generate(data="./test.csv", config=config)

        call_args = mock_generate.call_args
        passed_config = call_args[1]["config"]
        assert passed_config.count == 5
        assert passed_config.complexity == "simple"

    @patch("persona.sdk.generator.PersonaGenerator.generate")
    def test_count_override(self, mock_generate):
        """Test that count parameter overrides config."""
        mock_result = GenerationResultModel(personas=[])
        mock_generate.return_value = mock_result

        config = PersonaConfig(count=3)
        client = PersonaClient()
        result = client.generate(data="./test.csv", count=7, config=config)

        call_args = mock_generate.call_args
        assert call_args[1]["config"].count == 7

    @patch("persona.sdk.client.PersonaGenerator")
    def test_provider_override(self, mock_generator_class):
        """Test provider override for single generation."""
        mock_instance = Mock()
        mock_instance.generate.return_value = GenerationResultModel(personas=[])
        mock_generator_class.return_value = mock_instance

        client = PersonaClient(provider="anthropic")
        result = client.generate(data="./test.csv", provider="openai")

        # Should create new generator with openai
        # Check that the last call (override) was with openai
        calls = mock_generator_class.call_args_list
        assert len(calls) >= 2  # Init + override
        assert calls[-1][1]["provider"] == "openai"


class TestPersonaClientEstimateCost:
    """Test PersonaClient.estimate_cost() method."""

    @patch("persona.sdk.generator.PersonaGenerator.estimate_cost")
    def test_estimate_cost(self, mock_estimate):
        """Test cost estimation."""
        mock_estimate.return_value = {
            "estimated_cost": 0.05,
            "input_tokens": 1000,
            "output_tokens": 500,
        }

        client = PersonaClient()
        estimate = client.estimate_cost("./test.csv", count=3)

        assert estimate["estimated_cost"] == 0.05
        mock_estimate.assert_called_once()


class TestPersonaClientProgressCallback:
    """Test progress callback support."""

    def test_set_progress_callback(self):
        """Test setting progress callback."""
        callback = Mock()
        client = PersonaClient()
        client.set_progress_callback(callback)

        # Callback should be set on generator
        assert client._generator._progress_callback is not None


class TestPersonaClientValidateConfig:
    """Test config validation."""

    @patch("persona.sdk.generator.PersonaGenerator.validate_config")
    def test_validate_config(self, mock_validate):
        """Test configuration validation."""
        mock_validate.return_value = []

        client = PersonaClient()
        config = PersonaConfig(count=3)
        warnings = client.validate_config(config)

        assert warnings == []
        mock_validate.assert_called_once_with(config)


class TestPersonaClientFromConfigFile:
    """Test creating client from config file."""

    def test_from_config_file(self, tmp_path):
        """Test loading client from YAML config file."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
sdk:
  default_provider: openai
  default_model: gpt-4o
  default_count: 5
""")

        client = PersonaClient.from_config_file(config_file)
        assert client.provider == "openai"
        assert client.model == "gpt-4o"
        assert client.config.default_count == 5

    def test_from_config_file_not_found(self):
        """Test error when config file not found."""
        with pytest.raises(ConfigurationError) as exc_info:
            PersonaClient.from_config_file("/nonexistent/config.yaml")

        assert "not found" in str(exc_info.value).lower()


class TestPersonaClientFromEnvironment:
    """Test creating client from environment variables."""

    @patch.dict("os.environ", {"PERSONA_PROVIDER": "gemini", "PERSONA_COUNT": "7"})
    def test_from_environment(self):
        """Test loading client from environment variables."""
        client = PersonaClient.from_environment()
        assert client.provider == "gemini"
        assert client.config.default_count == 7

    def test_from_environment_defaults(self):
        """Test client from environment with no vars set."""
        client = PersonaClient.from_environment()
        # Should fall back to defaults
        assert client.provider == "anthropic"


class TestPersonaClientProperties:
    """Test client properties."""

    def test_provider_property(self):
        """Test provider property."""
        client = PersonaClient(provider="openai")
        assert client.provider == "openai"

    def test_model_property(self):
        """Test model property."""
        client = PersonaClient(provider="openai", model="gpt-4o")
        assert client.model == "gpt-4o"

    def test_config_property(self):
        """Test config property."""
        config = SDKConfig(default_count=10)
        client = PersonaClient(config=config)
        assert client.config.default_count == 10


class TestPersonaClientIntegration:
    """Integration tests for PersonaClient."""

    @patch("persona.sdk.generator.PersonaGenerator.generate")
    def test_full_workflow(self, mock_generate):
        """Test complete workflow from creation to generation."""
        # Mock generation result
        mock_result = GenerationResultModel(
            personas=[PersonaModel(id="p1", name="Test")],
            model="claude-sonnet-4-5-20250929",
            provider="anthropic",
        )
        mock_generate.return_value = mock_result

        # Create client and generate
        client = PersonaClient(provider="anthropic")
        result = client.generate(data="./test.csv", count=3)

        # Verify result
        assert len(result.personas) == 1
        assert result.personas[0].name == "Test"
        assert result.provider == "anthropic"
