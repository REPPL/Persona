"""
Tests for CLI functionality (F-008, F-015, F-086).
"""

import json
from pathlib import Path

import pytest
from persona.ui.cli import _reset_globals, app
from typer.testing import CliRunner

runner = CliRunner()


@pytest.fixture(autouse=True)
def reset_cli_globals():
    """Reset CLI global state before each test."""
    _reset_globals()
    yield
    _reset_globals()


class TestVersionFlag:
    """Tests for --version flag."""

    def test_version_flag(self):
        """Test --version flag shows version."""
        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "Persona" in result.stdout

    def test_version_short_flag(self):
        """Test -V short flag shows version."""
        result = runner.invoke(app, ["-V"])

        assert result.exit_code == 0
        assert "Persona" in result.stdout


class TestOutputModes:
    """Tests for CLI output modes (F-086)."""

    def test_no_color_flag_exists(self):
        """Test --no-color flag is available."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "--no-color" in result.stdout

    def test_no_color_flag_works(self):
        """Test --no-color flag doesn't break commands."""
        result = runner.invoke(app, ["--no-color", "check"])

        assert result.exit_code == 0
        assert "Persona Health Check" in result.stdout

    def test_quiet_flag_exists(self):
        """Test --quiet flag is available."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "--quiet" in result.stdout
        assert "-q" in result.stdout

    def test_quiet_flag_works(self):
        """Test --quiet flag doesn't break commands."""
        result = runner.invoke(app, ["--quiet", "check"])

        # Quiet mode should still succeed
        assert result.exit_code == 0

    def test_verbose_flag_exists(self):
        """Test --verbose flag is available."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "--verbose" in result.stdout
        assert "-v" in result.stdout

    def test_verbose_flag_works(self):
        """Test --verbose flag doesn't break commands."""
        result = runner.invoke(app, ["-v", "check"])

        assert result.exit_code == 0
        assert "Persona Health Check" in result.stdout

    def test_double_verbose_flag_works(self):
        """Test -vv flag doesn't break commands."""
        result = runner.invoke(app, ["-v", "-v", "check"])

        assert result.exit_code == 0
        assert "Persona Health Check" in result.stdout

    def test_no_color_env_variable(self, monkeypatch):
        """Test NO_COLOR environment variable is respected."""
        monkeypatch.setenv("NO_COLOR", "1")
        result = runner.invoke(app, ["check"])

        assert result.exit_code == 0
        # Command should work with NO_COLOR set
        assert "Persona Health Check" in result.stdout


