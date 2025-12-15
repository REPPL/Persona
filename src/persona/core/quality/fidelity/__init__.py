"""
Prompt fidelity scoring for persona generation.

This module provides comprehensive fidelity assessment, measuring how well
generated personas adhere to prompt instructions, constraints, and style
requirements across multiple dimensions.

Example:
    >>> from persona.core.quality.fidelity import FidelityScorer, PromptConstraints
    >>> from persona.core.generation.parser import Persona
    >>>
    >>> constraints = PromptConstraints(
    ...     required_fields=["name", "age", "goals"],
    ...     age_range=(25, 45),
    ...     goal_count=(3, 5),
    ... )
    >>>
    >>> scorer = FidelityScorer()
    >>> report = scorer.score(persona, constraints)
    >>> print(f"Fidelity: {report.overall_score:.2%}")
    >>> print(f"Passed: {report.passed}")
"""

from persona.core.quality.fidelity.constraints import ConstraintValidator
from persona.core.quality.fidelity.content import ContentChecker
from persona.core.quality.fidelity.dsl import ConstraintParser
from persona.core.quality.fidelity.models import (
    FidelityConfig,
    FidelityReport,
    PromptConstraints,
    Severity,
    Violation,
)
from persona.core.quality.fidelity.schema import SchemaValidator
from persona.core.quality.fidelity.scorer import FidelityScorer
from persona.core.quality.fidelity.style import StyleChecker

__all__ = [
    # Core classes
    "FidelityScorer",
    "FidelityReport",
    "FidelityConfig",
    "PromptConstraints",
    "Violation",
    "Severity",
    # Validators
    "SchemaValidator",
    "ContentChecker",
    "ConstraintValidator",
    "StyleChecker",
    # DSL parser
    "ConstraintParser",
]
