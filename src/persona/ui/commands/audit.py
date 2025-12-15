"""
Audit trail CLI commands (F-123).

Commands for querying, exporting, and managing audit records.
"""

from datetime import datetime
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from persona.core.audit import AuditConfig, AuditTrail

app = typer.Typer(
    name="audit",
    help="View and manage generation audit trail (F-123).",
    no_args_is_help=True,
)

console = Console()


@app.command("list")
def list_records(
    provider: Annotated[
        Optional[str],
        typer.Option("--provider", "-p", help="Filter by provider."),
    ] = None,
    model: Annotated[
        Optional[str],
        typer.Option("--model", "-m", help="Filter by model."),
    ] = None,
    start_date: Annotated[
        Optional[str],
        typer.Option("--start", "-s", help="Filter records after date (ISO format)."),
    ] = None,
    end_date: Annotated[
        Optional[str],
        typer.Option("--end", "-e", help="Filter records before date (ISO format)."),
    ] = None,
    limit: Annotated[
        Optional[int],
        typer.Option("--limit", "-n", help="Maximum number of records to show."),
    ] = 20,
) -> None:
    """
    List audit records.

    Example:
        persona audit list
        persona audit list --provider anthropic --limit 10
        persona audit list --start 2025-01-01
    """
    config = AuditConfig()
    trail = AuditTrail(config)

    # Parse dates
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None

    records = trail.query(
        start_date=start_dt,
        end_date=end_dt,
        provider=provider,
        model=model,
        limit=limit,
    )

    if not records:
        console.print("[yellow]No audit records found.[/yellow]")
        return

    # Create table
    table = Table(title=f"Audit Records ({len(records)} shown)")
    table.add_column("Audit ID", style="cyan", no_wrap=True)
    table.add_column("Timestamp")
    table.add_column("Provider")
    table.add_column("Model")
    table.add_column("Personas")
    table.add_column("Time (ms)")

    for record in records:
        table.add_row(
            record.audit_id[:8] + "...",
            record.timestamp.strftime("%Y-%m-%d %H:%M"),
            record.generation.provider,
            record.generation.model[:20],
            str(record.output.persona_count),
            str(record.output.generation_time_ms),
        )

    console.print(table)
    console.print(
        f"\n[dim]Total records in database: {trail.count()}[/dim]"
    )


@app.command("show")
def show_record(
    audit_id: Annotated[
        str,
        typer.Argument(help="Audit record ID to display."),
    ],
    json_output: Annotated[
        bool,
        typer.Option("--json", help="Output as JSON."),
    ] = False,
) -> None:
    """
    Show detailed audit record.

    Example:
        persona audit show abc123
        persona audit show abc123 --json
    """
    config = AuditConfig()
    trail = AuditTrail(config)

    record = trail.get(audit_id)

    if not record:
        console.print(f"[red]Error:[/red] Record not found: {audit_id}")
        raise typer.Exit(1)

    if json_output:
        import json
        print(json.dumps(json.loads(record.model_dump_json()), indent=2))
        return

    # Rich output
    console.print(Panel.fit(
        f"[bold]Audit Record[/bold]\n{record.audit_id}",
        border_style="cyan",
    ))

    console.print("\n[bold]Session Information:[/bold]")
    console.print(f"  Timestamp: {record.timestamp.isoformat()}")
    console.print(f"  Tool Version: {record.tool_version}")
    console.print(f"  User: {record.session.user}")
    console.print(f"  Platform: {record.session.platform}")
    console.print(f"  Python: {record.session.python_version}")

    console.print("\n[bold]Input Data:[/bold]")
    console.print(f"  Data Hash: {record.input.data_hash[:32]}...")
    if record.input.data_path:
        console.print(f"  Data Path: {record.input.data_path}")
    console.print(f"  Record Count: {record.input.record_count}")
    if record.input.format:
        console.print(f"  Format: {record.input.format}")

    console.print("\n[bold]Generation:[/bold]")
    console.print(f"  Provider: {record.generation.provider}")
    console.print(f"  Model: {record.generation.model}")
    console.print(f"  Prompt Hash: {record.generation.prompt_hash[:32]}...")
    if record.generation.workflow:
        console.print(f"  Workflow: {record.generation.workflow}")
    if record.generation.template:
        console.print(f"  Template: {record.generation.template}")
    if record.generation.parameters:
        console.print(f"  Parameters: {record.generation.parameters}")

    console.print("\n[bold]Output:[/bold]")
    console.print(f"  Personas Hash: {record.output.personas_hash[:32]}...")
    console.print(f"  Persona Count: {record.output.persona_count}")
    console.print(f"  Generation Time: {record.output.generation_time_ms} ms")
    if record.output.output_path:
        console.print(f"  Output Path: {record.output.output_path}")
    if record.output.tokens_used:
        console.print(f"  Tokens Used: {record.output.tokens_used}")

    if record.signature:
        console.print("\n[bold]Signature:[/bold]")
        console.print(f"  HMAC-SHA256: {record.signature[:32]}...")


