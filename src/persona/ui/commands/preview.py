"""
Preview command for inspecting data before generation.
"""

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.panel import Panel
from rich.table import Table

from persona.core.preview import DataPreviewer, IssueSeverity
from persona.ui.console import get_console

preview_app = typer.Typer(
    name="preview",
    help="Preview data files before generating personas.",
)


@preview_app.callback(invoke_without_command=True)
def preview(
    ctx: typer.Context,
    data_path: Annotated[
        Path,
        typer.Argument(
            help="Path to data file or directory to preview.",
            exists=True,
        ),
    ],
    model: Annotated[
        str,
        typer.Option(
            "--model",
            "-m",
            help="Model to use for cost estimation.",
        ),
    ] = "claude-sonnet-4-20250514",
    count: Annotated[
        int,
        typer.Option(
            "--count",
            "-n",
            help="Number of personas to estimate for.",
        ),
    ] = 3,
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output results as JSON.",
        ),
    ] = False,
    show_sample: Annotated[
        bool,
        typer.Option(
            "--sample",
            "-s",
            help="Show sample content from files.",
        ),
    ] = False,
) -> None:
    """
    Preview data files before generating personas.

    Shows file information, token counts, cost estimates, and any
    potential issues without making any LLM API calls.

    Example:
        persona preview ./data/interviews.csv
        persona preview ./data/ --count 5 --sample
    """
    if ctx.invoked_subcommand is not None:
        return

    console = get_console()

    from persona import __version__

    if not json_output:
        console.print(f"[dim]Persona {__version__}[/dim]\n")

    # Preview data
    previewer = DataPreviewer(model=model, persona_count=count)
    result = previewer.preview(data_path)

    if json_output:
        # JSON output mode
        output = {
            "command": "preview",
            "version": __version__,
            "success": not result.has_errors,
            "data": result.to_dict(),
        }
        print(json.dumps(output, indent=2))
        return

    # Rich output mode
    console.print(
        Panel.fit(
            f"[bold]Data Preview[/bold]\n{data_path}",
            border_style="blue",
        )
    )

    # Summary table
    summary_table = Table(show_header=False, box=None)
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value")

    summary_table.add_row("Files found", str(result.total_files))
    summary_table.add_row("Loadable files", str(len(result.loadable_files)))
    summary_table.add_row("Total tokens", f"{result.total_tokens:,}")
    summary_table.add_row("Total size", _format_size(result.total_size_bytes))
    summary_table.add_row("Est. cost", f"${result.estimated_cost_usd:.4f}")
    summary_table.add_row("Model", result.model)
    summary_table.add_row("Personas", str(result.persona_count))

    console.print(summary_table)
    console.print()

    # Files table
    if result.files:
        files_table = Table(title="Files")
        files_table.add_column("File", style="cyan")
        files_table.add_column("Format")
        files_table.add_column("Tokens", justify="right")
        files_table.add_column("Size", justify="right")
        files_table.add_column("Status")

        for file_preview in result.files:
            status = "[green]✓[/green]" if file_preview.loadable else "[red]✗[/red]"

            # Add issue indicators
            if file_preview.issues:
                error_count = sum(
                    1 for i in file_preview.issues if i.severity == IssueSeverity.ERROR
                )
                warn_count = sum(
                    1
                    for i in file_preview.issues
                    if i.severity == IssueSeverity.WARNING
                )
                if error_count:
                    status = f"[red]✗ {error_count} error(s)[/red]"
                elif warn_count:
                    status = f"[yellow]⚠ {warn_count} warning(s)[/yellow]"

            files_table.add_row(
                file_preview.file_path.name,
                file_preview.format,
                f"{file_preview.token_count:,}",
                _format_size(file_preview.size_bytes),
                status,
            )

        console.print(files_table)

    # Show sample content if requested
    if show_sample and result.loadable_files:
        console.print("\n[bold]Sample Content:[/bold]")
        for file_preview in result.loadable_files[:3]:  # Limit to 3 files
            if file_preview.sample_content:
                console.print(f"\n[cyan]{file_preview.file_path.name}:[/cyan]")
                console.print(
                    Panel(
                        file_preview.sample_content,
                        border_style="dim",
                    )
                )

    # Show issues
    all_issues = list(result.issues)
    for file_preview in result.files:
        all_issues.extend(file_preview.issues)

    if all_issues:
        console.print("\n[bold]Issues:[/bold]")
        for issue in all_issues:
            if issue.severity == IssueSeverity.ERROR:
                console.print(f"  [red]✗[/red] {issue.message}")
            elif issue.severity == IssueSeverity.WARNING:
                console.print(f"  [yellow]⚠[/yellow] {issue.message}")
            else:
                console.print(f"  [blue]ℹ[/blue] {issue.message}")

    # Final status
    if result.has_errors:
        console.print("\n[red]Preview completed with errors.[/red]")
        raise typer.Exit(1)
    elif result.has_warnings:
        console.print("\n[yellow]Preview completed with warnings.[/yellow]")
    else:
        console.print("\n[green]Ready for generation.[/green]")


def _format_size(size_bytes: int) -> str:
    """Format file size in human-readable form."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
