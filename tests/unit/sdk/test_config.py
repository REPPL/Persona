"""Tests for SDK configuration management."""

from unittest.mock import patch

import pytest
from persona.sdk.config import SDKConfig
from persona.sdk.exceptions import ConfigurationError


class TestSDKConfigDefaults:
    """Test SDKConfig default values."""

    def test_default_values(self):
        """Test that defaults are correct."""
        config = SDKConfig()
        assert config.default_provider == "anthropic"
        assert config.default_model is None
        assert config.default_count == 3
        assert config.default_complexity == "moderate"
        assert config.default_detail_level == "standard"
        assert config.default_temperature == 0.7

    def test_from_defaults(self):
        """Test from_defaults() class method."""
        config = SDKConfig.from_defaults()
        assert config.default_provider == "anthropic"
        assert config.default_count == 3


class TestSDKConfigCustomValues:
    """Test custom configuration values."""

    def test_custom_provider(self):
        """Test setting custom provider."""
        config = SDKConfig(default_provider="openai")
        assert config.default_provider == "openai"

    def test_custom_model(self):
        """Test setting custom model."""
        config = SDKConfig(default_model="gpt-4o")
        assert config.default_model == "gpt-4o"

    def test_custom_count(self):
        """Test setting custom count."""
        config = SDKConfig(default_count=5)
        assert config.default_count == 5

    def test_custom_complexity(self):
        """Test setting custom complexity."""
        config = SDKConfig(default_complexity="complex")
        assert config.default_complexity == "complex"

    def test_custom_detail_level(self):
        """Test setting custom detail level."""
        config = SDKConfig(default_detail_level="detailed")
        assert config.default_detail_level == "detailed"

    def test_custom_temperature(self):
        """Test setting custom temperature."""
        config = SDKConfig(default_temperature=0.5)
        assert config.default_temperature == 0.5


class TestSDKConfigValidation:
    """Test configuration validation."""

    def test_invalid_provider(self):
        """Test that invalid provider raises error."""
        with pytest.raises(ValueError) as exc_info:
            SDKConfig(default_provider="invalid")
        assert "invalid provider" in str(exc_info.value).lower()

    def test_valid_providers(self):
        """Test all valid providers."""
        for provider in ["anthropic", "openai", "gemini"]:
            config = SDKConfig(default_provider=provider)
            assert config.default_provider == provider

    def test_invalid_complexity(self):
        """Test that invalid complexity raises error."""
        with pytest.raises(ValueError) as exc_info:
            SDKConfig(default_complexity="invalid")
        assert "invalid complexity" in str(exc_info.value).lower()

    def test_valid_complexities(self):
        """Test all valid complexity levels."""
        for complexity in ["simple", "moderate", "complex"]:
            config = SDKConfig(default_complexity=complexity)
            assert config.default_complexity == complexity

    def test_invalid_detail_level(self):
        """Test that invalid detail level raises error."""
        with pytest.raises(ValueError) as exc_info:
            SDKConfig(default_detail_level="invalid")
        assert "invalid detail_level" in str(exc_info.value).lower()

    def test_valid_detail_levels(self):
        """Test all valid detail levels."""
        for level in ["minimal", "standard", "detailed"]:
            config = SDKConfig(default_detail_level=level)
            assert config.default_detail_level == level

    def test_count_min_validation(self):
        """Test count minimum validation."""
        with pytest.raises(ValueError):
            SDKConfig(default_count=0)

    def test_count_max_validation(self):
        """Test count maximum validation."""
        with pytest.raises(ValueError):
            SDKConfig(default_count=21)

    def test_temperature_min_validation(self):
        """Test temperature minimum validation."""
        with pytest.raises(ValueError):
            SDKConfig(default_temperature=-0.1)

    def test_temperature_max_validation(self):
        """Test temperature maximum validation."""
        with pytest.raises(ValueError):
            SDKConfig(default_temperature=2.1)


