"""
Template management CLI commands.

Commands for listing, creating, and managing custom prompt templates.
"""

from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

from persona.ui.console import get_console

template_app = typer.Typer(
    name="template",
    help="Manage custom prompt templates.",
    no_args_is_help=True,
)


@template_app.command("list")
def list_templates(
    source: Annotated[
        Optional[str],
        typer.Option(
            "--source", "-s",
            help="Filter by source (builtin, user, project).",
        ),
    ] = None,
    tag: Annotated[
        Optional[str],
        typer.Option(
            "--tag", "-t",
            help="Filter by tag.",
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
    List available templates.

    Example:
        persona template list
        persona template list --source builtin
        persona template list --tag healthcare
    """
    import json

    from persona.core.config import TemplateLoader

    console = get_console()
    loader = TemplateLoader()

    if json_output:
        result = {
            "command": "template list",
            "success": True,
            "data": {
                "templates": [],
            },
        }

        for template_id in loader.list_templates(source=source, tag=tag):
            try:
                info = loader.get_info(template_id)
                result["data"]["templates"].append({
                    "id": info.id,
                    "name": info.metadata.name,
                    "source": info.source,
                    "description": info.metadata.description,
                    "tags": info.metadata.tags,
                    "variables": info.variables,
                })
            except Exception as e:
                result["data"]["templates"].append({
                    "id": template_id,
                    "error": str(e),
                })

        print(json.dumps(result, indent=2))
        return

    # Rich output
    console.print(Panel.fit(
        "[bold]Available Templates[/bold]",
        border_style="cyan",
    ))

    templates = loader.list_templates(source=source, tag=tag)

    if not templates:
        console.print("\n[dim]No templates found.[/dim]")
        if not source:
            console.print("[dim]Run 'persona template create' to create one.[/dim]")
        return

    # Group by source
    by_source: dict[str, list] = {"builtin": [], "user": [], "project": []}

    for template_id in templates:
        try:
            info = loader.get_info(template_id)
            by_source[info.source].append(info)
        except Exception:
            continue

    for source_name, source_templates in by_source.items():
        if not source_templates:
            continue

        source_label = {
            "builtin": "Built-in Templates",
            "user": "User Templates (~/.persona/templates/)",
            "project": "Project Templates (.persona/templates/)",
        }.get(source_name, source_name)

        console.print(f"\n[bold]{source_label}:[/bold]")

        for info in source_templates:
            tags_str = ", ".join(info.metadata.tags) if info.metadata.tags else ""
            console.print(f"  • {info.id}")
            console.print(f"    [dim]{info.metadata.name}[/dim]")
            if info.metadata.description:
                console.print(f"    [dim]{info.metadata.description[:60]}...[/dim]" if len(info.metadata.description) > 60 else f"    [dim]{info.metadata.description}[/dim]")
            if tags_str:
                console.print(f"    [cyan]Tags: {tags_str}[/cyan]")


@template_app.command("show")
def show_template(
    template_id: Annotated[
        str,
        typer.Argument(help="Template ID to show."),
    ],
    content: Annotated[
        bool,
        typer.Option(
            "--content", "-c",
            help="Show full template content.",
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
    Show details for a template.

    Example:
        persona template show default
        persona template show healthcare --content
    """
    import json

    from persona.core.config import TemplateLoader

    console = get_console()
    loader = TemplateLoader()

    try:
        info = loader.get_info(template_id)
        template_content = loader.load(template_id) if content or json_output else None
    except FileNotFoundError as e:
        if json_output:
            print(json.dumps({"error": str(e)}, indent=2))
        else:
            console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

    if json_output:
        result = {
            "command": "template show",
            "success": True,
            "data": {
                "id": info.id,
                "path": str(info.path),
                "source": info.source,
                "metadata": {
                    "name": info.metadata.name,
                    "description": info.metadata.description,
                    "author": info.metadata.author,
                    "version": info.metadata.version,
                    "extends": info.metadata.extends,
                    "tags": info.metadata.tags,
                },
                "variables": info.variables,
                "content": template_content,
            },
        }
        print(json.dumps(result, indent=2))
        return

    # Rich output
    console.print(Panel.fit(
        f"[bold]{info.metadata.name}[/bold] ({info.id})",
        border_style="cyan",
    ))

    table = Table(show_header=False, box=None)
    table.add_column("Property", style="bold")
    table.add_column("Value")

    table.add_row("ID", info.id)
    table.add_row("Name", info.metadata.name)
    table.add_row("Source", info.source)
    table.add_row("Path", str(info.path))
    if info.metadata.description:
        table.add_row("Description", info.metadata.description)
    if info.metadata.author:
        table.add_row("Author", info.metadata.author)
    table.add_row("Version", info.metadata.version)
    if info.metadata.extends:
        table.add_row("Extends", info.metadata.extends)
    if info.metadata.tags:
        table.add_row("Tags", ", ".join(info.metadata.tags))

    console.print(table)

    # Variables
    console.print("\n[bold]Variables:[/bold]")
    if info.variables:
        for var in sorted(info.variables):
            console.print(f"  • {var}")
    else:
        console.print("  [dim]No variables[/dim]")

    # Content
    if content:
        console.print("\n[bold]Content:[/bold]")
        syntax = Syntax(loader.load(template_id), "jinja2", theme="monokai", line_numbers=True)
        console.print(syntax)


@template_app.command("create")
def create_template(
    template_id: Annotated[
        str,
        typer.Argument(help="Unique template ID."),
    ],
    name: Annotated[
        str,
        typer.Option("--name", "-n", help="Human-readable name."),
    ],
    description: Annotated[
        str,
        typer.Option("--description", "-d", help="Template description."),
    ] = "",
    based_on: Annotated[
        Optional[str],
        typer.Option("--based-on", "-b", help="Base template to copy from."),
    ] = None,
    tags: Annotated[
        Optional[str],
        typer.Option("--tags", "-t", help="Comma-separated tags."),
    ] = None,
    project_level: Annotated[
        bool,
        typer.Option("--project", help="Save to project directory."),
    ] = False,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Overwrite existing template."),
    ] = False,
) -> None:
    """
    Create a new custom template.

    Example:
        persona template create my-template --name "My Template"
        persona template create healthcare-v2 --based-on healthcare --name "Healthcare v2"
    """
    from persona.core.config import TemplateLoader

    console = get_console()
    loader = TemplateLoader()

    # Check if exists
    if loader.exists(template_id) and not force:
        console.print(f"[red]Error:[/red] Template '{template_id}' already exists.")
        console.print("Use --force to overwrite.")
        raise typer.Exit(1)

    # Prepare tags list
    tag_list = [t.strip() for t in tags.split(",")] if tags else []

    # Create content
    if based_on:
        try:
            base_content = loader.load(based_on)
            # Replace metadata
            content = _create_template_content(
                name=name,
                description=description,
                tags=tag_list,
                body=_extract_body(base_content),
            )
        except FileNotFoundError:
            console.print(f"[red]Error:[/red] Base template '{based_on}' not found.")
            raise typer.Exit(1)
    else:
        # Create minimal template
        content = _create_template_content(
            name=name,
            description=description,
            tags=tag_list,
            body=_default_template_body(),
        )

    # Save
    try:
        path = loader.save(
            template_id,
            content,
            user_level=not project_level,
            overwrite=force,
        )
        console.print(f"[green]✓[/green] Template '{template_id}' created.")
        console.print(f"  Saved to: {path}")
    except Exception as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@template_app.command("test")
def test_template(
    template_id: Annotated[
        str,
        typer.Argument(help="Template ID to test."),
    ],
    count: Annotated[
        int,
        typer.Option("--count", "-n", help="Number of personas (test variable)."),
    ] = 3,
    complexity: Annotated[
        str,
        typer.Option("--complexity", help="Complexity level (test variable)."),
    ] = "moderate",
    detail_level: Annotated[
        str,
        typer.Option("--detail-level", help="Detail level (test variable)."),
    ] = "standard",
) -> None:
    """
    Test a template with sample variables.

    Example:
        persona template test default
        persona template test healthcare --count 5
    """
    from persona.core.config import TemplateLoader

    console = get_console()
    loader = TemplateLoader()

    # Test variables
    test_vars = {
        "count": count,
        "complexity": complexity,
        "detail_level": detail_level,
        "data": "[Sample research data would appear here]",
        "include_reasoning": True,
    }

    console.print(f"[bold]Testing template:[/bold] {template_id}")
    console.print(f"[bold]Variables:[/bold] {test_vars}")
    console.print()

    # Validate
    is_valid, errors = loader.validate_template(template_id, **test_vars)

    if not is_valid:
        console.print("[red]✗ Template validation failed[/red]")
        for error in errors:
            console.print(f"  • {error}")
        raise typer.Exit(1)

    console.print("[green]✓ Template validation passed[/green]")

    # Show required variables
    try:
        required_vars = loader.get_variables(template_id)
        console.print(f"\n[bold]Required variables:[/bold]")
        for var in sorted(required_vars):
            status = "[green]✓[/green]" if var in test_vars else "[yellow]○[/yellow]"
            console.print(f"  {status} {var}")

        # Show preview
        console.print("\n[bold]Rendered preview (first 500 chars):[/bold]")
        from jinja2 import Environment, BaseLoader
        content = loader.load(template_id)
        env = Environment(loader=BaseLoader())
        template = env.from_string(content)
        rendered = template.render(**test_vars)
        preview = rendered[:500] + "..." if len(rendered) > 500 else rendered
        console.print(f"[dim]{preview}[/dim]")

    except Exception as e:
        console.print(f"[red]Error during test:[/red] {e}")
        raise typer.Exit(1)


@template_app.command("export")
def export_template(
    template_id: Annotated[
        str,
        typer.Argument(help="Template ID to export."),
    ],
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output file path."),
    ],
) -> None:
    """
    Export a template to a file.

    Example:
        persona template export healthcare --output ./my-healthcare.j2
    """
    from persona.core.config import TemplateLoader

    console = get_console()
    loader = TemplateLoader()

    try:
        path = loader.export_template(template_id, output)
        console.print(f"[green]✓[/green] Template exported to: {path}")
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


@template_app.command("import")
def import_template(
    source: Annotated[
        Path,
        typer.Argument(help="Source file to import."),
    ],
    template_id: Annotated[
        Optional[str],
        typer.Option("--id", help="Custom template ID (uses filename if not provided)."),
    ] = None,
    project_level: Annotated[
        bool,
        typer.Option("--project", help="Save to project directory."),
    ] = False,
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Overwrite existing template."),
    ] = False,
) -> None:
    """
    Import a template from a file.

    Example:
        persona template import ./my-template.j2
        persona template import ./template.j2 --id custom-name
    """
    from persona.core.config import TemplateLoader

    console = get_console()
    loader = TemplateLoader()

    try:
        imported_id = loader.import_template(
            source,
            template_id=template_id,
            user_level=not project_level,
            overwrite=force,
        )
        console.print(f"[green]✓[/green] Template imported as: {imported_id}")
    except FileNotFoundError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    except FileExistsError as e:
        console.print(f"[red]Error:[/red] {e}")
        console.print("Use --force to overwrite.")
        raise typer.Exit(1)


