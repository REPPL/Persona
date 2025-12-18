"""
Persona templates module.

This module provides template functionality for generating personas
in different domain-specific formats.
"""

from persona.core.templates.manager import (
    PersonaTemplate,
    TemplateCategory,
    TemplateField,
    TemplateManager,
)

__all__ = [
    "TemplateManager",
    "PersonaTemplate",
    "TemplateField",
    "TemplateCategory",
]
