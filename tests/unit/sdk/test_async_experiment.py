"""Tests for AsyncExperimentSDK class."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from persona.sdk import AsyncExperimentSDK, ExperimentConfig, PersonaConfig
from persona.sdk.exceptions import ConfigurationError, DataError


class TestAsyncExperimentSDKInit:
    """Tests for AsyncExperimentSDK initialisation."""

    def test_default_base_dir(self):
        """Test default base directory."""
        sdk = AsyncExperimentSDK()
        assert sdk.base_dir == Path("./experiments")

    def test_custom_base_dir(self):
        """Test custom base directory."""
        sdk = AsyncExperimentSDK("/custom/path")
        assert sdk.base_dir == Path("/custom/path")

    def test_path_object_accepted(self):
        """Test Path object is accepted."""
        sdk = AsyncExperimentSDK(Path("/custom/path"))
        assert sdk.base_dir == Path("/custom/path")


class TestAsyncExperimentSDKCreate:
    """Tests for async experiment creation."""

    @pytest.mark.asyncio
    async def test_acreate_experiment(self):
        """Test asynchronously creating an experiment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = AsyncExperimentSDK(tmpdir)
            config = ExperimentConfig(name="async-test")
            exp = await sdk.acreate(config)

            assert exp.name == "async-test"
            assert Path(exp.path).exists()
            assert exp.data_dir.exists()
            assert exp.outputs_dir.exists()

    @pytest.mark.asyncio
    async def test_acreate_experiment_already_exists(self):
        """Test creating duplicate experiment raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = AsyncExperimentSDK(tmpdir)
            config = ExperimentConfig(name="duplicate")

            await sdk.acreate(config)

            with pytest.raises(ConfigurationError) as exc_info:
                await sdk.acreate(config)

            assert "already exists" in str(exc_info.value).lower()


class TestAsyncExperimentSDKLoad:
    """Tests for async loading experiments."""

    @pytest.mark.asyncio
    async def test_aload_experiment(self):
        """Test asynchronously loading an existing experiment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = AsyncExperimentSDK(tmpdir)

            config = ExperimentConfig(name="load-test")
            await sdk.acreate(config)

            exp = await sdk.aload("load-test")
            assert exp.name == "load-test"

    @pytest.mark.asyncio
    async def test_aload_nonexistent_experiment(self):
        """Test loading nonexistent experiment raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = AsyncExperimentSDK(tmpdir)

            with pytest.raises(ConfigurationError) as exc_info:
                await sdk.aload("nonexistent")

            assert "not found" in str(exc_info.value).lower()


class TestAsyncExperimentSDKList:
    """Tests for async listing experiments."""

    @pytest.mark.asyncio
    async def test_alist_empty(self):
        """Test listing with no experiments."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = AsyncExperimentSDK(tmpdir)
            experiments = await sdk.alist_experiments()
            assert experiments == []

    @pytest.mark.asyncio
    async def test_alist_multiple(self):
        """Test listing multiple experiments."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = AsyncExperimentSDK(tmpdir)

            await sdk.acreate(ExperimentConfig(name="exp-1"))
            await sdk.acreate(ExperimentConfig(name="exp-2"))
            await sdk.acreate(ExperimentConfig(name="exp-3"))

            experiments = await sdk.alist_experiments()
            names = [e.name for e in experiments]

            assert len(experiments) == 3
            assert "exp-1" in names
            assert "exp-2" in names
            assert "exp-3" in names


class TestAsyncExperimentSDKDelete:
    """Tests for async deleting experiments."""

    @pytest.mark.asyncio
    async def test_adelete_without_confirm(self):
        """Test delete without confirm does nothing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = AsyncExperimentSDK(tmpdir)
            await sdk.acreate(ExperimentConfig(name="delete-test"))

            result = await sdk.adelete("delete-test", confirm=False)
            assert result is False
            assert await sdk.aexists("delete-test")

    @pytest.mark.asyncio
    async def test_adelete_with_confirm(self):
        """Test delete with confirm removes experiment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = AsyncExperimentSDK(tmpdir)
            await sdk.acreate(ExperimentConfig(name="delete-test"))

            result = await sdk.adelete("delete-test", confirm=True)
            assert result is True
            assert not await sdk.aexists("delete-test")

    @pytest.mark.asyncio
    async def test_adelete_nonexistent(self):
        """Test deleting nonexistent experiment raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = AsyncExperimentSDK(tmpdir)

            with pytest.raises(ConfigurationError):
                await sdk.adelete("nonexistent", confirm=True)


