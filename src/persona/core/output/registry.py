"""
Formatter registry for extensible output formatting.

This module provides a plugin architecture for output formatters,
enabling registration of custom formatters and discovery via entry points.
"""

from abc import ABC, abstractmethod
from collections.abc import Callable
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Protocol

from persona.core.generation.parser import Persona


class OutputSection(Enum):
    """Available output sections for persona formatting."""

    DEMOGRAPHICS = "demographics"
    GOALS = "goals"
    PAIN_POINTS = "pain_points"
    BEHAVIOURS = "behaviours"
    MOTIVATIONS = "motivations"
    QUOTES = "quotes"
    EVIDENCE = "evidence"
    REASONING = "reasoning"
    METADATA = "metadata"
    ADDITIONAL = "additional"


@dataclass
class SectionConfig:
    """Configuration for output sections."""

    include: set[OutputSection] = field(
        default_factory=lambda: {
            OutputSection.DEMOGRAPHICS,
            OutputSection.GOALS,
            OutputSection.PAIN_POINTS,
            OutputSection.BEHAVIOURS,
            OutputSection.MOTIVATIONS,
            OutputSection.QUOTES,
        }
    )
    exclude: set[OutputSection] = field(default_factory=set)

    # Presets
    @classmethod
    def minimal(cls) -> "SectionConfig":
        """Minimal output: demographics, goals, pain points only."""
        return cls(
            include={
                OutputSection.DEMOGRAPHICS,
                OutputSection.GOALS,
                OutputSection.PAIN_POINTS,
            }
        )

    @classmethod
    def design(cls) -> "SectionConfig":
        """Design-focused output for UX/design teams."""
        return cls(
            include={
                OutputSection.DEMOGRAPHICS,
                OutputSection.GOALS,
                OutputSection.PAIN_POINTS,
                OutputSection.BEHAVIOURS,
                OutputSection.QUOTES,
            }
        )

    @classmethod
    def research(cls) -> "SectionConfig":
        """Research-focused output with evidence and reasoning."""
        return cls(
            include={
                OutputSection.DEMOGRAPHICS,
                OutputSection.GOALS,
                OutputSection.PAIN_POINTS,
                OutputSection.BEHAVIOURS,
                OutputSection.MOTIVATIONS,
                OutputSection.QUOTES,
                OutputSection.EVIDENCE,
                OutputSection.REASONING,
            }
        )

    @classmethod
    def full(cls) -> "SectionConfig":
        """Full output with all sections."""
        return cls(include=set(OutputSection))

    def should_include(self, section: OutputSection) -> bool:
        """Check if a section should be included in output."""
        if section in self.exclude:
            return False
        return section in self.include


@dataclass
class FormatterInfo:
    """Metadata about a registered formatter."""

    name: str
    description: str
    extension: str
    formatter_class: type["FormatterProtocol"]
    supports_sections: bool = True
    supports_comparison: bool = False


class FormatterProtocol(Protocol):
    """Protocol defining the formatter interface."""

    def format(
        self,
        persona: Persona,
        sections: SectionConfig | None = None,
    ) -> str:
        """Format a single persona to string output."""
        ...

    def format_multiple(
        self,
        personas: list[Persona],
        sections: SectionConfig | None = None,
    ) -> str:
        """Format multiple personas to string output."""
        ...

    def extension(self) -> str:
        """Return the file extension for this format."""
        ...


class BaseFormatterV2(ABC):
    """
    Abstract base class for output formatters (v2).

    This version adds support for section filtering and comparison tables.
    """

    def __init__(self, sections: SectionConfig | None = None) -> None:
        """
        Initialise formatter with section configuration.

        Args:
            sections: Optional section configuration. Defaults to design preset.
        """
        self._sections = sections or SectionConfig.design()

    @abstractmethod
    def format(
        self,
        persona: Persona,
        sections: SectionConfig | None = None,
    ) -> str:
        """
        Format a persona to string output.

        Args:
            persona: The persona to format.
            sections: Optional section override.

        Returns:
            Formatted string representation.
        """
        ...

    def format_multiple(
        self,
        personas: list[Persona],
        sections: SectionConfig | None = None,
    ) -> str:
        """
        Format multiple personas to string output.

        Default implementation concatenates individual formats.
        Override for formats that support comparison views.

        Args:
            personas: List of personas to format.
            sections: Optional section override.

        Returns:
            Formatted string representation.
        """
        effective_sections = sections or self._sections
        return "\n\n---\n\n".join(self.format(p, effective_sections) for p in personas)

    @abstractmethod
    def extension(self) -> str:
        """Return the file extension for this format."""
        ...

    def _get_sections(self, override: SectionConfig | None = None) -> SectionConfig:
        """Get effective section configuration."""
        return override or self._sections


