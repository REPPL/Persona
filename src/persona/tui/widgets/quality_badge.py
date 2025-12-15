"""
Quality badge widget for displaying persona quality scores.

This module provides widgets for rendering quality scores with
appropriate colour coding and labels.
"""

from textual.app import ComposeResult
from textual.widgets import Label, Static


class QualityBadge(Static):
    """
    Badge widget for displaying quality scores.

    Shows quality score with colour coding:
    - Excellent: >= 85 (green)
    - Good: >= 70 (blue)
    - Acceptable: >= 50 (yellow)
    - Poor: < 50 (red)

    Example:
        badge = QualityBadge(87.5)
    """

    DEFAULT_CSS = """
    QualityBadge {
        width: auto;
        height: 1;
        padding: 0 1;
        border: round;
    }

    QualityBadge.excellent {
        background: $success;
        color: $text;
    }

    QualityBadge.good {
        background: $accent;
        color: $text;
    }

    QualityBadge.acceptable {
        background: $warning;
        color: $text;
    }

    QualityBadge.poor {
        background: $error;
        color: $text;
    }

    QualityBadge.failing {
        background: $error-darken-1;
        color: $text;
    }
    """

    def __init__(self, score: float, show_label: bool = True) -> None:
        """
        Initialise quality badge.

        Args:
            score: Quality score (0-100).
            show_label: Whether to show text label.
        """
        super().__init__()
        self.score = score
        self.show_label = show_label
        self._update_classes()

    def compose(self) -> ComposeResult:
        """Compose the badge content."""
        if self.show_label:
            level = self._get_level_text()
            yield Label(f"{level} {self.score:.0f}")
        else:
            yield Label(f"{self.score:.0f}")

    def _update_classes(self) -> None:
        """Update CSS classes based on score."""
        # Remove all quality classes
        self.remove_class("excellent", "good", "acceptable", "poor", "failing")

        # Add appropriate class
        if self.score >= 85:
            self.add_class("excellent")
        elif self.score >= 70:
            self.add_class("good")
        elif self.score >= 50:
            self.add_class("acceptable")
        elif self.score >= 30:
            self.add_class("poor")
        else:
            self.add_class("failing")

    def _get_level_text(self) -> str:
        """Get quality level text."""
        if self.score >= 85:
            return "Excellent"
        elif self.score >= 70:
            return "Good"
        elif self.score >= 50:
            return "Acceptable"
        elif self.score >= 30:
            return "Poor"
        else:
            return "Failing"

    def update_score(self, score: float) -> None:
        """
        Update the displayed score.

        Args:
            score: New quality score (0-100).
        """
        self.score = score
        self._update_classes()
        self.refresh()
