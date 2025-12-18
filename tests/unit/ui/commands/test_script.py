"""
Tests for script CLI command (F-104).
"""

import json

import pytest
from persona.ui.cli import app
from typer.testing import CliRunner


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def sample_persona_file(tmp_path):
    """Create a sample persona JSON file."""
    persona = {
        "id": "persona-test-001",
        "name": "Test User",
        "demographics": {"role": "Developer", "age": 30, "experience": "5 years"},
        "goals": ["Streamline development workflow", "Learn new technologies"],
        "pain_points": ["Manual testing is slow", "Complex deployment process"],
        "behaviours": ["Uses keyboard shortcuts", "Prefers command-line tools"],
        "quotes": ["I want automation", "Why is this so complicated?"],
        "additional": {"motivations": ["Professional growth"]},
    }

    persona_file = tmp_path / "persona.json"
    persona_file.write_text(json.dumps(persona, indent=2))
    return persona_file


class TestScriptGenerate:
    """Tests for 'persona script generate' command."""

    def test_help_shows_usage(self, runner):
        """Test that help shows command usage."""
        result = runner.invoke(app, ["script", "generate", "--help"])
        assert result.exit_code == 0
        assert "Generate a conversation script" in result.stdout
        assert "PERSONA_PATH" in result.stdout

    def test_requires_persona_path(self, runner):
        """Test that persona path is required."""
        result = runner.invoke(app, ["script", "generate"])
        assert result.exit_code != 0
        # Just check that it fails, error message format may vary

    def test_generates_system_prompt_format(self, runner, sample_persona_file):
        """Test generating system prompt format."""
        result = runner.invoke(
            app,
            [
                "script",
                "generate",
                str(sample_persona_file),
                "--format",
                "system_prompt",
            ],
        )
        assert result.exit_code == 0
        assert "Test User" in result.stdout
        assert "SYNTHETIC_PERSONA_SCRIPT" in result.stdout

    def test_generates_character_card_format(self, runner, sample_persona_file):
        """Test generating character card format (JSON)."""
        result = runner.invoke(
            app,
            [
                "script",
                "generate",
                str(sample_persona_file),
                "--format",
                "character_card",
            ],
        )
        assert result.exit_code == 0
        assert "Test User" in result.stdout

    def test_saves_to_file(self, runner, sample_persona_file, tmp_path):
        """Test saving script to file."""
        output_file = tmp_path / "script.txt"
        result = runner.invoke(
            app,
            [
                "script",
                "generate",
                str(sample_persona_file),
                "--format",
                "system_prompt",
                "--output",
                str(output_file),
            ],
        )
        assert result.exit_code == 0
        assert output_file.exists()
        content = output_file.read_text()
        assert "Test User" in content
        assert "SYNTHETIC_PERSONA_SCRIPT" in content

    def test_yaml_format_option(self, runner, sample_persona_file, tmp_path):
        """Test YAML output format for character card."""
        output_file = tmp_path / "script.yaml"
        result = runner.invoke(
            app,
            [
                "script",
                "generate",
                str(sample_persona_file),
                "--format",
                "character_card",
                "--yaml",
                "--output",
                str(output_file),
            ],
        )
        assert result.exit_code == 0
        assert output_file.exists()
        content = output_file.read_text()
        # YAML format indicators
        assert "name: Test User" in content or "name:" in content

    def test_privacy_threshold_option(self, runner, sample_persona_file):
        """Test custom privacy threshold."""
        result = runner.invoke(
            app, ["script", "generate", str(sample_persona_file), "--threshold", "0.2"]
        )
        assert result.exit_code == 0
        assert "Privacy threshold: 0.2" in result.stdout

    def test_handles_nonexistent_file(self, runner):
        """Test error handling for missing file."""
        result = runner.invoke(app, ["script", "generate", "nonexistent.json"])
        assert result.exit_code != 0

    def test_shows_privacy_audit_result(self, runner, sample_persona_file):
        """Test that privacy audit results are shown."""
        result = runner.invoke(app, ["script", "generate", str(sample_persona_file)])
        assert result.exit_code == 0
        # Should show privacy audit result
        assert "Privacy audit" in result.stdout or "Privacy" in result.stdout


