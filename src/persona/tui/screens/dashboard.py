"""
Dashboard screen for the TUI.

This module provides the main dashboard screen that shows
experiments, recent runs, and system status.
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Label, Static

from persona.tui.config import TUIConfig
from persona.tui.widgets.cost_tracker import CostTracker
from persona.tui.widgets.experiment_list import ExperimentList
from persona.tui.widgets.progress_panel import ProgressPanel


class DashboardScreen(Screen):
    """
    Main dashboard screen.

    Layout:
    - Left sidebar: Experiment list
    - Main area: Progress panel and recent activity
    - Right panel (wide mode): Cost tracker

    Features:
    - Experiment selection and management
    - Real-time progress monitoring
    - Cost tracking
    - Responsive layout (adapts to terminal size)

    Example:
        screen = DashboardScreen(config)
        app.push_screen(screen)
    """

    CSS_PATH = "../styles/dashboard.tcss"

    def __init__(self, config: TUIConfig) -> None:
        """
        Initialise the dashboard screen.

        Args:
            config: TUI configuration.
        """
        super().__init__()
        self.config = config

    def compose(self) -> ComposeResult:
        """Compose the dashboard layout."""
        with Horizontal(id="dashboard-container"):
            # Left sidebar - Experiment list
            with Container(id="sidebar", classes="sidebar"):
                yield ExperimentList(self.config.experiments_dir)

            # Main content area
            with Vertical(id="main-content", classes="main"):
                yield Label("Dashboard", id="content-title")
                yield ProgressPanel()
                yield Container(id="recent-activity")

            # Right panel - Cost tracker (hidden on compact/standard)
            with Container(id="details-panel", classes="details-panel"):
                yield CostTracker()

    def on_mount(self) -> None:
        """Called when screen mounts - set up responsive classes."""
        self._update_layout()

    def on_resize(self, event) -> None:
        """Handle resize events."""
        self._update_layout()

    def _update_layout(self) -> None:
        """Update layout based on terminal width."""
        width = self.app.size.width
        breakpoint = self.config.get_breakpoint(width)

        # Apply breakpoint class to dashboard container
        container = self.query_one("#dashboard-container")
        container.remove_class("compact", "standard", "wide")
        container.add_class(breakpoint)

    def on_experiment_list_experiment_selected(
        self, message: ExperimentList.ExperimentSelected
    ) -> None:
        """Handle experiment selection."""
        # Update main content to show experiment details
        self.notify(f"Selected experiment: {message.experiment_name}")
        # TODO: Load experiment details and recent runs

    def on_experiment_list_new_experiment_requested(
        self, message: ExperimentList.NewExperimentRequested
    ) -> None:
        """Handle new experiment request."""
        self.notify("New experiment creation coming soon!")
        # TODO: Show new experiment dialog


class RecentActivityPanel(Static):
    """
    Panel for displaying recent experiment activity.

    Shows:
    - Recent generation runs
    - Status indicators
    - Quick stats
    """

    DEFAULT_CSS = """
    RecentActivityPanel {
        height: auto;
        border: solid $primary;
        padding: 1 2;
    }

    RecentActivityPanel .title {
        text-style: bold;
        color: $accent;
    }

    RecentActivityPanel .empty {
        color: $text-muted;
        margin: 1 0;
    }

    RecentActivityPanel .run-item {
        margin: 1 0;
    }
    """

    def compose(self) -> ComposeResult:
        """Compose the recent activity panel."""
        with Vertical():
            yield Label("📋 Recent Activity", classes="title")
            yield Label("No recent runs", classes="empty")

    def load_recent_runs(self, experiment_name: str | None = None) -> None:
        """
        Load and display recent runs.

        Args:
            experiment_name: Optional experiment to filter by.
        """
        # TODO: Implement loading from run history
        pass