class TestCheckCommand:
    """Tests for check command."""

    def test_check_shows_status(self):
        """Test check command shows health status."""
        result = runner.invoke(app, ["check"])

        assert result.exit_code == 0
        assert "Persona Health Check" in result.stdout
        assert "Installation: OK" in result.stdout

    def test_check_shows_providers(self):
        """Test check command shows provider status."""
        result = runner.invoke(app, ["check"])

        assert result.exit_code == 0
        assert "Provider Status:" in result.stdout
        assert "anthropic" in result.stdout.lower()
        assert "openai" in result.stdout.lower()
        assert "gemini" in result.stdout.lower()

    def test_check_with_configured_provider(self, monkeypatch):
        """Test check shows configured providers."""
        monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
        result = runner.invoke(app, ["check"])

        assert result.exit_code == 0
        assert "Configured" in result.stdout

    def test_check_json_output(self):
        """Test check command with --json flag produces valid JSON."""
        result = runner.invoke(app, ["check", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["command"] == "check"
        assert "version" in data
        assert data["success"] is True
        assert "providers" in data["data"]
        assert "anthropic" in data["data"]["providers"]
        assert "openai" in data["data"]["providers"]
        assert "gemini" in data["data"]["providers"]

    def test_check_json_provider_structure(self):
        """Test check --json has correct provider structure."""
        result = runner.invoke(app, ["check", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        provider = data["data"]["providers"]["anthropic"]
        assert "configured" in provider
        assert "env_var" in provider
        assert provider["env_var"] == "ANTHROPIC_API_KEY"


class TestModelsCommand:
    """Tests for models command."""

    def test_models_help(self):
        """Test models command help is available."""
        result = runner.invoke(app, ["models", "--help"])

        assert result.exit_code == 0
        assert "--provider" in result.stdout
        assert "--json" in result.stdout

    def test_models_list_all(self):
        """Test models command lists models."""
        result = runner.invoke(app, ["models"])

        assert result.exit_code == 0
        # Should show some models
        assert "per M tokens" in result.stdout

    def test_models_filter_by_provider(self):
        """Test models command filters by provider."""
        result = runner.invoke(app, ["models", "--provider", "anthropic"])

        assert result.exit_code == 0
        # Should only show anthropic models
        assert "anthropic" in result.stdout

    def test_models_json_output(self):
        """Test models command with JSON output."""
        result = runner.invoke(app, ["models", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["command"] == "models"
        assert data["success"] is True
        assert "providers" in data["data"]


class TestCostCommand:
    """Tests for cost command."""

    def test_cost_help(self):
        """Test cost command help is available."""
        result = runner.invoke(app, ["cost", "--help"])

        assert result.exit_code == 0
        assert "--from" in result.stdout
        assert "--tokens" in result.stdout
        assert "--count" in result.stdout
        assert "--json" in result.stdout

    def test_cost_default_tokens(self):
        """Test cost command with default token estimate."""
        result = runner.invoke(app, ["cost"])

        assert result.exit_code == 0
        # Should show cost table even with default tokens

    def test_cost_with_token_count(self):
        """Test cost command with specified token count."""
        result = runner.invoke(app, ["cost", "--tokens", "10000"])

        assert result.exit_code == 0
        assert "10,000" in result.stdout

    def test_cost_json_output(self):
        """Test cost command with --json flag."""
        result = runner.invoke(app, ["cost", "--tokens", "5000", "--json"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["command"] == "cost"
        assert data["success"] is True
        assert "estimates" in data["data"]
        assert data["data"]["input_tokens"] == 5000

    def test_cost_json_single_model(self):
        """Test cost command JSON output for single model."""
        result = runner.invoke(
            app,
            [
                "cost",
                "--tokens",
                "5000",
                "--model",
                "claude-sonnet-4-20250514",
                "--json",
            ],
        )

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["command"] == "cost"
        assert "model" in data["data"]
        assert data["data"]["model"] == "claude-sonnet-4-20250514"


class TestInitCommand:
    """Tests for init command."""

    def test_init_creates_structure(self, tmp_path: Path):
        """Test init command creates directory structure."""
        result = runner.invoke(app, ["init", "test-project", "--path", str(tmp_path)])

        assert result.exit_code == 0
        project_dir = tmp_path / "test-project"
        assert project_dir.exists()
        assert (project_dir / "data").exists()
        assert (project_dir / "output").exists()
        assert (project_dir / "templates").exists()
        assert (project_dir / "persona.yaml").exists()

    def test_init_creates_config(self, tmp_path: Path):
        """Test init command creates config file."""
        runner.invoke(app, ["init", "test-project", "--path", str(tmp_path)])

        config_path = tmp_path / "test-project" / "persona.yaml"
        content = config_path.read_text()

        assert "provider: anthropic" in content
        assert "count: 3" in content
        assert "name: test-project" in content

    def test_init_does_not_overwrite_config(self, tmp_path: Path):
        """Test init doesn't overwrite existing config."""
        project_dir = tmp_path / "test-project"
        project_dir.mkdir(parents=True)
        config_path = project_dir / "persona.yaml"
        config_path.write_text("existing: config\n")

        # Use input="n\n" to answer "no" to the continue anyway prompt
        runner.invoke(
            app, ["init", "test-project", "--path", str(tmp_path)], input="n\n"
        )

        content = config_path.read_text()
        assert "existing: config" in content


class TestExperimentCommands:
    """Tests for experiment subcommands."""

    def test_experiment_create(self, tmp_path: Path):
        """Test creating an experiment."""
        result = runner.invoke(
            app,
            ["experiment", "create", "test-exp", "--base-dir", str(tmp_path)],
        )

        assert result.exit_code == 0
        assert "Created experiment" in result.stdout
        assert (tmp_path / "test-exp").exists()

    def test_experiment_create_with_options(self, tmp_path: Path):
        """Test creating experiment with options."""
        result = runner.invoke(
            app,
            [
                "experiment",
                "create",
                "my-exp",
                "--description",
                "Test description",
                "--provider",
                "openai",
                "--count",
                "5",
                "--base-dir",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0
        assert "Created experiment" in result.stdout

    def test_experiment_list_empty(self, tmp_path: Path):
        """Test listing when no experiments exist."""
        result = runner.invoke(
            app,
            ["experiment", "list", "--base-dir", str(tmp_path)],
        )

        assert result.exit_code == 0
        assert "No experiments found" in result.stdout

    def test_experiment_list_with_experiments(self, tmp_path: Path):
        """Test listing experiments."""
        # Create some experiments
        runner.invoke(
            app, ["experiment", "create", "exp-1", "--base-dir", str(tmp_path)]
        )
        runner.invoke(
            app, ["experiment", "create", "exp-2", "--base-dir", str(tmp_path)]
        )

        result = runner.invoke(app, ["experiment", "list", "--base-dir", str(tmp_path)])

        assert result.exit_code == 0
        assert "exp-1" in result.stdout
        assert "exp-2" in result.stdout

    def test_experiment_list_json_output(self, tmp_path: Path):
        """Test experiment list with JSON output."""
        runner.invoke(
            app, ["experiment", "create", "json-exp", "--base-dir", str(tmp_path)]
        )

        result = runner.invoke(
            app,
            ["experiment", "list", "--json", "--base-dir", str(tmp_path)],
        )

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["command"] == "experiment list"
        assert data["success"] is True
        assert len(data["data"]["experiments"]) == 1
        assert data["data"]["experiments"][0]["name"] == "json-exp"

    def test_experiment_list_json_empty(self, tmp_path: Path):
        """Test experiment list JSON output when empty."""
        result = runner.invoke(
            app,
            ["experiment", "list", "--json", "--base-dir", str(tmp_path)],
        )

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["success"] is True
        assert data["data"]["experiments"] == []

    def test_experiment_show(self, tmp_path: Path):
        """Test showing experiment details."""
        runner.invoke(
            app,
            [
                "experiment",
                "create",
                "show-test",
                "--description",
                "Test description",
                "--base-dir",
                str(tmp_path),
            ],
        )

        result = runner.invoke(
            app,
            ["experiment", "show", "show-test", "--base-dir", str(tmp_path)],
        )

        assert result.exit_code == 0
        assert "show-test" in result.stdout
        assert "Test description" in result.stdout

    def test_experiment_show_not_found(self, tmp_path: Path):
        """Test showing nonexistent experiment."""
        result = runner.invoke(
            app,
            ["experiment", "show", "nonexistent", "--base-dir", str(tmp_path)],
        )

        assert result.exit_code == 1
        assert "not found" in result.stdout

    def test_experiment_delete_with_force(self, tmp_path: Path):
        """Test deleting experiment with force flag."""
        runner.invoke(
            app, ["experiment", "create", "deletable", "--base-dir", str(tmp_path)]
        )

        result = runner.invoke(
            app,
            [
                "experiment",
                "delete",
                "deletable",
                "--force",
                "--base-dir",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 0
        assert "Deleted experiment" in result.stdout
        assert not (tmp_path / "deletable").exists()

    def test_experiment_delete_not_found(self, tmp_path: Path):
        """Test deleting nonexistent experiment."""
        result = runner.invoke(
            app,
            [
                "experiment",
                "delete",
                "nonexistent",
                "--force",
                "--base-dir",
                str(tmp_path),
            ],
        )

        assert result.exit_code == 1
        assert "not found" in result.stdout


class TestGenerateCommand:
    """Tests for generate command."""

    def test_generate_help(self):
        """Test generate command help."""
        result = runner.invoke(app, ["generate", "--help"])

        assert result.exit_code == 0
        assert "--from" in result.stdout
        assert "--count" in result.stdout
        assert "--provider" in result.stdout

    def test_generate_dry_run(self, tmp_path: Path):
        """Test generate with dry run."""
        # Create test data
        data_file = tmp_path / "test.csv"
        data_file.write_text("id,name,feedback\n1,User,Great product!\n")

        result = runner.invoke(
            app,
            ["generate", "--from", str(data_file), "--dry-run"],
        )

        assert result.exit_code == 0
        assert "Dry run" in result.stdout

    def test_generate_missing_file(self, tmp_path: Path):
        """Test generate with missing file."""
        result = runner.invoke(
            app,
            ["generate", "--from", str(tmp_path / "nonexistent.csv")],
        )

        assert result.exit_code == 1  # Custom path resolution error

    def test_generate_unconfigured_provider(self, tmp_path: Path, monkeypatch):
        """Test generate with unconfigured provider."""
        # Ensure no API keys are set
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

        data_file = tmp_path / "test.csv"
        data_file.write_text("id,feedback\n1,Test\n")

        result = runner.invoke(
            app,
            ["generate", "--from", str(data_file)],
        )

        assert result.exit_code == 1
        assert "not configured" in result.stdout
