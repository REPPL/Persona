"""
Faithfulness validation command for personas.

Provides hallucination detection through claim extraction,
source matching, and optional HHEM classification.
"""

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.panel import Panel
from rich.table import Table

from persona.core.generation.parser import Persona
from persona.ui.console import get_console

faithfulness_app = typer.Typer(
    name="faithfulness",
    help="Detect hallucinations and validate persona faithfulness to source data.",
)


@faithfulness_app.callback(invoke_without_command=True)
def faithfulness(
    ctx: typer.Context,
    persona_path: Annotated[
        Path,
        typer.Argument(
            help="Path to persona JSON file or output directory.",
            exists=True,
        ),
    ],
    source_path: Annotated[
        Path,
        typer.Option(
            "--source", "-s",
            help="Path to source data file (required).",
            exists=True,
        ),
    ],
    output_format: Annotated[
        str,
        typer.Option(
            "--output", "-o",
            help="Output format: rich, json, markdown.",
        ),
    ] = "rich",
    save_to: Annotated[
        Optional[Path],
        typer.Option(
            "--save",
            help="Save report to file.",
        ),
    ] = None,
    minimum_score: Annotated[
        Optional[float],
        typer.Option(
            "--min-score",
            help="Exit with error if faithfulness below threshold (0-100).",
        ),
    ] = None,
    threshold: Annotated[
        float,
        typer.Option(
            "--threshold", "-t",
            help="Similarity threshold for claim support (0-1).",
        ),
    ] = 0.7,
    use_hhem: Annotated[
        bool,
        typer.Option(
            "--hhem",
            help="Use HHEM classifier for enhanced hallucination detection.",
        ),
    ] = False,
    llm_provider: Annotated[
        str,
        typer.Option(
            "--llm-provider",
            help="LLM provider for claim extraction (anthropic, openai, ollama).",
        ),
    ] = "ollama",
    llm_model: Annotated[
        Optional[str],
        typer.Option(
            "--llm-model",
            help="Specific LLM model for claim extraction.",
        ),
    ] = None,
    embedding_provider: Annotated[
        str,
        typer.Option(
            "--embedding-provider",
            help="Embedding provider for source matching (openai).",
        ),
    ] = "openai",
    show_claims: Annotated[
        bool,
        typer.Option(
            "--show-claims",
            help="Show all extracted claims in output.",
        ),
    ] = False,
    show_unsupported: Annotated[
        bool,
        typer.Option(
            "--show-unsupported",
            help="Show details of unsupported claims.",
        ),
    ] = True,
) -> None:
    """
    Validate persona faithfulness to source data.

    Detects hallucinations by:
    1. Extracting factual claims from persona attributes
    2. Matching claims against source data using semantic similarity
    3. Optionally refining with HHEM (Hallucination Detection) classifier

    Example:
        persona faithfulness ./personas.json --source ./data.txt
        persona faithfulness ./output/ -s ./research.txt --min-score 80
        persona faithfulness ./personas.json -s ./data.txt --hhem --threshold 0.8
    """
    if ctx.invoked_subcommand is not None:
        return

    console = get_console()

    from persona import __version__
    from persona.core.embedding.factory import EmbeddingProviderFactory
    from persona.core.providers import ProviderFactory
    from persona.core.quality.faithfulness import FaithfulnessValidator

    # Load personas
    try:
        personas = _load_personas(persona_path)
    except Exception as e:
        if output_format == "json":
            print(json.dumps({"success": False, "error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error loading personas:[/red] {e}")
        raise typer.Exit(1)

    if not personas:
        if output_format == "json":
            print(json.dumps({"success": False, "error": "No personas found"}, indent=2))
        else:
            console.print("[yellow]No personas found to validate.[/yellow]")
        raise typer.Exit(1)

    # Load source data
    try:
        source_data = source_path.read_text(encoding="utf-8")
    except Exception as e:
        if output_format == "json":
            print(json.dumps({"success": False, "error": f"Failed to load source: {e}"}, indent=2))
        else:
            console.print(f"[red]Error loading source data:[/red] {e}")
        raise typer.Exit(1)

    # Create providers
    try:
        llm_provider_instance = ProviderFactory.create(llm_provider)
        if llm_model:
            llm_provider_instance.model = llm_model
    except Exception as e:
        if output_format == "json":
            print(json.dumps({"success": False, "error": f"Failed to create LLM provider: {e}"}, indent=2))
        else:
            console.print(f"[red]Error creating LLM provider:[/red] {e}")
        raise typer.Exit(1)

    try:
        embedding_provider_instance = EmbeddingProviderFactory.create(embedding_provider)
    except Exception as e:
        if output_format == "json":
            print(json.dumps({"success": False, "error": f"Failed to create embedding provider: {e}"}, indent=2))
        else:
            console.print(f"[red]Error creating embedding provider:[/red] {e}")
        raise typer.Exit(1)

    # Create validator
    try:
        validator = FaithfulnessValidator(
            llm_provider=llm_provider_instance,
            embedding_provider=embedding_provider_instance,
            use_hhem=use_hhem,
            support_threshold=threshold,
        )
    except Exception as e:
        if output_format == "json":
            print(json.dumps({"success": False, "error": f"Failed to initialise validator: {e}"}, indent=2))
        else:
            console.print(f"[red]Error initialising validator:[/red] {e}")
        raise typer.Exit(1)

    # Validate personas
    if output_format == "rich" and not console._quiet:
        console.print(f"[dim]Persona {__version__}[/dim]\n")
        console.print(f"[dim]Validating {len(personas)} persona(s) against source data...[/dim]\n")

    try:
        reports = validator.validate_batch(personas, source_data)
    except Exception as e:
        if output_format == "json":
            print(json.dumps({"success": False, "error": str(e)}, indent=2))
        else:
            console.print(f"[red]Validation error:[/red] {e}")
        raise typer.Exit(1)

    # Calculate summary statistics
    total_claims = sum(len(r.claims) for r in reports)
    total_supported = sum(r.supported_count for r in reports)
    total_unsupported = sum(r.unsupported_count for r in reports)
    avg_faithfulness = sum(r.faithfulness_score for r in reports) / len(reports) if reports else 0

    # Output results
    if output_format == "json":
        output = {
            "command": "faithfulness",
            "version": __version__,
            "success": True,
            "data": {
                "persona_count": len(reports),
                "summary": {
                    "total_claims": total_claims,
                    "supported_claims": total_supported,
                    "unsupported_claims": total_unsupported,
                    "average_faithfulness": round(avg_faithfulness, 1),
                    "support_threshold": threshold,
                    "used_hhem": use_hhem,
                },
                "reports": [_report_to_dict(r, show_claims) for r in reports],
            },
        }
        output_text = json.dumps(output, indent=2)
        print(output_text)
        if save_to:
            save_to.write_text(output_text)
    elif output_format == "markdown":
        report = _generate_markdown_report(reports, threshold, use_hhem, show_claims, show_unsupported)
        print(report)
        if save_to:
            save_to.write_text(report)
    else:
        _display_rich_output(console, reports, threshold, use_hhem, show_claims, show_unsupported)
        if save_to:
            save_to.write_text(json.dumps({
                "summary": {
                    "total_claims": total_claims,
                    "supported_claims": total_supported,
                    "unsupported_claims": total_unsupported,
                    "average_faithfulness": round(avg_faithfulness, 1),
                },
                "reports": [_report_to_dict(r, show_claims) for r in reports],
            }, indent=2))

    # Check minimum score threshold
    if minimum_score is not None:
        failing = [r for r in reports if r.faithfulness_score < minimum_score]
        if failing:
            if output_format != "json":
                console.print(
                    f"\n[red]Error:[/red] {len(failing)} persona(s) "
                    f"below minimum faithfulness of {minimum_score}%"
                )
            raise typer.Exit(1)


def _display_rich_output(
    console,
    reports,
    threshold: float,
    use_hhem: bool,
    show_claims: bool,
    show_unsupported: bool,
) -> None:
    """Display results with Rich formatting."""
    console.print(Panel.fit(
        "[bold]Faithfulness Validation Report[/bold]",
        border_style="blue",
    ))

    # Summary statistics
    total_claims = sum(len(r.claims) for r in reports)
    total_supported = sum(r.supported_count for r in reports)
    total_unsupported = sum(r.unsupported_count for r in reports)
    avg_faithfulness = sum(r.faithfulness_score for r in reports) / len(reports) if reports else 0

    summary = Table(show_header=False, box=None)
    summary.add_column("Metric", style="cyan")
    summary.add_column("Value")
    summary.add_row("Personas validated", str(len(reports)))
    summary.add_row("Total claims", str(total_claims))
    summary.add_row("Supported claims", f"[green]{total_supported}[/green]")
    summary.add_row(
        "Unsupported claims",
        f"[red]{total_unsupported}[/red]" if total_unsupported > 0 else "0"
    )
    summary.add_row("Average faithfulness", _colour_faithfulness(avg_faithfulness))
    summary.add_row("Support threshold", f"{threshold:.1%}")
    summary.add_row("HHEM classifier", "Enabled" if use_hhem else "Disabled")

    console.print(summary)
    console.print()

    # Individual results table
    results_table = Table(title="Validation Results")
    results_table.add_column("Persona", style="cyan")
    results_table.add_column("Claims", justify="right")
    results_table.add_column("Supported", justify="right")
    results_table.add_column("Unsupported", justify="right")
    results_table.add_column("Faithfulness", justify="right")
    results_table.add_column("Status")

    for report in reports:
        name = report.persona_name or report.persona_id[:20]

        if report.faithfulness_score >= 80:
            status = "[green]✓ Good[/green]"
        elif report.faithfulness_score >= 60:
            status = "[yellow]⚠ Fair[/yellow]"
        else:
            status = "[red]✗ Poor[/red]"

        results_table.add_row(
            name,
            str(report.total_claims),
            f"[green]{report.supported_count}[/green]",
            f"[red]{report.unsupported_count}[/red]" if report.unsupported_count > 0 else "0",
            _colour_faithfulness(report.faithfulness_score),
            status,
        )

    console.print(results_table)

    # Show unsupported claims details
    if show_unsupported:
        reports_with_issues = [r for r in reports if r.unsupported_count > 0]
        if reports_with_issues:
            console.print("\n[bold]Unsupported Claims (Potential Hallucinations):[/bold]")

            for report in reports_with_issues:
                name = report.persona_name or report.persona_id
                console.print(f"\n[cyan]{name}[/cyan] ({report.unsupported_count} unsupported):")

                for claim in report.unsupported_claims[:5]:  # Limit to 5 per persona
                    console.print(f"  [red]•[/red] [{claim.claim_type.value}] {claim.text}")
                    if claim.source_field:
                        console.print(f"    [dim]Field: {claim.source_field}[/dim]")

                if len(report.unsupported_claims) > 5:
                    console.print(f"  [dim]... and {len(report.unsupported_claims) - 5} more[/dim]")

    # Show all claims if requested
    if show_claims:
        console.print("\n[bold]All Extracted Claims:[/bold]")

        for report in reports:
            name = report.persona_name or report.persona_id
            console.print(f"\n[cyan]{name}[/cyan] ({len(report.claims)} claims):")

            for claim in report.claims:
                # Find matching result
                match = next((m for m in report.matches if m.claim.text == claim.text), None)
                if match and match.is_supported:
                    console.print(f"  [green]✓[/green] {claim.text}")
                else:
                    console.print(f"  [red]✗[/red] {claim.text}")


def _generate_markdown_report(
    reports,
    threshold: float,
    use_hhem: bool,
    show_claims: bool,
    show_unsupported: bool,
) -> str:
    """Generate a Markdown report."""
    total_claims = sum(len(r.claims) for r in reports)
    total_supported = sum(r.supported_count for r in reports)
    total_unsupported = sum(r.unsupported_count for r in reports)
    avg_faithfulness = sum(r.faithfulness_score for r in reports) / len(reports) if reports else 0

    lines = [
        "# Faithfulness Validation Report",
        "",
        "## Summary",
        "",
        f"- **Personas validated:** {len(reports)}",
        f"- **Total claims:** {total_claims}",
        f"- **Supported claims:** {total_supported}",
        f"- **Unsupported claims:** {total_unsupported}",
        f"- **Average faithfulness:** {avg_faithfulness:.1f}%",
        f"- **Support threshold:** {threshold:.1%}",
        f"- **HHEM classifier:** {'Enabled' if use_hhem else 'Disabled'}",
        "",
        "## Results by Persona",
        "",
        "| Persona | Claims | Supported | Unsupported | Faithfulness | Status |",
        "|---------|--------|-----------|-------------|--------------|--------|",
    ]

    for report in reports:
        name = report.persona_name or report.persona_id[:20]
        if report.faithfulness_score >= 80:
            status = "✓ Good"
        elif report.faithfulness_score >= 60:
            status = "⚠ Fair"
        else:
            status = "✗ Poor"

        lines.append(
            f"| {name} | {report.total_claims} | {report.supported_count} | "
            f"{report.unsupported_count} | {report.faithfulness_score:.1f}% | {status} |"
        )

    if show_unsupported:
        reports_with_issues = [r for r in reports if r.unsupported_count > 0]
        if reports_with_issues:
            lines.extend([
                "",
                "## Unsupported Claims (Potential Hallucinations)",
                "",
            ])

            for report in reports_with_issues:
                name = report.persona_name or report.persona_id
                lines.append(f"### {name}")
                lines.append("")

                for claim in report.unsupported_claims:
                    lines.append(f"- **[{claim.claim_type.value}]** {claim.text}")
                    if claim.source_field:
                        lines.append(f"  - Field: {claim.source_field}")

                lines.append("")

    return "\n".join(lines)


def _colour_faithfulness(score: float) -> str:
    """Return faithfulness score with appropriate colour markup."""
    if score >= 80:
        return f"[green]{score:.1f}%[/green]"
    elif score >= 60:
        return f"[yellow]{score:.1f}%[/yellow]"
    else:
        return f"[red]{score:.1f}%[/red]"


def _report_to_dict(report, include_claims: bool = False) -> dict:
    """Convert a FaithfulnessReport to a dictionary."""
    result = {
        "persona_id": report.persona_id,
        "persona_name": report.persona_name,
        "total_claims": report.total_claims,
        "supported_count": report.supported_count,
        "unsupported_count": report.unsupported_count,
        "faithfulness_score": report.faithfulness_score,
        "hallucination_ratio": report.hallucination_ratio,
        "details": report.details,
        "unsupported_claims": [
            {
                "text": c.text,
                "type": c.claim_type.value,
                "source_field": c.source_field,
            }
            for c in report.unsupported_claims
        ],
    }

    if include_claims:
        result["all_claims"] = [
            {
                "text": c.text,
                "type": c.claim_type.value,
                "source_field": c.source_field,
            }
            for c in report.claims
        ]

    return result


def _load_personas(path: Path) -> list[Persona]:
    """Load personas from a file or directory."""
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

    return []
