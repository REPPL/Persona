"""
Output formatting and file management module.

This module provides functionality for formatting and saving
generated personas to various output formats.
"""

from persona.core.output.manager import OutputManager
from persona.core.output.formatters import JSONFormatter, MarkdownFormatter

__all__ = [
    "OutputManager",
    "JSONFormatter",
    "MarkdownFormatter",
]
