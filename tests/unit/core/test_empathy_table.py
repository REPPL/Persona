"""
Tests for empathy map table output functionality (F-030).
"""

import pytest
from pathlib import Path
from dataclasses import dataclass

from persona.core.output import (
    EmpathyTableFormatter,
    EmpathyTableRow,
    EmpathyTableConfig,
    TableFormat,
)
from persona.core.data import ParticipantTypeMap, EmpathyMap


class TestTableFormat:
    """Tests for TableFormat enum."""

    def test_format_values(self):
        """Test format enum values."""
        assert TableFormat.MARKDOWN.value == "markdown"
        assert TableFormat.HTML.value == "html"
        assert TableFormat.RICH.value == "rich"

    def test_all_formats(self):
        """Test all formats are defined."""
        assert len(TableFormat) == 3


class TestEmpathyTableRow:
    """Tests for EmpathyTableRow dataclass."""

    def test_basic_creation(self):
        """Test basic row creation."""
        row = EmpathyTableRow(name="Test User")

        assert row.name == "Test User"
        assert row.tasks == []
        assert row.feelings == []
        assert row.influences == []
        assert row.pain_points == []
        assert row.goals == []

    def test_full_creation(self):
        """Test row with all dimensions."""
        row = EmpathyTableRow(
            name="Alice",
            tasks=["Collecting", "Sharing"],
            feelings=["Excited", "Happy"],
            influences=["Friends", "Social media"],
            pain_points=["Cost", "Time"],
            goals=["Complete collection", "Connect with others"],
        )

        assert row.name == "Alice"
        assert len(row.tasks) == 2
        assert len(row.feelings) == 2
        assert len(row.influences) == 2
        assert len(row.pain_points) == 2
        assert len(row.goals) == 2

    def test_from_participant_type_map(self):
        """Test creation from ParticipantTypeMap."""
        ptm = ParticipantTypeMap(
            participant_type="music_fan",
            tasks=["Listen daily"],
            feelings=["Passionate"],
            influences=["Artists"],
            pain_points=["Cost"],
            goals=["Discover new music"],
        )

        row = EmpathyTableRow.from_participant_type_map(ptm)

        assert row.name == "music_fan"
        assert row.tasks == ["Listen daily"]
        assert row.feelings == ["Passionate"]
        assert row.goals == ["Discover new music"]

    def test_from_persona(self):
        """Test creation from persona-like object."""

        @dataclass
        class MockPersona:
            name: str = "TestPersona"
            behaviours: list = None
            goals: list = None
            pain_points: list = None

            def __post_init__(self):
                self.behaviours = self.behaviours or []
                self.goals = self.goals or []
                self.pain_points = self.pain_points or []

        persona = MockPersona(
            name="Developer Dave",
            behaviours=["Code daily", "Review PRs"],
            goals=["Ship features", "Write clean code"],
            pain_points=["Technical debt", "Meetings"],
        )

        row = EmpathyTableRow.from_persona(persona)

        assert row.name == "Developer Dave"
        assert "Code daily" in row.tasks  # behaviours map to tasks
        assert "Ship features" in row.goals
        assert "Technical debt" in row.pain_points