class TestAsyncExperimentSDKExists:
    """Tests for async exists check."""

    @pytest.mark.asyncio
    async def test_aexists_true(self):
        """Test aexists returns True for existing experiment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = AsyncExperimentSDK(tmpdir)
            await sdk.acreate(ExperimentConfig(name="exists-test"))

            assert await sdk.aexists("exists-test") is True

    @pytest.mark.asyncio
    async def test_aexists_false(self):
        """Test aexists returns False for nonexistent experiment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = AsyncExperimentSDK(tmpdir)
            assert await sdk.aexists("nonexistent") is False

    def test_sync_exists_method(self):
        """Test sync exists method for convenience."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = AsyncExperimentSDK(tmpdir)
            assert sdk.exists("nonexistent") is False


class TestAsyncExperimentSDKData:
    """Tests for async data management."""

    @pytest.mark.asyncio
    async def test_aadd_data_copy(self):
        """Test asynchronously adding data by copying."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = AsyncExperimentSDK(tmpdir)
            exp = await sdk.acreate(ExperimentConfig(name="data-test"))

            source = Path(tmpdir) / "source.csv"
            source.write_text("data,value\n1,2\n")

            result = await sdk.aadd_data("data-test", source, copy=True)

            assert result.exists()
            assert result.parent == exp.data_dir
            assert result.read_text() == "data,value\n1,2\n"

    @pytest.mark.asyncio
    async def test_aadd_data_nonexistent_file(self):
        """Test adding nonexistent file raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = AsyncExperimentSDK(tmpdir)
            await sdk.acreate(ExperimentConfig(name="data-test"))

            with pytest.raises(DataError):
                await sdk.aadd_data("data-test", "/nonexistent/file.csv")

    @pytest.mark.asyncio
    async def test_alist_data_empty(self):
        """Test listing data in empty experiment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = AsyncExperimentSDK(tmpdir)
            await sdk.acreate(ExperimentConfig(name="empty-data"))

            files = await sdk.alist_data("empty-data")
            assert files == []

    @pytest.mark.asyncio
    async def test_alist_data_multiple(self):
        """Test listing multiple data files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = AsyncExperimentSDK(tmpdir)
            await sdk.acreate(ExperimentConfig(name="multi-data"))

            for name in ["file1.csv", "file2.json", "file3.md"]:
                source = Path(tmpdir) / name
                source.write_text("data\n")
                await sdk.aadd_data("multi-data", source)

            files = await sdk.alist_data("multi-data")
            names = [f.name for f in files]

            assert len(files) == 3
            assert "file1.csv" in names
            assert "file2.json" in names
            assert "file3.md" in names


class TestAsyncExperimentSDKOutputs:
    """Tests for async output management."""

    @pytest.mark.asyncio
    async def test_aget_outputs_empty(self):
        """Test getting outputs from empty experiment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = AsyncExperimentSDK(tmpdir)
            await sdk.acreate(ExperimentConfig(name="output-test"))

            outputs = await sdk.aget_outputs("output-test")
            assert outputs == []

    @pytest.mark.asyncio
    async def test_aget_outputs_multiple(self):
        """Test getting multiple output directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = AsyncExperimentSDK(tmpdir)
            exp = await sdk.acreate(ExperimentConfig(name="output-test"))

            for name in ["20241201_120000", "20241202_130000"]:
                output_dir = exp.outputs_dir / name
                output_dir.mkdir()

            outputs = await sdk.aget_outputs("output-test")
            names = [o.name for o in outputs]

            assert len(outputs) == 2
            assert "20241201_120000" in names
            assert "20241202_130000" in names


class TestAsyncExperimentSDKStatistics:
    """Tests for async experiment statistics."""

    @pytest.mark.asyncio
    async def test_aget_statistics(self):
        """Test getting experiment statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = AsyncExperimentSDK(tmpdir)
            config = ExperimentConfig(
                name="stats-test",
                description="Statistics test",
                provider="openai",
            )
            await sdk.acreate(config)

            source = Path(tmpdir) / "data.csv"
            source.write_text("test data content\n")
            await sdk.aadd_data("stats-test", source)

            stats = await sdk.aget_statistics("stats-test")

            assert stats["name"] == "stats-test"
            assert stats["description"] == "Statistics test"
            assert stats["provider"] == "openai"
            assert stats["data_file_count"] == 1
            assert stats["data_size_bytes"] > 0
            assert stats["run_count"] == 0


