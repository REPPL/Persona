"""
Base utilities for quality assessment commands.

Provides common functionality shared across bias, diversity, fidelity,
faithfulness, academic, and verify commands.
"""

import json
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from persona.core.generation.parser import Persona


def load_personas(path: Path) -> list[Persona]:
    """
    Load personas from a file or directory.

    Handles multiple JSON structures:
    - Single persona object
    - List of persona objects
    - Object with "personas" key containing list

    Args:
        path: Path to JSON file or output directory.

    Returns:
        List of Persona objects.

    Raises:
        FileNotFoundError: If path does not exist.
        ValueError: If no personas found or invalid format.
    """
    if not path.exists():
        raise FileNotFoundError(f"Path does not exist: {path}")

    if path.is_file():
        return _load_from_file(path)
    else:
        return _load_from_directory(path)


def _load_from_file(path: Path) -> list[Persona]:
    """Load personas from a JSON file."""
    with open(path) as f:
        data = json.load(f)

    if isinstance(data, list):
        return [Persona.from_dict(p) for p in data]
    elif isinstance(data, dict):
        if "personas" in data:
            return [Persona.from_dict(p) for p in data["personas"]]
        else:
            return [Persona.from_dict(data)]

    raise ValueError(f"Unexpected data format in {path}")


def _load_from_directory(path: Path) -> list[Persona]:
    """Load personas from an output directory."""
    personas = []

    # Look for personas.json first
    personas_file = path / "personas.json"
    if personas_file.exists():
        with open(personas_file) as f:
            data = json.load(f)
        if isinstance(data, list):
            return [Persona.from_dict(p) for p in data]
        elif isinstance(data, dict) and "personas" in data:
            return [Persona.from_dict(p) for p in data["personas"]]

    # Fall back to individual persona files
    for json_file in sorted(path.glob("persona_*.json")):
        with open(json_file) as f:
            data = json.load(f)
        personas.append(Persona.from_dict(data))

    return personas


def load_single_persona(path: Path) -> Persona:
    """
    Load a single persona from a file.

    Args:
        path: Path to JSON file.

    Returns:
        Single Persona object.

    Raises:
        FileNotFoundError: If path does not exist.
        ValueError: If empty or invalid format.
    """
    with open(path) as f:
        data = json.load(f)

    if isinstance(data, list):
        if not data:
            raise ValueError("Empty persona list")
        data = data[0]

    return Persona.from_dict(data)


def colour_score(
    score: float,
    low_threshold: float = 0.3,
    high_threshold: float = 0.7,
    *,
    invert: bool = False,
    format_spec: str = ".3f",
) -> str:
    """
    Return score with appropriate Rich colour markup.

    Args:
        score: Score value (0-1 typically).
        low_threshold: Threshold below which score is "good" (green).
        high_threshold: Threshold above which score is "bad" (red).
        invert: If True, high scores are good (green), low are bad (red).
        format_spec: Format specification for score display.

    Returns:
        Rich markup string with coloured score.
    """
    formatted = f"{score:{format_spec}}"

    if invert:
        # High is good (e.g., fidelity, diversity scores)
        if score >= high_threshold:
            return f"[green]{formatted}[/green]"
        elif score >= low_threshold:
            return f"[yellow]{formatted}[/yellow]"
        else:
            return f"[red]{formatted}[/red]"
    else:
        # Low is good (e.g., bias scores)
        if score <= low_threshold:
            return f"[green]{formatted}[/green]"
        elif score <= high_threshold:
            return f"[yellow]{formatted}[/yellow]"
        else:
            return f"[red]{formatted}[/red]"


def display_version_header(console: Console, quiet: bool = False) -> None:
    """
    Display version header if not in quiet mode.

    Args:
        console: Rich console instance.
        quiet: If True, suppress output.
    """
    if quiet:
        return

    from persona import __version__

    console.print(f"[dim]Persona {__version__}[/dim]\n")


def handle_error(
    console: Console,
    message: str,
    output_format: str,
    error: Exception | str,
    exit_code: int = 1,
) -> None:
    """
    Handle error with consistent formatting across output modes.

    Args:
        console: Rich console instance.
        message: Error message prefix.
        output_format: Current output format (json, rich, markdown).
        error: Exception or error string.
        exit_code: Exit code for typer.Exit.

    Raises:
        typer.Exit: Always raises with specified exit code.
    """
    error_str = str(error)

    if output_format == "json":
        print(json.dumps({"success": False, "error": error_str}, indent=2))
    else:
        console.print(f"[red]{message}:[/red] {error_str}")

    raise typer.Exit(exit_code)


