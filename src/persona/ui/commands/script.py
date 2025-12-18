"""
Script generation commands for creating conversation scripts from personas.
"""

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.panel import Panel

from persona.core.generation.parser import Persona
from persona.core.scripts import (
    ConversationScriptGenerator,
    PrivacyConfig,
    ScriptFormat,
)
from persona.ui.console import get_console

script_app = typer.Typer(
    name="script",
    help="Generate conversation scripts from personas.",
)


@script_app.command("generate")
def generate(
    persona_path: Annotated[
        Path,
        typer.Argument(
            help="Path to persona JSON file.",
            exists=True,
        ),
    ],
    output: Annotated[
        Optional[Path],
        typer.Option(
            "--output",
            "-o",
            help="Output file path (defaults to stdout).",
        ),
    ] = None,
    format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Output format: character_card, system_prompt, jinja2_template.",
        ),
    ] = "character_card",
    yaml: Annotated[
        bool,
        typer.Option(
            "--yaml",
            help="Use YAML format for character_card output.",
        ),
    ] = False,
    strict: Annotated[
        bool,
        typer.Option(
            "--strict",
            help="Block output if privacy audit fails (default: true).",
        ),
    ] = True,
    threshold: Annotated[
        float,
        typer.Option(
            "--threshold",
            help="Privacy leakage threshold (0.0-1.0, default: 0.1).",
        ),
    ] = 0.1,
) -> None:
    """
    Generate a conversation script from a persona.

    Example:
        persona script generate ./persona.json
        persona script generate ./persona.json --format system_prompt -o script.txt
        persona script generate ./persona.json --format jinja2_template
    """
    console = get_console()

    from persona import __version__

    console.print(f"[dim]Persona {__version__}[/dim]\n")

    # Load persona
    console.print(f"[bold]Loading persona from:[/bold] {persona_path}")
    try:
        with open(persona_path) as f:
            persona_data = json.load(f)

        # Handle both single persona and list
        if isinstance(persona_data, list):
            if len(persona_data) == 0:
                console.print("[red]Error:[/red] No personas found in file.")
                raise typer.Exit(1)
            elif len(persona_data) > 1:
                console.print(
                    "[yellow]Warning:[/yellow] Multiple personas found, using first one."
                )
            persona_dict = persona_data[0]
        else:
            persona_dict = persona_data

        # Create Persona object
        persona = Persona(
            id=persona_dict.get("id", "unknown"),
            name=persona_dict.get("name", "Unknown"),
            demographics=persona_dict.get("demographics"),
            goals=persona_dict.get("goals", []),
            pain_points=persona_dict.get("pain_points", []),
            behaviours=persona_dict.get("behaviours", []),
            quotes=persona_dict.get("quotes", []),
            additional=persona_dict.get("additional", {}),
        )

        console.print(f"[green]✓[/green] Loaded persona: {persona.name}")
    except Exception as e:
        console.print(f"[red]Error loading persona:[/red] {e}")
        raise typer.Exit(1)

    # Parse format
    try:
        if format == "character_card":
            script_format = ScriptFormat.CHARACTER_CARD
        elif format == "system_prompt":
            script_format = ScriptFormat.SYSTEM_PROMPT
        elif format == "jinja2_template":
            script_format = ScriptFormat.JINJA2_TEMPLATE
        else:
            console.print(f"[red]Error:[/red] Unknown format: {format}")
            console.print(
                "Valid formats: character_card, system_prompt, jinja2_template"
            )
            raise typer.Exit(1)
    except ValueError as e:
        console.print(f"[red]Error:[/red] Invalid format: {e}")
        raise typer.Exit(1)

    # Configure privacy
    privacy_config = PrivacyConfig(
        max_leakage_score=threshold,
    )

    # Generate script
    console.print("\n[bold]Generating conversation script...[/bold]")
    console.print(f"Format: {format}")
    console.print(f"Privacy threshold: {threshold}")
    console.print()

    generator = ConversationScriptGenerator(
        privacy_config=privacy_config,
        block_on_failure=strict,
    )

    try:
        result = generator.generate(persona, format=script_format)
    except Exception as e:
        console.print(f"[red]Error generating script:[/red] {e}")
        raise typer.Exit(1)

    # Check if blocked
    if result.blocked:
        console.print("[red]✗ Script generation blocked by privacy audit[/red]")
        console.print(f"\n[yellow]Details:[/yellow] {result.error}")
        console.print("\nThe script contains potential source data leakage.")
        console.print(
            "This is a safety measure to prevent exposing original quotes/data."
        )
        raise typer.Exit(1)

    # Show privacy audit results
    audit = result.privacy_audit
    if audit.leakage_score > 0:
        status = "⚠️" if audit.leakage_score < threshold else "✗"
        console.print(
            f"[yellow]{status} Privacy audit:[/yellow] Leakage score: {audit.leakage_score:.3f}"
        )
        if audit.leakages:
            console.print(f"  Detected {len(audit.leakages)} potential leakage(s)")
    else:
        console.print("[green]✓ Privacy audit:[/green] No leakage detected")

    # Format output
    if script_format == ScriptFormat.CHARACTER_CARD:
        if yaml:
            from persona.core.scripts.formatters import CharacterCardFormatter

            formatter = CharacterCardFormatter(use_yaml=True)
            output_text = formatter.format(result.character_card)
        else:
            output_text = result.output
    else:
        output_text = result.output

    # Write or display output
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(output_text)
        console.print(f"\n[green]✓[/green] Script saved to: {output}")
    else:
        console.print("\n[bold]Generated Script:[/bold]\n")
        console.print(Panel(output_text, border_style="cyan"))


