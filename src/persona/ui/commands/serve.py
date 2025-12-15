"""
API server command.

This module provides the 'persona serve' command to start the REST API server.
"""

from typing import Annotated, Optional

import typer

from persona.ui.console import get_console

serve_app = typer.Typer(
    name="serve",
    help="Start the Persona REST API server.",
    no_args_is_help=True,
)


@serve_app.callback(invoke_without_command=True)
def serve(
    ctx: typer.Context,
    host: Annotated[
        str,
        typer.Option(
            "--host",
            "-h",
            help="Server host (default: 127.0.0.1)",
        ),
    ] = "127.0.0.1",
    port: Annotated[
        int,
        typer.Option(
            "--port",
            "-p",
            help="Server port (default: 8000)",
        ),
    ] = 8000,
    workers: Annotated[
        int,
        typer.Option(
            "--workers",
            "-w",
            help="Number of worker processes (default: 1)",
        ),
    ] = 1,
    reload: Annotated[
        bool,
        typer.Option(
            "--reload",
            help="Enable auto-reload for development",
        ),
    ] = False,
    auth_token: Annotated[
        Optional[str],
        typer.Option(
            "--auth-token",
            help="API authentication token (enables auth if provided)",
            envvar="PERSONA_API_AUTH_TOKEN",
        ),
    ] = None,
    log_level: Annotated[
        str,
        typer.Option(
            "--log-level",
            help="Logging level (debug, info, warning, error)",
        ),
    ] = "info",
) -> None:
    """
    Start the Persona REST API server.

    This command starts a FastAPI server that provides HTTP access to
    Persona's functionality.

    Example:
        persona serve --port 8000
        persona serve --host 0.0.0.0 --port 8080 --workers 4
        persona serve --auth-token secret123 --reload
    """
    console = get_console()

    try:
        import uvicorn
    except ImportError:
        console.print(
            "[red]Error:[/red] FastAPI and uvicorn not installed. "
            "Install with: pip install persona[api]"
        )
        raise typer.Exit(1)

    # Set environment variables for API config
    import os

    os.environ["PERSONA_API_HOST"] = host
    os.environ["PERSONA_API_PORT"] = str(port)
    os.environ["PERSONA_API_WORKERS"] = str(workers)

    if auth_token:
        os.environ["PERSONA_API_AUTH_ENABLED"] = "true"
        os.environ["PERSONA_API_AUTH_TOKEN"] = auth_token

    # Display startup info
    console.print("[bold]Persona API Server[/bold]")
    console.print(f"  Host: {host}")
    console.print(f"  Port: {port}")
    console.print(f"  Workers: {workers}")

    if auth_token:
        console.print("  [yellow]Authentication: Enabled[/yellow]")
    else:
        console.print("  [dim]Authentication: Disabled[/dim]")

    if reload:
        console.print("  [cyan]Auto-reload: Enabled (development mode)[/cyan]")

    console.print()
    console.print(f"  Docs: http://{host}:{port}/docs")
    console.print(f"  ReDoc: http://{host}:{port}/redoc")
    console.print(f"  Health: http://{host}:{port}/api/v1/health")
    console.print()
    console.print("[dim]Press CTRL+C to stop the server[/dim]")
    console.print()

    # Start server
    uvicorn.run(
        "persona.api.app:app",
        host=host,
        port=port,
        workers=workers if not reload else 1,  # reload mode requires workers=1
        reload=reload,
        log_level=log_level,
    )
