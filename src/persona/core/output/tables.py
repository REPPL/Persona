"""
Table output formatters for personas.

This module provides formatters for rendering personas as tables
in various formats: ASCII, Markdown, CSV, and LaTeX.
"""

import csv
import io
from dataclasses import dataclass, field
from enum import Enum

from persona.core.generation.parser import Persona
from persona.core.output.registry import (
    BaseFormatterV2,
    SectionConfig,
    register,
)


class TableOutputFormat(Enum):
    """Available table output formats."""

    ASCII = "ascii"
    MARKDOWN = "markdown"
    CSV = "csv"
    LATEX = "latex"


@dataclass
class TableColumn:
    """Configuration for a table column."""

    key: str
    header: str
    width: int = 20
    align: str = "left"  # left, right, center


@dataclass
class TableConfig:
    """Configuration for table formatting."""

    format: TableOutputFormat = TableOutputFormat.MARKDOWN
    columns: list[TableColumn] = field(default_factory=list)
    include_header: bool = True
    max_cell_width: int = 50
    truncate_long_values: bool = True

    @classmethod
    def default_columns(cls) -> list[TableColumn]:
        """Default column configuration for persona comparison."""
        return [
            TableColumn("name", "Name", width=20),
            TableColumn("goals", "Goals", width=30),
            TableColumn("pain_points", "Pain Points", width=30),
            TableColumn("behaviours", "Behaviours", width=25),
        ]

    @classmethod
    def attribute_view(cls, attribute: str) -> list[TableColumn]:
        """Column configuration for single-attribute view."""
        return [
            TableColumn("name", "Persona", width=20),
            TableColumn(attribute, attribute.replace("_", " ").title(), width=60),
        ]


class BaseTableFormatter(BaseFormatterV2):
    """Base class for table formatters."""

    def __init__(
        self,
        config: TableConfig | None = None,
        sections: SectionConfig | None = None,
    ) -> None:
        """
        Initialise table formatter.

        Args:
            config: Table configuration.
            sections: Section configuration.
        """
        super().__init__(sections=sections)
        self._config = config or TableConfig()
        if not self._config.columns:
            self._config.columns = TableConfig.default_columns()

    def _extract_value(self, persona: Persona, key: str) -> str:
        """Extract a value from a persona by key."""
        if key == "name":
            return persona.name
        if key == "id":
            return persona.id
        if key == "goals":
            return self._format_list(persona.goals)
        if key == "pain_points":
            return self._format_list(persona.pain_points)
        if key == "behaviours":
            return self._format_list(persona.behaviours or [])
        if key == "quotes":
            return self._format_list(persona.quotes or [])
        if key in persona.demographics:
            return str(persona.demographics[key])
        if persona.additional and key in persona.additional:
            value = persona.additional[key]
            if isinstance(value, list):
                return self._format_list(value)
            return str(value)
        return ""

    def _format_list(self, items: list[str]) -> str:
        """Format a list of items for table display."""
        if not items:
            return ""
        if len(items) == 1:
            return items[0]
        return "; ".join(items)

    def _truncate(self, value: str, max_width: int) -> str:
        """Truncate a value to max width."""
        if not self._config.truncate_long_values:
            return value
        if len(value) <= max_width:
            return value
        return value[: max_width - 3] + "..."

    def _build_rows(self, personas: list[Persona]) -> list[list[str]]:
        """Build table rows from personas."""
        rows = []
        for persona in personas:
            row = []
            for col in self._config.columns:
                value = self._extract_value(persona, col.key)
                truncated = self._truncate(value, col.width)
                row.append(truncated)
            rows.append(row)
        return rows

    def _get_headers(self) -> list[str]:
        """Get column headers."""
        return [col.header for col in self._config.columns]


class ASCIITableFormatter(BaseTableFormatter):
    """Format personas as ASCII tables."""

    def format(
        self,
        persona: Persona,
        sections: SectionConfig | None = None,
    ) -> str:
        """Format a single persona as ASCII table."""
        return self.format_multiple([persona], sections)

    def format_multiple(
        self,
        personas: list[Persona],
        sections: SectionConfig | None = None,
    ) -> str:
        """Format multiple personas as ASCII comparison table."""
        headers = self._get_headers()
        rows = self._build_rows(personas)

        # Calculate column widths
        widths = [len(h) for h in headers]
        for row in rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(cell))

        # Respect max width
        widths = [min(w, self._config.max_cell_width) for w in widths]

        # Build output
        lines = []

        # Header separator
        separator = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
        lines.append(separator)

        # Headers
        if self._config.include_header:
            header_row = "|"
            for i, header in enumerate(headers):
                header_row += f" {header:<{widths[i]}} |"
            lines.append(header_row)
            lines.append(separator)

        # Data rows
        for row in rows:
            row_str = "|"
            for i, cell in enumerate(row):
                truncated = self._truncate(cell, widths[i])
                row_str += f" {truncated:<{widths[i]}} |"
            lines.append(row_str)

        lines.append(separator)
        return "\n".join(lines)

    def extension(self) -> str:
        return ".txt"


