"""
Fidelity scoring command for personas.

Evaluates how well personas adhere to prompt constraints and requirements.
"""

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.panel import Panel
from rich.table import Table

from persona.core.generation.parser import Persona
from persona.core.quality.fidelity import (
    ConstraintParser,
    FidelityConfig,
    FidelityScorer,
    PromptConstraints,
    Severity,
)
from persona.ui.console import get_console

fidelity_app = typer.Typer(
    name="fidelity",
    help="Check prompt fidelity for generated personas.",
)


@fidelity_app.callback(invoke_without_command=True)
def check_fidelity(
    ctx: typer.Context,
    persona_path: Annotated[
        Path,
        typer.Argument(
            help="Path to persona JSON file.",
            exists=True,
        ),
    ],
    constraints: Annotated[
        Optional[Path],
        typer.Option(
            "--constraints",
            help="Path to YAML constraints file.",
        ),
    ] = None,
    require_fields: Annotated[
        Optional[str],
        typer.Option(
            "--require-fields",
            help="Comma-separated list of required fields.",
        ),
    ] = None,
    age_range: Annotated[
        Optional[str],
        typer.Option(
            "--age-range",
            help="Age range constraint (e.g., '25-45').",
        ),
    ] = None,
    goal_count: Annotated[
        Optional[str],
        typer.Option(
            "--goal-count",
            help="Goal count range (e.g., '3-5').",
        ),
    ] = None,
    output_format: Annotated[
        str,
        typer.Option(
            "--output",
            "-o",
            help="Output format: rich, json, markdown.",
        ),
    ] = "rich",
    report: Annotated[
        Optional[Path],
        typer.Option(
            "--report",
            help="Save markdown report to file.",
        ),
    ] = None,
    no_llm_judge: Annotated[
        bool,
        typer.Option(
            "--no-llm-judge",
            help="Disable LLM-based style checking.",
        ),
    ] = False,
    strict: Annotated[
        bool,
        typer.Option(
            "--strict",
            help="Fail on any violation (even low severity).",
        ),
    ] = False,
) -> None:
    """
    Check prompt fidelity for a persona.

    Validates that the generated persona adheres to constraints specified
    in the original prompt, including structural requirements, content
    keywords, numeric limits, and style requirements.

    Examples:
        # Check with YAML constraints file
        persona fidelity persona.json --constraints constraints.yaml

        # Quick check with inline constraints
        persona fidelity persona.json --require-fields name,age,goals --age-range 25-45

        # Generate markdown report
        persona fidelity persona.json --constraints tech.yaml --report report.md

        # Strict mode (fail on any violation)
        persona fidelity persona.json --constraints tech.yaml --strict
    """
    if ctx.invoked_subcommand is not None:
        return

    console = get_console()

    # Load persona
    try:
        persona = _load_persona(persona_path)
    except Exception as e:
        console.print(f"[red]Error loading persona:[/red] {e}")
        raise typer.Exit(1)

    # Load or build constraints
    try:
        if constraints:
            parser = ConstraintParser()
            prompt_constraints = parser.parse_file(constraints)
        else:
            prompt_constraints = _build_inline_constraints(
                require_fields, age_range, goal_count
            )
    except Exception as e:
        console.print(f"[red]Error loading constraints:[/red] {e}")
        raise typer.Exit(1)

    # Configure fidelity scorer
    config = FidelityConfig(use_llm_judge=not no_llm_judge)
    scorer = FidelityScorer(config)

    # Run fidelity check
    console.print("[cyan]Running fidelity checks...[/cyan]")
    fidelity_report = scorer.score(persona, prompt_constraints)

    # Display results
    if output_format == "json":
        print(json.dumps(fidelity_report.to_dict(), indent=2))
    elif output_format == "markdown":
        markdown_output = _format_markdown_report(fidelity_report)
        console.print(markdown_output)
        if report:
            report.write_text(markdown_output)
            console.print(f"\n[green]Report saved to:[/green] {report}")
    else:  # rich
        _display_rich_report(console, fidelity_report)

    # Save markdown report if requested
    if report and output_format != "markdown":
        markdown_output = _format_markdown_report(fidelity_report)
        report.write_text(markdown_output)
        console.print(f"\n[green]Report saved to:[/green] {report}")

    # Exit with error if checks failed
    if strict and fidelity_report.violation_count > 0:
        console.print("\n[red]Fidelity check failed (strict mode)[/red]")
        raise typer.Exit(1)

    if not fidelity_report.passed:
        console.print("\n[yellow]Fidelity check failed[/yellow]")
        raise typer.Exit(1)


def _load_persona(path: Path) -> Persona:
    """Load persona from JSON file."""
    with path.open("r") as f:
        data = json.load(f)

    # Handle both single persona and list
    if isinstance(data, list):
        if not data:
            raise ValueError("Empty persona list")
        data = data[0]

    return Persona.from_dict(data)


