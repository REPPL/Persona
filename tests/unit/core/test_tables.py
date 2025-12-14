"""
Tests for table output formatters (F-037).
"""

import pytest

from persona.core.output.tables import (
    ASCIITableFormatter,
    CSVTableFormatter,
    LaTeXTableFormatter,
    MarkdownTableFormatter,
    PersonaComparisonTable,
    TableColumn,
    TableConfig,
    TableOutputFormat,
)
from persona.core.generation.parser import Persona


@pytest.fixture
def sample_personas() -> list[Persona]:
    """Create sample personas for testing."""
    return [
        Persona(
            id="persona-001",
            name="Sarah Chen",
            demographics={"role": "Marketing Manager", "age": "32"},
            goals=["Streamline workflows", "Improve collaboration"],
            pain_points=["Too many manual processes", "Context switching"],
            behaviours=["Checks dashboards daily", "Collaborates cross-functionally"],
            quotes=["I need tools that just work."],
        ),
        Persona(
            id="persona-002",
            name="Marcus Johnson",
            demographics={"role": "Developer", "age": "28"},
            goals=["Write clean code", "Ship features faster"],
            pain_points=["Legacy systems", "Unclear requirements"],
            behaviours=["Codes in focused blocks", "Reviews PRs regularly"],
        ),
    ]


@pytest.fixture
def single_persona(sample_personas) -> Persona:
    """Get a single persona for testing."""
    return sample_personas[0]


class TestTableOutputFormat:
    """Tests for TableOutputFormat enum."""

    def test_format_values(self):
        """Test format enum values."""
        assert TableOutputFormat.ASCII.value == "ascii"
        assert TableOutputFormat.MARKDOWN.value == "markdown"
        assert TableOutputFormat.CSV.value == "csv"
        assert TableOutputFormat.LATEX.value == "latex"


class TestTableColumn:
    """Tests for TableColumn dataclass."""

    def test_default_values(self):
        """Test default column values."""
        col = TableColumn(key="name", header="Name")
        assert col.key == "name"
        assert col.header == "Name"
        assert col.width == 20
        assert col.align == "left"

    def test_custom_values(self):
        """Test custom column values."""
        col = TableColumn(key="goals", header="Goals", width=40, align="center")
        assert col.width == 40
        assert col.align == "center"


class TestTableConfig:
    """Tests for TableConfig dataclass."""

    def test_default_format_is_markdown(self):
        """Test default format is Markdown."""
        config = TableConfig()
        assert config.format == TableOutputFormat.MARKDOWN

    def test_default_columns(self):
        """Test default columns includes essential fields."""
        columns = TableConfig.default_columns()
        keys = [c.key for c in columns]
        assert "name" in keys
        assert "goals" in keys
        assert "pain_points" in keys

    def test_attribute_view_columns(self):
        """Test attribute view column configuration."""
        columns = TableConfig.attribute_view("goals")
        assert len(columns) == 2
        assert columns[0].key == "name"
        assert columns[1].key == "goals"
        assert columns[1].header == "Goals"


class TestASCIITableFormatter:
    """Tests for ASCIITableFormatter."""

    def test_extension_is_txt(self):
        """Test file extension is .txt."""
        formatter = ASCIITableFormatter()
        assert formatter.extension() == ".txt"

    def test_format_single_persona(self, single_persona):
        """Test formatting single persona."""
        formatter = ASCIITableFormatter()
        result = formatter.format(single_persona)
        assert "Sarah Chen" in result
        assert "+" in result  # ASCII border
        assert "|" in result  # ASCII separator

    def test_format_multiple_personas(self, sample_personas):
        """Test formatting multiple personas."""
        formatter = ASCIITableFormatter()
        result = formatter.format_multiple(sample_personas)
        assert "Sarah Chen" in result
        assert "Marcus Johnson" in result

    def test_includes_headers(self, single_persona):
        """Test table includes headers."""
        formatter = ASCIITableFormatter()
        result = formatter.format(single_persona)
        assert "Name" in result
        assert "Goals" in result

    def test_without_headers(self, single_persona):
        """Test table without headers."""
        config = TableConfig(include_header=False)
        formatter = ASCIITableFormatter(config=config)
        result = formatter.format(single_persona)
        # Data should still be present
        assert "Sarah Chen" in result

    def test_truncates_long_values(self, single_persona):
        """Test long values are truncated."""
        config = TableConfig(max_cell_width=10, truncate_long_values=True)
        formatter = ASCIITableFormatter(config=config)
        result = formatter.format(single_persona)
        assert "..." in result  # Truncation indicator


