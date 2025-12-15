"""
Privacy command for PII detection and anonymisation.
"""

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.panel import Panel
from rich.table import Table

from persona.core.data import DataLoader
from persona.ui.console import get_console

privacy_app = typer.Typer(
    name="privacy",
    help="Detect and anonymise PII in data files.",
)


@privacy_app.command("scan")
def scan(
    input_path: Annotated[
        Path,
        typer.Option(
            "--input",
            "-i",
            help="Path to data file or directory to scan.",
            exists=True,
        ),
    ],
    threshold: Annotated[
        float,
        typer.Option(
            "--threshold",
            "-t",
            help="Minimum confidence score for detection (0.0-1.0).",
        ),
    ] = 0.5,
    entities: Annotated[
        Optional[str],
        typer.Option(
            "--entities",
            "-e",
            help="Comma-separated list of entity types to detect (default: all).",
        ),
    ] = None,
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output results as JSON.",
        ),
    ] = False,
) -> None:
    """
    Scan data for PII without modification.

    This command detects PII in your data files and shows what would
    be anonymised, without actually modifying the files.

    Example:
        persona privacy scan --input ./data/interviews.csv
        persona privacy scan -i ./data --threshold 0.7
        persona privacy scan -i data.txt --entities PERSON,EMAIL_ADDRESS
    """
    from persona import __version__

    console = get_console()

    # Check if privacy module is available
    try:
        from persona.core.privacy import PIIDetector
    except ImportError:
        console.print(
            "[red]Error:[/red] Privacy module not installed.\n"
            "Install with: [cyan]pip install persona[privacy][/cyan]\n"
            "Then run: [cyan]python -m spacy download en_core_web_lg[/cyan]"
        )
        raise typer.Exit(1)

    if not json_output:
        console.print(f"[dim]Persona {__version__}[/dim]\n")
        console.print(f"[bold]Scanning:[/bold] {input_path}")

    # Load data
    loader = DataLoader()
    try:
        content, files = loader.load_path(input_path)
    except Exception as e:
        console.print(f"[red]Error loading data:[/red] {e}")
        raise typer.Exit(1)

    # Parse entity types if provided
    entity_list = None
    if entities:
        entity_list = [e.strip().upper() for e in entities.split(",")]

    # Initialise detector
    try:
        detector = PIIDetector(
            score_threshold=threshold,
            entities=entity_list,
        )

        if not detector.is_available():
            error = detector.get_import_error()
            console.print(
                f"[red]Error:[/red] PII detection not available.\n"
                f"Install with: [cyan]pip install persona[privacy][/cyan]\n"
                f"Original error: {error}"
            )
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error initialising detector:[/red] {e}")
        raise typer.Exit(1)

    # Detect PII
    try:
        scan_result = detector.scan_text(content)
    except Exception as e:
        console.print(f"[red]Error detecting PII:[/red] {e}")
        raise typer.Exit(1)

    entities_found = scan_result["entities"]
    entity_types = scan_result["entity_types"]

    if json_output:
        # JSON output
        result = {
            "command": "privacy_scan",
            "version": __version__,
            "success": True,
            "data": {
                "input_path": str(input_path),
                "files_scanned": len(files),
                "entity_count": scan_result["entity_count"],
                "entity_types": entity_types,
                "has_pii": scan_result["has_pii"],
                "entities": [
                    {
                        "type": e.type,
                        "text": e.text,
                        "start": e.start,
                        "end": e.end,
                        "score": e.score,
                    }
                    for e in entities_found
                ],
            },
        }
        print(json.dumps(result, indent=2))
        return

    # Rich output
    console.print()

    if not entities_found:
        console.print("[green]✓[/green] No PII detected!")
        console.print(
            "[dim]Your data appears safe to use without anonymisation.[/dim]"
        )
        return

    # Show summary
    console.print(
        f"[yellow]⚠[/yellow] Found [bold]{len(entities_found)}[/bold] PII entities"
    )
    console.print()

    # Group by type
    by_type: dict[str, list] = {}
    for entity in entities_found:
        if entity.type not in by_type:
            by_type[entity.type] = []
        by_type[entity.type].append(entity)

    # Create table
    table = Table(title="Detected PII")
    table.add_column("Type", style="cyan")
    table.add_column("Count", justify="right")
    table.add_column("Examples", style="yellow")

    for entity_type, entities_of_type in sorted(by_type.items()):
        # Get unique examples (up to 3)
        examples = list({e.text for e in entities_of_type})[:3]
        examples_str = ", ".join(examples)
        if len(entities_of_type) > 3:
            examples_str += ", ..."

        table.add_row(entity_type, str(len(entities_of_type)), examples_str)

    console.print(table)
    console.print()

    # Recommendation
    console.print(
        "[bold]Recommendation:[/bold] Use [cyan]persona privacy anonymise[/cyan] "
        "to create a safe version."
    )
    console.print(
        "Or use [cyan]--anonymise[/cyan] flag with "
        "[cyan]persona generate[/cyan] to anonymise during generation."
    )


