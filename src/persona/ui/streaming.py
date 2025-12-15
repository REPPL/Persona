"""
Streaming output display for Persona CLI (F-094).

Provides real-time progress feedback during persona generation using Rich Live.
"""

import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Optional

from rich.console import Console, Group
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    Progress,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
    SpinnerColumn,
)
from rich.table import Table
from rich.text import Text
from rich.tree import Tree


@dataclass
class PersonaProgress:
    """Progress information for a single persona."""

    index: int
    name: Optional[str] = None
    title: Optional[str] = None
    summary: Optional[str] = None
    status: str = "pending"  # pending, generating, complete
    start_time: Optional[float] = None
    end_time: Optional[float] = None


@dataclass
class GenerationProgress:
    """Overall generation progress state."""

    total: int
    current: int = 0
    personas: list[PersonaProgress] = field(default_factory=list)
    input_tokens: int = 0
    output_tokens: int = 0
    estimated_cost: float = 0.0
    start_time: Optional[float] = None
    provider: str = ""
    model: str = ""
    status: str = "starting"  # starting, generating, parsing, complete, error

    def __post_init__(self):
        """Initialize persona tracking."""
        if not self.personas:
            self.personas = [
                PersonaProgress(index=i + 1) for i in range(self.total)
            ]


class StreamingOutput:
    """
    Real-time streaming output for persona generation.

    Uses Rich Live display to show:
    - Progress bar with ETA
    - Completed personas as they finish
    - Running token count and cost
    - Status messages

    Falls back to line-by-line output in non-TTY environments.
    """

    def __init__(
        self,
        console: Optional[Console] = None,
        show_progress: bool = True,
    ) -> None:
        """
        Initialize streaming output.

        Args:
            console: Rich console for output.
            show_progress: Whether to show progress bar (can be disabled).
        """
        self.console = console or Console()
        self.show_progress = show_progress
        self.is_tty = sys.stdout.isatty()
        self._live: Optional[Live] = None
        self._progress_bar: Optional[Progress] = None
        self._task_id = None
        self._state: Optional[GenerationProgress] = None

    def start(
        self,
        total: int,
        provider: str = "",
        model: str = "",
    ) -> Callable[[str], None]:
        """
        Start streaming output and return progress callback.

        Args:
            total: Total number of personas to generate.
            provider: LLM provider name.
            model: Model name.

        Returns:
            Callback function for progress updates.
        """
        self._state = GenerationProgress(
            total=total,
            provider=provider,
            model=model,
            start_time=time.time(),
        )

        if self.is_tty and self.show_progress:
            self._start_live()
        else:
            self._print_header()

        return self._handle_progress

    def finish(
        self,
        personas: list,
        input_tokens: int = 0,
        output_tokens: int = 0,
    ) -> None:
        """
        Finish streaming output and show summary.

        Args:
            personas: List of generated personas.
            input_tokens: Total input tokens used.
            output_tokens: Total output tokens used.
        """
        if self._state:
            self._state.status = "complete"
            self._state.input_tokens = input_tokens
            self._state.output_tokens = output_tokens

            # Update persona info
            for i, persona in enumerate(personas):
                if i < len(self._state.personas):
                    self._state.personas[i].name = getattr(persona, "name", f"Persona {i + 1}")
                    self._state.personas[i].title = getattr(persona, "title", None)
                    self._state.personas[i].status = "complete"

            if self._live:
                self._update_display()

        self._stop_live()
        self._show_completion_summary(personas, input_tokens, output_tokens)

    def error(self, message: str) -> None:
        """
        Handle error during generation.

        Args:
            message: Error message to display.
        """
        if self._state:
            self._state.status = "error"

        self._stop_live()
        self.console.print(f"\n[red]Error:[/red] {message}")

    def _start_live(self) -> None:
        """Start Rich Live display."""
        self._progress_bar = Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=self.console,
        )

        self._task_id = self._progress_bar.add_task(
            "Generating personas...",
            total=self._state.total if self._state else 1,
        )

        self._live = Live(
            self._build_display(),
            console=self.console,
            refresh_per_second=4,
            transient=True,
        )
        self._live.start()

    def _stop_live(self) -> None:
        """Stop Rich Live display."""
        if self._live:
            self._live.stop()
            self._live = None

    def _update_display(self) -> None:
        """Update the live display."""
        if self._live and self._state:
            self._live.update(self._build_display())

    def _build_display(self) -> Group:
        """Build the display group for Live."""
        if not self._state:
            return Group()

        components = []

        # Progress bar
        if self._progress_bar:
            components.append(self._progress_bar)

        # Persona tree
        tree = self._build_persona_tree()
        components.append(tree)

        # Token/cost info
        token_info = self._build_token_info()
        components.append(token_info)

        return Group(*components)

    def _build_persona_tree(self) -> Tree:
        """Build tree of persona progress."""
        tree = Tree("[bold]Personas[/bold]")

        if not self._state:
            return tree

        for persona in self._state.personas:
            if persona.status == "complete":
                name = persona.name or f"Persona {persona.index}"
                title = f" ({persona.title})" if persona.title else ""
                tree.add(f"[green]✓[/green] {name}{title}")
            elif persona.status == "generating":
                tree.add(f"[yellow]●[/yellow] Generating persona {persona.index}...")
            else:
                tree.add(f"[dim]○[/dim] Persona {persona.index}")

        return tree

    def _build_token_info(self) -> Text:
        """Build token usage information."""
        if not self._state:
            return Text()

        elapsed = time.time() - self._state.start_time if self._state.start_time else 0
        elapsed_str = f"{int(elapsed // 60)}m {int(elapsed % 60)}s"

        tokens_total = self._state.input_tokens + self._state.output_tokens
        cost_str = f"${self._state.estimated_cost:.4f}" if self._state.estimated_cost else "calculating..."

        return Text.from_markup(
            f"\n[dim]Elapsed: {elapsed_str} │ "
            f"Tokens: {tokens_total:,} │ "
            f"Cost: {cost_str}[/dim]"
        )

    def _handle_progress(self, message: str) -> None:
        """
        Handle progress callback from pipeline.

        Args:
            message: Progress message from pipeline.
        """
        if not self._state:
            return

        # Parse message and update state
        message_lower = message.lower()

        if "loading" in message_lower:
            self._state.status = "loading"
        elif "generating" in message_lower:
            self._state.status = "generating"
            # Mark next pending persona as generating
            for persona in self._state.personas:
                if persona.status == "pending":
                    persona.status = "generating"
                    persona.start_time = time.time()
                    break
        elif "parsing" in message_lower:
            self._state.status = "parsing"
        elif "complete" in message_lower:
            self._state.status = "complete"
            # Mark all generating as complete
            for persona in self._state.personas:
                if persona.status == "generating":
                    persona.status = "complete"
                    persona.end_time = time.time()

        # Update display
        if self.is_tty and self.show_progress:
            if self._progress_bar and self._task_id is not None:
                completed = sum(1 for p in self._state.personas if p.status == "complete")
                self._progress_bar.update(self._task_id, completed=completed)
            self._update_display()
        else:
            self._print_progress(message)

    def _print_header(self) -> None:
        """Print header for non-TTY output."""
        if not self._state:
            return

        self.console.print(f"\nGenerating {self._state.total} personas...")
        if self._state.provider:
            self.console.print(f"Provider: {self._state.provider}")
        if self._state.model:
            self.console.print(f"Model: {self._state.model}")
        self.console.print()

    def _print_progress(self, message: str) -> None:
        """Print progress for non-TTY output."""
        if not self._state:
            self.console.print(message)
            return

        # Format progress indicator
        completed = sum(1 for p in self._state.personas if p.status == "complete")
        prefix = f"[{completed}/{self._state.total}]"

        self.console.print(f"{prefix} {message}")

    def _show_completion_summary(
        self,
        personas: list,
        input_tokens: int,
        output_tokens: int,
    ) -> None:
        """Show completion summary."""
        if not self._state:
            return

        elapsed = time.time() - self._state.start_time if self._state.start_time else 0
        elapsed_str = f"{int(elapsed // 60)}m {int(elapsed % 60)}s"

        # Simple completion message - detailed summary shown by command
        self.console.print()
        self.console.print(f"[green]✓[/green] Generation complete ({elapsed_str})")


