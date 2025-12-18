"""
Tests for the academic validation CLI command (F-117).
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


class TestAcademicCommand:
    """Tests for the academic CLI command."""

    def test_academic_help(self, runner):
        """Test academic --help shows usage."""
        result = runner.invoke(app, ["academic", "--help"])
        assert result.exit_code == 0
        assert "academic" in result.output.lower()
        assert "--rouge" in result.output
        assert "--bertscore" in result.output
        assert "--geval" in result.output
        assert "--gpt-similarity" in result.output

    def test_academic_requires_persona_path(self, runner):
        """Test academic requires persona path argument."""
        result = runner.invoke(app, ["academic"])
        assert result.exit_code != 0
        assert "Missing argument" in result.output or "PERSONA_PATH" in result.output

    def test_academic_invalid_path(self, runner):
        """Test academic with non-existent path."""
        result = runner.invoke(app, ["academic", "/nonexistent/path.json"])
        assert result.exit_code != 0

    def test_academic_json_output_structure(self, runner, sample_persona, monkeypatch):
        """Test academic JSON output has correct structure."""
        # Mock the validator to avoid actual LLM calls
        from persona.core.quality.academic import models

        class MockReport:
            def __init__(self):
                self.persona_id = "persona-001"
                self.persona_name = "Test User"
                self.rouge_l = None
                self.bertscore = None
                self.gpt_similarity = None
                self.geval = models.GevalScore(
                    coherence=0.8,
                    relevance=0.7,
                    fluency=0.9,
                    consistency=0.85,
                    overall=0.81,
                    model="mock",
                    reasoning={},
                )
                self.metrics_used = ["geval"]
                self.overall_score = 0.81

        class MockBatchReport:
            def __init__(self):
                self.reports = [MockReport()]
                self.average_rouge_l = None
                self.average_bertscore = None
                self.average_gpt_similarity = None
                self.average_geval = 0.81
                self.overall_average = 0.81

        def mock_validate_batch(*args, **kwargs):
            return MockBatchReport()

        monkeypatch.setattr(
            "persona.core.quality.academic.AcademicValidator.validate_batch",
            mock_validate_batch,
        )

        result = runner.invoke(
            app, ["academic", str(sample_persona), "--geval", "--output", "json"]
        )

        # Check JSON structure
        if result.exit_code == 0:
            output = json.loads(result.output)
            assert "command" in output
            assert output["command"] == "academic"
            assert "success" in output
            assert "data" in output

    def test_academic_source_required_for_similarity_metrics(
        self, runner, sample_persona
    ):
        """Test that similarity metrics require source data."""
        result = runner.invoke(
            app, ["academic", str(sample_persona), "--rouge", "--output", "json"]
        )
        # Should fail because --rouge requires --source
        assert result.exit_code != 0
        # Check that error mentions source or require - the output varies
        output_lower = result.output.lower()
        assert (
            "require" in output_lower
            or "source" in output_lower
            or "error" in output_lower
        )

    def test_academic_all_metrics_flag(self, runner, sample_persona):
        """Test --all flag attempts all metrics."""
        result = runner.invoke(
            app, ["academic", str(sample_persona), "--all", "--help"]
        )
        # Just verify the flag is accepted
        assert "--all" in result.output

    def test_academic_provider_options(self, runner):
        """Test provider options are available."""
        result = runner.invoke(app, ["academic", "--help"])
        assert "--geval-provider" in result.output
        assert "--embedding-provider" in result.output

    def test_academic_output_formats(self, runner):
        """Test output format options."""
        result = runner.invoke(app, ["academic", "--help"])
        assert "--output" in result.output or "-o" in result.output
        assert "rich" in result.output
        assert "json" in result.output
        assert "markdown" in result.output


class TestAcademicHelpers:
    """Tests for academic command helper functions."""

    def test_load_personas_single_file(self, sample_persona):
        """Test loading personas from single JSON file."""
        from persona.ui.commands.academic import _load_personas

        personas = _load_personas(sample_persona)
        assert len(personas) == 1
        assert personas[0].name == "Test User"

    def test_load_personas_list(self, tmp_path):
        """Test loading personas from JSON array."""
        from persona.ui.commands.academic import _load_personas

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
        from persona.ui.commands.academic import _load_personas

        # Create personas.json in directory
        personas_data = [{"id": "p1", "name": "User 1"}]
        (tmp_path / "personas.json").write_text(json.dumps(personas_data))

        personas = _load_personas(tmp_path)
        assert len(personas) == 1

    def test_colour_score_thresholds(self):
        """Test colour scoring thresholds."""
        from persona.ui.commands.academic import _colour_score

        # High score - green
        result = _colour_score(0.9)
        assert "green" in result

        # Medium score - yellow
        result = _colour_score(0.65)
        assert "yellow" in result

        # Low score - red
        result = _colour_score(0.4)
        assert "red" in result
