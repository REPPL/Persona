"""Tests for persona.sdk module."""


import pytest
from persona.sdk import (
    AsyncPersonaGenerator,
    ConfigurationError,
    ExperimentSDK,
    GenerationResultModel,
    PersonaConfig,
    PersonaError,
    PersonaGenerator,
    PersonaModel,
    ProviderError,
)


class TestPersonaGeneratorInit:
    """Tests for PersonaGenerator initialisation."""

    def test_init_default_provider(self):
        """Test default provider is anthropic."""
        generator = PersonaGenerator()
        assert generator._provider == "anthropic"
        assert generator._model is None

    def test_init_with_provider(self):
        """Test initialising with specific provider."""
        generator = PersonaGenerator(provider="openai", model="gpt-4o")
        assert generator._provider == "openai"
        assert generator._model == "gpt-4o"

    def test_init_invalid_provider(self):
        """Test that invalid provider raises ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            PersonaGenerator(provider="invalid")
        assert "invalid" in str(exc_info.value).lower()


class TestPersonaConfig:
    """Tests for PersonaConfig model."""

    def test_default_config(self):
        """Test PersonaConfig with defaults."""
        config = PersonaConfig()
        assert config.count == 3
        assert config.complexity == "moderate"
        assert config.detail_level == "standard"

    def test_custom_config(self):
        """Test PersonaConfig with custom values."""
        config = PersonaConfig(
            count=5,
            complexity="complex",
            detail_level="detailed",
        )
        assert config.count == 5
        assert config.complexity == "complex"
        assert config.detail_level == "detailed"

    def test_config_validation(self):
        """Test that config validates count."""
        config = PersonaConfig(count=1)
        assert config.count >= 1


class TestPersonaModel:
    """Tests for PersonaModel."""

    def test_persona_model_creation(self):
        """Test creating a PersonaModel."""
        persona = PersonaModel(
            id="test-001",
            name="Test User",
            title="Software Developer",
            background="Works in tech",
            goals=["Build software", "Learn new things"],
            frustrations=["Too many meetings"],
            behaviors=["Codes daily"],
        )
        assert persona.name == "Test User"
        assert persona.title == "Software Developer"
        assert len(persona.goals) == 2

    def test_persona_model_to_dict(self):
        """Test PersonaModel to_dict method."""
        persona = PersonaModel(
            id="test-002",
            name="Test User",
            title="Developer",
            background="Tech background",
            goals=["Goal 1"],
            frustrations=["Frustration 1"],
            behaviors=["Behavior 1"],
        )
        data = persona.model_dump()
        assert data["name"] == "Test User"
        assert "goals" in data


class TestGenerationResultModel:
    """Tests for GenerationResultModel."""

    def test_result_model_creation(self):
        """Test creating GenerationResultModel."""
        persona = PersonaModel(
            id="test-003",
            name="Test",
            title="Test",
            background="Test",
            goals=[],
            frustrations=[],
            behaviors=[],
        )
        result = GenerationResultModel(
            personas=[persona],
            model="test-model",
            provider="anthropic",
        )
        assert len(result.personas) == 1
        assert result.model == "test-model"
        assert result.token_usage.input_tokens == 0  # default


class TestModuleExports:
    """Tests for module exports from persona package."""

    def test_persona_generator_exported(self):
        """Test PersonaGenerator is exported from persona."""
        from persona import PersonaGenerator as PG

        assert PG is PersonaGenerator

    def test_persona_config_exported(self):
        """Test PersonaConfig is exported from persona."""
        from persona import PersonaConfig as PC

        assert PC is PersonaConfig

    def test_experiment_sdk_exported(self):
        """Test ExperimentSDK is exported from persona."""
        from persona import ExperimentSDK as ES

        assert ES is ExperimentSDK

    def test_async_generator_exported(self):
        """Test AsyncPersonaGenerator is exported from persona."""
        from persona import AsyncPersonaGenerator as APG

        assert APG is AsyncPersonaGenerator

    def test_exceptions_exported(self):
        """Test exceptions are exported from persona."""
        from persona import (
            ConfigurationError,
            PersonaError,
            ProviderError,
        )

        assert issubclass(ConfigurationError, PersonaError)
        assert issubclass(ProviderError, PersonaError)


class TestExceptionHierarchy:
    """Tests for SDK exception hierarchy."""

    def test_configuration_error_is_persona_error(self):
        """ConfigurationError inherits from PersonaError."""
        error = ConfigurationError("test", field="test", value="test")
        assert isinstance(error, PersonaError)

    def test_provider_error_is_persona_error(self):
        """ProviderError inherits from PersonaError."""
        error = ProviderError("test", provider="anthropic")
        assert isinstance(error, PersonaError)

    def test_exception_with_details(self):
        """Test exceptions store details."""
        error = ConfigurationError(
            "Invalid config",
            field="provider",
            value="invalid",
        )
        assert "Invalid config" in str(error)