class SimpleProgress:
    """
    Simple line-by-line progress for non-TTY environments.

    Alternative to StreamingOutput when Rich Live is not available.
    """

    def __init__(self, console: Optional[Console] = None) -> None:
        """Initialize simple progress."""
        self.console = console or Console()
        self._total = 0
        self._current = 0

    def start(self, total: int, **kwargs) -> Callable[[str], None]:
        """Start progress tracking."""
        self._total = total
        self._current = 0
        self.console.print(f"\nGenerating {total} personas...\n")
        return self._handle_progress

    def _handle_progress(self, message: str) -> None:
        """Handle progress message."""
        self.console.print(f"  {message}")

    def finish(self, personas: list, input_tokens: int = 0, output_tokens: int = 0) -> None:
        """Show completion."""
        self.console.print(f"\n[green]✓[/green] Generated {len(personas)} personas")
        self.console.print(f"  Tokens: {input_tokens + output_tokens:,}")


def get_progress_handler(
    console: Optional[Console] = None,
    show_progress: bool = True,
) -> StreamingOutput | SimpleProgress:
    """
    Get appropriate progress handler for environment.

    Args:
        console: Rich console for output.
        show_progress: Whether to show progress bar.

    Returns:
        StreamingOutput for TTY, SimpleProgress for non-TTY.
    """
    if sys.stdout.isatty() and show_progress:
        return StreamingOutput(console=console, show_progress=True)
    else:
        return SimpleProgress(console=console)
