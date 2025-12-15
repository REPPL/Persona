"""
Progress panel widget for monitoring generation.

This module provides widgets for displaying real-time progress
during persona generation.
"""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label, ProgressBar, Static


class ProgressPanel(Static):
    """
    Panel for displaying generation progress.

    Shows:
    - Overall progress bar
    - Current step/task
    - Personas generated count
    - Token usage
    - Estimated cost

    Example:
        panel = ProgressPanel()
        panel.update_progress(0.5, "Generating personas...")
        panel.set_personas_count(5, 10)
    """

    DEFAULT_CSS = """
    ProgressPanel {
        height: auto;
        border: solid $accent;
        padding: 1 2;
    }

    ProgressPanel .title {
        text-style: bold;
        color: $accent;
    }

    ProgressPanel .status {
        color: $text;
        margin: 1 0;
    }

    ProgressPanel .stats {
        color: $text-muted;
    }

    ProgressPanel ProgressBar {
        margin: 1 0;
    }
    """

    def __init__(self) -> None:
        """Initialise the progress panel."""
        super().__init__()
        self.current_progress = 0.0
        self.current_status = "Idle"
        self.personas_generated = 0
        self.personas_total = 0
        self.tokens_used = 0
        self.estimated_cost = 0.0

    def compose(self) -> ComposeResult:
        """Compose the progress panel layout."""
        with Vertical():
            yield Label("📊 Generation Progress", classes="title")
            yield ProgressBar(id="progress-bar", total=100, show_percentage=True)
            yield Label("Idle", id="status-label", classes="status")
            yield Label("Personas: 0/0", id="persona-count", classes="stats")
            yield Label("Tokens: 0 | Cost: $0.00", id="token-cost", classes="stats")

    def update_progress(self, progress: float, status: str = "") -> None:
        """
        Update the progress bar and status.

        Args:
            progress: Progress value (0.0 to 1.0).
            status: Current status message.
        """
        self.current_progress = max(0.0, min(1.0, progress))
        if status:
            self.current_status = status

        # Update progress bar
        progress_bar = self.query_one("#progress-bar", ProgressBar)
        progress_bar.update(progress=int(self.current_progress * 100))

        # Update status label
        status_label = self.query_one("#status-label", Label)
        status_label.update(self.current_status)

    def set_personas_count(self, generated: int, total: int) -> None:
        """
        Update personas count.

        Args:
            generated: Number of personas generated.
            total: Total personas to generate.
        """
        self.personas_generated = generated
        self.personas_total = total

        count_label = self.query_one("#persona-count", Label)
        count_label.update(f"Personas: {generated}/{total}")

    def set_tokens_cost(self, tokens: int, cost: float) -> None:
        """
        Update token usage and cost.

        Args:
            tokens: Total tokens used.
            cost: Estimated cost in USD.
        """
        self.tokens_used = tokens
        self.estimated_cost = cost

        cost_label = self.query_one("#token-cost", Label)
        cost_label.update(f"Tokens: {tokens:,} | Cost: ${cost:.4f}")

    def reset(self) -> None:
        """Reset the progress panel to initial state."""
        self.current_progress = 0.0
        self.current_status = "Idle"
        self.personas_generated = 0
        self.personas_total = 0
        self.tokens_used = 0
        self.estimated_cost = 0.0

        self.update_progress(0.0, "Idle")
        self.set_personas_count(0, 0)
        self.set_tokens_cost(0, 0.0)

    def is_active(self) -> bool:
        """Check if generation is currently active."""
        return 0 < self.current_progress < 1.0