class MarkdownTableFormatter(BaseTableFormatter):
    """Format personas as Markdown tables."""

    def format(
        self,
        persona: Persona,
        sections: SectionConfig | None = None,
    ) -> str:
        """Format a single persona as Markdown table."""
        return self.format_multiple([persona], sections)

    def format_multiple(
        self,
        personas: list[Persona],
        sections: SectionConfig | None = None,
    ) -> str:
        """Format multiple personas as Markdown comparison table."""
        headers = self._get_headers()
        rows = self._build_rows(personas)

        lines = []

        # Header row
        if self._config.include_header:
            header_line = "| " + " | ".join(headers) + " |"
            lines.append(header_line)

            # Separator with alignment
            sep_parts = []
            for col in self._config.columns:
                if col.align == "center":
                    sep_parts.append(":---:")
                elif col.align == "right":
                    sep_parts.append("---:")
                else:
                    sep_parts.append("---")
            lines.append("| " + " | ".join(sep_parts) + " |")

        # Data rows
        for row in rows:
            # Escape pipe characters in cells
            escaped = [cell.replace("|", "\\|") for cell in row]
            lines.append("| " + " | ".join(escaped) + " |")

        return "\n".join(lines)

    def extension(self) -> str:
        return ".md"


class CSVTableFormatter(BaseTableFormatter):
    """Format personas as CSV."""

    def format(
        self,
        persona: Persona,
        sections: SectionConfig | None = None,
    ) -> str:
        """Format a single persona as CSV."""
        return self.format_multiple([persona], sections)

    def format_multiple(
        self,
        personas: list[Persona],
        sections: SectionConfig | None = None,
    ) -> str:
        """Format multiple personas as CSV."""
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)

        # Header row
        if self._config.include_header:
            headers = self._get_headers()
            writer.writerow(headers)

        # Data rows
        rows = self._build_rows(personas)
        for row in rows:
            writer.writerow(row)

        return output.getvalue()

    def extension(self) -> str:
        return ".csv"


