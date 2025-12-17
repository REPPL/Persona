"""
Variant management CLI commands.

Provides commands for creating, listing, and managing experiment variants
(named parameter sets) using the SQLite experiment store.
"""

import json
from typing import Annotated, Optional

import typer
from rich.panel import Panel
from rich.table import Table

from persona.ui.console import get_console

variant_app = typer.Typer(
    name="variant",
    help="Manage experiment variants (named parameter sets).",
)


def _get_store():
    """Get SQLite experiment store."""
    from persona.core.experiments import SQLiteExperimentStore, get_default_db_path

    return SQLiteExperimentStore(get_default_db_path())


def _resolve_experiment(store, experiment: str) -> str:
    """Resolve experiment name or ID to experiment ID."""
    # Try as ID first
    exp = store.get_experiment(experiment)
    if exp is not None:
        return exp["experiment_id"]

    # Try as name
    exp = store.get_experiment_by_name(experiment)
    if exp is not None:
        return exp["experiment_id"]

    raise typer.BadParameter(f"Experiment not found: {experiment}")


@variant_app.command("create")
def create_variant(
    experiment: Annotated[
        str,
        typer.Argument(help="Experiment name or ID."),
    ],
    name: Annotated[
        str,
        typer.Argument(help="Name for the variant."),
    ],
    params: Annotated[
        Optional[list[str]],
        typer.Option(
            "--param",
            "-p",
            help="Parameter in key=value format. Can be repeated.",
        ),
    ] = None,
    params_json: Annotated[
        Optional[str],
        typer.Option(
            "--json",
            "-j",
            help="Parameters as JSON string.",
        ),
    ] = None,
    description: Annotated[
        Optional[str],
        typer.Option(
            "--description",
            "-d",
            help="Description of the variant.",
        ),
    ] = None,
) -> None:
    """
    Create a variant for an experiment.

    Variants are named parameter sets that allow comparing different
    configurations within the same experiment.

    Examples:
        # Create with individual parameters
        persona variant create my-experiment high-temp --param temperature=0.9

        # Create with multiple parameters
        persona variant create my-experiment creative \\
            --param temperature=0.9 \\
            --param top_p=0.95 \\
            --description "High creativity settings"

        # Create with JSON parameters
        persona variant create my-experiment precise \\
            --json '{"temperature": 0.3, "top_p": 0.8}'
    """
    console = get_console()
    store = _get_store()

    try:
        exp_id = _resolve_experiment(store, experiment)

        # Parse parameters
        parameters: dict = {}

        if params_json:
            try:
                parameters = json.loads(params_json)
            except json.JSONDecodeError as e:
                console.print(f"[red]Error:[/red] Invalid JSON: {e}")
                raise typer.Exit(1)

        if params:
            for param in params:
                if "=" not in param:
                    console.print(
                        f"[red]Error:[/red] Invalid parameter format: {param}"
                    )
                    console.print("Use: --param key=value")
                    raise typer.Exit(1)
                key, value = param.split("=", 1)
                # Try to parse value as JSON (for numbers, booleans)
                try:
                    parameters[key] = json.loads(value)
                except json.JSONDecodeError:
                    parameters[key] = value

        if not parameters:
            console.print("[yellow]Warning:[/yellow] No parameters specified.")
            if not typer.confirm("Create variant with empty parameters?"):
                raise typer.Exit(0)

        var_id = store.create_variant(
            experiment_id=exp_id,
            name=name,
            parameters=parameters,
            description=description or "",
        )

        console.print(f"[green]✓[/green] Created variant: [bold]{name}[/bold]")
        console.print(f"  ID: {var_id}")
        console.print(f"  Parameters: {json.dumps(parameters)}")

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    finally:
        store.close()


