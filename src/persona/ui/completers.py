"""
Shell completion helpers for Persona CLI (F-095).

Provides custom completers for provider names, model IDs, and output formats.
"""

from collections.abc import Iterator
from typing import Optional

import typer

from persona.core.cost import PricingData


def complete_provider(incomplete: str) -> Iterator[tuple[str, str]]:
    """Complete provider names.

    Args:
        incomplete: The partial string to complete.

    Yields:
        Tuples of (value, help_text) for matching providers.
    """
    providers = [
        ("anthropic", "Claude models from Anthropic"),
        ("openai", "GPT models from OpenAI"),
        ("gemini", "Gemini models from Google"),
    ]

    for value, help_text in providers:
        if value.startswith(incomplete.lower()):
            yield value, help_text


def complete_model(
    ctx: Optional[typer.Context] = None, incomplete: str = ""
) -> Iterator[tuple[str, str]]:
    """Complete model names based on selected provider.

    Args:
        ctx: Typer context containing parsed parameters (optional).
        incomplete: The partial string to complete.

    Yields:
        Tuples of (value, help_text) for matching models.
    """
    # Get provider from context if available
    provider: Optional[str] = None
    if ctx is not None and ctx.params:
        provider = ctx.params.get("provider")

    # Get all models or filter by provider
    for pricing in PricingData.list_models(provider=provider):
        if pricing.model.startswith(incomplete) or incomplete == "":
            help_text = f"{pricing.provider} - ${float(pricing.input_price):.2f}/M in"
            yield pricing.model, help_text


def complete_format(incomplete: str) -> Iterator[tuple[str, str]]:
    """Complete output format names.

    Args:
        incomplete: The partial string to complete.

    Yields:
        Tuples of (value, help_text) for matching formats.
    """
    formats = [
        ("json", "Structured JSON output"),
        ("markdown", "Human-readable markdown"),
        ("yaml", "YAML configuration format"),
    ]

    for value, help_text in formats:
        if value.startswith(incomplete.lower()):
            yield value, help_text


def complete_workflow(incomplete: str) -> Iterator[tuple[str, str]]:
    """Complete workflow names.

    Args:
        incomplete: The partial string to complete.

    Yields:
        Tuples of (value, help_text) for matching workflows.
    """
    workflows = [
        ("default", "Balanced generation workflow"),
        ("research", "Detailed, methodical research workflow"),
        ("quick", "Fast, minimal generation"),
    ]

    for value, help_text in workflows:
        if value.startswith(incomplete.lower()):
            yield value, help_text


def complete_complexity(incomplete: str) -> Iterator[tuple[str, str]]:
    """Complete complexity level names.

    Args:
        incomplete: The partial string to complete.

    Yields:
        Tuples of (value, help_text) for matching complexity levels.
    """
    levels = [
        ("simple", "Basic demographics, minimal detail"),
        ("moderate", "Balanced detail (default)"),
        ("complex", "Rich backgrounds, detailed attributes"),
    ]

    for value, help_text in levels:
        if value.startswith(incomplete.lower()):
            yield value, help_text


def complete_detail_level(incomplete: str) -> Iterator[tuple[str, str]]:
    """Complete detail level names.

    Args:
        incomplete: The partial string to complete.

    Yields:
        Tuples of (value, help_text) for matching detail levels.
    """
    levels = [
        ("minimal", "Bullet points, key facts only"),
        ("standard", "Short paragraphs (default)"),
        ("detailed", "Full narratives, examples"),
    ]

    for value, help_text in levels:
        if value.startswith(incomplete.lower()):
            yield value, help_text


def complete_log_level(incomplete: str) -> Iterator[tuple[str, str]]:
    """Complete log level names.

    Args:
        incomplete: The partial string to complete.

    Yields:
        Tuples of (value, help_text) for matching log levels.
    """
    levels = [
        ("debug", "Most verbose logging"),
        ("info", "Standard logging (default)"),
        ("warning", "Warnings and errors only"),
        ("error", "Errors only"),
    ]

    for value, help_text in levels:
        if value.startswith(incomplete.lower()):
            yield value, help_text
