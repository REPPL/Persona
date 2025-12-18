"""
Narrative text output formatter for personas.

This module provides formatters that generate flowing narrative prose
descriptions of personas, suitable for presentations and empathy-building.
"""

from dataclasses import dataclass, field
from enum import Enum

from persona.core.generation.parser import Persona
from persona.core.output.registry import (
    BaseFormatterV2,
    OutputSection,
    SectionConfig,
    register,
)


class Perspective(Enum):
    """Narrative perspective options."""

    FIRST_PERSON = "first_person"
    THIRD_PERSON = "third_person"


@dataclass
class NarrativeConfig:
    """Configuration for narrative formatting."""

    perspective: Perspective = Perspective.THIRD_PERSON
    include_day_in_life: bool = True
    include_what_drives: bool = True
    include_challenges: bool = True
    include_quotes: bool = True
    sections: SectionConfig = field(default_factory=SectionConfig.design)


class NarrativeFormatter(BaseFormatterV2):
    """
    Format personas as flowing narrative prose.

    Generates human-readable narrative descriptions suitable for
    presentations, design documentation, and empathy-building workshops.

    Example:
        formatter = NarrativeFormatter(perspective=Perspective.FIRST_PERSON)
        narrative = formatter.format(persona)
    """

    def __init__(
        self,
        perspective: Perspective = Perspective.THIRD_PERSON,
        config: NarrativeConfig | None = None,
        sections: SectionConfig | None = None,
    ) -> None:
        """
        Initialise narrative formatter.

        Args:
            perspective: First-person or third-person narrative.
            config: Full narrative configuration (overrides other args).
            sections: Section configuration for filtering.
        """
        super().__init__(sections=sections)

        if config:
            self._config = config
        else:
            self._config = NarrativeConfig(
                perspective=perspective,
                sections=sections or SectionConfig.design(),
            )

    def format(
        self,
        persona: Persona,
        sections: SectionConfig | None = None,
    ) -> str:
        """
        Format a persona as narrative prose.

        Args:
            persona: The persona to format.
            sections: Optional section override.

        Returns:
            Narrative text description.
        """
        effective_sections = sections or self._config.sections
        lines: list[str] = []

        # Title and introduction
        lines.append(self._format_introduction(persona))
        lines.append("")

        # Demographics as narrative
        if effective_sections.should_include(OutputSection.DEMOGRAPHICS):
            demo_narrative = self._format_demographics_narrative(persona)
            if demo_narrative:
                lines.append(demo_narrative)
                lines.append("")

        # Day in the life
        if self._config.include_day_in_life:
            day_narrative = self._format_day_in_life(persona)
            if day_narrative:
                lines.append(day_narrative)
                lines.append("")

        # What drives them (goals and motivations)
        if self._config.include_what_drives:
            if effective_sections.should_include(
                OutputSection.GOALS
            ) or effective_sections.should_include(OutputSection.MOTIVATIONS):
                drives_narrative = self._format_what_drives(persona, effective_sections)
                if drives_narrative:
                    lines.append(drives_narrative)
                    lines.append("")

        # Challenges (pain points)
        if self._config.include_challenges:
            if effective_sections.should_include(OutputSection.PAIN_POINTS):
                challenges_narrative = self._format_challenges(persona)
                if challenges_narrative:
                    lines.append(challenges_narrative)
                    lines.append("")

        # Quotes
        if self._config.include_quotes:
            if (
                effective_sections.should_include(OutputSection.QUOTES)
                and persona.quotes
            ):
                quotes_narrative = self._format_quotes(persona)
                if quotes_narrative:
                    lines.append(quotes_narrative)
                    lines.append("")

        return "\n".join(lines).strip()

    def format_multiple(
        self,
        personas: list[Persona],
        sections: SectionConfig | None = None,
    ) -> str:
        """
        Format multiple personas as narrative sections.

        Args:
            personas: List of personas to format.
            sections: Optional section override.

        Returns:
            Combined narrative with page breaks.
        """
        effective_sections = sections or self._config.sections
        narratives = [self.format(p, effective_sections) for p in personas]
        return "\n\n---\n\n".join(narratives)

    def extension(self) -> str:
        """Return file extension."""
        return ".md"

    def _format_introduction(self, persona: Persona) -> str:
        """Format the persona introduction."""
        if self._config.perspective == Perspective.FIRST_PERSON:
            return f"# I'm {persona.name}\n"
        else:
            return f"# Meet {persona.name}\n"

    def _format_demographics_narrative(self, persona: Persona) -> str:
        """Format demographics as flowing prose."""
        if not persona.demographics:
            return ""

        parts: list[str] = []
        name = persona.name
        demo = persona.demographics

        # Build demographic description
        age = demo.get("age") or demo.get("age_group") or demo.get("age_range")
        role = demo.get("role") or demo.get("occupation") or demo.get("job_title")
        location = demo.get("location") or demo.get("city") or demo.get("region")
        experience = demo.get("experience") or demo.get("years_experience")

        if self._config.perspective == Perspective.FIRST_PERSON:
            if age:
                parts.append(f"I'm {age} years old")
            if role:
                if parts:
                    parts.append(f"and work as a {role}")
                else:
                    parts.append(f"I work as a {role}")
            if location:
                parts.append(f"based in {location}")
            if experience:
                parts.append(f"with {experience} of experience")
        else:
            if age:
                parts.append(f"{name} is {age}")
            if role:
                if parts:
                    parts.append(f"working as a {role}")
                else:
                    parts.append(f"{name} works as a {role}")
            if location:
                parts.append(f"in {location}")
            if experience:
                parts.append(f"with {experience} of experience")

        if not parts:
            return ""

        return " ".join(parts) + "."

    def _format_day_in_life(self, persona: Persona) -> str:
        """Format a 'day in the life' narrative section."""
        name = persona.name
        behaviours = persona.behaviours or []

        if not behaviours:
            return ""

        if self._config.perspective == Perspective.FIRST_PERSON:
            header = "## A Day in My Life\n\n"
            intro = "My typical day involves "
        else:
            header = f"## A Day in {name}'s Life\n\n"
            intro = f"{name}'s typical day involves "

        # Convert behaviours to narrative
        if len(behaviours) == 1:
            narrative = f"{intro}{behaviours[0].lower()}."
        elif len(behaviours) == 2:
            narrative = f"{intro}{behaviours[0].lower()} and {behaviours[1].lower()}."
        else:
            behaviour_list = ", ".join(b.lower() for b in behaviours[:-1])
            narrative = f"{intro}{behaviour_list}, and {behaviours[-1].lower()}."

        return header + narrative

    def _format_what_drives(
        self,
        persona: Persona,
        sections: SectionConfig,
    ) -> str:
        """Format goals and motivations as narrative."""
        name = persona.name

        if self._config.perspective == Perspective.FIRST_PERSON:
            header = "## What Drives Me\n\n"
        else:
            header = f"## What Drives {name}\n\n"

        parts: list[str] = []

        # Goals
        if sections.should_include(OutputSection.GOALS) and persona.goals:
            if self._config.perspective == Perspective.FIRST_PERSON:
                goals_intro = "At my core, I want to "
            else:
                goals_intro = f"At {name.split()[0] if ' ' in name else name}'s core, the drive is to "

            if len(persona.goals) == 1:
                parts.append(f"{goals_intro}{persona.goals[0].lower()}.")
            else:
                goal_list = self._format_list_as_prose(persona.goals)
                parts.append(f"{goals_intro}{goal_list}.")

        # Motivations (from additional fields)
        motivations = (
            persona.additional.get("motivations", []) if persona.additional else []
        )
        if sections.should_include(OutputSection.MOTIVATIONS) and motivations:
            if self._config.perspective == Perspective.FIRST_PERSON:
                mot_intro = "I'm motivated by "
            else:
                mot_intro = "Key motivations include "

            if isinstance(motivations, list):
                parts.append(f"{mot_intro}{self._format_list_as_prose(motivations)}.")
            else:
                parts.append(f"{mot_intro}{motivations}.")

        if not parts:
            return ""

        return header + " ".join(parts)

    def _format_challenges(self, persona: Persona) -> str:
        """Format pain points as narrative."""
        if not persona.pain_points:
            return ""

        name = persona.name

        if self._config.perspective == Perspective.FIRST_PERSON:
            header = "## My Challenges\n\n"
            intro = "I struggle with "
        else:
            header = f"## {name}'s Challenges\n\n"
            intro = f"{name} struggles with "

        challenge_prose = self._format_list_as_prose(persona.pain_points)
        return header + f"{intro}{challenge_prose}."

    def _format_quotes(self, persona: Persona) -> str:
        """Format quotes as narrative section."""
        if not persona.quotes:
            return ""

        if self._config.perspective == Perspective.FIRST_PERSON:
            header = "## In My Own Words\n\n"
        else:
            header = f"## In {persona.name}'s Own Words\n\n"

        quote_blocks = [f'> "{quote}"' for quote in persona.quotes[:3]]  # Max 3 quotes
        return header + "\n\n".join(quote_blocks)

    def _format_list_as_prose(self, items: list[str]) -> str:
        """Convert a list to prose format."""
        if not items:
            return ""
        if len(items) == 1:
            return items[0].lower()
        if len(items) == 2:
            return f"{items[0].lower()} and {items[1].lower()}"

        # Oxford comma style
        return (
            ", ".join(item.lower() for item in items[:-1])
            + f", and {items[-1].lower()}"
        )


# Register the formatter
@register(
    name="narrative",
    description="Flowing narrative prose format for presentations",
    extension=".md",
    supports_sections=True,
    supports_comparison=False,
)
class RegisteredNarrativeFormatter(NarrativeFormatter):
    """Registered version of NarrativeFormatter."""

    pass


class FirstPersonNarrativeFormatter(NarrativeFormatter):
    """Convenience formatter for first-person narratives."""

    def __init__(
        self,
        config: NarrativeConfig | None = None,
        sections: SectionConfig | None = None,
    ) -> None:
        """Initialise with first-person perspective."""
        super().__init__(
            perspective=Perspective.FIRST_PERSON,
            config=config,
            sections=sections,
        )


class ThirdPersonNarrativeFormatter(NarrativeFormatter):
    """Convenience formatter for third-person narratives."""

    def __init__(
        self,
        config: NarrativeConfig | None = None,
        sections: SectionConfig | None = None,
    ) -> None:
        """Initialise with third-person perspective."""
        super().__init__(
            perspective=Perspective.THIRD_PERSON,
            config=config,
            sections=sections,
        )
