"""
Tests for experiment management functionality (F-006).
"""

from pathlib import Path

import pytest
from persona.core.experiments import Experiment, ExperimentManager
from persona.core.experiments.manager import ExperimentConfig


class TestExperimentConfig:
    """Tests for ExperimentConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = ExperimentConfig(name="test")

        assert config.name == "test"
        assert config.provider == "anthropic"
        assert config.workflow == "default"
        assert config.count == 3

    def test_from_dict(self):
        """Test creating config from dictionary."""
        data = {
            "name": "my-exp",
            "description": "Test experiment",
            "provider": "openai",
            "count": 5,
        }

        config = ExperimentConfig.from_dict(data)

        assert config.name == "my-exp"
        assert config.description == "Test experiment"
        assert config.provider == "openai"
        assert config.count == 5

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = ExperimentConfig(
            name="test",
            description="Description",
            provider="gemini",
        )

        data = config.to_dict()

        assert data["name"] == "test"
        assert data["description"] == "Description"
        assert data["provider"] == "gemini"


class TestExperiment:
    """Tests for Experiment dataclass."""

    def test_create_experiment(self, tmp_path: Path):
        """Test creating an experiment."""
        config = ExperimentConfig(name="test-exp")
        exp = Experiment(path=tmp_path / "test-exp", config=config)

        assert exp.name == "test-exp"
        assert exp.path == tmp_path / "test-exp"

    def test_directories(self, tmp_path: Path):
        """Test experiment directory paths."""
        exp_path = tmp_path / "test-exp"
        config = ExperimentConfig(name="test-exp")
        exp = Experiment(path=exp_path, config=config)

        assert exp.data_dir == exp_path / "data"
        assert exp.outputs_dir == exp_path / "outputs"

    def test_list_outputs_empty(self, tmp_path: Path):
        """Test listing outputs when none exist."""
        config = ExperimentConfig(name="test")
        exp = Experiment(path=tmp_path / "test", config=config)

        outputs = exp.list_outputs()
        assert outputs == []


class TestExperimentManager:
    """Tests for ExperimentManager class."""

    def test_create_experiment(self, tmp_path: Path):
        """Test creating an experiment."""
        manager = ExperimentManager(base_dir=tmp_path)
        exp = manager.create("my-experiment", description="Test")

        assert exp.name == "my-experiment"
        assert exp.path.exists()
        assert (exp.path / "config.yaml").exists()
        assert (exp.path / "data").exists()
        assert (exp.path / "outputs").exists()
        assert (exp.path / "README.md").exists()

    def test_create_experiment_with_config(self, tmp_path: Path):
        """Test creating experiment with custom config."""
        manager = ExperimentManager(base_dir=tmp_path)
        exp = manager.create(
            "custom-exp",
            provider="openai",
            count=5,
            complexity="complex",
        )

        assert exp.config.provider == "openai"
        assert exp.config.count == 5
        assert exp.config.complexity == "complex"

    def test_create_experiment_already_exists(self, tmp_path: Path):
        """Test error when experiment already exists."""
        manager = ExperimentManager(base_dir=tmp_path)
        manager.create("duplicate")

        with pytest.raises(ValueError) as excinfo:
            manager.create("duplicate")

        assert "already exists" in str(excinfo.value)

    def test_load_experiment(self, tmp_path: Path):
        """Test loading an existing experiment."""
        manager = ExperimentManager(base_dir=tmp_path)
        manager.create("loadable", description="Test loading")

        loaded = manager.load("loadable")

        assert loaded.name == "loadable"
        assert loaded.config.description == "Test loading"

    def test_load_nonexistent(self, tmp_path: Path):
        """Test error loading nonexistent experiment."""
        manager = ExperimentManager(base_dir=tmp_path)

        with pytest.raises(FileNotFoundError):
            manager.load("nonexistent")

    def test_list_experiments(self, tmp_path: Path):
        """Test listing experiments."""
        manager = ExperimentManager(base_dir=tmp_path)

        manager.create("exp-a")
        manager.create("exp-b")
        manager.create("exp-c")

        experiments = manager.list_experiments()

        assert len(experiments) == 3
        assert "exp-a" in experiments
        assert "exp-b" in experiments
        assert "exp-c" in experiments

    def test_list_experiments_empty(self, tmp_path: Path):
        """Test listing when no experiments exist."""
        manager = ExperimentManager(base_dir=tmp_path)
        experiments = manager.list_experiments()

        assert experiments == []

    def test_exists(self, tmp_path: Path):
        """Test checking experiment existence."""
        manager = ExperimentManager(base_dir=tmp_path)
        manager.create("exists-test")

        assert manager.exists("exists-test") is True
        assert manager.exists("nonexistent") is False

    def test_delete_experiment(self, tmp_path: Path):
        """Test deleting an experiment."""
        manager = ExperimentManager(base_dir=tmp_path)
        exp = manager.create("deletable")
        exp_path = exp.path

        # Without confirmation
        result = manager.delete("deletable", confirm=False)
        assert result is False
        assert exp_path.exists()

        # With confirmation
        result = manager.delete("deletable", confirm=True)
        assert result is True
        assert not exp_path.exists()

    def test_delete_nonexistent(self, tmp_path: Path):
        """Test deleting nonexistent experiment."""
        manager = ExperimentManager(base_dir=tmp_path)

        with pytest.raises(FileNotFoundError):
            manager.delete("nonexistent", confirm=True)

    def test_name_sanitisation(self, tmp_path: Path):
        """Test experiment name sanitisation."""
        manager = ExperimentManager(base_dir=tmp_path)

        # Spaces converted to hyphens
        exp1 = manager.create("my experiment name")
        assert "my-experiment-name" in str(exp1.path)

        # Special characters removed
        exp2 = manager.create("Test@Experiment#2024!")
        assert "@" not in str(exp2.path)
        assert "#" not in str(exp2.path)

    def test_readme_content(self, tmp_path: Path):
        """Test README file content."""
        manager = ExperimentManager(base_dir=tmp_path)
        exp = manager.create("readme-test", description="Test description")

        readme_path = exp.path / "README.md"
        content = readme_path.read_text()

        assert "readme-test" in content
        assert "Test description" in content
        assert "config.yaml" in content
