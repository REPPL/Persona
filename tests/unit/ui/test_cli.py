"""
Tests for CLI functionality (F-008, F-015).
"""

import os
import pytest
from pathlib import Path
from typer.testing import CliRunner

from persona.ui.cli import app


runner = CliRunner()


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


class TestInitCommand:
    """Tests for init command."""

    def test_init_creates_structure(self, tmp_path: Path):
        """Test init command creates directory structure."""
        result = runner.invoke(app, ["init", str(tmp_path)])

        assert result.exit_code == 0
        assert (tmp_path / "experiments").exists()
        assert (tmp_path / "data").exists()
        assert (tmp_path / "templates").exists()
        assert (tmp_path / "persona.yaml").exists()

    def test_init_creates_config(self, tmp_path: Path):
        """Test init command creates config file."""
        runner.invoke(app, ["init", str(tmp_path)])

        config_path = tmp_path / "persona.yaml"
        content = config_path.read_text()

        assert "provider: anthropic" in content
        assert "count: 3" in content

    def test_init_does_not_overwrite_config(self, tmp_path: Path):
        """Test init doesn't overwrite existing config."""
        config_path = tmp_path / "persona.yaml"
        config_path.write_text("existing: config\n")

        runner.invoke(app, ["init", str(tmp_path)])

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
                "experiment", "create", "my-exp",
                "--description", "Test description",
                "--provider", "openai",
                "--count", "5",
                "--base-dir", str(tmp_path),
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
        runner.invoke(app, ["experiment", "create", "exp-1", "--base-dir", str(tmp_path)])
        runner.invoke(app, ["experiment", "create", "exp-2", "--base-dir", str(tmp_path)])

        result = runner.invoke(app, ["experiment", "list", "--base-dir", str(tmp_path)])

        assert result.exit_code == 0
        assert "exp-1" in result.stdout
        assert "exp-2" in result.stdout

    def test_experiment_show(self, tmp_path: Path):
        """Test showing experiment details."""
        runner.invoke(
            app,
            [
                "experiment", "create", "show-test",
                "--description", "Test description",
                "--base-dir", str(tmp_path),
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
        runner.invoke(app, ["experiment", "create", "deletable", "--base-dir", str(tmp_path)])

        result = runner.invoke(
            app,
            ["experiment", "delete", "deletable", "--force", "--base-dir", str(tmp_path)],
        )

        assert result.exit_code == 0
        assert "Deleted experiment" in result.stdout
        assert not (tmp_path / "deletable").exists()

    def test_experiment_delete_not_found(self, tmp_path: Path):
        """Test deleting nonexistent experiment."""
        result = runner.invoke(
            app,
            ["experiment", "delete", "nonexistent", "--force", "--base-dir", str(tmp_path)],
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

        assert result.exit_code == 2  # Typer validation error

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
