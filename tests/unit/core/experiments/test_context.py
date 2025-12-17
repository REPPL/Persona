"""Unit tests for ExperimentContext."""

from pathlib import Path

import pytest
import yaml

from persona.core.experiments.context import ExperimentContext


class TestExperimentContextProperties:
    """Tests for ExperimentContext property accessors."""

    @pytest.fixture
    def temp_experiment(self, tmp_path):
        """Create temporary experiment directory."""
        exp_dir = tmp_path / "test-experiment"
        exp_dir.mkdir()
        (exp_dir / "data").mkdir()
        (exp_dir / "outputs").mkdir()
        return exp_dir

    @pytest.fixture
    def context(self, temp_experiment):
        """Create context for temp experiment."""
        return ExperimentContext(root=temp_experiment, name="test-experiment")

    def test_config_path(self, context, temp_experiment):
        """Should return correct config path."""
        assert context.config_path == temp_experiment / "config.yaml"

    def test_data_dir(self, context, temp_experiment):
        """Should return correct data directory."""
        assert context.data_dir == temp_experiment / "data"

    def test_outputs_dir(self, context, temp_experiment):
        """Should return correct outputs directory."""
        assert context.outputs_dir == temp_experiment / "outputs"

    def test_history_path(self, context, temp_experiment):
        """Should return correct history path."""
        assert context.history_path == temp_experiment / "history.json"

    def test_readme_path(self, context, temp_experiment):
        """Should return correct README path."""
        assert context.readme_path == temp_experiment / "README.md"


class TestExperimentContextStatus:
    """Tests for ExperimentContext status properties."""

    @pytest.fixture
    def temp_experiment(self, tmp_path):
        """Create temporary experiment directory."""
        exp_dir = tmp_path / "test-experiment"
        exp_dir.mkdir()
        (exp_dir / "data").mkdir()
        (exp_dir / "outputs").mkdir()
        return exp_dir

    @pytest.fixture
    def context(self, temp_experiment):
        """Create context for temp experiment."""
        return ExperimentContext(root=temp_experiment, name="test-experiment")

    def test_exists_true(self, context):
        """Should return True when directory exists."""
        assert context.exists is True

    def test_exists_false(self, tmp_path):
        """Should return False when directory doesn't exist."""
        ctx = ExperimentContext(root=tmp_path / "nonexistent", name="fake")
        assert ctx.exists is False

    def test_has_config_false(self, context):
        """Should return False when no config file."""
        assert context.has_config is False

    def test_has_config_true(self, context, temp_experiment):
        """Should return True when config file exists."""
        (temp_experiment / "config.yaml").write_text("name: test")
        assert context.has_config is True

    def test_has_data_false(self, context):
        """Should return False when data dir is empty."""
        assert context.has_data is False

    def test_has_data_true(self, context, temp_experiment):
        """Should return True when data dir has files."""
        (temp_experiment / "data" / "test.csv").write_text("a,b,c")
        assert context.has_data is True

    def test_has_outputs_false(self, context):
        """Should return False when outputs dir is empty."""
        assert context.has_outputs is False

    def test_has_outputs_true(self, context, temp_experiment):
        """Should return True when outputs dir has entries."""
        (temp_experiment / "outputs" / "20241217_120000").mkdir()
        assert context.has_outputs is True

    def test_has_history_false(self, context):
        """Should return False when no history file."""
        assert context.has_history is False

    def test_has_history_true(self, context, temp_experiment):
        """Should return True when history file exists."""
        (temp_experiment / "history.json").write_text("{}")
        assert context.has_history is True


class TestExperimentContextConfig:
    """Tests for ExperimentContext configuration methods."""

    @pytest.fixture
    def temp_experiment(self, tmp_path):
        """Create temporary experiment with config."""
        exp_dir = tmp_path / "test-experiment"
        exp_dir.mkdir()
        (exp_dir / "data").mkdir()
        (exp_dir / "outputs").mkdir()

        config = {
            "name": "test-experiment",
            "description": "Test description",
            "defaults": {
                "provider": "anthropic",
                "model": "claude-sonnet-4-5-20250514",
                "count": 5,
            },
        }
        with open(exp_dir / "config.yaml", "w") as f:
            yaml.dump(config, f)

        return exp_dir

    @pytest.fixture
    def context(self, temp_experiment):
        """Create context for temp experiment."""
        return ExperimentContext(root=temp_experiment, name="test-experiment")

    def test_load_config(self, context):
        """Should load configuration."""
        config = context.load_config()
        assert config["name"] == "test-experiment"
        assert config["description"] == "Test description"
        assert config["defaults"]["provider"] == "anthropic"

    def test_load_config_empty_when_missing(self, tmp_path):
        """Should return empty dict when config missing."""
        exp_dir = tmp_path / "no-config"
        exp_dir.mkdir()
        ctx = ExperimentContext(root=exp_dir, name="no-config")

        config = ctx.load_config()
        assert config == {}

    def test_save_config(self, context, temp_experiment):
        """Should save configuration."""
        new_config = {
            "name": "updated",
            "defaults": {"provider": "openai"},
        }
        context.save_config(new_config)

        # Reload and verify
        with open(temp_experiment / "config.yaml") as f:
            saved = yaml.safe_load(f)

        assert saved["name"] == "updated"
        assert saved["defaults"]["provider"] == "openai"

    def test_get_config_value_simple(self, context):
        """Should get simple config value."""
        value = context.get_config_value("name")
        assert value == "test-experiment"

    def test_get_config_value_nested(self, context):
        """Should get nested config value with dot notation."""
        value = context.get_config_value("defaults.provider")
        assert value == "anthropic"

    def test_get_config_value_default(self, context):
        """Should return default for missing key."""
        value = context.get_config_value("nonexistent", default="fallback")
        assert value == "fallback"


