"""Tests for PersonaGenerator SDK class."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from persona.sdk import PersonaConfig, PersonaGenerator
from persona.sdk.exceptions import (
    ConfigurationError,
    DataError,
    GenerationError,
)


class TestPersonaGeneratorInit:
    """Tests for PersonaGenerator initialisation."""

    def test_default_provider(self):
        """Test default provider is anthropic."""
        generator = PersonaGenerator()
        assert generator.provider == "anthropic"
        assert generator.model is None

    def test_custom_provider(self):
        """Test custom provider."""
        generator = PersonaGenerator(provider="openai")
        assert generator.provider == "openai"

    def test_custom_model(self):
        """Test custom model."""
        generator = PersonaGenerator(model="gpt-4")
        assert generator.model == "gpt-4"

    def test_all_valid_providers(self):
        """Test all valid providers."""
        for provider in ["anthropic", "openai", "gemini"]:
            generator = PersonaGenerator(provider=provider)
            assert generator.provider == provider

    def test_invalid_provider(self):
        """Test invalid provider raises ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            PersonaGenerator(provider="invalid")
        assert "invalid" in str(exc_info.value).lower()
        assert exc_info.value.field == "provider"

    def test_provider_case_sensitive(self):
        """Test provider names are case sensitive."""
        with pytest.raises(ConfigurationError):
            PersonaGenerator(provider="Anthropic")


class TestPersonaGeneratorProgress:
    """Tests for progress callback."""

    def test_set_progress_callback(self):
        """Test setting progress callback."""
        generator = PersonaGenerator()
        callback = Mock()
        generator.set_progress_callback(callback)
        assert generator._progress_callback == callback

    def test_progress_callback_is_none_initially(self):
        """Test progress callback is None by default."""
        generator = PersonaGenerator()
        assert generator._progress_callback is None


class TestPersonaGeneratorValidation:
    """Tests for configuration validation."""

    def test_validate_config_high_count(self):
        """Test validation warns on high count."""
        generator = PersonaGenerator()
        config = PersonaConfig(count=15)
        warnings = generator.validate_config(config)
        assert any("count" in w.lower() for w in warnings)

    def test_validate_config_high_temperature(self):
        """Test validation warns on high temperature."""
        generator = PersonaGenerator()
        config = PersonaConfig(temperature=1.5)
        warnings = generator.validate_config(config)
        assert any("temperature" in w.lower() for w in warnings)

    def test_validate_config_low_tokens(self):
        """Test validation warns on low max_tokens with multiple personas."""
        generator = PersonaGenerator()
        config = PersonaConfig(max_tokens=500, count=5)
        warnings = generator.validate_config(config)
        assert any("token" in w.lower() for w in warnings)

    def test_validate_config_ok(self):
        """Test validation returns no warnings for good config."""
        generator = PersonaGenerator()
        config = PersonaConfig(count=3, temperature=0.7, max_tokens=4096)
        warnings = generator.validate_config(config)
        assert warnings == []


class TestPersonaGeneratorGenerate:
    """Tests for generate method."""

    def test_generate_data_not_found(self):
        """Test generate raises DataError for missing file."""
        generator = PersonaGenerator()
        with pytest.raises(DataError) as exc_info:
            generator.generate("/nonexistent/path.csv")
        assert "not found" in str(exc_info.value).lower()

    def test_generate_with_config(self):
        """Test generate with custom config."""
        generator = PersonaGenerator()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("participant,response\nP1,I like fast tools\n")
            f.flush()

            # Mock the core pipeline
            with patch("persona.core.generation.GenerationPipeline") as MockPipeline:
                mock_instance = MockPipeline.return_value
                mock_result = Mock()
                mock_result.personas = []
                mock_result.reasoning = None
                mock_result.input_tokens = 100
                mock_result.output_tokens = 50
                mock_result.model = "test-model"
                mock_result.provider = "anthropic"
                mock_result.source_files = [Path(f.name)]
                mock_instance.generate.return_value = mock_result

                config = PersonaConfig(count=5)
                result = generator.generate(f.name, config=config)

                assert result is not None
                mock_instance.generate.assert_called_once()

            Path(f.name).unlink()

    def test_generate_wraps_file_not_found(self):
        """Test generate wraps FileNotFoundError as DataError."""
        generator = PersonaGenerator()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("data\n")
            f.flush()
            temp_path = f.name

            with patch("persona.core.generation.GenerationPipeline") as MockPipeline:
                mock_instance = MockPipeline.return_value
                mock_instance.generate.side_effect = FileNotFoundError("File gone")

                with pytest.raises(DataError):
                    generator.generate(temp_path)

            Path(temp_path).unlink()

    def test_generate_wraps_value_error(self):
        """Test generate wraps ValueError as DataError."""
        generator = PersonaGenerator()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("data\n")
            f.flush()
            temp_path = f.name

            with patch("persona.core.generation.GenerationPipeline") as MockPipeline:
                mock_instance = MockPipeline.return_value
                mock_instance.generate.side_effect = ValueError("Invalid data")

                with pytest.raises(DataError):
                    generator.generate(temp_path)

            Path(temp_path).unlink()

    def test_generate_wraps_runtime_error(self):
        """Test generate wraps RuntimeError as GenerationError."""
        generator = PersonaGenerator()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("data\n")
            f.flush()
            temp_path = f.name

            with patch("persona.core.generation.GenerationPipeline") as MockPipeline:
                mock_instance = MockPipeline.return_value
                mock_instance.generate.side_effect = RuntimeError("Generation failed")

                with pytest.raises(GenerationError):
                    generator.generate(temp_path)

            Path(temp_path).unlink()

    def test_generate_with_default_config(self):
        """Test generate with default config."""
        generator = PersonaGenerator()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("participant,response\nP1,Test response\n")
            f.flush()

            with patch("persona.core.generation.GenerationPipeline") as MockPipeline:
                mock_instance = MockPipeline.return_value
                mock_result = Mock()
                mock_result.personas = []
                mock_result.reasoning = None
                mock_result.input_tokens = 100
                mock_result.output_tokens = 50
                mock_result.model = "test-model"
                mock_result.provider = "anthropic"
                mock_result.source_files = [Path(f.name)]
                mock_instance.generate.return_value = mock_result

                # No config provided
                result = generator.generate(f.name)
                assert result is not None

            Path(f.name).unlink()


