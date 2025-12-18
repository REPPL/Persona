"""
Experiment list widget for the TUI dashboard.

This module provides widgets for displaying and selecting experiments.
"""

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.message import Message
from textual.widgets import Button, Label, ListItem, ListView, Static

from persona.core.experiments import ExperimentManager


class ExperimentListItem(ListItem):
    """
    List item for an experiment.

    Displays experiment name, status indicator, and metadata.
    """

    def __init__(self, name: str, has_outputs: bool = False) -> None:
        """
        Initialise experiment list item.

        Args:
            name: Experiment name.
            has_outputs: Whether experiment has output runs.
        """
        super().__init__()
        self.experiment_name = name
        self.has_outputs = has_outputs

    def compose(self) -> ComposeResult:
        """Compose the list item."""
        status_icon = "✓" if self.has_outputs else "○"
        yield Label(f"{status_icon} {self.experiment_name}")


class ExperimentList(Static):
    """
    Widget for displaying list of experiments.

    Features:
    - List of experiments with status icons
    - Selection highlighting
    - "New experiment" button
    - Filtering and search

    Example:
        exp_list = ExperimentList()
        exp_list.load_experiments()
    """

    DEFAULT_CSS = """
    ExperimentList {
        height: 100%;
        border: solid $primary;
        padding: 0;
    }

    ExperimentList .title {
        text-style: bold;
        color: $accent;
        dock: top;
        height: 1;
        padding: 1 2;
        background: $panel;
    }

    ExperimentList ListView {
        height: 1fr;
    }

    ExperimentList Button {
        dock: bottom;
        width: 100%;
    }

    ExperimentList .empty {
        color: $text-muted;
        text-align: center;
        margin: 2 0;
    }
    """

    def __init__(self, experiments_dir: Path) -> None:
        """
        Initialise experiment list.

        Args:
            experiments_dir: Path to experiments directory.
        """
        super().__init__()
        self.experiments_dir = experiments_dir
        self.manager = ExperimentManager(experiments_dir)
        self.selected_experiment: str | None = None

    def compose(self) -> ComposeResult:
        """Compose the experiment list layout."""
        yield Label("EXPERIMENTS", classes="title")
        with VerticalScroll():
            yield ListView(id="experiment-list")
        yield Button("➕ New Experiment", id="new-experiment-btn", variant="success")

    def on_mount(self) -> None:
        """Load experiments when mounted."""
        self.load_experiments()

    def load_experiments(self) -> None:
        """Load and display experiments from disk."""
        list_view = self.query_one("#experiment-list", ListView)
        list_view.clear()

        experiments = self.manager.list_experiments()

        if not experiments:
            list_view.append(ListItem(Label("No experiments found", classes="empty")))
            return

        for exp_name in experiments:
            try:
                exp = self.manager.load(exp_name)
                has_outputs = len(exp.list_outputs()) > 0
                list_view.append(ExperimentListItem(exp_name, has_outputs))
            except Exception:
                # Skip invalid experiments
                continue

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handle experiment selection."""
        if isinstance(event.item, ExperimentListItem):
            self.selected_experiment = event.item.experiment_name
            # Post a message that can be caught by parent screen
            self.post_message(self.ExperimentSelected(event.item.experiment_name))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "new-experiment-btn":
            self.post_message(self.NewExperimentRequested())

    def get_selected(self) -> str | None:
        """Get currently selected experiment name."""
        return self.selected_experiment

    class ExperimentSelected(Message):
        """Message sent when an experiment is selected."""

        def __init__(self, experiment_name: str) -> None:
            super().__init__()
            self.experiment_name = experiment_name

    class NewExperimentRequested(Message):
        """Message sent when new experiment button is pressed."""

        pass
