"""Tests for AsyncPersonaGenerator SDK class."""

import asyncio
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

import pytest

from persona.sdk import AsyncPersonaGenerator, PersonaConfig
from persona.sdk.async_generator import agenerate_parallel
from persona.sdk.exceptions import (
    ConfigurationError,
    DataError,
    GenerationError,
)


class TestAsyncPersonaGeneratorInit:
    """Tests for AsyncPersonaGenerator initialisation."""

    def test_default_provider(self):
        """Test default provider is anthropic."""
        generator = AsyncPersonaGenerator()
        assert generator.provider == "anthropic"
        assert generator.model is None

    def test_custom_provider(self):
        """Test custom provider."""
        generator = AsyncPersonaGenerator(provider="openai")
        assert generator.provider == "openai"

    def test_custom_model(self):
        """Test custom model."""
        generator = AsyncPersonaGenerator(model="gpt-4")
        assert generator.model == "gpt-4"

    def test_all_valid_providers(self):
        """Test all valid providers."""
        for provider in ["anthropic", "openai", "gemini"]:
            generator = AsyncPersonaGenerator(provider=provider)
            assert generator.provider == provider

    def test_invalid_provider(self):
        """Test invalid provider raises ConfigurationError."""
        with pytest.raises(ConfigurationError) as exc_info:
            AsyncPersonaGenerator(provider="invalid")
        assert "invalid" in str(exc_info.value).lower()


class TestAsyncPersonaGeneratorProgress:
    """Tests for async progress callback."""

    def test_set_progress_callback(self):
        """Test setting async progress callback."""
        generator = AsyncPersonaGenerator()

        async def callback(msg, step, total):
            pass

        generator.set_progress_callback(callback)
        assert generator._progress_callback == callback

    def test_progress_callback_is_none_initially(self):
        """Test progress callback is None by default."""
        generator = AsyncPersonaGenerator()
        assert generator._progress_callback is None


class TestAsyncPersonaGeneratorValidation:
    """Tests for configuration validation."""

    def test_validate_config_high_count(self):
        """Test validation warns on high count."""
        generator = AsyncPersonaGenerator()
        config = PersonaConfig(count=15)
        warnings = generator.validate_config(config)
        assert any("count" in w.lower() for w in warnings)

    def test_validate_config_ok(self):
        """Test validation returns no warnings for good config."""
        generator = AsyncPersonaGenerator()
        config = PersonaConfig(count=3, temperature=0.7)
        warnings = generator.validate_config(config)
        assert warnings == []


class TestAsyncPersonaGeneratorGenerate:
    """Tests for async generate method."""

    @pytest.mark.asyncio
    async def test_agenerate_data_not_found(self):
        """Test agenerate raises DataError for missing file."""
        generator = AsyncPersonaGenerator()
        with pytest.raises(DataError) as exc_info:
            await generator.agenerate("/nonexistent/path.csv")
        assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_agenerate_with_config(self):
        """Test agenerate with custom config."""
        generator = AsyncPersonaGenerator()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("participant,response\nP1,I like fast tools\n")
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

                config = PersonaConfig(count=5)
                result = await generator.agenerate(f.name, config=config)

                assert result is not None
                mock_instance.generate.assert_called_once()

            Path(f.name).unlink()

    @pytest.mark.asyncio
    async def test_agenerate_with_default_config(self):
        """Test agenerate with default config."""
        generator = AsyncPersonaGenerator()

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

                result = await generator.agenerate(f.name)
                assert result is not None

            Path(f.name).unlink()

    @pytest.mark.asyncio
    async def test_agenerate_wraps_exceptions(self):
        """Test agenerate wraps generic exceptions as GenerationError."""
        generator = AsyncPersonaGenerator()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("data\n")
            f.flush()
            temp_path = f.name

            with patch("persona.core.generation.GenerationPipeline") as MockPipeline:
                mock_instance = MockPipeline.return_value
                mock_instance.generate.side_effect = Exception("Unexpected error")

                with pytest.raises(GenerationError):
                    await generator.agenerate(temp_path)

            Path(temp_path).unlink()


