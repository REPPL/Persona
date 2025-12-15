"""
Tests for the faithfulness validation CLI command (F-118).
"""

import json
import pytest
from pathlib import Path
from typer.testing import CliRunner

from persona.ui.cli import app


@pytest.fixture
def runner():
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def sample_persona(tmp_path):
    """Create a sample persona file."""
    persona = {
        "id": "persona-001",
        "name": "Test User",
        "demographic": {
            "age": 30,
            "location": "London",
        },
        "goals": ["Find products", "Compare prices"],
        "frustrations": ["Complex navigation"],
    }
    filepath = tmp_path / "persona.json"
    filepath.write_text(json.dumps(persona))
    return filepath


@pytest.fixture
def sample_source(tmp_path):
    """Create a sample source data file."""
    content = """
    User research findings from interviews:
    - Users are typically 25-35 years old
    - Based in urban areas like London
    - Primary goal is to find and compare products
    - Frustrated by complex navigation patterns
    """
    filepath = tmp_path / "source.txt"
    filepath.write_text(content)
    return filepath


class TestFaithfulnessCommand:
    """Tests for the faithfulness CLI command."""

    def test_faithfulness_help(self, runner):
        """Test faithfulness --help shows usage."""
        result = runner.invoke(app, ["faithfulness", "--help"])
        assert result.exit_code == 0
        assert "faithfulness" in result.output.lower()
        assert "--source" in result.output
        assert "--threshold" in result.output
        assert "--hhem" in result.output

    def test_faithfulness_requires_persona_path(self, runner):
        """Test faithfulness requires persona path argument."""
        result = runner.invoke(app, ["faithfulness"])
        assert result.exit_code != 0
        assert "Missing" in result.output or "PERSONA_PATH" in result.output

    def test_faithfulness_requires_source(self, runner, sample_persona):
        """Test faithfulness requires --source option."""
        result = runner.invoke(app, ["faithfulness", str(sample_persona)])
        assert result.exit_code != 0
        assert "source" in result.output.lower() or "required" in result.output.lower()

    def test_faithfulness_invalid_path(self, runner, sample_source):
        """Test faithfulness with non-existent persona path."""
        result = runner.invoke(
            app,
            ["faithfulness", "/nonexistent/path.json", "--source", str(sample_source)],
        )
        assert result.exit_code != 0

    def test_faithfulness_invalid_source(self, runner, sample_persona):
        """Test faithfulness with non-existent source path."""
        result = runner.invoke(
            app,
            ["faithfulness", str(sample_persona), "--source", "/nonexistent/source.txt"],
        )
        assert result.exit_code != 0

    def test_faithfulness_provider_options(self, runner):
        """Test provider options are available."""
        result = runner.invoke(app, ["faithfulness", "--help"])
        assert "--llm-provider" in result.output
        assert "--embedding-provider" in result.output
        assert "--llm-model" in result.output

    def test_faithfulness_output_formats(self, runner):
        """Test output format options."""
        result = runner.invoke(app, ["faithfulness", "--help"])
        assert "--output" in result.output or "-o" in result.output
        assert "rich" in result.output
        assert "json" in result.output
        assert "markdown" in result.output

    def test_faithfulness_threshold_option(self, runner):
        """Test threshold option is available."""
        result = runner.invoke(app, ["faithfulness", "--help"])
        assert "--threshold" in result.output
        assert "0.7" in result.output  # default value

    def test_faithfulness_show_options(self, runner):
        """Test show options are available."""
        result = runner.invoke(app, ["faithfulness", "--help"])
        assert "--show-claims" in result.output
        assert "--show-unsupported" in result.output

    def test_faithfulness_hhem_option(self, runner):
        """Test HHEM option is available."""
        result = runner.invoke(app, ["faithfulness", "--help"])
        assert "--hhem" in result.output

    def test_faithfulness_min_score_option(self, runner):
        """Test minimum score threshold option."""
        result = runner.invoke(app, ["faithfulness", "--help"])
        assert "--min-score" in result.output


class TestFaithfulnessHelpers:
    """Tests for faithfulness command helper functions."""

    def test_load_personas_single_file(self, sample_persona):
        """Test loading personas from single JSON file."""
        from persona.ui.commands.faithfulness import _load_personas

        personas = _load_personas(sample_persona)
        assert len(personas) == 1
        assert personas[0].name == "Test User"

    def test_load_personas_list(self, tmp_path):
        """Test loading personas from JSON array."""
        from persona.ui.commands.faithfulness import _load_personas

        personas_data = [
            {"id": "p1", "name": "User 1"},
            {"id": "p2", "name": "User 2"},
        ]
        filepath = tmp_path / "personas.json"
        filepath.write_text(json.dumps(personas_data))

        personas = _load_personas(filepath)
        assert len(personas) == 2

    def test_load_personas_directory(self, tmp_path):
        """Test loading personas from directory."""
        from persona.ui.commands.faithfulness import _load_personas

        # Create personas.json in directory
        personas_data = [{"id": "p1", "name": "User 1"}]
        (tmp_path / "personas.json").write_text(json.dumps(personas_data))

        personas = _load_personas(tmp_path)
        assert len(personas) == 1

    def test_colour_faithfulness_thresholds(self):
        """Test colour scoring thresholds for faithfulness."""
        from persona.ui.commands.faithfulness import _colour_faithfulness

        # High score - green
        result = _colour_faithfulness(85.0)
        assert "green" in result

        # Medium score - yellow
        result = _colour_faithfulness(70.0)
        assert "yellow" in result

        # Low score - red
        result = _colour_faithfulness(50.0)
        assert "red" in result

    def test_report_to_dict_structure(self):
        """Test report to dict conversion."""
        from persona.ui.commands.faithfulness import _report_to_dict
        from persona.core.quality.faithfulness.models import (
            Claim,
            ClaimType,
            FaithfulnessReport,
        )

        # Create minimal report
        claim = Claim(
            text="Test claim",
            source_field="name",
            claim_type=ClaimType.FACTUAL,
        )
        report = FaithfulnessReport(
            persona_id="p1",
            persona_name="Test",
            claims=[claim],
            matches=[],
            supported_ratio=0.5,
            hallucination_ratio=0.5,
            unsupported_claims=[claim],
            details={"test": True},
        )

        result = _report_to_dict(report, include_claims=True)

        assert "persona_id" in result
        assert "faithfulness_score" in result
        assert "unsupported_claims" in result
        assert "all_claims" in result

    def test_report_to_dict_without_claims(self):
        """Test report to dict without all claims."""
        from persona.ui.commands.faithfulness import _report_to_dict
        from persona.core.quality.faithfulness.models import FaithfulnessReport

        report = FaithfulnessReport(
            persona_id="p1",
            persona_name="Test",
            claims=[],
            matches=[],
            supported_ratio=1.0,
            hallucination_ratio=0.0,
            unsupported_claims=[],
            details={},
        )

        result = _report_to_dict(report, include_claims=False)

        assert "persona_id" in result
        assert "all_claims" not in result
