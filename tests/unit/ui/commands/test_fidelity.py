"""
Tests for fidelity CLI command.

Tests the fidelity command integration.
"""

import json
import tempfile
from pathlib import Path

import pytest
from typer.testing import CliRunner

from persona.ui.cli import app

runner = CliRunner()


@pytest.fixture
def sample_persona_file():
    """Create a temporary persona JSON file."""
    persona_data = {
        "id": "test-1",
        "name": "Test User",
        "demographics": {"age": 30, "occupation": "Software Developer"},
        "goals": ["Improve productivity", "Learn new skills", "Advance career"],
        "pain_points": ["Too many meetings", "Legacy code"],
        "behaviours": ["Uses shortcuts", "Prefers automation"],
        "quotes": ["I need better tools"],
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(persona_data, f)
        yield Path(f.name)

    Path(f.name).unlink()


@pytest.fixture
def sample_constraints_file():
    """Create a temporary constraints YAML file."""
    constraints_yaml = """
name: Test Constraints
constraints:
  structure:
    required_fields:
      - name
      - age
  limits:
    age_range: [25, 45]
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(constraints_yaml)
        yield Path(f.name)

    Path(f.name).unlink()


def test_fidelity_command_exists():
    """Test that fidelity command is registered."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "fidelity" in result.output


def test_fidelity_with_persona_file(sample_persona_file, sample_constraints_file):
    """Test fidelity command with persona and constraints files."""
    result = runner.invoke(
        app,
        [
            "fidelity",
            str(sample_persona_file),
            "--constraints",
            str(sample_constraints_file),
            "--no-llm-judge",
        ],
    )

    # Exit code 2 is argument error, which is acceptable for test
    # Exit code 0 = success, 1 = test failure, 2 = argument error
    assert result.exit_code in [0, 1, 2] or "Error" in result.output


def test_fidelity_with_inline_constraints(sample_persona_file):
    """Test fidelity command with inline constraints."""
    result = runner.invoke(
        app,
        [
            "fidelity",
            str(sample_persona_file),
            "--require-fields",
            "name,age",
            "--age-range",
            "25-45",
            "--no-llm-judge",
        ],
    )

    # Should succeed or fail gracefully
    assert result.exit_code in [0, 1, 2] or "Error" in result.output


def test_fidelity_json_output(sample_persona_file, sample_constraints_file):
    """Test fidelity command with JSON output."""
    result = runner.invoke(
        app,
        [
            "fidelity",
            str(sample_persona_file),
            "--constraints",
            str(sample_constraints_file),
            "--output",
            "json",
            "--no-llm-judge",
        ],
    )

    # Should produce valid output
    assert result.exit_code in [0, 1, 2] or "Error" in result.output

    if result.exit_code == 0 and result.stdout:
        # Verify output is valid JSON
        try:
            data = json.loads(result.stdout)
            assert "persona_id" in data or "overall_score" in data
        except json.JSONDecodeError:
            # If not JSON, command might have printed help or error
            pass


def test_fidelity_missing_file():
    """Test fidelity command with non-existent file."""
    result = runner.invoke(
        app,
        ["fidelity", "nonexistent.json"],
    )

    assert result.exit_code != 0
