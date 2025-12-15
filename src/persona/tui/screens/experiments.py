"""
Experiment browser screen for the TUI.

This module provides a screen for browsing, filtering, and
managing experiments.
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Button, Input, Label

from persona.tui.config import TUIConfig
from persona.tui.widgets.experiment_list import ExperimentList


class ExperimentBrowserScreen(Screen):
    """
    Experiment browser screen.

    Features:
    - Full list of experiments
    - Search/filter functionality
    - Create, edit, delete operations
    - Run statistics

    Example:
        screen = ExperimentBrowserScreen(config)
        app.push_screen(screen)
    """

    BINDINGS = [
        ("escape", "dismiss", "Back"),
        ("n", "new_experiment", "New"),
        ("slash", "search", "Search"),
    ]

    def __init__(self, config: TUIConfig) -> None:
        """
        Initialise experiment browser screen.

        Args:
            config: TUI configuration.
        """
        super().__init__()
        self.config = config

    def compose(self) -> ComposeResult:
        """Compose the experiment browser layout."""
        with Vertical():
            # Header with search
            with Horizontal(id="browser-header"):
                yield Label("Experiments", id="browser-title")
                yield Input(placeholder="Search...", id="search-input")
                yield Button("➕ New", id="new-btn", variant="success")

            # Experiment list
            with Container(id="browser-content"):
                yield ExperimentList(self.config.experiments_dir)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "new-btn":
            self.action_new_experiment()

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle search input changes."""
        if event.input.id == "search-input":
            self._filter_experiments(event.value)

    def action_new_experiment(self) -> None:
        """Create a new experiment."""
        self.notify("New experiment creation coming soon!")
        # TODO: Show new experiment dialog

    def action_search(self) -> None:
        """Focus the search input."""
        search_input = self.query_one("#search-input", Input)
        search_input.focus()

    def action_dismiss(self) -> None:
        """Dismiss this screen."""
        self.app.pop_screen()

    def _filter_experiments(self, query: str) -> None:
        """
        Filter experiments by search query.

        Args:
            query: Search query string.
        """
        # TODO: Implement filtering
        pass
