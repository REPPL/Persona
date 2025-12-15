"""
Bias and stereotype detection command for personas.

Provides comprehensive bias detection using lexicon-based,
embedding-based (WEAT), and LLM-based methods.
"""

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.panel import Panel
from rich.table import Table

from persona.core.generation.parser import Persona
from persona.ui.console import get_console

bias_app = typer.Typer(
    name="bias",
    help="Detect bias and stereotypes in personas.",
)


@bias_app.command("check")
def check_bias(
    persona_path: Annotated[
        Path,
        typer.Argument(
            help="Path to persona JSON file or output directory.",
            exists=True,
        ),
    ],
    categories: Annotated[
        str,
        typer.Option(
            "--categories", "-c",
            help="Comma-separated bias categories to check (gender,racial,age,professional).",
        ),
    ] = "gender,racial,age,professional",
    methods: Annotated[
        str,
        typer.Option(
            "--methods", "-m",
            help="Detection methods to use (lexicon,embedding,llm,all).",
        ),
    ] = "lexicon",
    threshold: Annotated[
        float,
        typer.Option(
            "--threshold", "-t",
            help="Confidence threshold for reporting findings (0-1).",
        ),
    ] = 0.3,
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
    max_score: Annotated[
        Optional[float],
        typer.Option(
            "--max-score",
            help="Exit with error if bias score exceeds threshold (0-1).",
        ),
    ] = None,
    llm_provider: Annotated[
        str,
        typer.Option(
            "--llm-provider",
            help="LLM provider for judge-based detection (anthropic, openai, ollama).",
        ),
    ] = "ollama",
    llm_model: Annotated[
        Optional[str],
        typer.Option(
            "--llm-model",
            help="Specific LLM model for judge-based detection.",
        ),
    ] = None,
) -> None:
    """
    Check personas for bias and stereotypes.

    Uses multiple detection methods to identify potential biases:
    - Lexicon: Pattern matching against HolisticBias vocabulary
    - Embedding: WEAT (Word Embedding Association Test) analysis
    - LLM: Judge model for subtle bias detection

    Example:
        persona bias check ./personas.json
        persona bias check ./output/ --methods lexicon,embedding
        persona bias check ./personas.json --methods llm --max-score 0.5
    """
    console = get_console()

    from persona import __version__
    from persona.core.providers import ProviderFactory
    from persona.core.quality.bias import BiasConfig, BiasDetector

    # Parse categories
    category_list = [c.strip() for c in categories.split(",")]

    # Parse methods
    if methods.lower() == "all":
        method_list = ["lexicon", "embedding", "llm"]
    else:
        method_list = [m.strip() for m in methods.split(",")]

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
            print(
                json.dumps(
                    {"success": False, "error": "No personas found"}, indent=2
                )
            )
        else:
            console.print("[yellow]No personas found to check.[/yellow]")
        raise typer.Exit(1)

    # Create LLM provider if needed
    llm_provider_instance = None
    if "llm" in method_list:
        try:
            llm_provider_instance = ProviderFactory.create(llm_provider)
            if llm_model:
                llm_provider_instance.model = llm_model
        except Exception as e:
            if output_format == "json":
                print(
                    json.dumps(
                        {
                            "success": False,
                            "error": f"Failed to create LLM provider: {e}",
                        },
                        indent=2,
                    )
                )
            else:
                console.print(f"[red]Error creating LLM provider:[/red] {e}")
            raise typer.Exit(1)

    # Create bias detector
    try:
        config = BiasConfig(
            methods=method_list, categories=category_list, threshold=threshold
        )
        detector = BiasDetector(config, llm_provider_instance)
    except Exception as e:
        if output_format == "json":
            print(
                json.dumps(
                    {"success": False, "error": f"Failed to initialise detector: {e}"},
                    indent=2,
                )
            )
        else:
            console.print(f"[red]Error initialising detector:[/red] {e}")
        raise typer.Exit(1)

    # Run detection
    if output_format == "rich" and not console._quiet:
        console.print(f"[dim]Persona {__version__}[/dim]\n")
        console.print(
            f"[dim]Checking {len(personas)} persona(s) for bias using: {', '.join(method_list)}...[/dim]\n"
        )

    try:
        reports = [detector.analyse(persona) for persona in personas]
    except Exception as e:
        if output_format == "json":
            print(json.dumps({"success": False, "error": str(e)}, indent=2))
        else:
            console.print(f"[red]Detection error:[/red] {e}")
        raise typer.Exit(1)

    # Calculate summary statistics
    total_findings = sum(len(r.findings) for r in reports)
    avg_bias_score = (
        sum(r.overall_score for r in reports) / len(reports) if reports else 0
    )
    personas_with_bias = sum(1 for r in reports if r.has_bias)

    # Output results
    if output_format == "json":
        output = {
            "command": "bias check",
            "version": __version__,
            "success": True,
            "data": {
                "persona_count": len(reports),
                "summary": {
                    "total_findings": total_findings,
                    "average_bias_score": round(avg_bias_score, 3),
                    "personas_with_bias": personas_with_bias,
                    "methods_used": method_list,
                    "categories_checked": category_list,
                    "threshold": threshold,
                },
                "reports": [r.to_dict() for r in reports],
            },
        }
        output_text = json.dumps(output, indent=2)
        print(output_text)
        if save_to:
            save_to.write_text(output_text)
    elif output_format == "markdown":
        report = _generate_markdown_report(reports, method_list, category_list)
        print(report)
        if save_to:
            save_to.write_text(report)
    else:
        _display_rich_output(console, reports, method_list, category_list)
        if save_to:
            save_to.write_text(
                json.dumps(
                    {
                        "summary": {
                            "total_findings": total_findings,
                            "average_bias_score": round(avg_bias_score, 3),
                            "personas_with_bias": personas_with_bias,
                        },
                        "reports": [r.to_dict() for r in reports],
                    },
                    indent=2,
                )
            )

    # Check maximum score threshold
    if max_score is not None:
        failing = [r for r in reports if r.overall_score > max_score]
        if failing:
            if output_format != "json":
                console.print(
                    f"\n[red]Error:[/red] {len(failing)} persona(s) "
                    f"exceed maximum bias score of {max_score}"
                )
            raise typer.Exit(1)