@app.command("export")
def export_records(
    format: Annotated[
        str,
        typer.Option("--format", "-f", help="Export format (json, csv, jsonl)."),
    ] = "json",
    output: Annotated[
        Optional[Path],
        typer.Option("--output", "-o", help="Output file path."),
    ] = None,
    provider: Annotated[
        Optional[str],
        typer.Option("--provider", "-p", help="Filter by provider."),
    ] = None,
    model: Annotated[
        Optional[str],
        typer.Option("--model", "-m", help="Filter by model."),
    ] = None,
    start_date: Annotated[
        Optional[str],
        typer.Option("--start", "-s", help="Filter records after date (ISO format)."),
    ] = None,
    end_date: Annotated[
        Optional[str],
        typer.Option("--end", "-e", help="Filter records before date (ISO format)."),
    ] = None,
) -> None:
    """
    Export audit records.

    Example:
        persona audit export --format json --output audit.json
        persona audit export --format csv --provider anthropic
    """
    config = AuditConfig()
    trail = AuditTrail(config)

    # Parse dates
    start_dt = datetime.fromisoformat(start_date) if start_date else None
    end_dt = datetime.fromisoformat(end_date) if end_date else None

    # Export
    result = trail.export(
        format=format,
        output_path=output,
        start_date=start_dt,
        end_date=end_dt,
        provider=provider,
        model=model,
    )

    if output:
        console.print(f"[green]Exported to:[/green] {output}")
    else:
        # Print to stdout
        print(result)


@app.command("verify")
def verify_record(
    audit_id: Annotated[
        str,
        typer.Argument(help="Audit record ID to verify."),
    ],
) -> None:
    """
    Verify audit record signature.

    Example:
        persona audit verify abc123
    """
    config = AuditConfig()
    trail = AuditTrail(config)

    record = trail.get(audit_id)

    if not record:
        console.print(f"[red]Error:[/red] Record not found: {audit_id}")
        raise typer.Exit(1)

    if not record.signature:
        console.print("[yellow]Warning:[/yellow] Record is not signed.")
        return

    is_valid, error = trail.verify(audit_id)

    if is_valid:
        console.print(f"[green]✓[/green] Signature valid for record: {audit_id}")
    else:
        console.print(f"[red]✗[/red] Signature verification failed: {error}")
        raise typer.Exit(1)


@app.command("prune")
def prune_records(
    retention_days: Annotated[
        Optional[int],
        typer.Option("--days", "-d", help="Retention period in days (default: 180)."),
    ] = None,
    confirm: Annotated[
        bool,
        typer.Option("--yes", "-y", help="Skip confirmation prompt."),
    ] = False,
) -> None:
    """
    Delete old audit records.

    Example:
        persona audit prune
        persona audit prune --days 90
    """
    config = AuditConfig()
    trail = AuditTrail(config)

    days = retention_days or config.retention_days

    if not confirm:
        response = typer.confirm(
            f"Delete audit records older than {days} days?",
            default=False,
        )
        if not response:
            console.print("[yellow]Cancelled.[/yellow]")
            return

    deleted_count = trail.prune(days)

    console.print(
        f"[green]✓[/green] Deleted {deleted_count} record(s) older than {days} days."
    )


@app.command("config")
def show_config() -> None:
    """
    Show audit trail configuration.

    Example:
        persona audit config
    """
    config = AuditConfig()

    console.print(Panel.fit(
        "[bold]Audit Trail Configuration[/bold]",
        border_style="cyan",
    ))

    console.print(f"\n[bold]Status:[/bold] {'Enabled' if config.enabled else 'Disabled'}")
    console.print(f"[bold]Storage:[/bold] {config.store_type}")
    console.print(f"[bold]Path:[/bold] {config.get_store_path()}")
    console.print(f"[bold]Retention:[/bold] {config.retention_days} days")
    console.print(
        f"[bold]Signing:[/bold] {'Enabled' if config.sign_records else 'Disabled'}"
    )

    trail = AuditTrail(config)
    count = trail.count()
    console.print(f"\n[bold]Total Records:[/bold] {count}")