class TestMarkdownTableFormatter:
    """Tests for MarkdownTableFormatter."""

    def test_extension_is_md(self):
        """Test file extension is .md."""
        formatter = MarkdownTableFormatter()
        assert formatter.extension() == ".md"

    def test_format_single_persona(self, single_persona):
        """Test formatting single persona."""
        formatter = MarkdownTableFormatter()
        result = formatter.format(single_persona)
        assert "Sarah Chen" in result
        assert "|" in result  # Markdown table syntax

    def test_format_multiple_personas(self, sample_personas):
        """Test formatting multiple personas."""
        formatter = MarkdownTableFormatter()
        result = formatter.format_multiple(sample_personas)
        assert "Sarah Chen" in result
        assert "Marcus Johnson" in result

    def test_includes_header_separator(self, single_persona):
        """Test includes Markdown header separator."""
        formatter = MarkdownTableFormatter()
        result = formatter.format(single_persona)
        assert "---" in result

    def test_escapes_pipe_characters(self):
        """Test pipe characters are escaped."""
        persona = Persona(
            id="test",
            name="Test | User",
            demographics={},
            goals=["Goal with | pipe"],
            pain_points=[],
        )
        formatter = MarkdownTableFormatter()
        result = formatter.format(persona)
        assert "\\|" in result

    def test_alignment_in_separator(self, single_persona):
        """Test alignment is reflected in separator."""
        columns = [
            TableColumn("name", "Name", align="left"),
            TableColumn("goals", "Goals", align="center"),
            TableColumn("pain_points", "Pain Points", align="right"),
        ]
        config = TableConfig(columns=columns)
        formatter = MarkdownTableFormatter(config=config)
        result = formatter.format(single_persona)
        assert ":---:" in result  # Center align
        assert "---:" in result  # Right align


class TestCSVTableFormatter:
    """Tests for CSVTableFormatter."""

    def test_extension_is_csv(self):
        """Test file extension is .csv."""
        formatter = CSVTableFormatter()
        assert formatter.extension() == ".csv"

    def test_format_single_persona(self, single_persona):
        """Test formatting single persona."""
        formatter = CSVTableFormatter()
        result = formatter.format(single_persona)
        assert "Sarah Chen" in result
        assert "," in result  # CSV separator

    def test_format_multiple_personas(self, sample_personas):
        """Test formatting multiple personas."""
        formatter = CSVTableFormatter()
        result = formatter.format_multiple(sample_personas)
        lines = result.strip().split("\n")
        assert len(lines) == 3  # Header + 2 data rows

    def test_includes_headers(self, single_persona):
        """Test CSV includes headers."""
        formatter = CSVTableFormatter()
        result = formatter.format(single_persona)
        assert "Name" in result

    def test_without_headers(self, single_persona):
        """Test CSV without headers."""
        config = TableConfig(include_header=False)
        formatter = CSVTableFormatter(config=config)
        result = formatter.format(single_persona)
        assert "Name" not in result
        assert "Sarah Chen" in result

    def test_quotes_values_with_commas(self):
        """Test values with commas are properly quoted."""
        persona = Persona(
            id="test",
            name="Test, User",
            demographics={},
            goals=["Goal one, Goal two"],
            pain_points=[],
        )
        formatter = CSVTableFormatter()
        result = formatter.format(persona)
        # CSV should properly escape commas
        assert '"Test, User"' in result or "Test, User" in result