@script_app.command("batch")
def batch_generate(
    input_dir: Annotated[
        Path,
        typer.Argument(
            help="Directory containing persona JSON files.",
            exists=True,
        ),
    ],
    output_dir: Annotated[
        Path,
        typer.Option(
            "--output",
            "-o",
            help="Output directory for scripts.",
        ),
    ] = Path("./scripts"),
    format: Annotated[
        str,
        typer.Option(
            "--format",
            "-f",
            help="Output format: character_card, system_prompt, jinja2_template.",
        ),
    ] = "character_card",
    yaml: Annotated[
        bool,
        typer.Option(
            "--yaml",
            help="Use YAML format for character_card output.",
        ),
    ] = False,
    strict: Annotated[
        bool,
        typer.Option(
            "--strict",
            help="Block output if privacy audit fails (default: true).",
        ),
    ] = True,
    threshold: Annotated[
        float,
        typer.Option(
            "--threshold",
            help="Privacy leakage threshold (0.0-1.0, default: 0.1).",
        ),
    ] = 0.1,
) -> None:
    """
    Generate conversation scripts for multiple personas.

    Example:
        persona script batch ./outputs/exp-001 --output ./scripts
        persona script batch ./outputs --format system_prompt
    """
    console = get_console()

    from persona import __version__

    console.print(f"[dim]Persona {__version__}[/dim]\n")

    # Find persona files
    if input_dir.is_file():
        persona_files = [input_dir]
    else:
        persona_files = list(input_dir.glob("**/*.json"))

    if not persona_files:
        console.print(f"[red]Error:[/red] No JSON files found in {input_dir}")
        raise typer.Exit(1)

    console.print(f"[bold]Found {len(persona_files)} persona file(s)[/bold]")
    console.print(f"Output directory: {output_dir}")
    console.print(f"Format: {format}\n")

    # Parse format
    try:
        if format == "character_card":
            script_format = ScriptFormat.CHARACTER_CARD
        elif format == "system_prompt":
            script_format = ScriptFormat.SYSTEM_PROMPT
        elif format == "jinja2_template":
            script_format = ScriptFormat.JINJA2_TEMPLATE
        else:
            console.print(f"[red]Error:[/red] Unknown format: {format}")
            raise typer.Exit(1)
    except ValueError as e:
        console.print(f"[red]Error:[/red] Invalid format: {e}")
        raise typer.Exit(1)

    # Configure privacy
    privacy_config = PrivacyConfig(
        max_leakage_score=threshold,
    )

    generator = ConversationScriptGenerator(
        privacy_config=privacy_config,
        block_on_failure=strict,
    )

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Process each persona
    success_count = 0
    blocked_count = 0
    error_count = 0

    for persona_file in persona_files:
        try:
            # Load persona
            with open(persona_file) as f:
                persona_data = json.load(f)

            # Handle both single persona and list
            if isinstance(persona_data, list):
                personas_to_process = persona_data
            else:
                personas_to_process = [persona_data]

            for persona_dict in personas_to_process:
                persona = Persona(
                    id=persona_dict.get("id", "unknown"),
                    name=persona_dict.get("name", "Unknown"),
                    demographics=persona_dict.get("demographics"),
                    goals=persona_dict.get("goals", []),
                    pain_points=persona_dict.get("pain_points", []),
                    behaviours=persona_dict.get("behaviours", []),
                    quotes=persona_dict.get("quotes", []),
                    additional=persona_dict.get("additional", {}),
                )

                # Generate script
                result = generator.generate(persona, format=script_format)

                if result.blocked:
                    console.print(
                        f"[yellow]⚠️[/yellow] {persona.name}: Blocked by privacy audit"
                    )
                    blocked_count += 1
                    continue

                # Format output
                if script_format == ScriptFormat.CHARACTER_CARD:
                    if yaml:
                        from persona.core.scripts.formatters import (
                            CharacterCardFormatter,
                        )

                        formatter = CharacterCardFormatter(use_yaml=True)
                        output_text = formatter.format(result.character_card)
                        extension = ".yaml"
                    else:
                        output_text = result.output
                        extension = ".json"
                elif script_format == ScriptFormat.SYSTEM_PROMPT:
                    output_text = result.output
                    extension = ".txt"
                else:  # JINJA2_TEMPLATE
                    output_text = result.output
                    extension = ".j2"

                # Save output
                output_file = output_dir / f"{persona.id}{extension}"
                output_file.write_text(output_text)

                console.print(f"[green]✓[/green] {persona.name} → {output_file.name}")
                success_count += 1

        except Exception as e:
            console.print(f"[red]✗[/red] {persona_file.name}: {e}")
            error_count += 1

    # Summary
    console.print("\n[bold]Summary:[/bold]")
    console.print(f"  Success: {success_count}")
    if blocked_count > 0:
        console.print(f"  Blocked: {blocked_count} (privacy audit)")
    if error_count > 0:
        console.print(f"  Errors:  {error_count}")

    if success_count > 0:
        console.print(f"\n[green]✓[/green] Scripts saved to: {output_dir}")
