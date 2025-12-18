"""Tests for ExperimentSDK class."""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from persona.sdk import ExperimentConfig, ExperimentSDK, PersonaConfig
from persona.sdk.exceptions import ConfigurationError, DataError


class TestExperimentSDKInit:
    """Tests for ExperimentSDK initialisation."""

    def test_default_base_dir(self):
        """Test default base directory."""
        sdk = ExperimentSDK()
        assert sdk.base_dir == Path("./experiments")

    def test_custom_base_dir(self):
        """Test custom base directory."""
        sdk = ExperimentSDK("/custom/path")
        assert sdk.base_dir == Path("/custom/path")

    def test_path_object_accepted(self):
        """Test Path object is accepted."""
        sdk = ExperimentSDK(Path("/custom/path"))
        assert sdk.base_dir == Path("/custom/path")


class TestExperimentSDKCreate:
    """Tests for experiment creation."""

    def test_create_experiment(self):
        """Test creating an experiment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)
            config = ExperimentConfig(name="test-experiment")
            exp = sdk.create(config)

            assert exp.name == "test-experiment"
            assert Path(exp.path).exists()
            assert exp.data_dir.exists()
            assert exp.outputs_dir.exists()

    def test_create_experiment_with_full_config(self):
        """Test creating experiment with full configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)
            config = ExperimentConfig(
                name="full-test",
                description="Full test experiment",
                provider="openai",
                model="gpt-4",
                workflow="custom",
                count=5,
            )
            exp = sdk.create(config)

            assert exp.name == "full-test"
            assert exp.description == "Full test experiment"
            assert exp.provider == "openai"
            assert exp.model == "gpt-4"
            assert exp.workflow == "custom"

    def test_create_experiment_already_exists(self):
        """Test creating duplicate experiment raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)
            config = ExperimentConfig(name="duplicate")

            sdk.create(config)

            with pytest.raises(ConfigurationError) as exc_info:
                sdk.create(config)

            assert "already exists" in str(exc_info.value).lower()

    def test_create_creates_readme(self):
        """Test creating experiment creates README."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)
            config = ExperimentConfig(name="readme-test")
            exp = sdk.create(config)

            readme_path = Path(exp.path) / "README.md"
            assert readme_path.exists()


class TestExperimentSDKLoad:
    """Tests for loading experiments."""

    def test_load_experiment(self):
        """Test loading an existing experiment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)

            # Create first
            config = ExperimentConfig(name="load-test")
            sdk.create(config)

            # Load
            exp = sdk.load("load-test")
            assert exp.name == "load-test"

    def test_load_nonexistent_experiment(self):
        """Test loading nonexistent experiment raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)

            with pytest.raises(ConfigurationError) as exc_info:
                sdk.load("nonexistent")

            assert "not found" in str(exc_info.value).lower()

    def test_load_preserves_config(self):
        """Test loading preserves experiment configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)

            config = ExperimentConfig(
                name="config-test",
                description="Test description",
                provider="openai",
            )
            sdk.create(config)

            exp = sdk.load("config-test")
            assert exp.description == "Test description"
            assert exp.provider == "openai"


class TestExperimentSDKList:
    """Tests for listing experiments."""

    def test_list_empty(self):
        """Test listing with no experiments."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)
            experiments = sdk.list_experiments()
            assert experiments == []

    def test_list_multiple(self):
        """Test listing multiple experiments."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)

            sdk.create(ExperimentConfig(name="exp-1"))
            sdk.create(ExperimentConfig(name="exp-2"))
            sdk.create(ExperimentConfig(name="exp-3"))

            experiments = sdk.list_experiments()
            names = [e.name for e in experiments]

            assert len(experiments) == 3
            assert "exp-1" in names
            assert "exp-2" in names
            assert "exp-3" in names


class TestExperimentSDKDelete:
    """Tests for deleting experiments."""

    def test_delete_without_confirm(self):
        """Test delete without confirm does nothing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)
            sdk.create(ExperimentConfig(name="delete-test"))

            result = sdk.delete("delete-test", confirm=False)
            assert result is False
            assert sdk.exists("delete-test")

    def test_delete_with_confirm(self):
        """Test delete with confirm removes experiment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)
            sdk.create(ExperimentConfig(name="delete-test"))

            result = sdk.delete("delete-test", confirm=True)
            assert result is True
            assert not sdk.exists("delete-test")

    def test_delete_nonexistent(self):
        """Test deleting nonexistent experiment raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)

            with pytest.raises(ConfigurationError):
                sdk.delete("nonexistent", confirm=True)


