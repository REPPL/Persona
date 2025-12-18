"""
Tests for automatic README generation (F-041).
"""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest
from persona.core.generation.parser import Persona
from persona.core.output.readme import (
    DEFAULT_README_TEMPLATE,
    CustomReadmeTemplate,
    GenerationSummary,
    PersonaSummary,
    ReadmeGenerator,
)


@pytest.fixture
def sample_summary() -> GenerationSummary:
    """Create a sample generation summary."""
    return GenerationSummary(
        generated_at=datetime(2025, 12, 14, 10, 30, 0),
        experiment_name="user-research-q4",
        persona_count=3,
        provider="Anthropic",
        model="claude-sonnet-4-5",
        source_files=["interviews.csv", "feedback.json", "survey.md"],
        input_tokens=5000,
        output_tokens=2000,
        cost=0.45,
    )


@pytest.fixture
def sample_personas() -> list[Persona]:
    """Create sample personas."""
    return [
        Persona(
            id="persona-001",
            name="Sarah Chen",
            demographics={"role": "Marketing Manager"},
            goals=["Streamline workflows", "Improve collaboration"],
            pain_points=["Manual processes", "Context switching"],
            additional={"title": "The Mobile Professional"},
        ),
        Persona(
            id="persona-002",
            name="Marcus Johnson",
            demographics={"role": "Developer"},
            goals=["Write clean code", "Ship faster"],
            pain_points=["Legacy systems"],
        ),
        Persona(
            id="persona-003",
            name="Priya Patel",
            demographics={"role": "Product Manager"},
            goals=["Deliver value"],
            pain_points=["Unclear priorities"],
        ),
    ]


class TestGenerationSummary:
    """Tests for GenerationSummary dataclass."""

    def test_creation(self, sample_summary):
        """Test summary creation."""
        assert sample_summary.persona_count == 3
        assert sample_summary.provider == "Anthropic"
        assert sample_summary.cost == 0.45

    def test_default_values(self):
        """Test default values."""
        summary = GenerationSummary(
            generated_at=datetime.now(),
        )
        assert summary.persona_count == 0
        assert summary.provider is None
        assert summary.source_files == []
        assert summary.cost == 0.0


class TestPersonaSummary:
    """Tests for PersonaSummary dataclass."""

    def test_creation(self):
        """Test persona summary creation."""
        summary = PersonaSummary(
            name="Test User",
            id="test-001",
            title="The Tester",
            goal_count=3,
            pain_point_count=2,
        )
        assert summary.name == "Test User"
        assert summary.title == "The Tester"

    def test_default_values(self):
        """Test default values."""
        summary = PersonaSummary(name="Test", id="test")
        assert summary.title == ""
        assert summary.goal_count == 0