class TestAsyncExperimentSDKGenerate:
    """Tests for async generation from experiments."""

    @pytest.mark.asyncio
    async def test_agenerate_no_data(self):
        """Test agenerate raises error with no data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = AsyncExperimentSDK(tmpdir)
            await sdk.acreate(ExperimentConfig(name="gen-test"))

            with pytest.raises(DataError) as exc_info:
                await sdk.agenerate("gen-test")

            assert "no data" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_agenerate_with_data(self):
        """Test agenerate with data files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = AsyncExperimentSDK(tmpdir)
            await sdk.acreate(
                ExperimentConfig(
                    name="gen-test",
                    provider="anthropic",
                )
            )

            source = Path(tmpdir) / "interviews.csv"
            source.write_text("participant,quote\nP1,I need speed\n")
            await sdk.aadd_data("gen-test", source)

            with patch("persona.core.generation.GenerationPipeline") as MockPipeline:
                mock_instance = MockPipeline.return_value
                mock_result = Mock()
                mock_result.personas = []
                mock_result.reasoning = None
                mock_result.input_tokens = 100
                mock_result.output_tokens = 50
                mock_result.model = "test-model"
                mock_result.provider = "anthropic"
                mock_result.source_files = [source]
                mock_instance.generate.return_value = mock_result

                result = await sdk.agenerate("gen-test")

                assert result is not None

    @pytest.mark.asyncio
    async def test_agenerate_with_custom_config(self):
        """Test agenerate with custom configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = AsyncExperimentSDK(tmpdir)
            await sdk.acreate(ExperimentConfig(name="gen-test"))

            source = Path(tmpdir) / "data.csv"
            source.write_text("data\n")
            await sdk.aadd_data("gen-test", source)

            with patch("persona.core.generation.GenerationPipeline") as MockPipeline:
                mock_instance = MockPipeline.return_value
                mock_result = Mock()
                mock_result.personas = []
                mock_result.reasoning = None
                mock_result.input_tokens = 100
                mock_result.output_tokens = 50
                mock_result.model = "test-model"
                mock_result.provider = "anthropic"
                mock_result.source_files = [source]
                mock_instance.generate.return_value = mock_result

                custom_config = PersonaConfig(count=10, complexity="complex")
                result = await sdk.agenerate("gen-test", config=custom_config)

                assert result is not None


class TestAsyncExperimentSDKSyncMethods:
    """Tests for sync convenience methods."""

    def test_sync_list_experiments(self):
        """Test sync list_experiments method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = AsyncExperimentSDK(tmpdir)
            experiments = sdk.list_experiments()
            assert experiments == []


class TestAsyncExperimentSDKIntegration:
    """Integration-style tests for AsyncExperimentSDK."""

    @pytest.mark.asyncio
    async def test_full_async_workflow(self):
        """Test complete async experiment workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = AsyncExperimentSDK(tmpdir)

            # Create experiment
            config = ExperimentConfig(
                name="async-workflow",
                description="Async workflow test",
                provider="anthropic",
            )
            exp = await sdk.acreate(config)
            assert await sdk.aexists("async-workflow")

            # Add data
            source = Path(tmpdir) / "interviews.csv"
            source.write_text("participant,response\nP1,Fast tools\n")
            await sdk.aadd_data("async-workflow", source)

            # Verify data
            files = await sdk.alist_data("async-workflow")
            assert len(files) == 1

            # Get statistics
            stats = await sdk.aget_statistics("async-workflow")
            assert stats["data_file_count"] == 1

            # List experiments
            experiments = await sdk.alist_experiments()
            assert any(e.name == "async-workflow" for e in experiments)

            # Delete
            await sdk.adelete("async-workflow", confirm=True)
            assert not await sdk.aexists("async-workflow")