class TestEmpathyTableConfig:
    """Tests for EmpathyTableConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = EmpathyTableConfig()

        assert config.title == "Empathy Map"
        assert config.max_items_per_cell == 5
        assert config.truncate_length == 100
        assert config.show_separator is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = EmpathyTableConfig(
            title="My Workshop Data",
            max_items_per_cell=3,
            truncate_length=50,
            show_separator=False,
        )

        assert config.title == "My Workshop Data"
        assert config.max_items_per_cell == 3


class TestEmpathyTableFormatter:
    """Tests for EmpathyTableFormatter class."""

    @pytest.fixture
    def sample_rows(self) -> list[EmpathyTableRow]:
        """Create sample table rows."""
        return [
            EmpathyTableRow(
                name="Superfan Alice",
                tasks=["Expanding collection", "Engaging with community"],
                feelings=["Easy to navigate", "Curation is critical"],
                influences=["Community", "Concerts"],
                pain_points=["Time-consuming", "Missing information"],
                goals=["Expand and share", "Safe interactions"],
            ),
            EmpathyTableRow(
                name="Musical Bob",
                tasks=["Experiencing music", "Learning"],
                feelings=["Storytelling", "Authenticity"],
                influences=["Audio quality", "Artists"],
                pain_points=["VR lacks authenticity"],
                goals=["Learn from artists"],
            ),
        ]

    @pytest.fixture
    def formatter(self) -> EmpathyTableFormatter:
        """Create a formatter instance."""
        return EmpathyTableFormatter()

    def test_init_default(self):
        """Test default initialisation."""
        formatter = EmpathyTableFormatter()

        assert formatter.config.title == "Empathy Map"

    def test_init_with_config(self):
        """Test initialisation with custom config."""
        config = EmpathyTableConfig(title="Custom Title")
        formatter = EmpathyTableFormatter(config)

        assert formatter.config.title == "Custom Title"

    def test_to_markdown_empty(self, formatter):
        """Test Markdown output with empty rows."""
        result = formatter.to_markdown([])
        assert result == ""

    def test_to_markdown(self, formatter, sample_rows):
        """Test Markdown table output."""
        result = formatter.to_markdown(sample_rows)

        # Check structure
        assert "# Empathy Map" in result
        assert "| Persona | Tasks | Feelings | Influences | Pain Points | Goals |" in result
        assert "|---|---|---|---|---|---|" in result

        # Check data
        assert "Superfan Alice" in result
        assert "Musical Bob" in result
        assert "Expanding collection" in result

    def test_to_markdown_escapes_special_chars(self, formatter):
        """Test Markdown escapes special characters."""
        rows = [
            EmpathyTableRow(
                name="Test|Pipe",
                tasks=["Task with | pipe"],
            )
        ]

        result = formatter.to_markdown(rows)

        # Pipes should be escaped/replaced
        assert "Test Pipe" in result  # Pipe replaced with space

    def test_to_html_empty(self, formatter):
        """Test HTML output with empty rows."""
        result = formatter.to_html([])
        assert result == ""

    def test_to_html(self, formatter, sample_rows):
        """Test HTML table output."""
        result = formatter.to_html(sample_rows)

        # Check document structure
        assert "<!DOCTYPE html>" in result
        assert "<html>" in result
        assert '<table class="empathy-table">' in result
        assert "<thead>" in result
        assert "<tbody>" in result

        # Check data
        assert "Superfan Alice" in result
        assert "Musical Bob" in result

    def test_to_html_standalone_false(self, formatter, sample_rows):
        """Test HTML output without document wrapper."""
        result = formatter.to_html(sample_rows, standalone=False)

        # Should not have document wrapper
        assert "<!DOCTYPE html>" not in result
        assert '<table class="empathy-table">' in result

    def test_to_html_escapes_special_chars(self, formatter):
        """Test HTML escapes special characters."""
        rows = [
            EmpathyTableRow(
                name="<script>alert('xss')</script>",
                tasks=["Task & more"],
            )
        ]

        result = formatter.to_html(rows)

        # HTML should be escaped
        assert "&lt;script&gt;" in result
        assert "Task &amp; more" in result
        assert "<script>alert" not in result

    def test_from_personas(self, formatter):
        """Test converting personas to rows."""

        @dataclass
        class MockPersona:
            name: str
            goals: list
            pain_points: list

        personas = [
            MockPersona(name="P1", goals=["G1"], pain_points=["PP1"]),
            MockPersona(name="P2", goals=["G2"], pain_points=["PP2"]),
        ]

        rows = formatter.from_personas(personas)

        assert len(rows) == 2
        assert rows[0].name == "P1"
        assert rows[1].name == "P2"

    def test_from_empathy_map(self, formatter):
        """Test converting empathy map to rows."""
        em = EmpathyMap(
            data=[
                ParticipantTypeMap(
                    participant_type="type_a",
                    tasks=["Task A"],
                    goals=["Goal A"],
                ),
                ParticipantTypeMap(
                    participant_type="type_b",
                    tasks=["Task B"],
                    goals=["Goal B"],
                ),
            ]
        )

        rows = formatter.from_empathy_map(em)

        assert len(rows) == 2
        assert rows[0].name == "type_a"
        assert rows[1].name == "type_b"

    def test_export_markdown(self, formatter, sample_rows, tmp_path: Path):
        """Test exporting to Markdown file."""
        output_path = tmp_path / "output"

        result_path = formatter.export(
            sample_rows,
            TableFormat.MARKDOWN,
            output_path,
        )

        assert result_path.suffix == ".md"
        assert result_path.exists()
        content = result_path.read_text()
        assert "# Empathy Map" in content

    def test_export_html(self, formatter, sample_rows, tmp_path: Path):
        """Test exporting to HTML file."""
        output_path = tmp_path / "output"

        result_path = formatter.export(
            sample_rows,
            TableFormat.HTML,
            output_path,
        )

        assert result_path.suffix == ".html"
        assert result_path.exists()
        content = result_path.read_text()
        assert "<!DOCTYPE html>" in content

    def test_export_with_extension(self, formatter, sample_rows, tmp_path: Path):
        """Test export respects provided extension."""
        output_path = tmp_path / "custom.md"

        result_path = formatter.export(
            sample_rows,
            TableFormat.MARKDOWN,
            output_path,
        )

        assert result_path == output_path

    def test_truncate_long_items(self, formatter):
        """Test truncation of long items."""
        config = EmpathyTableConfig(truncate_length=20)
        formatter = EmpathyTableFormatter(config)

        rows = [
            EmpathyTableRow(
                name="Test",
                tasks=["This is a very long task description that exceeds the limit"],
            )
        ]

        result = formatter.to_markdown(rows)

        # Should be truncated with ellipsis
        assert "..." in result

    def test_max_items_per_cell(self, formatter):
        """Test limiting items per cell."""
        config = EmpathyTableConfig(max_items_per_cell=2)
        formatter = EmpathyTableFormatter(config)

        rows = [
            EmpathyTableRow(
                name="Test",
                tasks=["Task 1", "Task 2", "Task 3", "Task 4", "Task 5"],
            )
        ]

        result = formatter.to_markdown(rows)

        # Should only show first 2 tasks
        assert "Task 1" in result
        assert "Task 2" in result
        assert "Task 3" not in result

    def test_empty_dimension_shows_placeholder(self, formatter):
        """Test empty dimensions show placeholder."""
        rows = [
            EmpathyTableRow(
                name="Test",
                tasks=[],  # Empty
            )
        ]

        result = formatter.to_markdown(rows)

        # Should show placeholder for empty
        assert "-" in result


class TestEmpathyTableRichOutput:
    """Tests for Rich terminal output."""

    @pytest.fixture
    def sample_rows(self) -> list[EmpathyTableRow]:
        """Create sample rows."""
        return [
            EmpathyTableRow(
                name="Test User",
                tasks=["Task 1"],
                feelings=["Happy"],
                influences=["Friends"],
                pain_points=["Issues"],
                goals=["Success"],
            )
        ]

    def test_to_rich_string(self, sample_rows):
        """Test Rich string output."""
        formatter = EmpathyTableFormatter()
        result = formatter.to_rich_string(sample_rows)

        # Should contain table content
        assert "Test User" in result or "Empathy Map" in result

    def test_to_rich_string_empty(self):
        """Test Rich output with empty rows."""
        formatter = EmpathyTableFormatter()
        result = formatter.to_rich_string([])
        assert result == ""


class TestEmpathyTableIntegration:
    """Integration tests for empathy table workflow."""

    def test_full_workflow_from_empathy_map(self, tmp_path: Path):
        """Test full workflow from empathy map to exported table."""
        # Create empathy map data
        em = EmpathyMap(
            participants=22,
            method="co-creation workshop",
            data=[
                ParticipantTypeMap(
                    participant_type="power_user",
                    tasks=["Advanced features", "Automation"],
                    feelings=["Confident", "Efficient"],
                    influences=["Documentation", "Community"],
                    pain_points=["Bugs", "Missing features"],
                    goals=["Mastery", "Productivity"],
                ),
                ParticipantTypeMap(
                    participant_type="casual_user",
                    tasks=["Basic tasks"],
                    feelings=["Uncertain"],
                    influences=["Friends"],
                    pain_points=["Complexity"],
                    goals=["Get things done"],
                ),
            ],
        )

        # Convert to table rows
        formatter = EmpathyTableFormatter(
            EmpathyTableConfig(title="Workshop Results")
        )
        rows = formatter.from_empathy_map(em)

        # Export to all formats
        md_path = formatter.export(rows, TableFormat.MARKDOWN, tmp_path / "table.md")
        html_path = formatter.export(rows, TableFormat.HTML, tmp_path / "table.html")

        # Verify exports
        assert md_path.exists()
        assert html_path.exists()

        md_content = md_path.read_text()
        assert "Workshop Results" in md_content
        assert "power_user" in md_content
        assert "casual_user" in md_content

        html_content = html_path.read_text()
        assert "Workshop Results" in html_content
        assert "<table" in html_content

    def test_multiple_personas_single_table(self, tmp_path: Path):
        """Test multiple personas in single table."""
        rows = [
            EmpathyTableRow(name=f"Persona {i}", goals=[f"Goal {i}"])
            for i in range(5)
        ]

        formatter = EmpathyTableFormatter()
        md = formatter.to_markdown(rows)

        # All personas should be in same table
        for i in range(5):
            assert f"Persona {i}" in md
            assert f"Goal {i}" in md
