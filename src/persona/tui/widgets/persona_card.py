"""
Persona card widget for displaying persona details.

This module provides widgets for rendering persona information
in a compact card format.
"""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.widgets import Label, Static

from persona.core.generation.parser import Persona


class PersonaCard(Static):
    """
    Card widget for displaying persona information.

    Shows:
    - Persona name and role
    - Age and location (if available)
    - Goals summary
    - Quality score badge

    Example:
        card = PersonaCard(persona)
    """

    DEFAULT_CSS = """
    PersonaCard {
        height: auto;
        border: solid $primary;
        padding: 1 2;
        margin: 1 0;
    }

    PersonaCard .name {
        text-style: bold;
        color: $accent;
    }

    PersonaCard .role {
        color: $text;
        margin: 0 0 1 0;
    }

    PersonaCard .demographics {
        color: $text-muted;
    }

    PersonaCard .goals {
        color: $text;
        margin: 1 0;
    }

    PersonaCard .quality {
        text-style: bold;
        dock: right;
    }

    PersonaCard .quality-excellent {
        color: $success;
    }

    PersonaCard .quality-good {
        color: $accent;
    }

    PersonaCard .quality-acceptable {
        color: $warning;
    }

    PersonaCard .quality-poor {
        color: $error;
    }
    """

    def __init__(self, persona: Persona, quality_score: float | None = None) -> None:
        """
        Initialise persona card.

        Args:
            persona: Persona to display.
            quality_score: Optional quality score (0-100).
        """
        super().__init__()
        self.persona = persona
        self.quality_score = quality_score

    def compose(self) -> ComposeResult:
        """Compose the persona card layout."""
        with Vertical():
            # Name and role
            yield Label(self.persona.name, classes="name")
            if self.persona.role:
                yield Label(f"Role: {self.persona.role}", classes="role")

            # Demographics
            demo_parts = []
            if self.persona.age:
                demo_parts.append(f"Age: {self.persona.age}")
            if self.persona.location:
                demo_parts.append(f"Location: {self.persona.location}")

            if demo_parts:
                yield Label(" | ".join(demo_parts), classes="demographics")

            # Goals summary
            if self.persona.goals:
                goals_text = ", ".join(self.persona.goals[:3])
                if len(self.persona.goals) > 3:
                    goals_text += f" (+{len(self.persona.goals) - 3} more)"
                yield Label(f"Goals: {goals_text}", classes="goals")

            # Quality badge
            if self.quality_score is not None:
                quality_class = self._get_quality_class(self.quality_score)
                yield Label(
                    f"Quality: {self.quality_score:.0f}/100",
                    classes=f"quality {quality_class}",
                )

    def _get_quality_class(self, score: float) -> str:
        """
        Get CSS class for quality score.

        Args:
            score: Quality score (0-100).

        Returns:
            CSS class name.
        """
        if score >= 85:
            return "quality-excellent"
        elif score >= 70:
            return "quality-good"
        elif score >= 50:
            return "quality-acceptable"
        else:
            return "quality-poor"