class TestExperimentSDKExists:
    """Tests for exists check."""

    def test_exists_true(self):
        """Test exists returns True for existing experiment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)
            sdk.create(ExperimentConfig(name="exists-test"))

            assert sdk.exists("exists-test") is True

    def test_exists_false(self):
        """Test exists returns False for nonexistent experiment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)
            assert sdk.exists("nonexistent") is False


class TestExperimentSDKData:
    """Tests for data management."""

    def test_add_data_copy(self):
        """Test adding data by copying."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)
            exp = sdk.create(ExperimentConfig(name="data-test"))

            # Create source file
            source = Path(tmpdir) / "source.csv"
            source.write_text("data,value\n1,2\n")

            result = sdk.add_data("data-test", source, copy=True)

            assert result.exists()
            assert result.parent == exp.data_dir
            assert result.read_text() == "data,value\n1,2\n"

    def test_add_data_nonexistent_file(self):
        """Test adding nonexistent file raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)
            sdk.create(ExperimentConfig(name="data-test"))

            with pytest.raises(DataError):
                sdk.add_data("data-test", "/nonexistent/file.csv")

    def test_add_data_nonexistent_experiment(self):
        """Test adding to nonexistent experiment raises error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)

            source = Path(tmpdir) / "source.csv"
            source.write_text("data\n")

            with pytest.raises(ConfigurationError):
                sdk.add_data("nonexistent", source)

    def test_list_data_empty(self):
        """Test listing data in empty experiment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)
            sdk.create(ExperimentConfig(name="empty-data"))

            files = sdk.list_data("empty-data")
            assert files == []

    def test_list_data_multiple(self):
        """Test listing multiple data files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)
            exp = sdk.create(ExperimentConfig(name="multi-data"))

            # Add multiple files
            for name in ["file1.csv", "file2.json", "file3.md"]:
                source = Path(tmpdir) / name
                source.write_text("data\n")
                sdk.add_data("multi-data", source)

            files = sdk.list_data("multi-data")
            names = [f.name for f in files]

            assert len(files) == 3
            assert "file1.csv" in names
            assert "file2.json" in names
            assert "file3.md" in names

    def test_list_data_ignores_hidden(self):
        """Test listing data ignores hidden files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)
            exp = sdk.create(ExperimentConfig(name="hidden-test"))

            # Add visible file
            source = Path(tmpdir) / "visible.csv"
            source.write_text("data\n")
            sdk.add_data("hidden-test", source)

            # Add hidden file directly
            hidden = exp.data_dir / ".hidden"
            hidden.write_text("hidden\n")

            files = sdk.list_data("hidden-test")
            names = [f.name for f in files]

            assert "visible.csv" in names
            assert ".hidden" not in names


class TestExperimentSDKOutputs:
    """Tests for output management."""

    def test_get_outputs_empty(self):
        """Test getting outputs from empty experiment."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)
            sdk.create(ExperimentConfig(name="output-test"))

            outputs = sdk.get_outputs("output-test")
            assert outputs == []

    def test_get_outputs_multiple(self):
        """Test getting multiple output directories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)
            exp = sdk.create(ExperimentConfig(name="output-test"))

            # Create output directories
            for name in ["20241201_120000", "20241202_130000"]:
                output_dir = exp.outputs_dir / name
                output_dir.mkdir()

            outputs = sdk.get_outputs("output-test")
            names = [o.name for o in outputs]

            assert len(outputs) == 2
            assert "20241201_120000" in names
            assert "20241202_130000" in names