class TestReadmeGenerator:
    """Tests for ReadmeGenerator."""

    def test_creation(self):
        """Test generator creation."""
        generator = ReadmeGenerator()
        assert generator._template_str == DEFAULT_README_TEMPLATE

    def test_creation_with_custom_template(self):
        """Test generator with custom template."""
        custom = "# Custom: {{ summary.persona_count }} personas"
        generator = ReadmeGenerator(template=custom)
        assert generator._template_str == custom

    def test_generate_returns_string(self, sample_summary, sample_personas):
        """Test generate returns a string."""
        generator = ReadmeGenerator()
        result = generator.generate(sample_summary, sample_personas)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_generate_includes_title(self, sample_summary, sample_personas):
        """Test README includes title."""
        generator = ReadmeGenerator()
        result = generator.generate(sample_summary, sample_personas)
        assert "# Persona Generation Output" in result

    def test_generate_includes_timestamp(self, sample_summary, sample_personas):
        """Test README includes generation timestamp."""
        generator = ReadmeGenerator()
        result = generator.generate(sample_summary, sample_personas)
        assert "2025-12-14" in result

    def test_generate_includes_experiment_name(self, sample_summary, sample_personas):
        """Test README includes experiment name."""
        generator = ReadmeGenerator()
        result = generator.generate(sample_summary, sample_personas)
        assert "user-research-q4" in result

    def test_generate_includes_persona_count(self, sample_summary, sample_personas):
        """Test README includes persona count."""
        generator = ReadmeGenerator()
        result = generator.generate(sample_summary, sample_personas)
        assert "**Personas Generated**: 3" in result

    def test_generate_includes_provider(self, sample_summary, sample_personas):
        """Test README includes provider info."""
        generator = ReadmeGenerator()
        result = generator.generate(sample_summary, sample_personas)
        assert "Anthropic" in result
        assert "claude-sonnet-4-5" in result

    def test_generate_includes_source_files(self, sample_summary, sample_personas):
        """Test README includes source files."""
        generator = ReadmeGenerator()
        result = generator.generate(sample_summary, sample_personas)
        assert "Source Files" in result
        assert "interviews.csv" in result

    def test_generate_includes_cost(self, sample_summary, sample_personas):
        """Test README includes cost."""
        generator = ReadmeGenerator()
        result = generator.generate(sample_summary, sample_personas)
        assert "$0.45" in result

    def test_generate_includes_tokens(self, sample_summary, sample_personas):
        """Test README includes token counts."""
        generator = ReadmeGenerator()
        result = generator.generate(sample_summary, sample_personas)
        assert "7000" in result  # Total tokens
        assert "5000 input" in result
        assert "2000 output" in result

    def test_generate_includes_persona_list(self, sample_summary, sample_personas):
        """Test README includes persona list."""
        generator = ReadmeGenerator()
        result = generator.generate(sample_summary, sample_personas)
        assert "Sarah Chen" in result
        assert "Marcus Johnson" in result
        assert "Priya Patel" in result

    def test_generate_includes_persona_titles(self, sample_summary, sample_personas):
        """Test README includes persona titles."""
        generator = ReadmeGenerator()
        result = generator.generate(sample_summary, sample_personas)
        assert "The Mobile Professional" in result

    def test_generate_includes_file_structure(self, sample_summary, sample_personas):
        """Test README includes file structure."""
        generator = ReadmeGenerator()
        result = generator.generate(sample_summary, sample_personas)
        assert "personas/" in result
        assert "metadata.json" in result
        assert "persona.json" in result

    def test_generate_includes_usage_section(self, sample_summary, sample_personas):
        """Test README includes usage section."""
        generator = ReadmeGenerator()
        result = generator.generate(sample_summary, sample_personas)
        assert "## Usage" in result
        assert "Loading Personas" in result

    def test_generate_shows_prompt_file_conditionally(
        self, sample_summary, sample_personas
    ):
        """Test prompt.txt shown conditionally."""
        generator = ReadmeGenerator()

        # With prompt
        result_with = generator.generate(
            sample_summary, sample_personas, has_prompt=True
        )
        assert "prompt.txt" in result_with

        # Without prompt
        result_without = generator.generate(
            sample_summary, sample_personas, has_prompt=False
        )
        # Should not show prompt.txt in file tree
        assert result_without.count("prompt.txt") == 0

    def test_generate_shows_reasoning_conditionally(
        self, sample_summary, sample_personas
    ):
        """Test reasoning.txt shown conditionally."""
        generator = ReadmeGenerator()

        # With reasoning
        result_with = generator.generate(
            sample_summary, sample_personas, has_reasoning=True
        )
        assert "reasoning.txt" in result_with

        # Without reasoning
        result_without = generator.generate(
            sample_summary, sample_personas, has_reasoning=False
        )
        assert result_without.count("reasoning.txt") == 0

    def test_generate_from_metadata(self, sample_personas):
        """Test generating from metadata dict."""
        metadata = {
            "generated_at": "2025-12-14T10:30:00",
            "experiment_name": "test-exp",
            "persona_count": 3,
            "provider": "OpenAI",
            "model": "gpt-4",
            "source_files": ["data.csv"],
            "input_tokens": 1000,
            "output_tokens": 500,
        }
        generator = ReadmeGenerator()
        result = generator.generate_from_metadata(metadata, sample_personas)
        assert "test-exp" in result
        assert "OpenAI" in result

    def test_extract_title_from_additional(self, sample_personas):
        """Test title extraction from additional fields."""
        generator = ReadmeGenerator()
        title = generator._extract_title(sample_personas[0])
        assert title == "The Mobile Professional"

    def test_extract_title_from_demographics(self, sample_personas):
        """Test title extraction from demographics role."""
        generator = ReadmeGenerator()
        title = generator._extract_title(sample_personas[1])  # No title in additional
        assert "Developer" in title

    def test_extract_title_empty(self):
        """Test title extraction when no title available."""
        persona = Persona(
            id="test",
            name="Test",
            demographics={},
            goals=[],
            pain_points=[],
        )
        generator = ReadmeGenerator()
        title = generator._extract_title(persona)
        assert title == ""


