"""
Output formatters for conversation scripts.

This module provides formatters for outputting character cards
in various formats: JSON/YAML, system prompt, and Jinja2 template.
"""

from abc import ABC, abstractmethod
from typing import Any

from jinja2 import Environment, BaseLoader

from persona.core.scripts.models import CharacterCard, ScriptFormat


class BaseScriptFormatter(ABC):
    """Abstract base class for script formatters."""

    @abstractmethod
    def format(self, card: CharacterCard) -> str:
        """Format a character card to string output."""
        ...

    @abstractmethod
    def extension(self) -> str:
        """Return the file extension for this format."""
        ...


class CharacterCardFormatter(BaseScriptFormatter):
    """
    Format character cards as JSON or YAML.

    This is the default format, providing a structured
    representation of the character.
    """

    def __init__(self, use_yaml: bool = False) -> None:
        """
        Initialise formatter.

        Args:
            use_yaml: If True, output YAML instead of JSON.
        """
        self._use_yaml = use_yaml

    def format(self, card: CharacterCard) -> str:
        """Format character card as JSON or YAML."""
        if self._use_yaml:
            return card.to_yaml()
        return card.to_json()

    def extension(self) -> str:
        return ".yaml" if self._use_yaml else ".json"


class SystemPromptFormatter(BaseScriptFormatter):
    """
    Format character cards as system prompts.

    Creates a comprehensive system prompt suitable for
    direct use with LLM APIs.
    """

    def __init__(self, include_synthetic_marker: bool = True) -> None:
        """
        Initialise formatter.

        Args:
            include_synthetic_marker: Whether to include synthetic marker.
        """
        self._include_marker = include_synthetic_marker

    def format(self, card: CharacterCard) -> str:
        """Format character card as system prompt."""
        lines = []

        # Opening
        lines.append(f"You are {card.identity.name}, {card.identity.title}.")
        lines.append("")

        if card.identity.demographics_summary:
            lines.append(f"**Background**: {card.identity.demographics_summary}")
            lines.append("")

        # Personality section
        lines.append("## Personality Traits")
        for trait in card.psychological_profile.personality_traits:
            lines.append(f"- {trait}")
        if card.psychological_profile.flaws:
            lines.append("")
            lines.append("**Character flaws** (express these naturally):")
            for flaw in card.psychological_profile.flaws:
                lines.append(f"- {flaw}")
        lines.append("")

        # Goals section
        if card.psychological_profile.goals:
            lines.append("## What Drives You")
            for goal in card.psychological_profile.goals:
                lines.append(f"- {goal}")
            lines.append("")

        # Motivations section
        if card.psychological_profile.motivations:
            lines.append("## Core Motivations")
            for mot in card.psychological_profile.motivations:
                lines.append(f"- {mot}")
            lines.append("")

        # Pain points section
        if card.psychological_profile.pain_points:
            lines.append("## Frustrations")
            lines.append("You experience these frustrations (express them when relevant):")
            for pain in card.psychological_profile.pain_points:
                lines.append(f"- {pain}")
            lines.append("")

        # Communication style section
        lines.append("## Communication Style")
        lines.append(f"**Tone**: {card.communication_style.tone}")
        lines.append(f"**Vocabulary Level**: {card.communication_style.vocabulary_level}")
        if card.communication_style.speech_patterns:
            lines.append("")
            lines.append("**Speech patterns**:")
            for pattern in card.communication_style.speech_patterns:
                lines.append(f"- {pattern}")
        lines.append("")

        # Knowledge boundaries section
        lines.append("## Knowledge Boundaries")
        lines.append("")
        lines.append("**You know about**:")
        for item in card.knowledge_boundaries.knows:
            lines.append(f"- {item}")
        lines.append("")
        lines.append("**You DON'T know about** (admit uncertainty):")
        for item in card.knowledge_boundaries.doesnt_know:
            lines.append(f"- {item}")
        if card.knowledge_boundaries.can_infer:
            lines.append("")
            lines.append("**You can reasonably infer** (but mark as inference):")
            for item in card.knowledge_boundaries.can_infer:
                lines.append(f"- {item}")
        lines.append("")

        # Guidelines section
        lines.append("## Response Guidelines")
        lines.append(f"- {card.guidelines.response_style}")
        lines.append(f"- {card.guidelines.uncertainty_handling}")
        lines.append(f"- {card.guidelines.character_maintenance}")
        for rule in card.guidelines.additional_rules:
            lines.append(f"- {rule}")
        lines.append("")

        # Synthetic marker
        if self._include_marker:
            lines.append("---")
            lines.append(f"[{card.provenance.synthetic_marker}]")

        return "\n".join(lines)

    def extension(self) -> str:
        return ".txt"


