"""
Output formatters for personas.

This module provides formatters for converting personas to
various output formats (JSON, Markdown, etc.).
"""

import json
from abc import ABC, abstractmethod

from persona.core.generation.parser import Persona


class BaseFormatter(ABC):
    """Abstract base class for output formatters."""

    @abstractmethod
    def format(self, persona: Persona) -> str:
        """
        Format a persona to string output.

        Args:
            persona: The persona to format.

        Returns:
            Formatted string representation.
        """
        ...

    @abstractmethod
    def extension(self) -> str:
        """Return the file extension for this format."""
        ...


class JSONFormatter(BaseFormatter):
    """Format personas as JSON."""

    def __init__(self, indent: int = 2) -> None:
        """
        Initialise JSON formatter.

        Args:
            indent: JSON indentation level.
        """
        self._indent = indent

    def format(self, persona: Persona) -> str:
        """Format persona as JSON string."""
        return json.dumps(persona.to_dict(), indent=self._indent, ensure_ascii=False)

    def extension(self) -> str:
        return ".json"


class MarkdownFormatter(BaseFormatter):
    """Format personas as Markdown."""

    def format(self, persona: Persona) -> str:
        """Format persona as Markdown document."""
        lines = []

        # Title
        lines.append(f"# {persona.name}")
        lines.append("")

        # ID
        lines.append(f"**ID**: {persona.id}")
        lines.append("")

        # Demographics
        if persona.demographics:
            lines.append("## Demographics")
            lines.append("")
            for key, value in persona.demographics.items():
                # Convert key to title case
                display_key = key.replace("_", " ").title()
                lines.append(f"- **{display_key}**: {value}")
            lines.append("")

        # Goals
        if persona.goals:
            lines.append("## Goals")
            lines.append("")
            for goal in persona.goals:
                lines.append(f"- {goal}")
            lines.append("")

        # Pain Points
        if persona.pain_points:
            lines.append("## Pain Points")
            lines.append("")
            for pain_point in persona.pain_points:
                lines.append(f"- {pain_point}")
            lines.append("")

        # Behaviours
        if persona.behaviours:
            lines.append("## Behaviours")
            lines.append("")
            for behaviour in persona.behaviours:
                lines.append(f"- {behaviour}")
            lines.append("")

        # Quotes
        if persona.quotes:
            lines.append("## Quotes")
            lines.append("")
            for quote in persona.quotes:
                lines.append(f'> "{quote}"')
                lines.append("")

        # Additional fields
        if persona.additional:
            lines.append("## Additional Information")
            lines.append("")
            for key, value in persona.additional.items():
                display_key = key.replace("_", " ").title()
                if isinstance(value, list):
                    lines.append(f"### {display_key}")
                    lines.append("")
                    for item in value:
                        lines.append(f"- {item}")
                    lines.append("")
                else:
                    lines.append(f"- **{display_key}**: {value}")
            lines.append("")

        return "\n".join(lines)

    def extension(self) -> str:
        return ".md"


class TextFormatter(BaseFormatter):
    """Format personas as plain text."""

    def format(self, persona: Persona) -> str:
        """Format persona as plain text."""
        lines = []

        lines.append(f"PERSONA: {persona.name}")
        lines.append(f"ID: {persona.id}")
        lines.append("=" * 50)
        lines.append("")

        if persona.demographics:
            lines.append("DEMOGRAPHICS")
            lines.append("-" * 20)
            for key, value in persona.demographics.items():
                display_key = key.replace("_", " ").title()
                lines.append(f"  {display_key}: {value}")
            lines.append("")

        if persona.goals:
            lines.append("GOALS")
            lines.append("-" * 20)
            for goal in persona.goals:
                lines.append(f"  - {goal}")
            lines.append("")

        if persona.pain_points:
            lines.append("PAIN POINTS")
            lines.append("-" * 20)
            for pain_point in persona.pain_points:
                lines.append(f"  - {pain_point}")
            lines.append("")

        if persona.behaviours:
            lines.append("BEHAVIOURS")
            lines.append("-" * 20)
            for behaviour in persona.behaviours:
                lines.append(f"  - {behaviour}")
            lines.append("")

        if persona.quotes:
            lines.append("QUOTES")
            lines.append("-" * 20)
            for quote in persona.quotes:
                lines.append(f'  "{quote}"')
            lines.append("")

        return "\n".join(lines)

    def extension(self) -> str:
        return ".txt"