@variant_app.command("list")
def list_variants(
    experiment: Annotated[
        str,
        typer.Argument(help="Experiment name or ID."),
    ],
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output as JSON.",
        ),
    ] = False,
) -> None:
    """
    List variants for an experiment.

    Example:
        persona variant list my-experiment
        persona variant list my-experiment --json
    """
    console = get_console()
    store = _get_store()

    try:
        exp_id = _resolve_experiment(store, experiment)
        exp = store.get_experiment(exp_id)
        variants = store.list_variants(exp_id)

        if json_output:
            output = {
                "experiment": exp["name"],
                "variants": variants,
            }
            print(json.dumps(output, indent=2))
            return

        if not variants:
            console.print(f"[yellow]No variants for experiment: {exp['name']}[/yellow]")
            console.print(
                f"Create one with: persona variant create {exp['name']} <name> --param key=value"
            )
            return

        console.print(
            Panel.fit(
                f"[bold]Variants for {exp['name']}[/bold]",
                border_style="cyan",
            )
        )

        table = Table()
        table.add_column("Name", style="cyan")
        table.add_column("Parameters")
        table.add_column("Description")

        for var in variants:
            params_str = json.dumps(var["parameters"], separators=(",", ":"))
            if len(params_str) > 40:
                params_str = params_str[:37] + "..."
            table.add_row(
                var["name"],
                params_str,
                var["description"] or "-",
            )

        console.print(table)

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    finally:
        store.close()


@variant_app.command("show")
def show_variant(
    experiment: Annotated[
        str,
        typer.Argument(help="Experiment name or ID."),
    ],
    name: Annotated[
        str,
        typer.Argument(help="Variant name."),
    ],
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output as JSON.",
        ),
    ] = False,
) -> None:
    """
    Show variant details.

    Example:
        persona variant show my-experiment high-temp
        persona variant show my-experiment high-temp --json
    """
    console = get_console()
    store = _get_store()

    try:
        exp_id = _resolve_experiment(store, experiment)
        variants = store.list_variants(exp_id)

        variant = None
        for v in variants:
            if v["name"] == name:
                variant = v
                break

        if variant is None:
            console.print(f"[red]Error:[/red] Variant not found: {name}")
            raise typer.Exit(1)

        if json_output:
            print(json.dumps(variant, indent=2))
            return

        console.print(
            Panel.fit(
                f"[bold]Variant: {variant['name']}[/bold]",
                border_style="cyan",
            )
        )

        if variant["description"]:
            console.print(f"\n{variant['description']}")

        console.print(f"\n[bold]ID:[/bold] {variant['variant_id']}")
        console.print(f"[bold]Created:[/bold] {variant['created_at']}")

        console.print("\n[bold]Parameters:[/bold]")
        for key, value in variant["parameters"].items():
            console.print(f"  {key}: {json.dumps(value)}")

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    finally:
        store.close()


@variant_app.command("update")
def update_variant(
    experiment: Annotated[
        str,
        typer.Argument(help="Experiment name or ID."),
    ],
    name: Annotated[
        str,
        typer.Argument(help="Variant name."),
    ],
    params: Annotated[
        Optional[list[str]],
        typer.Option(
            "--param",
            "-p",
            help="Parameter to add/update in key=value format.",
        ),
    ] = None,
    remove_params: Annotated[
        Optional[list[str]],
        typer.Option(
            "--remove",
            "-r",
            help="Parameter key to remove.",
        ),
    ] = None,
    description: Annotated[
        Optional[str],
        typer.Option(
            "--description",
            "-d",
            help="Update description.",
        ),
    ] = None,
) -> None:
    """
    Update a variant's parameters or description.

    Examples:
        # Add or update a parameter
        persona variant update my-experiment high-temp --param temperature=0.95

        # Remove a parameter
        persona variant update my-experiment high-temp --remove top_p

        # Update description
        persona variant update my-experiment high-temp -d "Very creative output"
    """
    console = get_console()
    store = _get_store()

    try:
        exp_id = _resolve_experiment(store, experiment)
        variants = store.list_variants(exp_id)

        variant = None
        for v in variants:
            if v["name"] == name:
                variant = v
                break

        if variant is None:
            console.print(f"[red]Error:[/red] Variant not found: {name}")
            raise typer.Exit(1)

        updates: dict = {}

        # Handle parameter updates
        if params or remove_params:
            parameters = dict(variant["parameters"])

            if remove_params:
                for key in remove_params:
                    if key in parameters:
                        del parameters[key]
                        console.print(f"[dim]Removed parameter: {key}[/dim]")

            if params:
                for param in params:
                    if "=" not in param:
                        console.print(
                            f"[red]Error:[/red] Invalid parameter format: {param}"
                        )
                        raise typer.Exit(1)
                    key, value = param.split("=", 1)
                    try:
                        parameters[key] = json.loads(value)
                    except json.JSONDecodeError:
                        parameters[key] = value
                    console.print(f"[dim]Set parameter: {key}={value}[/dim]")

            updates["parameters"] = parameters

        if description is not None:
            updates["description"] = description

        if not updates:
            console.print("[yellow]No updates specified.[/yellow]")
            return

        store.update_variant(variant["variant_id"], **updates)
        console.print(f"[green]✓[/green] Updated variant: {name}")

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    finally:
        store.close()