@template_app.command("remove")
def remove_template(
    template_id: Annotated[
        str,
        typer.Argument(help="Template ID to remove."),
    ],
    force: Annotated[
        bool,
        typer.Option("--force", "-f", help="Skip confirmation."),
    ] = False,
) -> None:
    """
    Remove a custom template.

    Example:
        persona template remove my-template
    """
    from persona.core.config import TemplateLoader

    console = get_console()
    loader = TemplateLoader()

    if not loader.exists(template_id):
        console.print(f"[red]Error:[/red] Template '{template_id}' not found.")
        raise typer.Exit(1)

    try:
        info = loader.get_info(template_id)
        if info.source == "builtin":
            console.print(f"[red]Error:[/red] Cannot remove built-in template.")
            raise typer.Exit(1)
    except FileNotFoundError:
        console.print(f"[red]Error:[/red] Template '{template_id}' not found.")
        raise typer.Exit(1)

    if not force:
        confirm = typer.confirm(f"Remove template '{template_id}'?")
        if not confirm:
            console.print("Cancelled.")
            raise typer.Exit(0)

    if loader.delete(template_id):
        console.print(f"[green]✓[/green] Template '{template_id}' removed.")
    else:
        console.print(f"[red]Error:[/red] Failed to remove template.")
        raise typer.Exit(1)


def _create_template_content(
    name: str,
    description: str,
    tags: list[str],
    body: str,
) -> str:
    """Create template content with front matter."""
    import yaml

    front_matter = {
        "name": name,
        "description": description,
        "tags": tags,
        "version": "1.0.0",
    }

    yaml_content = yaml.safe_dump(front_matter, default_flow_style=False)
    return f"{{# ---\n{yaml_content}--- #}}\n{body}"


def _extract_body(content: str) -> str:
    """Extract body from template content (after front matter)."""
    lines = content.split("\n")

    # Find end of front matter
    if lines[0].strip() != "{# ---":
        return content

    end_idx = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == "--- #}":
            end_idx = i
            break

    if end_idx is None:
        return content

    return "\n".join(lines[end_idx + 1:])


def _default_template_body() -> str:
    """Return default template body for new templates."""
    return """
You are an expert UX researcher specialising in persona development.

Analyse the following user research data and generate {{ count }} distinct user personas.

## Research Data

{{ data }}

## Requirements

Generate {{ count }} personas that:
1. Are distinct from each other
2. Are grounded in evidence from the research data
3. Include realistic details

## Output Format

Respond with valid JSON.
"""