class FormatterRegistry:
    """
    Registry for output formatters.

    Provides plugin architecture for discovering and instantiating formatters.

    Example:
        registry = FormatterRegistry()
        registry.register("json", JSONFormatter, "JSON output", ".json")

        formatter = registry.get("json")
        output = formatter.format(persona)
    """

    def __init__(self) -> None:
        """Initialise the formatter registry."""
        self._formatters: dict[str, FormatterInfo] = {}
        self._register_builtins()

    def _register_builtins(self) -> None:
        """Register built-in formatters."""
        # Defer import to avoid circular dependency
        from persona.core.output.formatters import (
            JSONFormatter,
            MarkdownFormatter,
            TextFormatter,
        )

        self.register(
            name="json",
            formatter_class=JSONFormatter,
            description="JSON format for programmatic use",
            extension=".json",
            supports_sections=False,
        )
        self.register(
            name="markdown",
            formatter_class=MarkdownFormatter,
            description="Markdown format for documentation",
            extension=".md",
            supports_sections=True,
        )
        self.register(
            name="text",
            formatter_class=TextFormatter,
            description="Plain text format for terminal display",
            extension=".txt",
            supports_sections=True,
        )

    def register(
        self,
        name: str,
        formatter_class: type,
        description: str,
        extension: str,
        supports_sections: bool = True,
        supports_comparison: bool = False,
    ) -> None:
        """
        Register a formatter.

        Args:
            name: Unique name for the formatter.
            formatter_class: The formatter class.
            description: Human-readable description.
            extension: File extension (including dot).
            supports_sections: Whether formatter respects section config.
            supports_comparison: Whether formatter supports comparison tables.

        Raises:
            ValueError: If name is already registered.
        """
        if name in self._formatters:
            raise ValueError(f"Formatter '{name}' is already registered")

        self._formatters[name] = FormatterInfo(
            name=name,
            description=description,
            extension=extension,
            formatter_class=formatter_class,
            supports_sections=supports_sections,
            supports_comparison=supports_comparison,
        )

    def unregister(self, name: str) -> None:
        """
        Unregister a formatter.

        Args:
            name: Name of the formatter to remove.

        Raises:
            KeyError: If formatter not found.
        """
        if name not in self._formatters:
            raise KeyError(f"Formatter '{name}' not found")
        del self._formatters[name]

    def get(self, name: str, **kwargs: Any) -> Any:
        """
        Get an instance of a formatter.

        Args:
            name: Name of the formatter.
            **kwargs: Arguments passed to formatter constructor.

        Returns:
            Formatter instance.

        Raises:
            KeyError: If formatter not found.
        """
        if name not in self._formatters:
            raise KeyError(
                f"Formatter '{name}' not found. Available: {self.list_names()}"
            )

        info = self._formatters[name]
        return info.formatter_class(**kwargs)

    def get_info(self, name: str) -> FormatterInfo:
        """
        Get metadata about a formatter.

        Args:
            name: Name of the formatter.

        Returns:
            FormatterInfo with formatter metadata.

        Raises:
            KeyError: If formatter not found.
        """
        if name not in self._formatters:
            raise KeyError(f"Formatter '{name}' not found")
        return self._formatters[name]

    def list_names(self) -> list[str]:
        """
        List all registered formatter names.

        Returns:
            List of formatter names.
        """
        return sorted(self._formatters.keys())

    def list_all(self) -> list[FormatterInfo]:
        """
        List all registered formatters with metadata.

        Returns:
            List of FormatterInfo objects.
        """
        return [self._formatters[name] for name in self.list_names()]

    def has(self, name: str) -> bool:
        """
        Check if a formatter is registered.

        Args:
            name: Name to check.

        Returns:
            True if registered.
        """
        return name in self._formatters


# Global registry instance
_global_registry: FormatterRegistry | None = None


def get_registry() -> FormatterRegistry:
    """
    Get the global formatter registry.

    Returns:
        The global FormatterRegistry instance.
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = FormatterRegistry()
    return _global_registry


def register(
    name: str,
    description: str = "",
    extension: str = ".txt",
    supports_sections: bool = True,
    supports_comparison: bool = False,
) -> Callable[[type], type]:
    """
    Decorator to register a formatter class.

    Example:
        @register("my-format", "My custom format", ".myf")
        class MyFormatter(BaseFormatterV2):
            ...

    Args:
        name: Unique name for the formatter.
        description: Human-readable description.
        extension: File extension (including dot).
        supports_sections: Whether formatter respects section config.
        supports_comparison: Whether formatter supports comparison tables.

    Returns:
        Decorator function.
    """

    def decorator(cls: type) -> type:
        registry = get_registry()
        registry.register(
            name=name,
            formatter_class=cls,
            description=description or f"{cls.__name__} formatter",
            extension=extension,
            supports_sections=supports_sections,
            supports_comparison=supports_comparison,
        )
        return cls

    return decorator
