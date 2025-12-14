"""
Empathy map table output formatter.

This module provides the EmpathyTableFormatter class for outputting
personas in the Boag empathy map table format with five dimensions:
Tasks, Feelings, Influences, Pain Points, and Goals.

References:
    Boag, P. (2015). Adapting Empathy Maps for UX Design. Boagworld.
    https://boagworld.com/usability/adapting-empathy-maps-for-ux-design/

    Lycett, M., Cundle, M., Grasso, L., Meechao, K., & Reppel, A. (2025).
    Materialising Design Fictions: Exploring Music Memorabilia in a Metaverse
    Environment. Information Systems Journal, 35, 1662-1678.
    https://doi.org/10.1111/isj.12600 (see Table 1 for table format).
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

try:
    from rich.console import Console
    from rich.table import Table as RichTable

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class TableFormat(Enum):
    """Output formats for empathy tables."""

    MARKDOWN = "markdown"
    HTML = "html"
    RICH = "rich"  # Terminal display via Rich


@dataclass
class EmpathyTableRow:
    """
    A single row in an empathy map table.

    Represents one persona/participant type with their empathy dimensions.

    Attributes:
        name: Persona/participant name.
        tasks: What they're trying to accomplish.
        feelings: How they feel during the experience.
        influences: What/who influences their decisions.
        pain_points: Frustrations and challenges.
        goals: What they want to achieve.
    """

    name: str
    tasks: list[str] = field(default_factory=list)
    feelings: list[str] = field(default_factory=list)
    influences: list[str] = field(default_factory=list)
    pain_points: list[str] = field(default_factory=list)
    goals: list[str] = field(default_factory=list)

    @classmethod
    def from_persona(cls, persona: Any) -> "EmpathyTableRow":
        """
        Create a row from a Persona object.

        Maps persona attributes to empathy map dimensions.

        Args:
            persona: A Persona object.

        Returns:
            EmpathyTableRow with mapped dimensions.
        """
        name = getattr(persona, "name", "Unknown")

        # Map persona attributes to empathy dimensions
        # Tasks: From behaviours (what they do)
        tasks = list(getattr(persona, "behaviours", []) or [])

        # Feelings: From motivations or attitudes if available
        feelings = list(getattr(persona, "motivations", []) or [])

        # Influences: From context or environment if available
        influences = list(getattr(persona, "influences", []) or [])

        # Pain Points: Direct mapping
        pain_points = list(getattr(persona, "pain_points", []) or [])

        # Goals: Direct mapping
        goals = list(getattr(persona, "goals", []) or [])

        return cls(
            name=name,
            tasks=tasks,
            feelings=feelings,
            influences=influences,
            pain_points=pain_points,
            goals=goals,
        )

    @classmethod
    def from_participant_type_map(cls, ptm: Any) -> "EmpathyTableRow":
        """
        Create a row from a ParticipantTypeMap.

        Args:
            ptm: A ParticipantTypeMap from empathy map input.

        Returns:
            EmpathyTableRow with direct dimension mapping.
        """
        return cls(
            name=ptm.participant_type,
            tasks=list(ptm.tasks),
            feelings=list(ptm.feelings),
            influences=list(ptm.influences),
            pain_points=list(ptm.pain_points),
            goals=list(ptm.goals),
        )


@dataclass
class EmpathyTableConfig:
    """
    Configuration for empathy table output.

    Attributes:
        title: Table title.
        max_items_per_cell: Max items to show per dimension.
        truncate_length: Max characters per item.
        show_separator: Whether to use bullet separators.
    """

    title: str = "Empathy Map"
    max_items_per_cell: int = 5
    truncate_length: int = 100
    show_separator: bool = True


class EmpathyTableFormatter:
    """
    Formats empathy map data as tables.

    Supports multiple output formats: Markdown, HTML, and Rich
    terminal display. Tables follow the Boag empathy map structure
    with five dimensions.

    Example:
        formatter = EmpathyTableFormatter()
        rows = [EmpathyTableRow.from_persona(p) for p in personas]
        markdown = formatter.to_markdown(rows)
        formatter.print_rich(rows)  # Terminal display
    """

    # Column definitions for empathy table
    COLUMNS = [
        ("Persona", "name"),
        ("Tasks", "tasks"),
        ("Feelings", "feelings"),
        ("Influences", "influences"),
        ("Pain Points", "pain_points"),
        ("Goals", "goals"),
    ]

    def __init__(self, config: EmpathyTableConfig | None = None) -> None:
        """
        Initialise the formatter.

        Args:
            config: Table configuration options.
        """
        self.config = config or EmpathyTableConfig()

    def to_markdown(self, rows: list[EmpathyTableRow]) -> str:
        """
        Format rows as a Markdown table.

        Args:
            rows: Table rows to format.

        Returns:
            Markdown table string.
        """
        if not rows:
            return ""

        lines = [f"# {self.config.title}", ""]

        # Header row
        headers = [col[0] for col in self.COLUMNS]
        lines.append("| " + " | ".join(headers) + " |")

        # Separator row
        lines.append("|" + "|".join(["---"] * len(headers)) + "|")

        # Data rows
        for row in rows:
            cells = []
            for _, attr in self.COLUMNS:
                value = getattr(row, attr)
                cells.append(self._format_cell_markdown(value))
            lines.append("| " + " | ".join(cells) + " |")

        return "\n".join(lines)

    def to_html(self, rows: list[EmpathyTableRow], standalone: bool = True) -> str:
        """
        Format rows as an HTML table.

        Args:
            rows: Table rows to format.
            standalone: If True, include full HTML document wrapper.

        Returns:
            HTML table string.
        """
        if not rows:
            return ""

        table_html = ['<table class="empathy-table">']

        # Header
        table_html.append("<thead>")
        table_html.append("<tr>")
        for col, _ in self.COLUMNS:
            table_html.append(f"<th>{col}</th>")
        table_html.append("</tr>")
        table_html.append("</thead>")

        # Body
        table_html.append("<tbody>")
        for row in rows:
            table_html.append("<tr>")
            for _, attr in self.COLUMNS:
                value = getattr(row, attr)
                cell_html = self._format_cell_html(value)
                table_html.append(f"<td>{cell_html}</td>")
            table_html.append("</tr>")
        table_html.append("</tbody>")

        table_html.append("</table>")

        if standalone:
            return self._wrap_html_document("\n".join(table_html))
        return "\n".join(table_html)

    def print_rich(self, rows: list[EmpathyTableRow]) -> None:
        """
        Print table to terminal using Rich.

        Args:
            rows: Table rows to display.

        Raises:
            ImportError: If Rich is not installed.
        """
        if not RICH_AVAILABLE:
            raise ImportError(
                "Rich is required for terminal display. "
                "Install with: pip install rich"
            )

        if not rows:
            return

        console = Console()
        table = RichTable(title=self.config.title)

        # Add columns
        for col, _ in self.COLUMNS:
            table.add_column(col, style="cyan" if col == "Persona" else None)

        # Add rows
        for row in rows:
            cells = []
            for _, attr in self.COLUMNS:
                value = getattr(row, attr)
                cells.append(self._format_cell_rich(value))
            table.add_row(*cells)

        console.print(table)

    def to_rich_string(self, rows: list[EmpathyTableRow]) -> str:
        """
        Format as string for Rich console output.

        Args:
            rows: Table rows to format.

        Returns:
            String representation of Rich table.
        """
        if not RICH_AVAILABLE or not rows:
            return ""

        from io import StringIO

        console = Console(file=StringIO(), force_terminal=True)
        table = RichTable(title=self.config.title)

        for col, _ in self.COLUMNS:
            table.add_column(col)

        for row in rows:
            cells = []
            for _, attr in self.COLUMNS:
                value = getattr(row, attr)
                cells.append(self._format_cell_rich(value))
            table.add_row(*cells)

        console.print(table)
        return console.file.getvalue()

    def export(
        self,
        rows: list[EmpathyTableRow],
        format: TableFormat,
        output_path: Path,
    ) -> Path:
        """
        Export table to file.

        Args:
            rows: Table rows to export.
            format: Output format.
            output_path: Destination path.

        Returns:
            Path to exported file.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        if format == TableFormat.MARKDOWN:
            content = self.to_markdown(rows)
            if not output_path.suffix:
                output_path = output_path.with_suffix(".md")
        elif format == TableFormat.HTML:
            content = self.to_html(rows, standalone=True)
            if not output_path.suffix:
                output_path = output_path.with_suffix(".html")
        elif format == TableFormat.RICH:
            content = self.to_rich_string(rows)
            if not output_path.suffix:
                output_path = output_path.with_suffix(".txt")
        else:
            raise ValueError(f"Unsupported format: {format}")

        output_path.write_text(content, encoding="utf-8")
        return output_path

    def from_personas(self, personas: list[Any]) -> list[EmpathyTableRow]:
        """
        Convert a list of personas to table rows.

        Args:
            personas: List of Persona objects.

        Returns:
            List of EmpathyTableRow objects.
        """
        return [EmpathyTableRow.from_persona(p) for p in personas]

    def from_empathy_map(self, empathy_map: Any) -> list[EmpathyTableRow]:
        """
        Convert an EmpathyMap to table rows.

        Args:
            empathy_map: EmpathyMap object with participant type data.

        Returns:
            List of EmpathyTableRow objects.
        """
        return [
            EmpathyTableRow.from_participant_type_map(ptm)
            for ptm in empathy_map.data
        ]

    def _format_cell_markdown(self, value: Any) -> str:
        """Format cell value for Markdown."""
        if isinstance(value, str):
            return self._escape_markdown(value)

        if isinstance(value, list):
            if not value:
                return "-"
            items = value[: self.config.max_items_per_cell]
            formatted = [self._truncate(str(i)) for i in items]
            if self.config.show_separator:
                return ", ".join(formatted)
            return " ".join(formatted)

        return str(value)

    def _format_cell_html(self, value: Any) -> str:
        """Format cell value for HTML."""
        if isinstance(value, str):
            return self._escape_html(value)

        if isinstance(value, list):
            if not value:
                return "<em>-</em>"
            items = value[: self.config.max_items_per_cell]
            list_items = [
                f"<li>{self._escape_html(self._truncate(str(i)))}</li>"
                for i in items
            ]
            return f"<ul>{''.join(list_items)}</ul>"

        return self._escape_html(str(value))

    def _format_cell_rich(self, value: Any) -> str:
        """Format cell value for Rich."""
        if isinstance(value, str):
            return value

        if isinstance(value, list):
            if not value:
                return "-"
            items = value[: self.config.max_items_per_cell]
            formatted = [self._truncate(str(i)) for i in items]
            return "\n".join(f"• {f}" for f in formatted)

        return str(value)

    def _truncate(self, text: str) -> str:
        """Truncate text to max length."""
        if len(text) <= self.config.truncate_length:
            return text
        return text[: self.config.truncate_length - 3] + "..."

    def _escape_markdown(self, text: str) -> str:
        """Escape special Markdown characters."""
        for char in ["|", "\n", "\r"]:
            text = text.replace(char, " ")
        return text.strip()

    def _escape_html(self, text: str) -> str:
        """Escape special HTML characters."""
        return (
            text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
        )

    def _wrap_html_document(self, table_html: str) -> str:
        """Wrap table in full HTML document."""
        return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>{self.config.title}</title>
<style>
body {{
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}}
h1 {{
    color: #333;
}}
.empathy-table {{
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
}}
.empathy-table th,
.empathy-table td {{
    border: 1px solid #ddd;
    padding: 12px;
    text-align: left;
    vertical-align: top;
}}
.empathy-table th {{
    background-color: #f5f5f5;
    font-weight: 600;
    color: #333;
}}
.empathy-table tr:nth-child(even) {{
    background-color: #fafafa;
}}
.empathy-table ul {{
    margin: 0;
    padding-left: 20px;
}}
.empathy-table li {{
    margin: 4px 0;
}}
</style>
</head>
<body>
<h1>{self.config.title}</h1>
{table_html}
</body>
</html>"""