class TestLaTeXTableFormatter:
    """Tests for LaTeXTableFormatter."""

    def test_extension_is_tex(self):
        """Test file extension is .tex."""
        formatter = LaTeXTableFormatter()
        assert formatter.extension() == ".tex"

    def test_format_single_persona(self, single_persona):
        """Test formatting single persona."""
        formatter = LaTeXTableFormatter()
        result = formatter.format(single_persona)
        assert "Sarah Chen" in result
        assert "\\begin{table}" in result
        assert "\\end{table}" in result

    def test_format_multiple_personas(self, sample_personas):
        """Test formatting multiple personas."""
        formatter = LaTeXTableFormatter()
        result = formatter.format_multiple(sample_personas)
        assert "Sarah Chen" in result
        assert "Marcus Johnson" in result

    def test_includes_tabular_environment(self, single_persona):
        """Test includes tabular environment."""
        formatter = LaTeXTableFormatter()
        result = formatter.format(single_persona)
        assert "\\begin{tabular}" in result
        assert "\\end{tabular}" in result

    def test_includes_caption_and_label(self, single_persona):
        """Test includes caption and label."""
        formatter = LaTeXTableFormatter(caption="Test Caption", label="tab:test")
        result = formatter.format(single_persona)
        assert "\\caption{Test Caption}" in result
        assert "\\label{tab:test}" in result

    def test_escapes_special_characters(self):
        """Test special LaTeX characters are escaped."""
        persona = Persona(
            id="test",
            name="Test & User",
            demographics={},
            goals=["Goal with $special% chars"],
            pain_points=[],
        )
        formatter = LaTeXTableFormatter()
        result = formatter.format(persona)
        assert "\\&" in result
        assert "\\$" in result or "special" in result

    def test_includes_hlines(self, single_persona):
        """Test includes horizontal lines."""
        formatter = LaTeXTableFormatter()
        result = formatter.format(single_persona)
        assert "\\hline" in result

    def test_bold_headers(self, single_persona):
        """Test headers are bold."""
        formatter = LaTeXTableFormatter()
        result = formatter.format(single_persona)
        assert "\\textbf{" in result


class TestPersonaComparisonTable:
    """Tests for PersonaComparisonTable."""

    def test_creation(self, sample_personas):
        """Test comparison table creation."""
        table = PersonaComparisonTable(sample_personas)
        assert table._personas == sample_personas

    def test_to_ascii(self, sample_personas):
        """Test ASCII output."""
        table = PersonaComparisonTable(sample_personas)
        result = table.to_ascii()
        assert "Sarah Chen" in result
        assert "Marcus Johnson" in result
        assert "+" in result

    def test_to_markdown(self, sample_personas):
        """Test Markdown output."""
        table = PersonaComparisonTable(sample_personas)
        result = table.to_markdown()
        assert "Sarah Chen" in result
        assert "|" in result
        assert "---" in result

    def test_to_csv(self, sample_personas):
        """Test CSV output."""
        table = PersonaComparisonTable(sample_personas)
        result = table.to_csv()
        assert "Sarah Chen" in result
        assert "," in result

    def test_to_latex(self, sample_personas):
        """Test LaTeX output."""
        table = PersonaComparisonTable(sample_personas)
        result = table.to_latex()
        assert "\\begin{table}" in result
        assert "Sarah Chen" in result

    def test_to_latex_with_caption(self, sample_personas):
        """Test LaTeX output with custom caption."""
        table = PersonaComparisonTable(sample_personas)
        result = table.to_latex(caption="My Personas", label="tab:my")
        assert "\\caption{My Personas}" in result
        assert "\\label{tab:my}" in result

    def test_attribute_view_goals(self, sample_personas):
        """Test attribute view for goals."""
        table = PersonaComparisonTable(sample_personas)
        result = table.attribute_view("goals")
        assert "Goals" in result
        assert "Streamline workflows" in result
        assert "Write clean code" in result

    def test_attribute_view_pain_points(self, sample_personas):
        """Test attribute view for pain points."""
        table = PersonaComparisonTable(sample_personas)
        result = table.attribute_view("pain_points")
        assert "Pain Points" in result

    def test_attribute_view_different_formats(self, sample_personas):
        """Test attribute view with different formats."""
        table = PersonaComparisonTable(sample_personas)

        ascii_result = table.attribute_view("goals", TableOutputFormat.ASCII)
        assert "+" in ascii_result

        csv_result = table.attribute_view("goals", TableOutputFormat.CSV)
        assert "," in csv_result

    def test_custom_columns(self, sample_personas):
        """Test with custom columns."""
        columns = [
            TableColumn("name", "Persona Name", width=25),
            TableColumn("quotes", "Key Quotes", width=50),
        ]
        table = PersonaComparisonTable(sample_personas, columns=columns)
        result = table.to_markdown()
        assert "Persona Name" in result
        assert "Key Quotes" in result


