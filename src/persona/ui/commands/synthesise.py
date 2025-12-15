"""
Synthesise command for privacy-preserving synthetic data generation.
"""

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.panel import Panel
from rich.table import Table

from persona.ui.console import get_console

synthesise_app = typer.Typer(
    name="synthesise",
    help="Generate privacy-preserving synthetic data from sensitive sources.",
)


@synthesise_app.callback(invoke_without_command=True)
def synthesise(
    ctx: typer.Context,
    input_path: Annotated[
        Optional[Path],
        typer.Option(
            "--input",
            "-i",
            help="Path to sensitive data file (CSV, JSON, YAML).",
            exists=True,
        ),
    ] = None,
    output_path: Annotated[
        Optional[Path],
        typer.Option(
            "--output",
            "-o",
            help="Path to save synthetic data (default: <input>_synthetic.<ext>).",
        ),
    ] = None,
    count: Annotated[
        int,
        typer.Option(
            "--count",
            "-n",
            help="Number of synthetic records to generate.",
        ),
    ] = 100,
    provider: Annotated[
        str,
        typer.Option(
            "--provider",
            "-p",
            help="LLM provider (ollama, anthropic, openai, gemini).",
        ),
    ] = "ollama",
    model: Annotated[
        Optional[str],
        typer.Option(
            "--model",
            "-m",
            help="Specific model to use (default: provider default).",
        ),
    ] = None,
    temperature: Annotated[
        float,
        typer.Option(
            "--temperature",
            "-t",
            help="Generation temperature (0.0-1.0).",
        ),
    ] = 0.7,
    batch_size: Annotated[
        int,
        typer.Option(
            "--batch-size",
            help="Records per API call.",
        ),
    ] = 10,
    no_validate: Annotated[
        bool,
        typer.Option(
            "--no-validate",
            help="Skip quality validation after generation.",
        ),
    ] = False,
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output results as JSON.",
        ),
    ] = False,
) -> None:
    """
    Generate synthetic data from sensitive sources.

    Creates privacy-safe synthetic data that preserves statistical properties
    while removing all PII using local LLM generation.

    Example:
        persona synthesise --input interviews.csv --output synthetic.csv
        persona synthesise -i data.json -n 100 --model qwen2.5:72b
    """
    # If subcommand invoked, don't run main logic
    if ctx.invoked_subcommand is not None:
        return

    # Main command requires input
    if input_path is None:
        console = get_console()
        console.print(
            "[red]Error:[/red] --input is required\n\n"
            "Usage: persona synthesise --input FILE --output FILE\n\n"
            "Try: persona synthesise --help"
        )
        raise typer.Exit(1)

    from persona import __version__
    from persona.core.synthetic import SyntheticPipeline

    console = get_console()

    if not json_output:
        console.print(f"[dim]Persona {__version__}[/dim]\n")
        console.print("[bold]Synthetic Data Generation[/bold]")
        console.print(f"[dim]Input:[/dim] {input_path}")

    # Determine output path
    if output_path is None:
        stem = input_path.stem
        suffix = input_path.suffix
        output_path = input_path.parent / f"{stem}_synthetic{suffix}"

    if not json_output:
        console.print(f"[dim]Output:[/dim] {output_path}")
        console.print()
        console.print(f"[dim]Generating {count} synthetic records...[/dim]")

    # Create pipeline
    try:
        pipeline = SyntheticPipeline(provider=provider, model=model)
    except Exception as e:
        console.print(f"[red]Error creating pipeline:[/red] {e}")
        raise typer.Exit(1)

    # Generate synthetic data
    try:
        result = pipeline.synthesise(
            input_path=input_path,
            output_path=output_path,
            count=count,
            preserve_schema=True,
            preserve_distribution=True,
            batch_size=batch_size,
            temperature=temperature,
            validate=not no_validate,
        )
    except Exception as e:
        console.print(f"[red]Error generating synthetic data:[/red] {e}")
        raise typer.Exit(1)

    if json_output:
        # JSON output
        output = {
            "command": "synthesise",
            "version": __version__,
            "success": True,
            "data": {
                "input_path": str(result.input_path),
                "output_path": str(result.output_path),
                "row_count": result.row_count,
                "model": result.model,
                "provider": result.provider,
                "generation_time": result.generation_time,
            },
        }

        if result.validation:
            output["data"]["validation"] = {
                "passed": result.validation.passed,
                "quality_score": result.validation.quality_score,
                "schema_match": result.validation.schema_match,
                "distribution_similarity": result.validation.distribution_similarity,
                "pii_detected": result.validation.pii_detected,
            }

        print(json.dumps(output, indent=2))
        return

    # Rich output
    console.print()
    console.print("[green]✓[/green] Generation complete!")
    console.print()

    # Summary table
    table = Table(title="Generation Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")

    table.add_row("Records generated", str(result.row_count))
    table.add_row("Model", result.model)
    table.add_row("Provider", result.provider)
    table.add_row("Generation time", f"{result.generation_time:.2f}s")
    table.add_row("Output file", str(result.output_path))

    console.print(table)

    # Validation results
    if result.validation:
        console.print()
        console.print("[bold]Validation Results:[/bold]")

        val = result.validation

        # Quality score
        quality_color = "green" if val.quality_score >= 0.85 else "yellow" if val.quality_score >= 0.70 else "red"
        console.print(
            f"[bold]Quality Score:[/bold] [{quality_color}]{val.quality_score:.2%}[/{quality_color}]"
        )

        # Metrics
        console.print(f"  Schema match: {'✓' if val.schema_match else '✗'} ({val.schema_match_score:.2%})")
        console.print(f"  Distribution similarity: {val.distribution_similarity:.2%}")
        console.print(f"  PII detected: {'✗ YES' if val.pii_detected else '✓ NO'}")

        if val.pii_detected:
            console.print(f"    [red]Warning: {val.pii_entity_count} PII entities found![/red]")
            console.print(f"    Types: {', '.join(val.pii_entity_types)}")

        if val.diversity_score:
            console.print(f"  Diversity: {val.diversity_score:.2%}")

        # Issues
        if val.issues:
            console.print()
            console.print("[yellow]Issues:[/yellow]")
            for issue in val.issues:
                console.print(f"  • {issue}")

        # Final status
        console.print()
        if val.passed:
            console.print("[green]✓ Validation passed![/green]")
        else:
            console.print("[yellow]⚠ Validation failed - review issues above[/yellow]")