class TestPersonaGeneratorEstimateCost:
    """Tests for cost estimation."""

    def test_estimate_cost_file_not_found(self):
        """Test estimate_cost raises DataError for missing file."""
        generator = PersonaGenerator()
        with pytest.raises(DataError):
            generator.estimate_cost("/nonexistent/path.csv")

    def test_estimate_cost_returns_dict(self):
        """Test estimate_cost returns expected dictionary."""
        generator = PersonaGenerator()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("participant,response\nP1,Test data for estimation\n")
            f.flush()

            with patch("persona.core.data.DataLoader") as MockLoader:
                mock_instance = MockLoader.return_value
                mock_instance.load_path.return_value = ("test data", [Path(f.name)])

                with patch("persona.core.cost.CostEstimator") as MockEstimator:
                    mock_estimator = MockEstimator.return_value
                    mock_estimator.estimate_input_tokens.return_value = 1000
                    mock_estimator.estimate_output_tokens.return_value = 500

                    mock_pricing = Mock()
                    mock_pricing.input_price = 3.0
                    mock_pricing.output_price = 15.0
                    mock_pricing.model_id = "test-model"
                    mock_estimator.get_pricing.return_value = mock_pricing

                    estimate = generator.estimate_cost(f.name)

                    assert "input_tokens" in estimate
                    assert "output_tokens" in estimate
                    assert "total_tokens" in estimate
                    assert "estimated_cost" in estimate
                    assert "model" in estimate
                    assert "provider" in estimate

            Path(f.name).unlink()


class TestPersonaGeneratorIntegration:
    """Integration-style tests for PersonaGenerator."""

    def test_full_workflow_mock(self):
        """Test complete workflow with mocks."""
        generator = PersonaGenerator(provider="anthropic", model="claude-sonnet-4.5")

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test data
            data_file = Path(tmpdir) / "interviews.csv"
            data_file.write_text("participant,quote\nP1,I need faster tools\n")

            with patch("persona.core.generation.GenerationPipeline") as MockPipeline:
                mock_instance = MockPipeline.return_value

                # Create mock persona
                mock_persona = Mock()
                mock_persona.id = "p-001"
                mock_persona.name = "Test User"
                mock_persona.title = "Developer"
                mock_persona.goals = ["Work faster"]
                mock_persona.pain_points = ["Slow tools"]
                mock_persona.behaviours = ["Uses shortcuts"]
                mock_persona.quotes = ["I need faster tools"]
                mock_persona.demographics = {"role": "developer"}
                mock_persona.additional = {}

                mock_result = Mock()
                mock_result.personas = [mock_persona]
                mock_result.reasoning = "Generated based on data"
                mock_result.input_tokens = 500
                mock_result.output_tokens = 200
                mock_result.model = "claude-sonnet-4.5"
                mock_result.provider = "anthropic"
                mock_result.source_files = [data_file]
                mock_instance.generate.return_value = mock_result

                result = generator.generate(data_file, config=PersonaConfig(count=3))

                assert len(result.personas) == 1
                assert result.personas[0].name == "Test User"
                assert result.token_usage.input_tokens == 500
                assert result.token_usage.output_tokens == 200
                assert result.provider == "anthropic"

    def test_progress_callback_invoked(self):
        """Test progress callback is invoked during generation."""
        generator = PersonaGenerator()
        progress_calls = []

        def track_progress(message, step, total):
            progress_calls.append((message, step, total))

        generator.set_progress_callback(track_progress)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("data\n")
            f.flush()

            with patch("persona.core.generation.GenerationPipeline") as MockPipeline:
                mock_instance = MockPipeline.return_value

                # Capture the callback that gets set
                def capture_callback(callback):
                    # Simulate calling the callback
                    callback("Loading...")
                    callback("Generating...")

                mock_instance.set_progress_callback.side_effect = capture_callback

                mock_result = Mock()
                mock_result.personas = []
                mock_result.reasoning = None
                mock_result.input_tokens = 100
                mock_result.output_tokens = 50
                mock_result.model = "test"
                mock_result.provider = "anthropic"
                mock_result.source_files = []
                mock_instance.generate.return_value = mock_result

                generator.generate(f.name)

                # Progress should have been called
                assert len(progress_calls) >= 2

            Path(f.name).unlink()