def _build_inline_constraints(
    require_fields: str | None,
    age_range: str | None,
    goal_count: str | None,
) -> PromptConstraints:
    """Build constraints from CLI arguments."""
    constraints = PromptConstraints()

    if require_fields:
        constraints.required_fields = [f.strip() for f in require_fields.split(",")]

    if age_range:
        parts = age_range.split("-")
        if len(parts) != 2:
            raise ValueError("Age range must be in format 'min-max' (e.g., '25-45')")
        constraints.age_range = (int(parts[0]), int(parts[1]))

    if goal_count:
        parts = goal_count.split("-")
        if len(parts) != 2:
            raise ValueError("Goal count must be in format 'min-max' (e.g., '3-5')")
        constraints.goal_count = (int(parts[0]), int(parts[1]))

    return constraints


def _display_rich_report(console, report) -> None:
    """Display fidelity report in rich format."""
    # Header
    status_color = "green" if report.passed else "red"
    status_text = "PASSED" if report.passed else "FAILED"

    console.print(
        Panel(
            f"[bold]Fidelity Report: {report.persona_name}[/bold]\n"
            f"Status: [{status_color}]{status_text}[/{status_color}]\n"
            f"Overall Score: {report.overall_score:.1%}",
            title="Prompt Fidelity Assessment",
            border_style="cyan",
        )
    )

    # Dimension scores table
    console.print("\n[bold]Dimension Scores[/bold]")
    table = Table(show_header=True)
    table.add_column("Dimension", style="cyan")
    table.add_column("Score", justify="right")
    table.add_column("Status", justify="center")

    dimensions = [
        ("Structure", report.structure_score),
        ("Content", report.content_score),
        ("Constraint", report.constraint_score),
        ("Style", report.style_score),
    ]

    for dim_name, score in dimensions:
        score_pct = f"{score:.1%}"
        status = "✓" if score >= 0.6 else "✗"
        status_color = "green" if score >= 0.6 else "red"

        table.add_row(
            dim_name,
            score_pct,
            f"[{status_color}]{status}[/{status_color}]",
        )

    console.print(table)

    # Violations
    if report.violations:
        console.print(f"\n[bold]Violations ({len(report.violations)})[/bold]")

        # Group by severity
        critical = [v for v in report.violations if v.severity == Severity.CRITICAL]
        high = [v for v in report.violations if v.severity == Severity.HIGH]
        medium = [v for v in report.violations if v.severity == Severity.MEDIUM]
        low = [v for v in report.violations if v.severity == Severity.LOW]

        for severity_name, violations, color in [
            ("Critical", critical, "red"),
            ("High", high, "yellow"),
            ("Medium", medium, "blue"),
            ("Low", low, "dim"),
        ]:
            if violations:
                console.print(
                    f"\n[{color}]{severity_name} ({len(violations)})[/{color}]"
                )
                for v in violations:
                    field_info = f" ({v.field})" if v.field else ""
                    console.print(f"  • {v.description}{field_info}")
                    if v.expected and v.actual:
                        console.print(f"    Expected: {v.expected}")
                        console.print(f"    Actual: {v.actual}")
    else:
        console.print("\n[green]No violations found[/green]")


def _format_markdown_report(report) -> str:
    """Format fidelity report as markdown."""
    status_badge = "✅ PASSED" if report.passed else "❌ FAILED"

    md = f"""# Fidelity Report: {report.persona_name}

**Status**: {status_badge}
**Overall Score**: {report.overall_score:.1%}
**Generated**: {report.generated_at}

---

## Dimension Scores

| Dimension | Score | Status |
|-----------|-------|--------|
| Structure | {report.structure_score:.1%} | {"✓" if report.structure_score >= 0.6 else "✗"} |
| Content | {report.content_score:.1%} | {"✓" if report.content_score >= 0.6 else "✗"} |
| Constraint | {report.constraint_score:.1%} | {"✓" if report.constraint_score >= 0.6 else "✗"} |
| Style | {report.style_score:.1%} | {"✓" if report.style_score >= 0.6 else "✗"} |

---

## Violations

"""

    if not report.violations:
        md += "*No violations found*\n"
    else:
        # Group by severity
        critical = [v for v in report.violations if v.severity == Severity.CRITICAL]
        high = [v for v in report.violations if v.severity == Severity.HIGH]
        medium = [v for v in report.violations if v.severity == Severity.MEDIUM]
        low = [v for v in report.violations if v.severity == Severity.LOW]

        for severity_name, violations, icon in [
            ("Critical", critical, "🔴"),
            ("High", high, "🟡"),
            ("Medium", medium, "🔵"),
            ("Low", low, "⚪"),
        ]:
            if violations:
                md += f"\n### {icon} {severity_name} ({len(violations)})\n\n"
                for v in violations:
                    field_info = f" (`{v.field}`)" if v.field else ""
                    md += f"- **{v.description}**{field_info}\n"
                    if v.expected and v.actual:
                        md += f"  - Expected: `{v.expected}`\n"
                        md += f"  - Actual: `{v.actual}`\n"

    md += f"""
---

## Summary

- **Total Violations**: {report.violation_count}
- **Critical**: {len([v for v in report.violations if v.severity == Severity.CRITICAL])}
- **High**: {len([v for v in report.violations if v.severity == Severity.HIGH])}
- **Medium**: {len([v for v in report.violations if v.severity == Severity.MEDIUM])}
- **Low**: {len([v for v in report.violations if v.severity == Severity.LOW])}
"""

    return md