@synthesise_app.command("validate")
def validate(
    original_path: Annotated[
        Path,
        typer.Option(
            "--original",
            help="Path to original data file.",
            exists=True,
        ),
    ],
    synthetic_path: Annotated[
        Path,
        typer.Option(
            "--synthetic",
            help="Path to synthetic data file.",
            exists=True,
        ),
    ],
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output results as JSON.",
        ),
    ] = False,
) -> None:
    """
    Validate synthetic data quality against original.

    Checks schema match, distribution similarity, PII presence,
    and other quality metrics.

    Example:
        persona synthesise validate --original interviews.csv --synthetic synthetic.csv
    """
    from persona import __version__
    from persona.core.synthetic import SyntheticValidator

    console = get_console()

    if not json_output:
        console.print(f"[dim]Persona {__version__}[/dim]\n")
        console.print("[bold]Validating Synthetic Data[/bold]")
        console.print(f"[dim]Original:[/dim] {original_path}")
        console.print(f"[dim]Synthetic:[/dim] {synthetic_path}")
        console.print()

    # Validate
    try:
        validator = SyntheticValidator()
        result = validator.validate(
            original_path=original_path,
            synthetic_path=synthetic_path,
        )
    except Exception as e:
        console.print(f"[red]Error validating:[/red] {e}")
        raise typer.Exit(1)

    if json_output:
        # JSON output
        output = {
            "command": "synthesise_validate",
            "version": __version__,
            "success": True,
            "data": {
                "passed": result.passed,
                "quality_score": result.quality_score,
                "schema_match": result.schema_match,
                "schema_match_score": result.schema_match_score,
                "distribution_similarity": result.distribution_similarity,
                "pii_detected": result.pii_detected,
                "pii_entity_count": result.pii_entity_count,
                "pii_entity_types": result.pii_entity_types,
                "diversity_score": result.diversity_score,
                "issues": result.issues,
            },
        }
        print(json.dumps(output, indent=2))
        return

    # Rich output
    quality_color = "green" if result.quality_score >= 0.85 else "yellow" if result.quality_score >= 0.70 else "red"
    console.print(
        f"[bold]Quality Score:[/bold] [{quality_color}]{result.quality_score:.2%}[/{quality_color}]"
    )
    console.print()

    # Metrics table
    table = Table(title="Validation Metrics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")
    table.add_column("Status")

    table.add_row(
        "Schema match",
        f"{result.schema_match_score:.2%}",
        "✓" if result.schema_match else "✗",
    )
    table.add_row(
        "Distribution similarity",
        f"{result.distribution_similarity:.2%}",
        "✓" if result.distribution_similarity >= 0.85 else "✗",
    )
    table.add_row(
        "PII detected",
        f"{result.pii_entity_count} entities",
        "✓" if not result.pii_detected else "✗",
    )

    if result.diversity_score:
        table.add_row(
            "Diversity",
            f"{result.diversity_score:.2%}",
            "✓" if result.diversity_score >= 0.70 else "✗",
        )

    console.print(table)

    # Issues
    if result.issues:
        console.print()
        console.print("[yellow]Issues:[/yellow]")
        for issue in result.issues:
            console.print(f"  • {issue}")

    # Final status
    console.print()
    if result.passed:
        console.print("[green]✓ Validation passed![/green]")
    else:
        console.print("[yellow]⚠ Validation failed[/yellow]")


