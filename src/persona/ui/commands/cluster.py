"""
Cluster command for grouping similar personas.
"""

import json
from pathlib import Path
from typing import Annotated, Optional

import typer
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree

from persona.core.clustering import ClusterMethod, PersonaClusterer
from persona.ui.console import get_console

cluster_app = typer.Typer(
    name="cluster",
    help="Cluster personas to identify similar groups and suggest consolidation.",
)


@cluster_app.callback(invoke_without_command=True)
def cluster(
    ctx: typer.Context,
    persona_path: Annotated[
        Path,
        typer.Argument(
            help="Path to persona JSON file or output directory.",
            exists=True,
        ),
    ],
    method: Annotated[
        str,
        typer.Option(
            "--method",
            "-m",
            help="Clustering method (similarity, hierarchical, kmeans).",
        ),
    ] = "similarity",
    threshold: Annotated[
        float,
        typer.Option(
            "--threshold",
            "-t",
            help="Similarity threshold for clustering (0-1).",
        ),
    ] = 0.6,
    k: Annotated[
        Optional[int],
        typer.Option(
            "--k",
            help="Number of clusters for k-means (auto if not specified).",
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
    Cluster personas to identify similar groups.

    Groups similar personas together and suggests consolidation
    opportunities to reduce redundancy.

    Example:
        persona cluster ./personas.json
        persona cluster ./outputs/ --method hierarchical --threshold 0.7
    """
    if ctx.invoked_subcommand is not None:
        return

    console = get_console()

    from persona import __version__

    if not json_output:
        console.print(f"[dim]Persona {__version__}[/dim]\n")

    # Parse method
    try:
        cluster_method = ClusterMethod(method.lower())
    except ValueError:
        valid_methods = ", ".join(m.value for m in ClusterMethod)
        if json_output:
            print(
                json.dumps(
                    {
                        "command": "cluster",
                        "success": False,
                        "error": f"Invalid method: {method}. Valid methods: {valid_methods}",
                    },
                    indent=2,
                )
            )
        else:
            console.print(f"[red]Invalid method:[/red] {method}")
            console.print(f"Valid methods: {valid_methods}")
        raise typer.Exit(1)

    # Load personas
    try:
        personas = _load_personas(persona_path)
    except Exception as e:
        if json_output:
            print(
                json.dumps(
                    {
                        "command": "cluster",
                        "success": False,
                        "error": str(e),
                    },
                    indent=2,
                )
            )
        else:
            console.print(f"[red]Error loading personas:[/red] {e}")
        raise typer.Exit(1)

    if len(personas) < 2:
        if json_output:
            print(
                json.dumps(
                    {
                        "command": "cluster",
                        "success": False,
                        "error": "Need at least 2 personas to cluster",
                    },
                    indent=2,
                )
            )
        else:
            console.print("[yellow]Need at least 2 personas to cluster.[/yellow]")
        raise typer.Exit(1)

    # Cluster
    clusterer = PersonaClusterer(similarity_threshold=threshold)

    kwargs = {"threshold": threshold}
    if k is not None:
        kwargs["k"] = k

    result = clusterer.cluster(personas, method=cluster_method, **kwargs)

    if not result.success:
        if json_output:
            print(
                json.dumps(
                    {
                        "command": "cluster",
                        "success": False,
                        "error": result.error,
                    },
                    indent=2,
                )
            )
        else:
            console.print(f"[red]Clustering failed:[/red] {result.error}")
        raise typer.Exit(1)

    if json_output:
        print(
            json.dumps(
                {
                    "command": "cluster",
                    "version": __version__,
                    "success": True,
                    "data": result.to_dict(),
                },
                indent=2,
            )
        )
        return

    # Rich output
    console.print(
        Panel.fit(
            f"[bold]Persona Clustering[/bold]\n"
            f"{len(personas)} personas → {result.cluster_count} clusters",
            border_style="blue",
        )
    )

    # Summary
    summary_table = Table(show_header=False, box=None)
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value")

    summary_table.add_row("Total personas", str(result.total_personas))
    summary_table.add_row("Clusters found", str(result.cluster_count))
    summary_table.add_row("Method", result.method.value)
    summary_table.add_row("Threshold", f"{threshold:.0%}")
    summary_table.add_row(
        "Consolidation suggestions", str(len(result.consolidation_suggestions))
    )

    console.print(summary_table)
    console.print()

    # Clusters visualisation
    console.print("[bold]Clusters:[/bold]")

    for cluster in result.clusters:
        # Build a tree for each cluster
        tree = Tree(
            f"[bold cyan]{cluster.label}[/bold cyan] "
            f"({cluster.size} personas, cohesion: {cluster.cohesion:.0%})"
        )

        for persona in cluster.personas:
            is_centroid = persona.id == cluster.centroid_id
            prefix = "[yellow]★[/yellow] " if is_centroid else "  "
            tree.add(f"{prefix}{persona.name} ({persona.id})")

        console.print(tree)
        console.print()

    # Consolidation suggestions
    if result.consolidation_suggestions:
        console.print("[bold yellow]Consolidation Suggestions:[/bold yellow]")

        for i, suggestion in enumerate(result.consolidation_suggestions, 1):
            names = [p.name for p in suggestion.personas]
            console.print(
                f"\n{i}. [bold]{suggestion.merged_name}[/bold] "
                f"(confidence: {suggestion.confidence:.0%})"
            )
            console.print(f"   Personas: {', '.join(names)}")
            console.print(f"   Reason: {suggestion.reason}")
            console.print(f"   Similarity: {suggestion.similarity_score:.0%}")

    # Summary
    if len(result.clusters) == len(personas):
        console.print("\n[green]All personas are distinct.[/green]")
    elif result.consolidation_suggestions:
        console.print(
            f"\n[yellow]Consider consolidating {len(result.consolidation_suggestions)} "
            f"group(s) to reduce redundancy.[/yellow]"
        )
    else:
        console.print(
            f"\n[green]Clustering complete: {result.cluster_count} groups identified.[/green]"
        )


def _load_personas(path: Path):
    """Load personas from a file or directory."""
    from persona.core.generation.parser import Persona

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