@bias_app.command("report")
def generate_report(
    persona_path: Annotated[
        Path,
        typer.Argument(
            help="Path to persona JSON file or output directory.",
            exists=True,
        ),
    ],
    output_file: Annotated[
        Path,
        typer.Option(
            "--output", "-o",
            help="Output file path for detailed report.",
        ),
    ],
    format: Annotated[
        str,
        typer.Option(
            "--format", "-f",
            help="Report format: markdown, json.",
        ),
    ] = "markdown",
    methods: Annotated[
        str,
        typer.Option(
            "--methods", "-m",
            help="Detection methods to use (lexicon,embedding,llm,all).",
        ),
    ] = "all",
    categories: Annotated[
        str,
        typer.Option(
            "--categories", "-c",
            help="Comma-separated bias categories to check.",
        ),
    ] = "gender,racial,age,professional",
    llm_provider: Annotated[
        str,
        typer.Option(
            "--llm-provider",
            help="LLM provider for judge-based detection.",
        ),
    ] = "ollama",
) -> None:
    """
    Generate detailed bias analysis report.

    Creates a comprehensive report with all findings, evidence,
    and recommendations for bias mitigation.

    Example:
        persona bias report ./personas.json --output report.md
        persona bias report ./output/ -o analysis.json --format json
    """
    console = get_console()

    # Reuse check_bias logic but always save to file
    try:
        check_bias(
            persona_path=persona_path,
            categories=categories,
            methods=methods,
            threshold=0.3,
            output_format=format,
            save_to=output_file,
            max_score=None,
            llm_provider=llm_provider,
            llm_model=None,
        )
        console.print(f"\n[green]Report saved to:[/green] {output_file}")
    except typer.Exit:
        raise
    except Exception as e:
        console.print(f"[red]Error generating report:[/red] {e}")
        raise typer.Exit(1)