@synthesise_app.command("preview")
def preview(
    input_path: Annotated[
        Path,
        typer.Option(
            "--input",
            "-i",
            help="Path to data file to preview.",
            exists=True,
        ),
    ],
    count: Annotated[
        int,
        typer.Option(
            "--count",
            "-n",
            help="Number of sample records to show.",
        ),
    ] = 5,
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output results as JSON.",
        ),
    ] = False,
) -> None:
    """
    Preview data schema and distributions (dry run).

    Analyses input data and shows what would be used for
    synthetic generation without actually generating anything.

    Example:
        persona synthesise preview --input interviews.csv
        persona synthesise preview -i data.json --count 3
    """
    from persona import __version__
    from persona.core.synthetic import DataAnalyser

    console = get_console()

    if not json_output:
        console.print(f"[dim]Persona {__version__}[/dim]\n")
        console.print("[bold]Data Preview[/bold]")
        console.print(f"[dim]Input:[/dim] {input_path}")
        console.print()

    # Analyse
    try:
        analyser = DataAnalyser()
        schema = analyser.analyse_file(input_path)
    except Exception as e:
        console.print(f"[red]Error analysing data:[/red] {e}")
        raise typer.Exit(1)

    if json_output:
        # JSON output
        output = {
            "command": "synthesise_preview",
            "version": __version__,
            "success": True,
            "data": {
                "row_count": schema.row_count,
                "column_count": len(schema.columns),
                "format": schema.format,
                "columns": [
                    {
                        "name": col.column_name,
                        "type": col.column_type,
                        "unique_count": col.unique_count,
                        "null_count": col.null_count,
                        "sample_values": col.sample_values[:count],
                    }
                    for col in schema.columns
                ],
            },
        }
        print(json.dumps(output, indent=2))
        return

    # Rich output
    console.print(f"[bold]Rows:[/bold] {schema.row_count}")
    console.print(f"[bold]Columns:[/bold] {len(schema.columns)}")
    console.print(f"[bold]Format:[/bold] {schema.format}")
    console.print()

    # Column details
    for col in schema.columns:
        console.print(f"[cyan]• {col.column_name}[/cyan]")
        console.print(f"  Type: {col.column_type}")
        console.print(f"  Unique: {col.unique_count}")

        if col.null_count > 0:
            console.print(f"  Nulls: {col.null_count}")

        if col.sample_values:
            samples = col.sample_values[:count]
            console.print(f"  Samples: {', '.join(str(v) for v in samples)}")

        if col.categorical_distribution:
            console.print("  Top categories:")
            sorted_dist = sorted(
                col.categorical_distribution.items(),
                key=lambda x: x[1],
                reverse=True,
            )[:3]
            for value, freq in sorted_dist:
                pct = (freq / schema.row_count) * 100
                console.print(f"    - {value}: {pct:.1f}%")

        if col.numeric_stats:
            console.print("  Stats:")
            console.print(f"    Range: {col.numeric_stats['min']:.2f} - {col.numeric_stats['max']:.2f}")
            console.print(f"    Mean: {col.numeric_stats['mean']:.2f} (±{col.numeric_stats['std']:.2f})")

        console.print()