class TestSDKConfigFromEnvironment:
    """Test loading configuration from environment variables."""

    @patch.dict("os.environ", {"PERSONA_PROVIDER": "openai"})
    def test_provider_from_env(self):
        """Test loading provider from environment."""
        config = SDKConfig.from_environment()
        assert config.default_provider == "openai"

    @patch.dict("os.environ", {"PERSONA_MODEL": "gpt-4o"})
    def test_model_from_env(self):
        """Test loading model from environment."""
        config = SDKConfig.from_environment()
        assert config.default_model == "gpt-4o"

    @patch.dict("os.environ", {"PERSONA_COUNT": "5"})
    def test_count_from_env(self):
        """Test loading count from environment."""
        config = SDKConfig.from_environment()
        assert config.default_count == 5

    @patch.dict("os.environ", {"PERSONA_COMPLEXITY": "complex"})
    def test_complexity_from_env(self):
        """Test loading complexity from environment."""
        config = SDKConfig.from_environment()
        assert config.default_complexity == "complex"

    @patch.dict("os.environ", {"PERSONA_DETAIL_LEVEL": "detailed"})
    def test_detail_level_from_env(self):
        """Test loading detail level from environment."""
        config = SDKConfig.from_environment()
        assert config.default_detail_level == "detailed"

    @patch.dict("os.environ", {"PERSONA_TEMPERATURE": "0.5"})
    def test_temperature_from_env(self):
        """Test loading temperature from environment."""
        config = SDKConfig.from_environment()
        assert config.default_temperature == 0.5

    @patch.dict(
        "os.environ",
        {
            "PERSONA_PROVIDER": "gemini",
            "PERSONA_COUNT": "7",
            "PERSONA_TEMPERATURE": "0.8",
        },
    )
    def test_multiple_from_env(self):
        """Test loading multiple values from environment."""
        config = SDKConfig.from_environment()
        assert config.default_provider == "gemini"
        assert config.default_count == 7
        assert config.default_temperature == 0.8

    def test_from_env_with_no_vars(self):
        """Test that defaults are used when no env vars are set."""
        config = SDKConfig.from_environment()
        assert config.default_provider == "anthropic"
        assert config.default_count == 3

    @patch.dict("os.environ", {"PERSONA_COUNT": "invalid"})
    def test_invalid_count_from_env(self):
        """Test error when env var has invalid value."""
        with pytest.raises(ConfigurationError) as exc_info:
            SDKConfig.from_environment()
        assert "PERSONA_COUNT" in str(exc_info.value)


class TestSDKConfigFromFile:
    """Test loading configuration from YAML file."""

    def test_from_file_basic(self, tmp_path):
        """Test loading basic config from file."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            """
sdk:
  default_provider: openai
  default_count: 5
"""
        )
        config = SDKConfig.from_file(config_file)
        assert config.default_provider == "openai"
        assert config.default_count == 5

    def test_from_file_full(self, tmp_path):
        """Test loading full config from file."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            """
sdk:
  default_provider: gemini
  default_model: gemini-1.5-pro
  default_count: 7
  default_complexity: complex
  default_detail_level: detailed
  default_temperature: 0.8