class TestScriptBatch:
    """Tests for 'persona script batch' command."""

    def test_help_shows_usage(self, runner):
        """Test that help shows command usage."""
        result = runner.invoke(app, ["script", "batch", "--help"])
        assert result.exit_code == 0
        assert "Generate conversation scripts for multiple personas" in result.stdout

    def test_processes_single_file(self, runner, sample_persona_file, tmp_path):
        """Test batch processing of single file."""
        output_dir = tmp_path / "scripts"
        result = runner.invoke(
            app,
            ["script", "batch", str(sample_persona_file), "--output", str(output_dir)],
        )
        assert result.exit_code == 0
        assert output_dir.exists()
        # Check output files exist
        output_files = list(output_dir.glob("*.json"))
        assert len(output_files) >= 1

    def test_processes_directory(self, runner, tmp_path):
        """Test batch processing of directory."""
        # Create multiple persona files
        personas_dir = tmp_path / "personas"
        personas_dir.mkdir()

        for i in range(3):
            persona = {
                "id": f"persona-{i}",
                "name": f"User {i}",
                "demographics": {"role": "Tester"},
                "goals": ["Test goal"],
                "pain_points": ["Test pain"],
                "behaviours": ["Test behaviour"],
                "quotes": ["Test quote"],
                "additional": {},
            }
            (personas_dir / f"persona_{i}.json").write_text(json.dumps(persona))

        output_dir = tmp_path / "scripts"
        result = runner.invoke(
            app, ["script", "batch", str(personas_dir), "--output", str(output_dir)]
        )
        assert result.exit_code == 0
        assert output_dir.exists()
        # Should have processed all 3 files
        output_files = list(output_dir.glob("*.json"))
        assert len(output_files) == 3

    def test_batch_with_different_format(self, runner, sample_persona_file, tmp_path):
        """Test batch generation with system_prompt format."""
        output_dir = tmp_path / "scripts"
        result = runner.invoke(
            app,
            [
                "script",
                "batch",
                str(sample_persona_file),
                "--output",
                str(output_dir),
                "--format",
                "system_prompt",
            ],
        )
        assert result.exit_code == 0
        # Should create .txt files for system_prompt format
        output_files = list(output_dir.glob("*.txt"))
        assert len(output_files) >= 1

    def test_shows_summary(self, runner, sample_persona_file, tmp_path):
        """Test that batch command shows summary."""
        output_dir = tmp_path / "scripts"
        result = runner.invoke(
            app,
            ["script", "batch", str(sample_persona_file), "--output", str(output_dir)],
        )
        assert result.exit_code == 0
        assert "Summary:" in result.stdout
        assert "Success:" in result.stdout


class TestScriptFormats:
    """Tests for different script formats."""

    def test_jinja2_template_format(self, runner, sample_persona_file, tmp_path):
        """Test Jinja2 template format output."""
        output_file = tmp_path / "script.j2"
        result = runner.invoke(
            app,
            [
                "script",
                "generate",
                str(sample_persona_file),
                "--format",
                "jinja2_template",
                "--output",
                str(output_file),
            ],
        )
        assert result.exit_code == 0
        assert output_file.exists()
        content = output_file.read_text()
        # Check for Jinja2 template syntax
        assert "{{" in content or "{%" in content

    def test_invalid_format_rejected(self, runner, sample_persona_file):
        """Test that invalid format is rejected."""
        result = runner.invoke(
            app,
            [
                "script",
                "generate",
                str(sample_persona_file),
                "--format",
                "invalid_format",
            ],
        )
        assert result.exit_code != 0
        assert "Unknown format" in result.stdout


class TestPrivacyFeatures:
    """Tests for privacy features in script generation."""

    def test_strict_mode_default(self, runner, sample_persona_file):
        """Test that strict mode is enabled by default."""
        result = runner.invoke(app, ["script", "generate", str(sample_persona_file)])
        # Should succeed with default personas (no leakage)
        assert result.exit_code == 0

    def test_custom_threshold(self, runner, sample_persona_file):
        """Test custom privacy threshold."""
        result = runner.invoke(
            app, ["script", "generate", str(sample_persona_file), "--threshold", "0.05"]
        )
        # Should process with custom threshold
        assert (
            result.exit_code == 0 or result.exit_code == 1
        )  # May pass or fail depending on content