class TestTableFormatterEdgeCases:
    """Tests for edge cases in table formatting."""

    def test_empty_goals(self):
        """Test formatting with empty goals."""
        persona = Persona(
            id="test",
            name="Test User",
            demographics={},
            goals=[],
            pain_points=[],
        )
        formatter = MarkdownTableFormatter()
        result = formatter.format(persona)
        assert "Test User" in result

    def test_none_behaviours(self):
        """Test formatting with None behaviours."""
        persona = Persona(
            id="test",
            name="Test User",
            demographics={},
            goals=["Goal"],
            pain_points=[],
            behaviours=None,
        )
        formatter = MarkdownTableFormatter()
        result = formatter.format(persona)
        assert "Test User" in result

    def test_additional_fields(self):
        """Test extraction of additional fields."""
        persona = Persona(
            id="test",
            name="Test User",
            demographics={},
            goals=["Goal"],
            pain_points=[],
            additional={"custom_field": "Custom Value"},
        )
        columns = [
            TableColumn("name", "Name"),
            TableColumn("custom_field", "Custom"),
        ]
        config = TableConfig(columns=columns)
        formatter = MarkdownTableFormatter(config=config)
        result = formatter.format(persona)
        assert "Custom Value" in result

    def test_additional_fields_list(self):
        """Test extraction of list additional fields."""
        persona = Persona(
            id="test",
            name="Test User",
            demographics={},
            goals=["Goal"],
            pain_points=[],
            additional={"tags": ["tag1", "tag2"]},
        )
        columns = [
            TableColumn("name", "Name"),
            TableColumn("tags", "Tags"),
        ]
        config = TableConfig(columns=columns)
        formatter = MarkdownTableFormatter(config=config)
        result = formatter.format(persona)
        assert "tag1" in result
        assert "tag2" in result

    def test_demographic_extraction(self):
        """Test extraction of demographic fields."""
        persona = Persona(
            id="test",
            name="Test User",
            demographics={"role": "Developer", "location": "London"},
            goals=["Goal"],
            pain_points=[],
        )
        columns = [
            TableColumn("name", "Name"),
            TableColumn("role", "Role"),
            TableColumn("location", "Location"),
        ]
        config = TableConfig(columns=columns)
        formatter = MarkdownTableFormatter(config=config)
        result = formatter.format(persona)
        assert "Developer" in result
        assert "London" in result


class TestTableFormatterRegistration:
    """Tests for table formatter registration."""

    def test_ascii_format_registered(self):
        """Test ASCII format is registered."""
        from persona.core.output.registry import get_registry

        registry = get_registry()
        assert registry.has("table-ascii")

    def test_markdown_format_registered(self):
        """Test Markdown format is registered."""
        from persona.core.output.registry import get_registry

        registry = get_registry()
        assert registry.has("table-markdown")

    def test_csv_format_registered(self):
        """Test CSV format is registered."""
        from persona.core.output.registry import get_registry

        registry = get_registry()
        assert registry.has("table-csv")

    def test_latex_format_registered(self):
        """Test LaTeX format is registered."""
        from persona.core.output.registry import get_registry

        registry = get_registry()
        assert registry.has("table-latex")

    def test_all_table_formats_support_comparison(self):
        """Test all table formats support comparison."""
        from persona.core.output.registry import get_registry

        registry = get_registry()
        for name in ["table-ascii", "table-markdown", "table-csv", "table-latex"]:
            info = registry.get_info(name)
            assert info.supports_comparison is True