def check_threshold(
    console: Console,
    score: float,
    max_score: float | None,
    output_format: str,
    item_name: str = "item",
) -> None:
    """
    Check if score exceeds maximum threshold.

    Args:
        console: Rich console instance.
        score: Current score to check.
        max_score: Maximum allowed score (None to skip check).
        output_format: Current output format.
        item_name: Name of item for error message.

    Raises:
        typer.Exit: If score exceeds threshold.
    """
    if max_score is None:
        return

    if score > max_score:
        if output_format != "json":
            console.print(
                f"\n[red]Error:[/red] {item_name} score ({score:.3f}) "
                f"exceeds maximum threshold ({max_score})"
            )
        raise typer.Exit(1)


class QualityOutputFormatter:
    """
    Handles output formatting for quality assessment commands.

    Provides consistent JSON, markdown, and rich output formatting
    with support for saving to files.
    """

    def __init__(
        self,
        console: Console,
        output_format: str = "rich",
        save_path: Path | None = None,
    ):
        """
        Initialise output formatter.

        Args:
            console: Rich console instance.
            output_format: Output format (json, markdown, rich, table).
            save_path: Optional path to save output.
        """
        self.console = console
        self.output_format = output_format
        self.save_path = save_path

    def output_json(
        self,
        data: dict[str, Any],
        command_name: str,
    ) -> None:
        """
        Output data as JSON.

        Args:
            data: Data to output.
            command_name: Name of the command for metadata.
        """
        from persona import __version__

        output = {
            "command": command_name,
            "version": __version__,
            "success": True,
            "data": data,
        }

        output_text = json.dumps(output, indent=2)
        print(output_text)

        if self.save_path:
            self.save_path.write_text(output_text)

    def save_data(self, data: dict[str, Any]) -> None:
        """
        Save data to file if save_path is set.

        Args:
            data: Data to save as JSON.
        """
        if self.save_path:
            self.save_path.write_text(json.dumps(data, indent=2))

    def save_text(self, text: str) -> None:
        """
        Save text to file if save_path is set.

        Args:
            text: Text to save.
        """
        if self.save_path:
            self.save_path.write_text(text)


def create_summary_table(
    metrics: list[tuple[str, str]],
    *,
    show_header: bool = False,
) -> Table:
    """
    Create a summary metrics table.

    Args:
        metrics: List of (metric_name, value) tuples.
        show_header: Whether to show column headers.

    Returns:
        Rich Table with metrics.
    """
    table = Table(show_header=show_header, box=None)
    table.add_column("Metric", style="cyan")
    table.add_column("Value")

    for metric_name, value in metrics:
        table.add_row(metric_name, value)

    return table


def create_results_table(
    title: str,
    columns: list[tuple[str, str, str]],
    rows: list[list[str]],
) -> Table:
    """
    Create a results table with standard formatting.

    Args:
        title: Table title.
        columns: List of (name, style, justify) tuples.
        rows: List of row data lists.

    Returns:
        Rich Table with results.
    """
    table = Table(title=title)

    for col_name, style, justify in columns:
        table.add_column(col_name, style=style, justify=justify)

    for row in rows:
        table.add_row(*row)

    return table


def create_panel(
    content: str,
    title: str | None = None,
    border_style: str = "cyan",
) -> Panel:
    """
    Create a styled panel.

    Args:
        content: Panel content.
        title: Optional panel title.
        border_style: Border colour style.

    Returns:
        Rich Panel.
    """
    return Panel.fit(content, title=title, border_style=border_style)


def format_percentage(value: float, decimal_places: int = 1) -> str:
    """
    Format a decimal value as percentage.

    Args:
        value: Value between 0 and 1.
        decimal_places: Number of decimal places.

    Returns:
        Formatted percentage string.
    """
    return f"{value:.{decimal_places}%}"


def format_count_with_colour(
    count: int,
    colour: str,
    zero_colour: str = "dim",
) -> str:
    """
    Format count with colour, using different colour for zero.

    Args:
        count: Count value.
        colour: Colour for non-zero counts.
        zero_colour: Colour for zero counts.

    Returns:
        Rich markup string.
    """
    if count > 0:
        return f"[{colour}]{count}[/{colour}]"
    return f"[{zero_colour}]0[/{zero_colour}]"
