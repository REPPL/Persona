"""
Tests for output formatting functionality (F-005).
"""

import json
from pathlib import Path

from persona.core.generation.parser import Persona
from persona.core.generation.pipeline import GenerationResult
from persona.core.output import JSONFormatter, MarkdownFormatter, OutputManager
from persona.core.output.formatters import TextFormatter


class TestJSONFormatter:
    """Tests for JSON formatter."""

    def test_format_persona(self):
        """Test formatting persona as JSON."""
        persona = Persona(
            id="p001",
            name="Test User",
            demographics={"age_range": "25-34"},
            goals=["Goal 1"],
        )

        formatter = JSONFormatter()
        result = formatter.format(persona)

        # Verify it's valid JSON
        data = json.loads(result)
        assert data["id"] == "p001"
        assert data["name"] == "Test User"

    def test_extension(self):
        """Test file extension."""
        formatter = JSONFormatter()
        assert formatter.extension() == ".json"

    def test_custom_indent(self):
        """Test custom indentation."""
        persona = Persona(id="p001", name="Test")
        formatter = JSONFormatter(indent=4)
        result = formatter.format(persona)

        # 4-space indent should have more characters than 2-space
        formatter2 = JSONFormatter(indent=2)
        result2 = formatter2.format(persona)

        assert len(result) > len(result2)


class TestMarkdownFormatter:
    """Tests for Markdown formatter."""

    def test_format_persona(self):
        """Test formatting persona as Markdown."""
        persona = Persona(
            id="p001",
            name="Alice Smith",
            demographics={"age_range": "30-39", "occupation": "Developer"},
            goals=["Build great software"],
            pain_points=["Too many meetings"],
            behaviours=["Uses keyboard shortcuts"],
            quotes=["Code is poetry"],
        )

        formatter = MarkdownFormatter()
        result = formatter.format(persona)

        assert "# Alice Smith" in result
        assert "## Demographics" in result
        assert "## Goals" in result
        assert "## Pain Points" in result
        assert "## Behaviours" in result
        assert "## Quotes" in result
        assert "Code is poetry" in result

    def test_extension(self):
        """Test file extension."""
        formatter = MarkdownFormatter()
        assert formatter.extension() == ".md"

    def test_format_minimal(self):
        """Test formatting minimal persona."""
        persona = Persona(id="p001", name="Bob")
        formatter = MarkdownFormatter()
        result = formatter.format(persona)

        assert "# Bob" in result
        assert "**ID**: p001" in result


class TestTextFormatter:
    """Tests for plain text formatter."""

    def test_format_persona(self):
        """Test formatting persona as plain text."""
        persona = Persona(
            id="p001",
            name="Carol",
            goals=["Learn new skills"],
        )

        formatter = TextFormatter()
        result = formatter.format(persona)

        assert "PERSONA: Carol" in result
        assert "ID: p001" in result
        assert "GOALS" in result
        assert "Learn new skills" in result

    def test_extension(self):
        """Test file extension."""
        formatter = TextFormatter()
        assert formatter.extension() == ".txt"


