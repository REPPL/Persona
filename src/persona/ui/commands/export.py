"""
Export command for exporting personas to various formats.
"""

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.panel import Panel
from rich.table import Table

from persona.core.export import ExportFormat, PersonaExporter
from persona.ui.console import get_console

export_app = typer.Typer(
    name="export",
    help="Export personas to various formats (JSON, Markdown, Figma, Miro, etc.).",
)


@export_app.callback(invoke_without_command=True)
def export(
    ctx: typer.Context,
    persona_path: Annotated[
        Path,
        typer.Argument(
            help="Path to persona JSON file or output directory.",
            exists=True,
        ),
    ],
    output: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            help="Output file or directory path.",
        ),
    ] = Path("./export"),
    format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Export format (json, markdown, html, figma, miro, uxpressia, csv).",
        ),
    ] = "markdown",
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output results as JSON (command result, not export format).",
        ),
    ] = False,
    preview: Annotated[
        bool,
        typer.Option(
            "--preview",
            "-p",
            help="Preview export without writing to file.",
        ),
    ] = False,
) -> None:
    """
    Export personas to various formats.

    Supports design tools like Figma and Miro, as well as
    standard formats like Markdown, HTML, and CSV.

    Example:
        persona export ./personas.json --format markdown
        persona export ./outputs/ --format figma --output ./exports/
    """
    if ctx.invoked_subcommand is not None:
        return

    console = get_console()

    from persona import __version__

    if not json_output:
        console.print(f"[dim]Persona {__version__}[/dim]\n")

    # Parse format
    try:
        export_format = ExportFormat(format.lower())
    except ValueError:
        valid_formats = ", ".join(f.value for f in ExportFormat)
        if json_output:
            print(
                json.dumps(
                    {
                        "command": "export",
                        "success": False,
                        "error": f"Invalid format: {format}. Valid formats: {valid_formats}",
                    },
                    indent=2,
                )
            )
        else:
            console.print(f"[red]Invalid format:[/red] {format}")
            console.print(f"Valid formats: {valid_formats}")
        raise typer.Exit(1)

    # Load personas
    try:
        personas = _load_personas(persona_path)
    except Exception as e:
        if json_output:
            print(
                json.dumps(
                    {
                        "command": "export",
                        "success": False,
                        "error": str(e),
                    },
                    indent=2,
                )
            )
        else:
            console.print(f"[red]Error loading personas:[/red] {e}")
        raise typer.Exit(1)

    if not personas:
        if json_output:
            print(
                json.dumps(
                    {
                        "command": "export",
                        "success": False,
                        "error": "No personas found to export",
                    },
                    indent=2,
                )
            )
        else:
            console.print("[yellow]No personas found to export.[/yellow]")
        raise typer.Exit(1)

    exporter = PersonaExporter()

    if preview:
        # Preview mode
        preview_content = exporter.preview(personas, export_format)

        if json_output:
            print(
                json.dumps(
                    {
                        "command": "export",
                        "version": __version__,
                        "success": True,
                        "data": {
                            "format": export_format.value,
                            "persona_count": len(personas),
                            "preview": preview_content,
                        },
                    },
                    indent=2,
                )
            )
        else:
            console.print(
                Panel.fit(
                    f"[bold]Export Preview[/bold]\n"
                    f"Format: {export_format.value} | Personas: {len(personas)}",
                    border_style="blue",
                )
            )
            console.print(Panel(preview_content, title="Preview", border_style="dim"))
        return

    # Export
    result = exporter.export(personas, export_format, output)

    if json_output:
        print(
            json.dumps(
                {
                    "command": "export",
                    "version": __version__,
                    "success": result.success,
                    "data": result.to_dict(),
                },
                indent=2,
            )
        )
        if not result.success:
            raise typer.Exit(1)
        return

    # Rich output
    console.print(
        Panel.fit(
            f"[bold]Persona Export[/bold]\n{persona_path}",
            border_style="blue",
        )
    )

    if result.success:
        console.print(f"[green]✓[/green] Exported {result.persona_count} persona(s)")
        console.print(f"[green]✓[/green] Format: {result.format.value}")
        console.print(f"[green]✓[/green] Output: {result.output_path}")
        console.print("\n[green]Export complete.[/green]")
    else:
        console.print(f"[red]✗[/red] Export failed: {result.error}")
        raise typer.Exit(1)


@export_app.command("formats")
def list_formats() -> None:
    """
    List available export formats.

    Example:
        persona export formats
    """
    console = get_console()

    from persona import __version__

    console.print(f"[dim]Persona {__version__}[/dim]\n")

    exporter = PersonaExporter()
    formats = exporter.list_formats()

    console.print("[bold]Available Export Formats:[/bold]\n")

    table = Table()
    table.add_column("Format", style="cyan")
    table.add_column("Name")
    table.add_column("Extension")

    for fmt in formats:
        table.add_row(fmt["id"], fmt["name"], fmt["extension"])

    console.print(table)

    console.print("\n[dim]Use: persona export <path> --format <format>[/dim]")


def _load_personas(path: Path):
    """Load personas from a file or directory."""
    from persona.core.generation.parser import Persona

    if path.is_file():
        with open(path) as f:
            data = json.load(f)

        if isinstance(data, list):
            return [Persona.from_dict(p) for p in data]
        elif isinstance(data, dict):
            if "personas" in data:
                return [Persona.from_dict(p) for p in data["personas"]]
            else:
                return [Persona.from_dict(data)]
    else:
        personas = []

        personas_file = path / "personas.json"
        if personas_file.exists():
            with open(personas_file) as f:
                data = json.load(f)
            if isinstance(data, list):
                return [Persona.from_dict(p) for p in data]
            elif "personas" in data:
                return [Persona.from_dict(p) for p in data["personas"]]

        for json_file in path.glob("persona_*.json"):
            with open(json_file) as f:
                data = json.load(f)
            personas.append(Persona.from_dict(data))

        return personas
