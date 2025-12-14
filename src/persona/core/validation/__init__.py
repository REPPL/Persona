"""
Persona validation module.

This module provides functionality for validating generated personas
against quality criteria and data consistency checks.
"""

from persona.core.validation.validator import (
    PersonaValidator,
    ValidationResult,
    ValidationRule,
)

__all__ = [
    "PersonaValidator",
    "ValidationResult",
    "ValidationRule",
]
