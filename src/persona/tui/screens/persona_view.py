"""
Persona viewer screen for the TUI.

This module provides a detailed view of a single persona with
all attributes, quality scores, and evidence links.
"""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical, VerticalScroll
from textual.screen import Screen
from textual.widgets import Button, Label

from persona.core.generation.parser import Persona
from persona.tui.widgets.quality_badge import QualityBadge


class PersonaViewerScreen(Screen):
    """
    Persona detail viewer screen.

    Shows:
    - Complete persona attributes
    - Quality score with breakdown
    - Evidence links
    - Navigation between personas

    Example:
        screen = PersonaViewerScreen(persona, quality_score)
        app.push_screen(screen)
    """

    BINDINGS = [
        ("escape", "dismiss", "Back"),
        ("left", "previous", "Previous"),
        ("right", "next", "Next"),
    ]

    def __init__(
        self,
        persona: Persona,
        quality_score: float | None = None,
        all_personas: list[Persona] | None = None,
    ) -> None:
        """
        Initialise persona viewer screen.

        Args:
            persona: Persona to display.
            quality_score: Optional quality score.
            all_personas: List of all personas for navigation.
        """
        super().__init__()
        self.persona = persona
        self.quality_score = quality_score
        self.all_personas = all_personas or [persona]
        self.current_index = 0

        # Find current index
        for i, p in enumerate(self.all_personas):
            if p.id == persona.id:
                self.current_index = i
                break

    def compose(self) -> ComposeResult:
        """Compose the persona viewer layout."""
        with Vertical():
            # Header with navigation
            with Horizontal(id="viewer-header"):
                yield Button("←", id="prev-btn", variant="default")
                yield Label(
                    f"Persona {self.current_index + 1} of {len(self.all_personas)}",
                    id="nav-label",
                )
                yield Button("→", id="next-btn", variant="default")

            # Persona details
            with VerticalScroll(id="viewer-content"):
                yield self._build_persona_details()

    def _build_persona_details(self) -> Container:
        """Build the persona details container."""
        container = Container(id="persona-details")

        # Name and role
        container.mount(Label(self.persona.name, classes="persona-name"))
        if self.persona.role:
            container.mount(Label(f"Role: {self.persona.role}", classes="persona-role"))

        # Quality badge
        if self.quality_score is not None:
            container.mount(QualityBadge(self.quality_score))

        # Demographics section
        if any([self.persona.age, self.persona.location, self.persona.background]):
            demo_section = Container(classes="section")
            demo_section.mount(Label("Demographics", classes="section-title"))

            if self.persona.age:
                demo_section.mount(Label(f"Age: {self.persona.age}"))
            if self.persona.location:
                demo_section.mount(Label(f"Location: {self.persona.location}"))
            if self.persona.background:
                demo_section.mount(Label(f"Background: {self.persona.background}"))

            container.mount(demo_section)

        # Goals section
        if self.persona.goals:
            goals_section = Container(classes="section")
            goals_section.mount(Label("Goals", classes="section-title"))
            for goal in self.persona.goals:
                goals_section.mount(Label(f"• {goal}", classes="list-item"))
            container.mount(goals_section)

        # Frustrations section
        if self.persona.frustrations:
            frust_section = Container(classes="section")
            frust_section.mount(Label("Frustrations", classes="section-title"))
            for frustration in self.persona.frustrations:
                frust_section.mount(Label(f"• {frustration}", classes="list-item"))
            container.mount(frust_section)

        # Behaviours section
        if self.persona.behaviours:
            behav_section = Container(classes="section")
            behav_section.mount(Label("Behaviours", classes="section-title"))
            for behaviour in self.persona.behaviours:
                behav_section.mount(Label(f"• {behaviour}", classes="list-item"))
            container.mount(behav_section)

        return container

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses."""
        if event.button.id == "prev-btn":
            self.action_previous()
        elif event.button.id == "next-btn":
            self.action_next()

    def action_previous(self) -> None:
        """Navigate to previous persona."""
        if self.current_index > 0:
            self.current_index -= 1
            self._update_persona()

    def action_next(self) -> None:
        """Navigate to next persona."""
        if self.current_index < len(self.all_personas) - 1:
            self.current_index += 1
            self._update_persona()

    def action_dismiss(self) -> None:
        """Dismiss this screen."""
        self.app.pop_screen()

    def _update_persona(self) -> None:
        """Update displayed persona after navigation."""
        self.persona = self.all_personas[self.current_index]

        # Update navigation label
        nav_label = self.query_one("#nav-label", Label)
        nav_label.update(
            f"Persona {self.current_index + 1} of {len(self.all_personas)}"
        )

        # Rebuild details
        viewer_content = self.query_one("#viewer-content", VerticalScroll)
        viewer_content.remove_children()
        viewer_content.mount(self._build_persona_details())
