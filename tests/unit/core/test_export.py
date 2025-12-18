"""
Tests for export functionality (F-026).
"""

import json
from pathlib import Path

import pytest
from persona.core.export import (
    ExportFormat,
    ExportResult,
    PersonaExporter,
)
from persona.core.generation.parser import Persona


class TestExportFormat:
    """Tests for ExportFormat enum."""

    def test_format_values(self):
        """Test format enum values."""
        assert ExportFormat.JSON.value == "json"
        assert ExportFormat.MARKDOWN.value == "markdown"
        assert ExportFormat.HTML.value == "html"
        assert ExportFormat.FIGMA.value == "figma"
        assert ExportFormat.MIRO.value == "miro"
        assert ExportFormat.CSV.value == "csv"


class TestExportResult:
    """Tests for ExportResult dataclass."""

    def test_success_result(self):
        """Test successful result."""
        result = ExportResult(
            success=True,
            format=ExportFormat.JSON,
            output_path=Path("output.json"),
            persona_count=3,
        )

        assert result.success is True
        assert result.persona_count == 3

    def test_failed_result(self):
        """Test failed result."""
        result = ExportResult(
            success=False,
            format=ExportFormat.JSON,
            error="Export failed",
        )

        assert result.success is False
        assert result.error == "Export failed"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = ExportResult(
            success=True,
            format=ExportFormat.MARKDOWN,
            output_path=Path("output.md"),
            persona_count=2,
        )

        data = result.to_dict()

        assert data["success"] is True
        assert data["format"] == "markdown"
        assert data["persona_count"] == 2


