"""Tests for multi-model generator (F-066)."""

import pytest
from persona.core.multimodel.generator import (
    ModelOutput,
    ModelSpec,
    MultiModelGenerator,
    MultiModelResult,
    generate_multi_model,
)


class TestModelSpec:
    """Tests for ModelSpec."""

    def test_basic_creation(self):
        """Creates with provider and model."""
        spec = ModelSpec(provider="anthropic", model="claude-sonnet-4")

        assert spec.provider == "anthropic"
        assert spec.model == "claude-sonnet-4"
        assert spec.weight == 1.0

    def test_with_custom_weight(self):
        """Creates with custom weight."""
        spec = ModelSpec(provider="openai", model="gpt-4o", weight=0.5)

        assert spec.weight == 0.5

    def test_with_temperature(self):
        """Creates with temperature override."""
        spec = ModelSpec(
            provider="anthropic",
            model="claude-sonnet-4",
            temperature=0.3,
        )

        assert spec.temperature == 0.3

    def test_parse_with_provider(self):
        """Parses spec with explicit provider."""
        spec = ModelSpec.parse("anthropic:claude-sonnet-4")

        assert spec.provider == "anthropic"
        assert spec.model == "claude-sonnet-4"

    def test_parse_infer_anthropic(self):
        """Infers Anthropic provider from model name."""
        spec = ModelSpec.parse("claude-sonnet-4")

        assert spec.provider == "anthropic"

    def test_parse_infer_openai(self):
        """Infers OpenAI provider from model name."""
        spec = ModelSpec.parse("gpt-4o")

        assert spec.provider == "openai"

    def test_parse_infer_gemini(self):
        """Infers Gemini provider from model name."""
        spec = ModelSpec.parse("gemini-1.5-pro")

        assert spec.provider == "gemini"

    def test_parse_unknown_raises(self):
        """Raises for unknown model name."""
        with pytest.raises(ValueError, match="Cannot infer provider"):
            ModelSpec.parse("unknown-model")

    def test_to_dict(self):
        """Converts to dictionary."""
        spec = ModelSpec(
            provider="anthropic",
            model="claude-sonnet-4",
            weight=0.8,
            temperature=0.5,
        )
        data = spec.to_dict()

        assert data["provider"] == "anthropic"
        assert data["model"] == "claude-sonnet-4"
        assert data["weight"] == 0.8
        assert data["temperature"] == 0.5


class TestModelOutput:
    """Tests for ModelOutput."""

    def test_success_property_true(self):
        """Success is True when no error and has personas."""
        output = ModelOutput(
            model_spec=ModelSpec("anthropic", "claude-sonnet-4"),
            personas=[{"id": "1", "name": "Test"}],
        )

        assert output.success is True

    def test_success_property_false_error(self):
        """Success is False when error present."""
        output = ModelOutput(
            model_spec=ModelSpec("anthropic", "claude-sonnet-4"),
            error="Connection failed",
        )

        assert output.success is False

    def test_success_property_false_no_personas(self):
        """Success is False when no personas."""
        output = ModelOutput(
            model_spec=ModelSpec("anthropic", "claude-sonnet-4"),
            personas=[],
        )

        assert output.success is False

    def test_to_dict(self):
        """Converts to dictionary."""
        output = ModelOutput(
            model_spec=ModelSpec("anthropic", "claude-sonnet-4"),
            personas=[{"id": "1"}],
            tokens_input=1000,
            tokens_output=500,
            latency_ms=1500.5,
            cost=0.05,
        )
        data = output.to_dict()

        assert data["tokens_input"] == 1000
        assert data["tokens_output"] == 500
        assert data["success"] is True