@privacy_app.command("anonymise")
def anonymise(
    input_path: Annotated[
        Path,
        typer.Option(
            "--input",
            "-i",
            help="Path to data file or directory to anonymise.",
            exists=True,
        ),
    ],
    output_path: Annotated[
        Optional[Path],
        typer.Option(
            "--output",
            "-o",
            help="Path to save anonymised data (default: <input>_anonymised.<ext>).",
        ),
    ] = None,
    strategy: Annotated[
        str,
        typer.Option(
            "--strategy",
            "-s",
            help="Anonymisation strategy: redact, replace, hash.",
        ),
    ] = "redact",
    threshold: Annotated[
        float,
        typer.Option(
            "--threshold",
            "-t",
            help="Minimum confidence score for detection (0.0-1.0).",
        ),
    ] = 0.5,
    entities: Annotated[
        Optional[str],
        typer.Option(
            "--entities",
            "-e",
            help="Comma-separated list of entity types to anonymise (default: all).",
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Overwrite output file if it exists.",
        ),
    ] = False,
) -> None:
    """
    Anonymise PII in data files.

    Creates anonymised version of your data files, replacing or redacting
    detected PII according to the chosen strategy.

    Strategies:
        redact  - Replace PII with [TYPE] placeholders (default)
        replace - Replace PII with fake but realistic data
        hash    - Replace PII with deterministic hashes

    Example:
        persona privacy anonymise --input sensitive.csv --output safe.csv
        persona privacy anonymise -i data.txt -s replace
        persona privacy anonymise -i ./data --strategy hash --force
    """
    from persona import __version__

    console = get_console()

    # Check if privacy module is available
    try:
        from persona.core.privacy import (
            PIIDetector,
            PIIAnonymiser,
            AnonymisationStrategy,
        )
    except ImportError:
        console.print(
            "[red]Error:[/red] Privacy module not installed.\n"
            "Install with: [cyan]pip install persona[privacy][/cyan]\n"
            "Then run: [cyan]python -m spacy download en_core_web_lg[/cyan]"
        )
        raise typer.Exit(1)

    console.print(f"[dim]Persona {__version__}[/dim]\n")
    console.print(f"[bold]Anonymising:[/bold] {input_path}")

    # Validate strategy
    try:
        anon_strategy = AnonymisationStrategy(strategy.lower())
    except ValueError:
        console.print(
            f"[red]Error:[/red] Invalid strategy '{strategy}'. "
            "Choose from: redact, replace, hash"
        )
        raise typer.Exit(1)

    # Determine output path
    if output_path is None:
        if input_path.is_file():
            stem = input_path.stem
            suffix = input_path.suffix
            output_path = input_path.parent / f"{stem}_anonymised{suffix}"
        else:
            output_path = input_path.parent / f"{input_path.name}_anonymised"

    # Check if output exists
    if output_path.exists() and not force:
        console.print(
            f"[red]Error:[/red] Output path already exists: {output_path}\n"
            "Use --force to overwrite."
        )
        raise typer.Exit(1)

    # Load data
    loader = DataLoader()
    try:
        content, files = loader.load_path(input_path)
    except Exception as e:
        console.print(f"[red]Error loading data:[/red] {e}")
        raise typer.Exit(1)

    # Parse entity types if provided
    entity_list = None
    if entities:
        entity_list = [e.strip().upper() for e in entities.split(",")]

    # Initialise detector and anonymiser
    try:
        detector = PIIDetector(
            score_threshold=threshold,
            entities=entity_list,
        )
        anonymiser = PIIAnonymiser()

        if not detector.is_available():
            error = detector.get_import_error()
            console.print(
                f"[red]Error:[/red] PII detection not available.\n"
                f"Install with: [cyan]pip install persona[privacy][/cyan]\n"
                f"Original error: {error}"
            )
            raise typer.Exit(1)

        if not anonymiser.is_available():
            error = anonymiser.get_import_error()
            console.print(
                f"[red]Error:[/red] PII anonymisation not available.\n"
                f"Install with: [cyan]pip install persona[privacy][/cyan]\n"
                f"Original error: {error}"
            )
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]Error initialising privacy tools:[/red] {e}")
        raise typer.Exit(1)

    # Detect PII
    console.print("[dim]Detecting PII...[/dim]")
    try:
        entities_found = detector.detect(content)
    except Exception as e:
        console.print(f"[red]Error detecting PII:[/red] {e}")
        raise typer.Exit(1)

    if not entities_found:
        console.print("[green]✓[/green] No PII detected!")
        console.print("[dim]No anonymisation needed.[/dim]")
        raise typer.Exit(0)

    console.print(f"[dim]Found {len(entities_found)} PII entities[/dim]")

    # Anonymise
    console.print(f"[dim]Anonymising with strategy: {anon_strategy.value}...[/dim]")
    try:
        result = anonymiser.anonymise(content, entities_found, anon_strategy)
    except Exception as e:
        console.print(f"[red]Error anonymising:[/red] {e}")
        raise typer.Exit(1)

    # Save anonymised data
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(result.text)
    except Exception as e:
        console.print(f"[red]Error saving output:[/red] {e}")
        raise typer.Exit(1)

    # Show summary
    console.print()
    console.print("[green]✓[/green] Anonymisation complete!")
    console.print(f"[bold]Output:[/bold] {output_path}")
    console.print()

    # Statistics
    table = Table(title="Anonymisation Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", justify="right")

    table.add_row("Entities anonymised", str(result.entity_count))
    table.add_row("Entity types", ", ".join(sorted(result.entity_types)))
    table.add_row("Strategy", result.strategy.value)
    table.add_row("Original length", f"{result.original_length:,} chars")
    table.add_row("Anonymised length", f"{result.anonymised_length:,} chars")

    console.print(table)