class TestPersonaExporter:
    """Tests for PersonaExporter class."""

    @pytest.fixture
    def sample_personas(self):
        """Create sample personas for testing."""
        return [
            Persona(
                id="p001",
                name="Alice",
                goals=["Goal 1", "Goal 2"],
                pain_points=["Pain 1"],
                behaviours=["Behaviour 1"],
                demographics={"age": "30", "role": "Developer"},
            ),
            Persona(
                id="p002",
                name="Bob",
                goals=["Goal A"],
                pain_points=["Pain A", "Pain B"],
                demographics={"age": "25"},
            ),
        ]

    def test_init(self):
        """Test initialisation."""
        exporter = PersonaExporter()

        assert len(exporter._exporters) > 0

    def test_list_formats(self):
        """Test listing formats."""
        exporter = PersonaExporter()
        formats = exporter.list_formats()

        assert len(formats) >= 6
        ids = [f["id"] for f in formats]
        assert "json" in ids
        assert "markdown" in ids
        assert "figma" in ids

    def test_export_json(self, sample_personas, tmp_path: Path):
        """Test JSON export."""
        exporter = PersonaExporter()
        output_file = tmp_path / "personas.json"

        result = exporter.export(
            sample_personas,
            ExportFormat.JSON,
            output_file,
        )

        assert result.success is True
        assert result.output_path.exists()
        assert result.persona_count == 2

        # Verify content
        content = json.loads(output_file.read_text())
        assert "personas" in content
        assert len(content["personas"]) == 2

    def test_export_markdown(self, sample_personas, tmp_path: Path):
        """Test Markdown export."""
        exporter = PersonaExporter()
        output_file = tmp_path / "personas.md"

        result = exporter.export(
            sample_personas,
            ExportFormat.MARKDOWN,
            output_file,
        )

        assert result.success is True

        content = output_file.read_text()
        assert "# Personas" in content
        assert "## Alice" in content
        assert "## Bob" in content
        assert "Goal 1" in content

    def test_export_html(self, sample_personas, tmp_path: Path):
        """Test HTML export."""
        exporter = PersonaExporter()
        output_file = tmp_path / "personas.html"

        result = exporter.export(
            sample_personas,
            ExportFormat.HTML,
            output_file,
        )

        assert result.success is True

        content = output_file.read_text()
        assert "<!DOCTYPE html>" in content
        assert "Alice" in content
        assert "Bob" in content

    def test_export_figma(self, sample_personas, tmp_path: Path):
        """Test Figma export."""
        exporter = PersonaExporter()
        output_file = tmp_path / "personas-figma.json"

        result = exporter.export(
            sample_personas,
            ExportFormat.FIGMA,
            output_file,
        )

        assert result.success is True

        content = json.loads(output_file.read_text())
        assert content["type"] == "FRAME"
        assert "children" in content
        assert len(content["children"]) == 2

    def test_export_miro(self, sample_personas, tmp_path: Path):
        """Test Miro export."""
        exporter = PersonaExporter()
        output_file = tmp_path / "personas-miro.json"

        result = exporter.export(
            sample_personas,
            ExportFormat.MIRO,
            output_file,
        )

        assert result.success is True

        content = json.loads(output_file.read_text())
        assert content["type"] == "board_content"
        assert "items" in content
        assert len(content["items"]) == 2

    def test_export_uxpressia(self, sample_personas, tmp_path: Path):
        """Test UXPressia export."""
        exporter = PersonaExporter()
        output_file = tmp_path / "personas-uxpressia.json"

        result = exporter.export(
            sample_personas,
            ExportFormat.UXPRESSIA,
            output_file,
        )

        assert result.success is True

        content = json.loads(output_file.read_text())
        assert content["version"] == "1.0"
        assert "personas" in content
        assert len(content["personas"]) == 2

    def test_export_csv(self, sample_personas, tmp_path: Path):
        """Test CSV export."""
        exporter = PersonaExporter()
        output_file = tmp_path / "personas.csv"

        result = exporter.export(
            sample_personas,
            ExportFormat.CSV,
            output_file,
        )

        assert result.success is True

        content = output_file.read_text()
        lines = content.split("\n")
        assert len(lines) >= 3  # Header + 2 personas
        assert "id,name" in lines[0]

    def test_export_to_directory(self, sample_personas, tmp_path: Path):
        """Test export to directory (auto-names file)."""
        exporter = PersonaExporter()

        result = exporter.export(
            sample_personas,
            ExportFormat.JSON,
            tmp_path,
        )

        assert result.success is True
        assert (tmp_path / "personas.json").exists()

    def test_export_single(self, sample_personas, tmp_path: Path):
        """Test exporting single persona."""
        exporter = PersonaExporter()
        output_file = tmp_path / "single.json"

        result = exporter.export_single(
            sample_personas[0],
            ExportFormat.JSON,
            output_file,
        )

        assert result.success is True
        assert result.persona_count == 1

    def test_preview_json(self, sample_personas):
        """Test JSON preview."""
        exporter = PersonaExporter()
        preview = exporter.preview(sample_personas, ExportFormat.JSON)

        data = json.loads(preview)
        assert "personas" in data
        assert len(data["personas"]) == 2

    def test_preview_markdown(self, sample_personas):
        """Test Markdown preview."""
        exporter = PersonaExporter()
        preview = exporter.preview(sample_personas, ExportFormat.MARKDOWN)

        assert "# Personas" in preview
        assert "## Alice" in preview

    def test_preview_html(self, sample_personas):
        """Test HTML preview."""
        exporter = PersonaExporter()
        preview = exporter.preview(sample_personas, ExportFormat.HTML)

        assert "<!DOCTYPE html>" in preview
        assert "Alice" in preview

    def test_preview_figma(self, sample_personas):
        """Test Figma preview."""
        exporter = PersonaExporter()
        preview = exporter.preview(sample_personas, ExportFormat.FIGMA)

        data = json.loads(preview)
        assert data["type"] == "FRAME"

    def test_preview_miro(self, sample_personas):
        """Test Miro preview."""
        exporter = PersonaExporter()
        preview = exporter.preview(sample_personas, ExportFormat.MIRO)

        data = json.loads(preview)
        assert data["type"] == "board_content"

    def test_preview_csv(self, sample_personas):
        """Test CSV preview."""
        exporter = PersonaExporter()
        preview = exporter.preview(sample_personas, ExportFormat.CSV)

        assert "id,name" in preview
        assert "Alice" in preview

    def test_export_creates_parent_directory(self, sample_personas, tmp_path: Path):
        """Test export creates parent directories."""
        exporter = PersonaExporter()
        output_file = tmp_path / "nested" / "dir" / "personas.json"

        result = exporter.export(
            sample_personas,
            ExportFormat.JSON,
            output_file,
        )

        assert result.success is True
        assert output_file.exists()

    def test_export_empty_personas(self, tmp_path: Path):
        """Test exporting empty persona list."""
        exporter = PersonaExporter()
        output_file = tmp_path / "empty.json"

        result = exporter.export(
            [],
            ExportFormat.JSON,
            output_file,
        )

        assert result.success is True
        assert result.persona_count == 0

    def test_export_preserves_demographics(self, sample_personas, tmp_path: Path):
        """Test demographics are preserved in export."""
        exporter = PersonaExporter()
        output_file = tmp_path / "personas.json"

        exporter.export(sample_personas, ExportFormat.JSON, output_file)

        content = json.loads(output_file.read_text())
        alice = content["personas"][0]
        assert alice["demographics"]["age"] == "30"
        assert alice["demographics"]["role"] == "Developer"

    def test_export_preserves_lists(self, sample_personas, tmp_path: Path):
        """Test lists are preserved in export."""
        exporter = PersonaExporter()
        output_file = tmp_path / "personas.json"

        exporter.export(sample_personas, ExportFormat.JSON, output_file)

        content = json.loads(output_file.read_text())
        alice = content["personas"][0]
        assert len(alice["goals"]) == 2
        assert "Goal 1" in alice["goals"]

    def test_markdown_includes_all_sections(self, sample_personas):
        """Test Markdown includes all persona sections."""
        exporter = PersonaExporter()
        preview = exporter.preview(sample_personas, ExportFormat.MARKDOWN)

        assert "### Demographics" in preview
        assert "### Goals" in preview
        assert "### Pain Points" in preview
        assert "### Behaviours" in preview

    def test_html_includes_styling(self, sample_personas):
        """Test HTML includes CSS styling."""
        exporter = PersonaExporter()
        preview = exporter.preview(sample_personas, ExportFormat.HTML)

        assert "<style>" in preview
        assert ".persona" in preview

    def test_figma_structure(self, sample_personas):
        """Test Figma export has correct structure."""
        exporter = PersonaExporter()
        preview = exporter.preview(sample_personas, ExportFormat.FIGMA)

        data = json.loads(preview)
        assert data["name"] == "Personas"
        persona_frame = data["children"][0]
        assert "Persona: Alice" in persona_frame["name"]
        assert len(persona_frame["children"]) >= 3  # Name, Goals, Pain Points

    def test_miro_card_positions(self, sample_personas):
        """Test Miro export positions cards correctly."""
        exporter = PersonaExporter()
        preview = exporter.preview(sample_personas, ExportFormat.MIRO)

        data = json.loads(preview)
        items = data["items"]
        # Cards should have different x positions
        positions = [item["position"]["x"] for item in items]
        assert len(set(positions)) == len(positions)  # All unique

    def test_uxpressia_structure(self, sample_personas):
        """Test UXPressia export has correct structure."""
        exporter = PersonaExporter()
        preview = exporter.preview(sample_personas, ExportFormat.UXPRESSIA)

        data = json.loads(preview)
        assert data["version"] == "1.0"
        persona = data["personas"][0]
        assert "demographic" in persona
        assert "goals" in persona
        assert "painPoints" in persona
        assert "behaviors" in persona