class TestReadmeGeneratorSave:
    """Tests for ReadmeGenerator.save()."""

    def test_save_creates_file(self, sample_summary, sample_personas):
        """Test save creates README.md file."""
        generator = ReadmeGenerator()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            readme_path = generator.save(output_dir, sample_summary, sample_personas)

            assert readme_path.exists()
            assert readme_path.name == "README.md"

    def test_save_content_is_valid(self, sample_summary, sample_personas):
        """Test saved content is valid README."""
        generator = ReadmeGenerator()

        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            readme_path = generator.save(output_dir, sample_summary, sample_personas)

            content = readme_path.read_text()
            assert "# Persona Generation Output" in content
            assert "Sarah Chen" in content


class TestCustomReadmeTemplate:
    """Tests for CustomReadmeTemplate."""

    def test_available_variables(self):
        """Test available variables documentation."""
        vars = CustomReadmeTemplate.AVAILABLE_VARIABLES
        assert "summary" in vars
        assert "personas" in vars
        assert "output_dir" in vars

    def test_get_example_template(self):
        """Test getting example template."""
        template = CustomReadmeTemplate.get_example_template()
        assert template == DEFAULT_README_TEMPLATE
        assert "{{ summary.persona_count }}" in template

    def test_validate_valid_template(self):
        """Test validating a valid template."""
        template = "# {{ summary.persona_count }} personas"
        errors = CustomReadmeTemplate.validate_template(template)
        assert errors == []

    def test_validate_invalid_template(self):
        """Test validating an invalid template."""
        template = "# {{ unclosed"
        errors = CustomReadmeTemplate.validate_template(template)
        assert len(errors) > 0
        assert "syntax error" in errors[0].lower()


class TestReadmeGeneratorEdgeCases:
    """Tests for edge cases in README generation."""

    def test_empty_personas(self, sample_summary):
        """Test generation with empty personas list."""
        generator = ReadmeGenerator()
        result = generator.generate(sample_summary, [])
        assert "# Persona Generation Output" in result

    def test_no_experiment_name(self, sample_personas):
        """Test generation without experiment name."""
        summary = GenerationSummary(
            generated_at=datetime.now(),
            persona_count=3,
        )
        generator = ReadmeGenerator()
        result = generator.generate(summary, sample_personas)
        assert "# Persona Generation Output" in result

    def test_no_provider(self, sample_personas):
        """Test generation without provider info."""
        summary = GenerationSummary(
            generated_at=datetime.now(),
            persona_count=3,
        )
        generator = ReadmeGenerator()
        result = generator.generate(summary, sample_personas)
        assert "Provider" not in result or "None" not in result

    def test_zero_cost(self, sample_personas):
        """Test generation with zero cost."""
        summary = GenerationSummary(
            generated_at=datetime.now(),
            cost=0.0,
        )
        generator = ReadmeGenerator()
        result = generator.generate(summary, sample_personas)
        # Cost line should not appear for zero cost
        assert "$0.00" not in result

    def test_many_source_files_truncated(self, sample_personas):
        """Test many source files are truncated."""
        summary = GenerationSummary(
            generated_at=datetime.now(),
            source_files=["a.csv", "b.csv", "c.csv", "d.csv", "e.csv"],
        )
        generator = ReadmeGenerator()
        result = generator.generate(summary, sample_personas)
        assert "..." in result  # Indicates truncation

    def test_custom_template(self, sample_summary, sample_personas):
        """Test with custom template."""
        custom = "# Generated {{ summary.persona_count }} personas on {{ summary.generated_at.strftime('%Y-%m-%d') }}"
        generator = ReadmeGenerator(template=custom)
        result = generator.generate(sample_summary, sample_personas)
        assert "# Generated 3 personas on 2025-12-14" in result