class Jinja2TemplateFormatter(BaseScriptFormatter):
    """
    Format character cards as Jinja2 templates.

    Creates a template that can be rendered with additional
    context like conversation history.
    """

    DEFAULT_TEMPLATE = '''You are {{ identity.name }}{% if identity.title %}, {{ identity.title }}{% endif %}.

{% if identity.demographics_summary %}
Background: {{ identity.demographics_summary }}
{% endif %}

## Core Traits
{% for trait in psychological_profile.personality_traits %}
- {{ trait }}
{% endfor %}

{% if psychological_profile.flaws %}
## Character Flaws
{% for flaw in psychological_profile.flaws %}
- {{ flaw }}
{% endfor %}
{% endif %}

{% if psychological_profile.goals %}
## Goals
{% for goal in psychological_profile.goals %}
- {{ goal }}
{% endfor %}
{% endif %}

{% if psychological_profile.pain_points %}
## Frustrations
{% for pain in psychological_profile.pain_points %}
- {{ pain }}
{% endfor %}
{% endif %}

## Communication Style
Tone: {{ communication_style.tone }}
Vocabulary: {{ communication_style.vocabulary_level }}
{% for pattern in communication_style.speech_patterns %}
- {{ pattern }}
{% endfor %}

## Knowledge Boundaries
Knows: {{ knowledge_boundaries.knows | join(", ") }}
Doesn't know: {{ knowledge_boundaries.doesnt_know | join(", ") }}
{% if knowledge_boundaries.can_infer %}
Can infer: {{ knowledge_boundaries.can_infer | join(", ") }}
{% endif %}

## Guidelines
{{ guidelines.response_style }}
{{ guidelines.uncertainty_handling }}

{% if context %}
---
Current context: {{ context }}
{% endif %}

{% if conversation_history %}
---
Previous messages:
{% for msg in conversation_history %}
{{ msg.role }}: {{ msg.content }}
{% endfor %}
{% endif %}

[{{ provenance.synthetic_marker }}]
'''

    def __init__(self, custom_template: str | None = None) -> None:
        """
        Initialise formatter.

        Args:
            custom_template: Optional custom Jinja2 template.
        """
        self._template_str = custom_template or self.DEFAULT_TEMPLATE

    def format(self, card: CharacterCard) -> str:
        """Return the Jinja2 template (not rendered)."""
        return self._template_str

    def render(
        self,
        card: CharacterCard,
        context: str = "",
        conversation_history: list[dict[str, str]] | None = None,
    ) -> str:
        """
        Render the template with a character card and context.

        Args:
            card: The character card to render.
            context: Optional context for the conversation.
            conversation_history: Optional list of previous messages.

        Returns:
            Rendered template string.
        """
        env = Environment(loader=BaseLoader())
        template = env.from_string(self._template_str)

        card_dict = card.to_dict()
        return template.render(
            **card_dict,
            context=context,
            conversation_history=conversation_history or [],
        )

    def extension(self) -> str:
        return ".j2"

    def get_template(self) -> str:
        """Get the raw template string."""
        return self._template_str


def get_formatter(format: ScriptFormat, **kwargs: Any) -> BaseScriptFormatter:
    """
    Get a formatter for the specified format.

    Args:
        format: The script format.
        **kwargs: Additional arguments for the formatter.

    Returns:
        Appropriate formatter instance.
    """
    if format == ScriptFormat.CHARACTER_CARD:
        return CharacterCardFormatter(**kwargs)
    elif format == ScriptFormat.SYSTEM_PROMPT:
        return SystemPromptFormatter(**kwargs)
    elif format == ScriptFormat.JINJA2_TEMPLATE:
        return Jinja2TemplateFormatter(**kwargs)
    else:
        return CharacterCardFormatter(**kwargs)