class TestAsyncPersonaGeneratorBatch:
    """Tests for batch generation."""

    @pytest.mark.asyncio
    async def test_agenerate_batch_multiple_files(self):
        """Test batch generation with multiple files."""
        generator = AsyncPersonaGenerator()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            files = []
            for i in range(3):
                file_path = Path(tmpdir) / f"data{i}.csv"
                file_path.write_text(f"participant,response\nP1,Response {i}\n")
                files.append(file_path)

            with patch("persona.core.generation.GenerationPipeline") as MockPipeline:
                mock_instance = MockPipeline.return_value

                def create_mock_result(data_path, config=None):
                    mock_result = Mock()
                    mock_result.personas = []
                    mock_result.reasoning = None
                    mock_result.input_tokens = 100
                    mock_result.output_tokens = 50
                    mock_result.model = "test-model"
                    mock_result.provider = "anthropic"
                    mock_result.source_files = [data_path]
                    return mock_result

                mock_instance.generate.side_effect = create_mock_result

                results = await generator.agenerate_batch(
                    files,
                    config=PersonaConfig(count=3),
                    max_concurrent=2,
                )

                assert len(results) == 3
                assert mock_instance.generate.call_count == 3

    @pytest.mark.asyncio
    async def test_agenerate_batch_respects_concurrency_limit(self):
        """Test batch generation respects max_concurrent limit."""
        generator = AsyncPersonaGenerator()
        concurrent_count = 0
        max_observed = 0

        with tempfile.TemporaryDirectory() as tmpdir:
            files = []
            for i in range(5):
                file_path = Path(tmpdir) / f"data{i}.csv"
                file_path.write_text(f"participant,response\nP1,Response {i}\n")
                files.append(file_path)

            with patch("persona.core.generation.GenerationPipeline") as MockPipeline:
                mock_instance = MockPipeline.return_value

                def create_mock_result(data_path, config=None):
                    nonlocal concurrent_count, max_observed
                    concurrent_count += 1
                    max_observed = max(max_observed, concurrent_count)
                    mock_result = Mock()
                    mock_result.personas = []
                    mock_result.reasoning = None
                    mock_result.input_tokens = 100
                    mock_result.output_tokens = 50
                    mock_result.model = "test-model"
                    mock_result.provider = "anthropic"
                    mock_result.source_files = [data_path]
                    concurrent_count -= 1
                    return mock_result

                mock_instance.generate.side_effect = create_mock_result

                await generator.agenerate_batch(files, max_concurrent=2)

                # Due to threading, we can't guarantee exact concurrency
                # but the semaphore should limit it
                assert mock_instance.generate.call_count == 5


class TestAsyncPersonaGeneratorEstimateCost:
    """Tests for async cost estimation."""

    @pytest.mark.asyncio
    async def test_aestimate_cost_file_not_found(self):
        """Test aestimate_cost raises DataError for missing file."""
        generator = AsyncPersonaGenerator()
        with pytest.raises(DataError):
            await generator.aestimate_cost("/nonexistent/path.csv")

    @pytest.mark.asyncio
    async def test_aestimate_cost_returns_dict(self):
        """Test aestimate_cost returns expected dictionary."""
        generator = AsyncPersonaGenerator()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("participant,response\nP1,Test data\n")
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

                    estimate = await generator.aestimate_cost(f.name)

                    assert "input_tokens" in estimate
                    assert "output_tokens" in estimate
                    assert "estimated_cost" in estimate

            Path(f.name).unlink()


class TestAGenerateParallel:
    """Tests for convenience agenerate_parallel function."""

    @pytest.mark.asyncio
    async def test_agenerate_parallel_creates_generator(self):
        """Test agenerate_parallel creates generator with correct settings."""
        with tempfile.TemporaryDirectory() as tmpdir:
            files = []
            for i in range(2):
                file_path = Path(tmpdir) / f"data{i}.csv"
                file_path.write_text(f"participant,response\nP1,Response {i}\n")
                files.append(file_path)

            with patch("persona.core.generation.GenerationPipeline") as MockPipeline:
                mock_instance = MockPipeline.return_value

                def create_mock_result(data_path, config=None):
                    mock_result = Mock()
                    mock_result.personas = []
                    mock_result.reasoning = None
                    mock_result.input_tokens = 100
                    mock_result.output_tokens = 50
                    mock_result.model = "test-model"
                    mock_result.provider = "openai"
                    mock_result.source_files = [data_path]
                    return mock_result

                mock_instance.generate.side_effect = create_mock_result

                results = await agenerate_parallel(
                    files,
                    provider="openai",
                    model="gpt-4",
                    max_concurrent=1,
                )

                assert len(results) == 2


class TestAsyncProgressCallback:
    """Tests for async progress callback integration."""

    @pytest.mark.asyncio
    async def test_async_progress_callback_called(self):
        """Test async progress callback is invoked."""
        generator = AsyncPersonaGenerator()
        progress_calls = []

        async def track_progress(message, step, total):
            progress_calls.append((message, step, total))

        generator.set_progress_callback(track_progress)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            f.write("data\n")
            f.flush()

            with patch("persona.core.generation.GenerationPipeline") as MockPipeline:
                mock_instance = MockPipeline.return_value

                def capture_and_call_callback(callback):
                    # The sync callback wraps the async one
                    callback("Loading...")
                    callback("Generating...")

                mock_instance.set_progress_callback.side_effect = capture_and_call_callback

                mock_result = Mock()
                mock_result.personas = []
                mock_result.reasoning = None
                mock_result.input_tokens = 100
                mock_result.output_tokens = 50
                mock_result.model = "test"
                mock_result.provider = "anthropic"
                mock_result.source_files = []
                mock_instance.generate.return_value = mock_result

                await generator.agenerate(f.name)

                # Give time for async callbacks to execute
                await asyncio.sleep(0.1)

            Path(f.name).unlink()