class TestOutputManager:
    """Tests for OutputManager class."""

    def test_create_output_dir(self, tmp_path: Path):
        """Test creating output directory."""
        manager = OutputManager(base_dir=tmp_path)
        output_dir = manager._create_output_dir("test-run")

        assert output_dir.exists()
        assert output_dir.name == "test-run"

    def test_create_output_dir_timestamp(self, tmp_path: Path):
        """Test creating timestamped output directory."""
        manager = OutputManager(base_dir=tmp_path, timestamp_folders=True)
        output_dir = manager._create_output_dir()

        assert output_dir.exists()
        # Should be 8 digits + underscore + 6 digits
        assert len(output_dir.name) == 15

    def test_save_result(self, tmp_path: Path):
        """Test saving generation result."""
        manager = OutputManager(base_dir=tmp_path)

        personas = [
            Persona(id="p001", name="Alice", goals=["Goal 1"]),
            Persona(id="p002", name="Bob", goals=["Goal 2"]),
        ]

        result = GenerationResult(
            personas=personas,
            input_tokens=100,
            output_tokens=200,
            model="test-model",
            provider="test-provider",
            prompt="Test prompt",
            raw_response="Test response",
        )

        output_dir = manager.save(result, name="test-output")

        # Check files exist
        assert (output_dir / "metadata.json").exists()
        assert (output_dir / "prompt.txt").exists()
        assert (output_dir / "full_response.txt").exists()
        assert (output_dir / "personas" / "01" / "persona.json").exists()
        assert (output_dir / "personas" / "02" / "persona.json").exists()

    def test_save_metadata(self, tmp_path: Path):
        """Test metadata content."""
        manager = OutputManager(base_dir=tmp_path)

        result = GenerationResult(
            personas=[Persona(id="p001", name="Test")],
            input_tokens=50,
            output_tokens=100,
            model="gpt-4",
            provider="openai",
        )

        output_dir = manager.save(result, name="test-metadata")
        metadata = manager.load_metadata(output_dir)

        assert metadata["provider"] == "openai"
        assert metadata["model"] == "gpt-4"
        assert metadata["persona_count"] == 1
        assert metadata["input_tokens"] == 50
        assert metadata["output_tokens"] == 100
        assert metadata["total_tokens"] == 150

    def test_list_outputs(self, tmp_path: Path):
        """Test listing output directories."""
        manager = OutputManager(base_dir=tmp_path)

        # Create some outputs
        result = GenerationResult(
            personas=[Persona(id="p001", name="Test")],
            model="test",
            provider="test",
        )

        manager.save(result, name="output-1")
        manager.save(result, name="output-2")

        outputs = manager.list_outputs()

        assert len(outputs) == 2
        assert any(o.name == "output-1" for o in outputs)
        assert any(o.name == "output-2" for o in outputs)

    def test_list_outputs_empty(self, tmp_path: Path):
        """Test listing when no outputs exist."""
        manager = OutputManager(base_dir=tmp_path)
        outputs = manager.list_outputs()

        assert outputs == []

    def test_get_latest_output(self, tmp_path: Path):
        """Test getting latest output."""
        manager = OutputManager(base_dir=tmp_path)

        result = GenerationResult(
            personas=[Persona(id="p001", name="Test")],
            model="test",
            provider="test",
        )

        manager.save(result, name="output-a")
        manager.save(result, name="output-z")

        latest = manager.get_latest_output()

        assert latest is not None
        assert latest.name == "output-z"

    def test_get_latest_output_none(self, tmp_path: Path):
        """Test getting latest when none exist."""
        manager = OutputManager(base_dir=tmp_path)
        latest = manager.get_latest_output()

        assert latest is None

    def test_save_with_reasoning(self, tmp_path: Path):
        """Test saving result with reasoning."""
        manager = OutputManager(base_dir=tmp_path)

        result = GenerationResult(
            personas=[Persona(id="p001", name="Test")],
            reasoning="This is my reasoning.",
            model="test",
            provider="test",
        )

        output_dir = manager.save(result, name="test-reasoning")

        reasoning_path = output_dir / "reasoning.txt"
        assert reasoning_path.exists()
        assert "This is my reasoning" in reasoning_path.read_text()

    def test_persona_files_content(self, tmp_path: Path):
        """Test content of saved persona files."""
        manager = OutputManager(base_dir=tmp_path)

        persona = Persona(
            id="persona-001",
            name="Alice",
            demographics={"age_range": "25-34"},
            goals=["Learn Python"],
        )

        result = GenerationResult(
            personas=[persona],
            model="test",
            provider="test",
        )

        output_dir = manager.save(result, name="test-content")

        # Check JSON content
        json_path = output_dir / "personas" / "01" / "persona.json"
        json_data = json.loads(json_path.read_text())
        assert json_data["name"] == "Alice"
        assert json_data["goals"] == ["Learn Python"]

        # Check Markdown content
        md_path = output_dir / "personas" / "01" / "persona.md"
        md_content = md_path.read_text()
        assert "# Alice" in md_content
        assert "Learn Python" in md_content

    def test_save_with_url_sources(self, tmp_path: Path):
        """Test saving result with URL sources generates attribution.md."""
        from datetime import datetime

        from persona.core.data import Attribution, URLSource

        manager = OutputManager(base_dir=tmp_path)

        # Create URL source with attribution
        attribution = Attribution(
            title="Test Dataset",
            creators=["Test Organisation"],
            source_url="https://example.com/data.csv",
            licence="CC-BY-4.0",
            access_date=datetime.now(),
        )

        url_source = URLSource(
            original_url="https://example.com/data.csv",
            resolved_url="https://example.com/data.csv",
            content_type="text/csv",
            fetched_at=datetime.now(),
            size_bytes=1024,
            sha256="abc123",
            terms_accepted=True,
            attribution=attribution,
        )

        result = GenerationResult(
            personas=[Persona(id="p001", name="Test")],
            model="test",
            provider="test",
            url_sources=[url_source],
        )

        output_dir = manager.save(result, name="test-attribution")

        # Check attribution.md exists
        attribution_path = output_dir / "attribution.md"
        assert attribution_path.exists()

        content = attribution_path.read_text()
        assert "# Data Attribution" in content
        assert "Test Dataset" in content
        assert "CC-BY-4.0" in content

    def test_save_with_url_sources_no_attribution(self, tmp_path: Path):
        """Test saving URL sources without attribution falls back to basic info."""
        from datetime import datetime

        from persona.core.data import URLSource

        manager = OutputManager(base_dir=tmp_path)

        url_source = URLSource(
            original_url="https://example.com/data.csv",
            resolved_url="https://cdn.example.com/data.csv",
            content_type="text/csv",
            fetched_at=datetime.now(),
            size_bytes=2048,
            sha256="def456",
            terms_accepted=True,
        )

        result = GenerationResult(
            personas=[Persona(id="p001", name="Test")],
            model="test",
            provider="test",
            url_sources=[url_source],
        )

        output_dir = manager.save(result, name="test-basic-attribution")

        attribution_path = output_dir / "attribution.md"
        assert attribution_path.exists()

        content = attribution_path.read_text()
        assert "https://example.com/data.csv" in content
        assert "Resolved URL" in content

    def test_metadata_includes_url_sources(self, tmp_path: Path):
        """Test that metadata.json includes URL sources."""
        from datetime import datetime

        from persona.core.data import URLSource

        manager = OutputManager(base_dir=tmp_path)

        url_source = URLSource(
            original_url="https://example.com/data.csv",
            resolved_url="https://example.com/data.csv",
            content_type="text/csv",
            fetched_at=datetime.now(),
            size_bytes=512,
            sha256="xyz789",
            terms_accepted=True,
        )

        result = GenerationResult(
            personas=[Persona(id="p001", name="Test")],
            model="test",
            provider="test",
            url_sources=[url_source],
        )

        output_dir = manager.save(result, name="test-url-metadata")
        metadata = manager.load_metadata(output_dir)

        assert "url_sources" in metadata
        assert len(metadata["url_sources"]) == 1
        assert metadata["url_sources"][0]["original_url"] == "https://example.com/data.csv"
