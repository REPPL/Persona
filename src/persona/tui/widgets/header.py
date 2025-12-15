"""
App header widget for the TUI dashboard.

This module provides the AppHeader widget, which displays the application
title, current view, and key shortcuts.
"""

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.widgets import Label, Static


class AppHeader(Static):
    """
    Application header widget.

    Displays the app title, current view, and quick shortcuts.

    Example:
        header = AppHeader()
        header.update_view("Dashboard")
    """

    DEFAULT_CSS = """
    AppHeader {
        height: 3;
        dock: top;
        background: $primary;
        color: $text;
    }

    AppHeader Horizontal {
        height: 1;
        align: center middle;
    }

    AppHeader .title {
        text-style: bold;
        margin: 0 2;
    }

    AppHeader .view {
        color: $accent;
        margin: 0 2;
    }

    AppHeader .shortcuts {
        color: $text-muted;
        margin: 0 2;
    }
    """

    def __init__(self, view: str = "Dashboard") -> None:
        """
        Initialise the app header.

        Args:
            view: Current view name.
        """
        super().__init__()
        self.current_view = view

    def compose(self) -> ComposeResult:
        """Compose the header layout."""
        with Horizontal():
            yield Label("PERSONA DASHBOARD", classes="title")
            yield Label(f"› {self.current_view}", classes="view")
            yield Label("[?] Help  [Q] Quit", classes="shortcuts")

    def update_view(self, view: str) -> None:
        """
        Update the current view name.

        Args:
            view: New view name to display.
        """
        self.current_view = view
        # Find and update the view label
        for widget in self.query(".view"):
            if isinstance(widget, Label):
                widget.update(f"› {view}")
