"""
Command-line interface for Persona.

This module provides the main CLI entry point using Typer.
"""

import typer
from rich.console import Console

app = typer.Typer(
    name="persona",
    help="Generate realistic user personas from your data using AI.",
    no_args_is_help=True,
)

console = Console()


@app.command()
def version() -> None:
    """Show Persona version."""
    from persona import __version__
    console.print(f"Persona version {__version__}")


@app.command()
def check() -> None:
    """Check Persona installation and configuration."""
    from persona import __version__

    console.print("[bold]Persona Health Check[/bold]\n")
    console.print(f"[green]\u2713[/green] Version: {__version__}")
    console.print(f"[green]\u2713[/green] Installation: OK")
    console.print("\n[bold]Provider Status:[/bold]")

    import os
    providers = [
        ("ANTHROPIC_API_KEY", "Anthropic"),
        ("OPENAI_API_KEY", "OpenAI"),
        ("GOOGLE_API_KEY", "Google"),
    ]

    for env_var, name in providers:
        if os.getenv(env_var):
            console.print(f"  [green]\u2713[/green] {name}: Configured")
        else:
            console.print(f"  [yellow]\u25cb[/yellow] {name}: Not configured")


if __name__ == "__main__":
    app()