def _display_rich_output(
    console, reports, methods_used: list[str], categories_checked: list[str]
) -> None:
    """Display results with Rich formatting."""
    console.print(
        Panel.fit(
            "[bold]Bias Detection Report[/bold]",
            border_style="yellow",
        )
    )

    # Summary statistics
    total_findings = sum(len(r.findings) for r in reports)
    avg_bias_score = (
        sum(r.overall_score for r in reports) / len(reports) if reports else 0
    )
    personas_with_bias = sum(1 for r in reports if r.has_bias)

    summary = Table(show_header=False, box=None)
    summary.add_column("Metric", style="cyan")
    summary.add_column("Value")
    summary.add_row("Personas checked", str(len(reports)))
    summary.add_row("Total findings", str(total_findings))
    summary.add_row(
        "Personas with bias",
        f"[yellow]{personas_with_bias}[/yellow]" if personas_with_bias > 0 else "0",
    )
    summary.add_row("Average bias score", _colour_bias_score(avg_bias_score))
    summary.add_row("Methods used", ", ".join(methods_used))
    summary.add_row("Categories checked", ", ".join(categories_checked))

    console.print(summary)
    console.print()

    # Individual results table
    results_table = Table(title="Detection Results")
    results_table.add_column("Persona", style="cyan")
    results_table.add_column("Findings", justify="right")
    results_table.add_column("High", justify="right")
    results_table.add_column("Medium", justify="right")
    results_table.add_column("Low", justify="right")
    results_table.add_column("Bias Score", justify="right")
    results_table.add_column("Status")

    for report in reports:
        name = report.persona_name or report.persona_id[:20]

        if report.overall_score <= 0.3:
            status = "[green]✓ Clean[/green]"
        elif report.overall_score <= 0.6:
            status = "[yellow]⚠ Review[/yellow]"
        else:
            status = "[red]✗ Biased[/red]"

        results_table.add_row(
            name,
            str(len(report.findings)),
            f"[red]{report.high_severity_count}[/red]"
            if report.high_severity_count > 0
            else "0",
            f"[yellow]{report.medium_severity_count}[/yellow]"
            if report.medium_severity_count > 0
            else "0",
            str(report.low_severity_count),
            _colour_bias_score(report.overall_score),
            status,
        )

    console.print(results_table)

    # Show bias findings details
    reports_with_bias = [r for r in reports if r.has_bias]
    if reports_with_bias:
        console.print("\n[bold]Detected Biases:[/bold]")

        for report in reports_with_bias:
            name = report.persona_name or report.persona_id
            console.print(f"\n[cyan]{name}[/cyan] ({len(report.findings)} findings):")

            # Show by severity
            for severity_name in ["high", "medium", "low"]:
                from persona.core.quality.bias.models import Severity

                severity = getattr(Severity, severity_name.upper())
                severity_findings = report.get_findings_by_severity(severity)

                if severity_findings:
                    severity_colour = {
                        "high": "red",
                        "medium": "yellow",
                        "low": "dim",
                    }[severity_name]

                    for finding in severity_findings[:3]:  # Limit to 3 per severity
                        console.print(
                            f"  [{severity_colour}]•[/{severity_colour}] "
                            f"[{finding.category.value}] {finding.description}"
                        )
                        console.print(
                            f"    [dim]Evidence: {finding.evidence[:80]}...[/dim]"
                        )

            if len(report.findings) > 9:
                console.print(
                    f"  [dim]... and {len(report.findings) - 9} more findings[/dim]"
                )


def _generate_markdown_report(
    reports, methods_used: list[str], categories_checked: list[str]
) -> str:
    """Generate a Markdown report."""
    total_findings = sum(len(r.findings) for r in reports)
    avg_bias_score = (
        sum(r.overall_score for r in reports) / len(reports) if reports else 0
    )
    personas_with_bias = sum(1 for r in reports if r.has_bias)

    lines = [
        "# Bias Detection Report",
        "",
        "## Summary",
        "",
        f"- **Personas checked:** {len(reports)}",
        f"- **Total findings:** {total_findings}",
        f"- **Personas with bias:** {personas_with_bias}",
        f"- **Average bias score:** {avg_bias_score:.3f}",
        f"- **Methods used:** {', '.join(methods_used)}",
        f"- **Categories checked:** {', '.join(categories_checked)}",
        "",
        "## Results by Persona",
        "",
        "| Persona | Findings | High | Medium | Low | Bias Score | Status |",
        "|---------|----------|------|--------|-----|------------|--------|",
    ]

    for report in reports:
        name = report.persona_name or report.persona_id[:20]
        if report.overall_score <= 0.3:
            status = "✓ Clean"
        elif report.overall_score <= 0.6:
            status = "⚠ Review"
        else:
            status = "✗ Biased"

        lines.append(
            f"| {name} | {len(report.findings)} | {report.high_severity_count} | "
            f"{report.medium_severity_count} | {report.low_severity_count} | "
            f"{report.overall_score:.3f} | {status} |"
        )

    reports_with_bias = [r for r in reports if r.has_bias]
    if reports_with_bias:
        lines.extend(
            [
                "",
                "## Detected Biases",
                "",
            ]
        )

        for report in reports_with_bias:
            name = report.persona_name or report.persona_id
            lines.append(f"### {name}")
            lines.append("")
            lines.append(
                f"**Overall bias score:** {report.overall_score:.3f} "
                f"({len(report.findings)} findings)"
            )
            lines.append("")

            for finding in report.findings:
                lines.append(
                    f"- **[{finding.severity.value.upper()}] "
                    f"[{finding.category.value}]** {finding.description}"
                )
                lines.append(f"  - Evidence: {finding.evidence}")
                lines.append(f"  - Method: {finding.method}")
                lines.append(f"  - Confidence: {finding.confidence:.2f}")
                lines.append("")

    return "\n".join(lines)


def _colour_bias_score(score: float) -> str:
    """Return bias score with appropriate colour markup."""
    if score <= 0.3:
        return f"[green]{score:.3f}[/green]"
    elif score <= 0.6:
        return f"[yellow]{score:.3f}[/yellow]"
    else:
        return f"[red]{score:.3f}[/red]"


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