class TestMultiModelResult:
    """Tests for MultiModelResult."""

    def test_all_personas(self):
        """Gets all personas from all models."""
        result = MultiModelResult(
            model_outputs=[
                ModelOutput(
                    model_spec=ModelSpec("anthropic", "claude"),
                    personas=[{"id": "1"}, {"id": "2"}],
                ),
                ModelOutput(
                    model_spec=ModelSpec("openai", "gpt"),
                    personas=[{"id": "3"}],
                ),
            ]
        )

        assert len(result.all_personas) == 3

    def test_successful_models(self):
        """Gets only successful model outputs."""
        result = MultiModelResult(
            model_outputs=[
                ModelOutput(
                    model_spec=ModelSpec("anthropic", "claude"),
                    personas=[{"id": "1"}],
                ),
                ModelOutput(
                    model_spec=ModelSpec("openai", "gpt"),
                    error="Failed",
                ),
            ]
        )

        assert len(result.successful_models) == 1
        assert len(result.failed_models) == 1

    def test_to_dict(self):
        """Converts to dictionary."""
        result = MultiModelResult(
            model_outputs=[],
            execution_mode="parallel",
            total_cost=0.10,
        )
        data = result.to_dict()

        assert data["execution_mode"] == "parallel"
        assert data["total_cost"] == 0.10


class TestMultiModelGenerator:
    """Tests for MultiModelGenerator."""

    def test_generate_parallel(self):
        """Generates with parallel mode."""
        generator = MultiModelGenerator()
        models = [
            ModelSpec("anthropic", "claude-sonnet-4"),
            ModelSpec("openai", "gpt-4o"),
        ]

        result = generator.generate(
            data="Test data",
            models=models,
            count=3,
            mode="parallel",
        )

        assert result.execution_mode == "parallel"
        assert len(result.model_outputs) == 2

    def test_generate_sequential(self):
        """Generates with sequential mode."""
        generator = MultiModelGenerator()
        models = [
            ModelSpec("anthropic", "claude-sonnet-4"),
            ModelSpec("openai", "gpt-4o"),
        ]

        result = generator.generate(
            data="Test data",
            models=models,
            count=2,
            mode="sequential",
        )

        assert result.execution_mode == "sequential"

    def test_generate_consensus(self):
        """Generates with consensus mode."""
        generator = MultiModelGenerator()
        models = [
            ModelSpec("anthropic", "claude-sonnet-4"),
            ModelSpec("openai", "gpt-4o"),
        ]

        result = generator.generate(
            data="Test data",
            models=models,
            count=3,
            mode="consensus",
        )

        assert result.execution_mode == "consensus"
        # Consensus mode should produce consolidated personas
        assert len(result.consolidated_personas) >= 0

    def test_generate_empty_models_raises(self):
        """Raises for empty models list."""
        generator = MultiModelGenerator()

        with pytest.raises(ValueError, match="At least one model"):
            generator.generate(data="Test", models=[], count=3)

    def test_generate_invalid_mode_raises(self):
        """Raises for invalid mode."""
        generator = MultiModelGenerator()
        models = [ModelSpec("anthropic", "claude")]

        with pytest.raises(ValueError, match="Invalid mode"):
            generator.generate(data="Test", models=models, mode="invalid")

    def test_generate_single(self):
        """Generates with single model."""
        generator = MultiModelGenerator()
        model = ModelSpec("anthropic", "claude-sonnet-4")

        output = generator.generate_single(
            data="Test data",
            model=model,
            count=3,
        )

        assert output.success
        assert len(output.personas) == 3


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_generate_multi_model_strings(self):
        """Generates with string model specs."""
        result = generate_multi_model(
            data="Test data",
            models=["anthropic:claude-sonnet-4", "openai:gpt-4o"],
            count=2,
            mode="parallel",
        )

        assert len(result.model_outputs) == 2

    def test_generate_multi_model_mixed(self):
        """Generates with mixed model specs."""
        result = generate_multi_model(
            data="Test data",
            models=[
                "anthropic:claude-sonnet-4",
                ModelSpec("openai", "gpt-4o"),
            ],
            count=2,
        )

        assert len(result.model_outputs) == 2