@variant_app.command("delete")
def delete_variant(
    experiment: Annotated[
        str,
        typer.Argument(help="Experiment name or ID."),
    ],
    name: Annotated[
        str,
        typer.Argument(help="Variant name."),
    ],
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Skip confirmation.",
        ),
    ] = False,
) -> None:
    """
    Delete a variant.

    Example:
        persona variant delete my-experiment high-temp --force
    """
    console = get_console()
    store = _get_store()

    try:
        exp_id = _resolve_experiment(store, experiment)
        variants = store.list_variants(exp_id)

        variant = None
        for v in variants:
            if v["name"] == name:
                variant = v
                break

        if variant is None:
            console.print(f"[red]Error:[/red] Variant not found: {name}")
            raise typer.Exit(1)

        if not force:
            if not typer.confirm(f"Delete variant '{name}'?"):
                console.print("[yellow]Cancelled.[/yellow]")
                raise typer.Exit(0)

        store.delete_variant(variant["variant_id"])
        console.print(f"[green]✓[/green] Deleted variant: {name}")

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    finally:
        store.close()


@variant_app.command("compare")
def compare_variants(
    experiment: Annotated[
        str,
        typer.Argument(help="Experiment name or ID."),
    ],
    variant1: Annotated[
        str,
        typer.Argument(help="First variant name."),
    ],
    variant2: Annotated[
        str,
        typer.Argument(help="Second variant name."),
    ],
    json_output: Annotated[
        bool,
        typer.Option(
            "--json",
            help="Output as JSON.",
        ),
    ] = False,
) -> None:
    """
    Compare parameters between two variants.

    Example:
        persona variant compare my-experiment high-temp low-temp
    """
    console = get_console()
    store = _get_store()

    try:
        exp_id = _resolve_experiment(store, experiment)
        variants = store.list_variants(exp_id)

        var1 = None
        var2 = None
        for v in variants:
            if v["name"] == variant1:
                var1 = v
            if v["name"] == variant2:
                var2 = v

        if var1 is None:
            console.print(f"[red]Error:[/red] Variant not found: {variant1}")
            raise typer.Exit(1)
        if var2 is None:
            console.print(f"[red]Error:[/red] Variant not found: {variant2}")
            raise typer.Exit(1)

        # Compare parameters
        params1 = var1["parameters"]
        params2 = var2["parameters"]
        all_keys = set(params1.keys()) | set(params2.keys())

        differences = {}
        same = {}

        for key in all_keys:
            v1 = params1.get(key)
            v2 = params2.get(key)
            if v1 != v2:
                differences[key] = {variant1: v1, variant2: v2}
            else:
                same[key] = v1

        if json_output:
            output = {
                "variant1": variant1,
                "variant2": variant2,
                "differences": differences,
                "same": same,
            }
            print(json.dumps(output, indent=2))
            return

        console.print(
            Panel.fit(
                f"[bold]Comparing: {variant1} vs {variant2}[/bold]",
                border_style="cyan",
            )
        )

        if differences:
            console.print("\n[bold]Differences:[/bold]")
            table = Table()
            table.add_column("Parameter")
            table.add_column(variant1, style="cyan")
            table.add_column(variant2, style="green")

            for key in sorted(differences.keys()):
                v1 = differences[key].get(variant1)
                v2 = differences[key].get(variant2)
                table.add_row(
                    key,
                    json.dumps(v1) if v1 is not None else "[dim]<not set>[/dim]",
                    json.dumps(v2) if v2 is not None else "[dim]<not set>[/dim]",
                )

            console.print(table)
        else:
            console.print("\n[green]No differences in parameters.[/green]")

        if same:
            console.print(f"\n[bold]Same ({len(same)} parameters):[/bold]")
            for key in sorted(same.keys()):
                console.print(f"  {key}: {json.dumps(same[key])}")

    except ValueError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    finally:
        store.close()
