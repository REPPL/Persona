"""
Main TUI application for Persona.

This module provides the PersonaApp class, which is the main entry point
for the full-screen terminal user interface.
"""

from pathlib import Path

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header

from persona.tui.config import TUIConfig
from persona.tui.screens.dashboard import DashboardScreen


class PersonaApp(App):
    """
    Main TUI application for Persona.

    Provides a full-screen terminal interface for monitoring persona
    generation, browsing experiments, and managing the system.

    Key features:
    - Dashboard with real-time updates
    - Experiment browser and management
    - Persona viewer with quality scores
    - Cost tracking across runs
    - Responsive layout system

    Example:
        app = PersonaApp()
        app.run()

    Keyboard shortcuts:
        Q: Quit
        ?: Help
        D: Dashboard
        E: Experiments
    """

    TITLE = "Persona Dashboard"
    CSS_PATH = "styles/app.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit", priority=True),
        Binding("question_mark", "help", "Help"),
        Binding("d", "show_dashboard", "Dashboard"),
        Binding("e", "show_experiments", "Experiments"),
    ]

    def __init__(
        self,
        experiments_dir: str | Path = "./experiments",
        enable_mouse: bool = True,
    ) -> None:
        """
        Initialise the Persona TUI application.

        Args:
            experiments_dir: Path to experiments directory.
            enable_mouse: Whether to enable mouse support.
        """
        super().__init__()
        self.config = TUIConfig(
            experiments_dir=experiments_dir,
            enable_mouse=enable_mouse,
        )

    def on_mount(self) -> None:
        """Called when app mounts - validate terminal size."""
        # Get terminal size
        size = self.size
        is_valid, error = self.config.meets_requirements(size.width, size.height)

        if not is_valid:
            # Terminal too small - show error and exit
            self.exit(message=error)
            return

        # Push the dashboard screen
        self.push_screen(DashboardScreen(self.config))

    def compose(self) -> ComposeResult:
        """
        Compose the main app layout.

        Returns:
            Iterator of widgets to add to the app.
        """
        yield Header(show_clock=True)
        yield Container(id="app-content")
        yield Footer()

    def action_show_dashboard(self) -> None:
        """Show the dashboard screen."""
        self.push_screen(DashboardScreen(self.config))

    def action_show_experiments(self) -> None:
        """Show the experiments screen."""
        # TODO: Implement ExperimentBrowserScreen
        self.notify("Experiments screen coming soon!")

    def action_help(self) -> None:
        """Show help information."""
        help_text = """
Persona Dashboard - Keyboard Shortcuts

Navigation:
  Q             Quit application
  ?             Show this help
  D             Dashboard view
  E             Experiments browser

Dashboard:
  ↑/↓           Navigate lists
  Enter         Select/activate
  Tab           Next panel
  Shift+Tab     Previous panel
  Esc           Cancel/back

For more information, visit:
https://github.com/REPPL/Persona
        """
        self.notify(help_text.strip(), timeout=10)

    def on_resize(self, event) -> None:
        """Handle terminal resize events."""
        # Check if terminal is still large enough
        is_valid, error = self.config.meets_requirements(
            event.size.width, event.size.height
        )

        if not is_valid:
            self.exit(message=f"Terminal too small after resize:\n{error}")

        # Update breakpoint class on body
        breakpoint = self.config.get_breakpoint(event.size.width)
        self.app.set_class(breakpoint, "bp-*")