class TestExperimentSDKStatistics:
    """Tests for experiment statistics."""

    def test_get_statistics(self):
        """Test getting experiment statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)
            config = ExperimentConfig(
                name="stats-test",
                description="Statistics test",
                provider="openai",
            )
            exp = sdk.create(config)

            # Add some data
            source = Path(tmpdir) / "data.csv"
            source.write_text("test data content\n")
            sdk.add_data("stats-test", source)

            stats = sdk.get_statistics("stats-test")

            assert stats["name"] == "stats-test"
            assert stats["description"] == "Statistics test"
            assert stats["provider"] == "openai"
            assert stats["data_file_count"] == 1
            assert stats["data_size_bytes"] > 0
            assert stats["run_count"] == 0
            assert "created_at" in stats


class TestExperimentSDKGenerate:
    """Tests for generation from experiments."""

    def test_generate_no_data(self):
        """Test generate raises error with no data."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)
            sdk.create(ExperimentConfig(name="gen-test"))

            with pytest.raises(DataError) as exc_info:
                sdk.generate("gen-test")

            assert "no data" in str(exc_info.value).lower()

    def test_generate_with_data(self):
        """Test generate with data files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)
            exp = sdk.create(
                ExperimentConfig(
                    name="gen-test",
                    provider="anthropic",
                )
            )

            # Add data
            source = Path(tmpdir) / "interviews.csv"
            source.write_text("participant,quote\nP1,I need speed\n")
            sdk.add_data("gen-test", source)

            # Mock the generator
            with patch("persona.sdk.experiment.PersonaGenerator") as MockGenerator:
                mock_instance = MockGenerator.return_value
                mock_result = Mock()
                mock_result.personas = []
                mock_instance.generate.return_value = mock_result

                result = sdk.generate("gen-test")

                assert result is not None
                MockGenerator.assert_called_once_with(
                    provider="anthropic",
                    model=None,
                )

    def test_generate_with_custom_config(self):
        """Test generate with custom configuration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)
            sdk.create(ExperimentConfig(name="gen-test"))

            # Add data
            source = Path(tmpdir) / "data.csv"
            source.write_text("data\n")
            sdk.add_data("gen-test", source)

            with patch("persona.sdk.experiment.PersonaGenerator") as MockGenerator:
                mock_instance = MockGenerator.return_value
                mock_result = Mock()
                mock_result.personas = []
                mock_instance.generate.return_value = mock_result

                custom_config = PersonaConfig(count=10, complexity="complex")
                sdk.generate("gen-test", config=custom_config)

                # Verify generate was called with config as second positional arg
                call_args = mock_instance.generate.call_args
                assert call_args[0][1] == custom_config


class TestExperimentSDKIntegration:
    """Integration-style tests for ExperimentSDK."""

    def test_full_workflow(self):
        """Test complete experiment workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sdk = ExperimentSDK(tmpdir)

            # Create experiment
            config = ExperimentConfig(
                name="full-workflow",
                description="Full workflow test",
                provider="anthropic",
            )
            exp = sdk.create(config)
            assert sdk.exists("full-workflow")

            # Add data
            source = Path(tmpdir) / "interviews.csv"
            source.write_text("participant,response\nP1,Fast tools are essential\n")
            sdk.add_data("full-workflow", source)

            # Verify data
            files = sdk.list_data("full-workflow")
            assert len(files) == 1

            # Get statistics
            stats = sdk.get_statistics("full-workflow")
            assert stats["data_file_count"] == 1

            # List experiments
            experiments = sdk.list_experiments()
            assert any(e.name == "full-workflow" for e in experiments)

            # Delete
            sdk.delete("full-workflow", confirm=True)
            assert not sdk.exists("full-workflow")