class TestExperimentContextDataOps:
    """Tests for ExperimentContext data operations."""

    @pytest.fixture
    def temp_experiment(self, tmp_path):
        """Create experiment with data files."""
        exp_dir = tmp_path / "test-experiment"
        exp_dir.mkdir()
        data_dir = exp_dir / "data"
        data_dir.mkdir()
        (exp_dir / "outputs").mkdir()

        # Create some data files
        (data_dir / "users.csv").write_text("id,name\n1,Alice\n2,Bob")
        (data_dir / "config.json").write_text('{"key": "value"}')
        (data_dir / "notes.txt").write_text("Some notes")

        return exp_dir

    @pytest.fixture
    def context(self, temp_experiment):
        """Create context for temp experiment."""
        return ExperimentContext(root=temp_experiment, name="test-experiment")

    def test_list_data_files_all(self, context):
        """Should list all data files."""
        files = context.list_data_files()
        assert len(files) == 3

    def test_list_data_files_pattern(self, context):
        """Should filter by glob pattern."""
        files = context.list_data_files("*.csv")
        assert len(files) == 1
        assert files[0].name == "users.csv"

    def test_get_data_summary(self, context):
        """Should return data summary."""
        summary = context.get_data_summary()

        assert summary["file_count"] == 3
        assert summary["total_size_bytes"] > 0
        assert ".csv" in summary["extensions"]
        assert ".json" in summary["extensions"]
        assert ".txt" in summary["extensions"]


class TestExperimentContextOutputOps:
    """Tests for ExperimentContext output operations."""

    @pytest.fixture
    def temp_experiment(self, tmp_path):
        """Create experiment with output directories."""
        exp_dir = tmp_path / "test-experiment"
        exp_dir.mkdir()
        (exp_dir / "data").mkdir()
        outputs_dir = exp_dir / "outputs"
        outputs_dir.mkdir()

        # Create output directories
        (outputs_dir / "20241217_100000").mkdir()
        (outputs_dir / "20241217_120000").mkdir()
        (outputs_dir / "20241217_140000").mkdir()

        return exp_dir

    @pytest.fixture
    def context(self, temp_experiment):
        """Create context for temp experiment."""
        return ExperimentContext(root=temp_experiment, name="test-experiment")

    def test_list_outputs(self, context):
        """Should list output directories."""
        outputs = context.list_outputs()
        assert len(outputs) == 3

    def test_list_outputs_sorted_recent_first(self, context):
        """Should sort outputs with most recent first."""
        outputs = context.list_outputs()
        assert outputs[0].name == "20241217_140000"
        assert outputs[-1].name == "20241217_100000"

    def test_get_latest_output(self, context):
        """Should return most recent output."""
        latest = context.get_latest_output()
        assert latest is not None
        assert latest.name == "20241217_140000"

    def test_get_latest_output_none_when_empty(self, tmp_path):
        """Should return None when no outputs."""
        exp_dir = tmp_path / "empty-exp"
        exp_dir.mkdir()
        (exp_dir / "outputs").mkdir()
        ctx = ExperimentContext(root=exp_dir, name="empty-exp")

        assert ctx.get_latest_output() is None


class TestExperimentContextFactories:
    """Tests for ExperimentContext factory methods."""

    @pytest.fixture
    def temp_experiments_dir(self, tmp_path):
        """Create experiments directory with experiments."""
        base_dir = tmp_path / "experiments"
        base_dir.mkdir()

        # Create an experiment
        exp_dir = base_dir / "my-research"
        exp_dir.mkdir()
        (exp_dir / "data").mkdir()
        (exp_dir / "outputs").mkdir()
        (exp_dir / "config.yaml").write_text("name: my-research")

        return base_dir

    def test_from_path(self, temp_experiments_dir):
        """Should create context from path."""
        exp_path = temp_experiments_dir / "my-research"
        ctx = ExperimentContext.from_path(exp_path)

        assert ctx.name == "my-research"
        assert ctx.root == exp_path

    def test_from_path_raises_for_nonexistent(self, tmp_path):
        """Should raise FileNotFoundError for nonexistent path."""
        with pytest.raises(FileNotFoundError):
            ExperimentContext.from_path(tmp_path / "nonexistent")

    def test_load_by_name(self, temp_experiments_dir):
        """Should load experiment by name."""
        ctx = ExperimentContext.load("my-research", base_dir=temp_experiments_dir)

        assert ctx.name == "my-research"
        assert ctx.exists is True

    def test_load_raises_for_nonexistent(self, temp_experiments_dir):
        """Should raise FileNotFoundError for unknown name."""
        with pytest.raises(FileNotFoundError) as exc_info:
            ExperimentContext.load("nonexistent", base_dir=temp_experiments_dir)

        assert "not found" in str(exc_info.value).lower()

    def test_create_new_experiment(self, tmp_path):
        """Should create new experiment structure."""
        base_dir = tmp_path / "experiments"
        base_dir.mkdir()

        ctx = ExperimentContext.create(
            name="new-experiment",
            base_dir=base_dir,
            description="Test experiment",
            provider="openai",
            count=5,
        )

        assert ctx.exists is True
        assert ctx.data_dir.exists()
        assert ctx.outputs_dir.exists()
        assert ctx.config_path.exists()
        assert ctx.readme_path.exists()

        config = ctx.load_config()
        assert config["name"] == "new-experiment"
        assert config["description"] == "Test experiment"

    def test_create_raises_for_existing(self, temp_experiments_dir):
        """Should raise ValueError for existing experiment."""
        with pytest.raises(ValueError) as exc_info:
            ExperimentContext.create("my-research", base_dir=temp_experiments_dir)

        assert "already exists" in str(exc_info.value)