class LaTeXTableFormatter(BaseTableFormatter):
    """Format personas as LaTeX tables."""

    def __init__(
        self,
        config: TableConfig | None = None,
        sections: SectionConfig | None = None,
        caption: str = "Persona Comparison",
        label: str = "tab:personas",
    ) -> None:
        """
        Initialise LaTeX table formatter.

        Args:
            config: Table configuration.
            sections: Section configuration.
            caption: Table caption.
            label: LaTeX label for referencing.
        """
        super().__init__(config=config, sections=sections)
        self._caption = caption
        self._label = label

    def format(
        self,
        persona: Persona,
        sections: SectionConfig | None = None,
    ) -> str:
        """Format a single persona as LaTeX table."""
        return self.format_multiple([persona], sections)

    def format_multiple(
        self,
        personas: list[Persona],
        sections: SectionConfig | None = None,
    ) -> str:
        """Format multiple personas as LaTeX table."""
        headers = self._get_headers()
        rows = self._build_rows(personas)

        # Build column spec
        col_spec = "|" + "|".join("l" for _ in headers) + "|"

        lines = []
        lines.append("\\begin{table}[htbp]")
        lines.append("\\centering")
        lines.append(f"\\begin{{tabular}}{{{col_spec}}}")
        lines.append("\\hline")

        # Header row
        if self._config.include_header:
            escaped_headers = [self._escape_latex(h) for h in headers]
            lines.append(
                " & ".join(f"\\textbf{{{h}}}" for h in escaped_headers) + " \\\\"
            )
            lines.append("\\hline")

        # Data rows
        for row in rows:
            escaped_row = [self._escape_latex(cell) for cell in row]
            lines.append(" & ".join(escaped_row) + " \\\\")

        lines.append("\\hline")
        lines.append("\\end{tabular}")
        lines.append(f"\\caption{{{self._escape_latex(self._caption)}}}")
        lines.append(f"\\label{{{self._label}}}")
        lines.append("\\end{table}")

        return "\n".join(lines)

    def extension(self) -> str:
        return ".tex"

    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters."""
        replacements = [
            ("\\", "\\textbackslash{}"),
            ("&", "\\&"),
            ("%", "\\%"),
            ("$", "\\$"),
            ("#", "\\#"),
            ("_", "\\_"),
            ("{", "\\{"),
            ("}", "\\}"),
            ("~", "\\textasciitilde{}"),
            ("^", "\\textasciicircum{}"),
        ]
        result = text
        for old, new in replacements:
            result = result.replace(old, new)
        return result


class PersonaComparisonTable:
    """
    Generate comparison tables across multiple personas.

    Example:
        table = PersonaComparisonTable(personas)
        md = table.to_markdown()
        csv = table.to_csv()
    """

    def __init__(
        self,
        personas: list[Persona],
        columns: list[TableColumn] | None = None,
    ) -> None:
        """
        Initialise comparison table.

        Args:
            personas: List of personas to compare.
            columns: Optional column configuration.
        """
        self._personas = personas
        self._columns = columns or TableConfig.default_columns()

    def to_ascii(self) -> str:
        """Generate ASCII table."""
        config = TableConfig(format=TableOutputFormat.ASCII, columns=self._columns)
        formatter = ASCIITableFormatter(config=config)
        return formatter.format_multiple(self._personas)

    def to_markdown(self) -> str:
        """Generate Markdown table."""
        config = TableConfig(format=TableOutputFormat.MARKDOWN, columns=self._columns)
        formatter = MarkdownTableFormatter(config=config)
        return formatter.format_multiple(self._personas)

    def to_csv(self) -> str:
        """Generate CSV."""
        config = TableConfig(format=TableOutputFormat.CSV, columns=self._columns)
        formatter = CSVTableFormatter(config=config)
        return formatter.format_multiple(self._personas)

    def to_latex(
        self, caption: str = "Persona Comparison", label: str = "tab:personas"
    ) -> str:
        """Generate LaTeX table."""
        config = TableConfig(format=TableOutputFormat.LATEX, columns=self._columns)
        formatter = LaTeXTableFormatter(config=config, caption=caption, label=label)
        return formatter.format_multiple(self._personas)

    def attribute_view(
        self, attribute: str, format: TableOutputFormat = TableOutputFormat.MARKDOWN
    ) -> str:
        """
        Generate a single-attribute view table.

        Shows one attribute across all personas.

        Args:
            attribute: The attribute to display (e.g., "goals", "pain_points").
            format: Output format.

        Returns:
            Formatted table string.
        """
        columns = TableConfig.attribute_view(attribute)
        config = TableConfig(format=format, columns=columns)

        if format == TableOutputFormat.ASCII:
            formatter = ASCIITableFormatter(config=config)
        elif format == TableOutputFormat.CSV:
            formatter = CSVTableFormatter(config=config)
        elif format == TableOutputFormat.LATEX:
            formatter = LaTeXTableFormatter(config=config)
        else:
            formatter = MarkdownTableFormatter(config=config)

        return formatter.format_multiple(self._personas)


# Register formatters
@register(
    name="table-ascii",
    description="ASCII table format for terminal display",
    extension=".txt",
    supports_sections=False,
    supports_comparison=True,
)
class RegisteredASCIITableFormatter(ASCIITableFormatter):
    """Registered ASCII table formatter."""

    pass


@register(
    name="table-markdown",
    description="Markdown table format for documentation",
    extension=".md",
    supports_sections=False,
    supports_comparison=True,
)
class RegisteredMarkdownTableFormatter(MarkdownTableFormatter):
    """Registered Markdown table formatter."""

    pass


@register(
    name="table-csv",
    description="CSV format for spreadsheets",
    extension=".csv",
    supports_sections=False,
    supports_comparison=True,
)
class RegisteredCSVTableFormatter(CSVTableFormatter):
    """Registered CSV table formatter."""

    pass


@register(
    name="table-latex",
    description="LaTeX table format for academic papers",
    extension=".tex",
    supports_sections=False,
    supports_comparison=True,
)
class RegisteredLaTeXTableFormatter(LaTeXTableFormatter):
    """Registered LaTeX table formatter."""

    pass