"""
        )
        config = SDKConfig.from_file(config_file)
        assert config.default_provider == "gemini"
        assert config.default_model == "gemini-1.5-pro"
        assert config.default_count == 7
        assert config.default_complexity == "complex"
        assert config.default_detail_level == "detailed"
        assert config.default_temperature == 0.8

    def test_from_file_without_sdk_key(self, tmp_path):
        """Test loading config without 'sdk' wrapper key."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text(
            """
default_provider: openai
default_count: 5
"""
        )
        config = SDKConfig.from_file(config_file)
        assert config.default_provider == "openai"
        assert config.default_count == 5

    def test_from_file_not_found(self):
        """Test error when config file doesn't exist."""
        with pytest.raises(ConfigurationError) as exc_info:
            SDKConfig.from_file("/nonexistent/config.yaml")
        assert "not found" in str(exc_info.value).lower()

    def test_from_file_invalid_yaml(self, tmp_path):
        """Test error with invalid YAML."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("invalid: yaml: content:")

        with pytest.raises(ConfigurationError) as exc_info:
            SDKConfig.from_file(config_file)
        assert "yaml" in str(exc_info.value).lower()

    def test_from_file_not_dict(self, tmp_path):
        """Test error when YAML is not a dictionary."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("- item1\n- item2")

        with pytest.raises(ConfigurationError) as exc_info:
            SDKConfig.from_file(config_file)
        assert "object" in str(exc_info.value).lower()

    def test_from_file_path_recorded(self, tmp_path):
        """Test that config file path is recorded."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("default_provider: openai")

        config = SDKConfig.from_file(config_file)
        assert config.config_file_path == str(config_file)


class TestSDKConfigFromSources:
    """Test loading configuration from multiple sources."""

    @patch.dict("os.environ", {"PERSONA_PROVIDER": "gemini"})
    def test_from_sources_env_only(self):
        """Test loading from environment only."""
        config = SDKConfig.from_sources()
        assert config.default_provider == "gemini"

    def test_from_sources_file_only(self, tmp_path):
        """Test loading from file only."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("default_provider: openai\ndefault_count: 5")

        config = SDKConfig.from_sources(config_file=config_file, use_environment=False)
        assert config.default_provider == "openai"
        assert config.default_count == 5

    @patch.dict(
        "os.environ", {"PERSONA_COUNT": "10", "PERSONA_PROVIDER": "openai"}, clear=True
    )
    def test_from_sources_file_and_env(self, tmp_path):
        """Test that environment overrides file."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("default_provider: gemini\ndefault_count: 5")

        config = SDKConfig.from_sources(config_file=config_file)
        # Env sets provider and count, overriding file
        assert config.default_provider == "openai"
        assert config.default_count == 10

    @patch.dict("os.environ", {"PERSONA_PROVIDER": "gemini"})
    def test_from_sources_override_priority(self, tmp_path):
        """Test that overrides have highest priority."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("default_provider: openai\ndefault_count: 5")

        config = SDKConfig.from_sources(
            config_file=config_file,
            default_provider="anthropic",  # Override
            default_count=15,  # Override
        )
        # Overrides win
        assert config.default_provider == "anthropic"
        assert config.default_count == 15


class TestSDKConfigToFile:
    """Test saving configuration to file."""

    def test_to_file(self, tmp_path):
        """Test saving config to YAML file."""
        config = SDKConfig(
            default_provider="openai",
            default_model="gpt-4o",
            default_count=7,
        )

        config_file = tmp_path / "config.yaml"
        config.to_file(config_file)

        # Load it back
        loaded = SDKConfig.from_file(config_file)
        assert loaded.default_provider == "openai"
        assert loaded.default_model == "gpt-4o"
        assert loaded.default_count == 7

    def test_to_file_creates_directory(self, tmp_path):
        """Test that parent directories are created."""
        config = SDKConfig(default_provider="openai")
        config_file = tmp_path / "subdir" / "config.yaml"

        config.to_file(config_file)
        assert config_file.exists()


class TestSDKConfigToDict:
    """Test converting config to dictionary."""

    def test_to_dict(self):
        """Test to_dict() method."""
        config = SDKConfig(
            default_provider="openai",
            default_count=5,
        )
        d = config.to_dict()

        assert d["default_provider"] == "openai"
        assert d["default_count"] == 5
        assert d["default_complexity"] == "moderate"  # Default

    def test_to_dict_excludes_none(self):
        """Test that None values are excluded."""
        config = SDKConfig(default_model=None)
        d = config.to_dict()

        assert "default_model" not in d
