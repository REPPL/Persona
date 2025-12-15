"""
Real-time generation monitor screen for the TUI.

This module provides a screen for monitoring persona generation
in real-time with progress, token usage, and cost tracking.
"""

from decimal import Decimal

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Label, Log

from persona.tui.config import TUIConfig
from persona.tui.widgets.cost_tracker import CostTracker
from persona.tui.widgets.progress_panel import ProgressPanel


class GenerationMonitorScreen(Screen):
    """
    Real-time generation monitor screen.

    Features:
    - Live progress updates
    - Token usage tracking
    - Cost accumulation
    - Generation logs
    - Cancel button

    Example:
        screen = GenerationMonitorScreen(config)
        app.push_screen(screen)
        screen.start_generation(...)
    """

    BINDINGS = [
        ("escape", "cancel", "Cancel"),
    ]

    def __init__(self, config: TUIConfig) -> None:
        """
        Initialise generation monitor screen.

        Args:
            config: TUI configuration.
        """
        super().__init__()
        self.config = config
        self.is_generating = False
        self.can_cancel = True

    def compose(self) -> ComposeResult:
        """Compose the generation monitor layout."""
        with Vertical(id="monitor-container"):
            # Title
            yield Label("Generation Monitor", id="monitor-title")

            # Progress panel
            yield ProgressPanel()

            # Cost tracker
            yield CostTracker()

            # Log output
            with Container(id="log-container"):
                yield Label("Logs", classes="section-title")
                yield Log(id="generation-log", auto_scroll=True)

            # Cancel button
            yield Button("Cancel Generation", id="cancel-btn", variant="error")

    def start_generation(
        self,
        persona_count: int,
        model: str,
        provider: str,
    ) -> None:
        """
        Start monitoring a generation run.

        Args:
            persona_count: Number of personas to generate.
            model: Model being used.
            provider: Provider being used.
        """
        self.is_generating = True

        # Update progress panel
        progress = self.query_one(ProgressPanel)
        progress.reset()
        progress.set_personas_count(0, persona_count)
        progress.update_progress(0.0, f"Starting generation with {model}...")

        # Log start
        log = self.query_one("#generation-log", Log)
        log.write_line(f"Starting generation: {persona_count} personas")
        log.write_line(f"Model: {model} ({provider})")
        log.write_line("")

    def update_progress(
        self,
        progress: float,
        status: str = "",
        personas_done: int | None = None,
    ) -> None:
        """
        Update generation progress.

        Args:
            progress: Progress value (0.0 to 1.0).
            status: Current status message.
            personas_done: Number of personas completed.
        """
        progress_panel = self.query_one(ProgressPanel)
        progress_panel.update_progress(progress, status)

        if personas_done is not None:
            progress_panel.set_personas_count(
                personas_done, progress_panel.personas_total
            )

        # Log status
        if status:
            log = self.query_one("#generation-log", Log)
            log.write_line(status)

    def update_cost(self, tokens: int, cost: Decimal, provider: str) -> None:
        """
        Update token usage and cost.

        Args:
            tokens: Total tokens used.
            cost: Total cost in USD.
            provider: Provider name.
        """
        # Update progress panel
        progress_panel = self.query_one(ProgressPanel)
        progress_panel.set_tokens_cost(tokens, float(cost))

        # Update cost tracker
        cost_tracker = self.query_one(CostTracker)
        cost_tracker.add_cost(provider, cost)

    def complete_generation(self, success: bool = True) -> None:
        """
        Mark generation as complete.

        Args:
            success: Whether generation succeeded.
        """
        self.is_generating = False

        progress_panel = self.query_one(ProgressPanel)

        if success:
            progress_panel.update_progress(1.0, "Generation complete!")
            log = self.query_one("#generation-log", Log)
            log.write_line("")
            log.write_line("✓ Generation complete!")
        else:
            progress_panel.update_progress(0.0, "Generation failed")
            log = self.query_one("#generation-log", Log)
            log.write_line("")
            log.write_line("✗ Generation failed")

        # Disable cancel button
        cancel_btn = self.query_one("#cancel-btn", Button)
        cancel_btn.disabled = True

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "cancel-btn" and self.can_cancel:
            self.action_cancel()

    def action_cancel(self) -> None:
        """Cancel generation."""
        if self.is_generating and self.can_cancel:
            self.notify("Cancelling generation...")
            log = self.query_one("#generation-log", Log)
            log.write_line("Cancellation requested...")
            # TODO: Signal cancellation to generation process
