"""
Data models for prompt fidelity scoring.

This module provides data structures for representing fidelity constraints,
violations, configurations, and reports.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class Severity(Enum):
    """Severity level for fidelity violations."""

    CRITICAL = "critical"  # Major structural or constraint violation
    HIGH = "high"  # Significant content or style deviation
    MEDIUM = "medium"  # Minor deviation from requirements
    LOW = "low"  # Negligible or cosmetic issue


@dataclass
class Violation:
    """
    A single fidelity violation.

    Attributes:
        dimension: Which fidelity dimension was violated
                   ("structure", "content", "constraint", "style").
        field: Specific field name that violated (optional).
        description: Human-readable violation description.
        severity: How severe the violation is.
        expected: What was expected (optional).
        actual: What was found (optional).
    """

    dimension: str
    description: str
    severity: Severity
    field: str | None = None
    expected: Any = None
    actual: Any = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return {
            "dimension": self.dimension,
            "field": self.field,
            "description": self.description,
            "severity": self.severity.value,
            "expected": self.expected,
            "actual": self.actual,
        }


@dataclass
class PromptConstraints:
    """
    Constraints to validate against.

    This represents the requirements specified in the original prompt
    that the generated persona should adhere to.

    Attributes:
        required_fields: Fields that must be present and non-empty.
        field_types: Expected types for specific fields (e.g., {"age": "integer"}).
        age_range: Optional (min, max) age constraint.
        goal_count: Optional (min, max) number of goals.
        pain_point_count: Optional (min, max) number of pain points.
        behaviour_count: Optional (min, max) number of behaviours.
        complexity: Optional complexity level ("simple", "detailed", "comprehensive").
        style: Optional style requirement ("professional", "casual", "technical").
        custom_rules: List of custom rules for LLM evaluation.
        required_keywords: Keywords that must appear in specific fields.
        occupation_keywords: Keywords for occupation validation.
        goal_themes: Themes that should appear in goals.
    """

    required_fields: list[str] = field(default_factory=list)
    field_types: dict[str, str] = field(default_factory=dict)
    age_range: tuple[int, int] | None = None
    goal_count: tuple[int, int] | None = None
    pain_point_count: tuple[int, int] | None = None
    behaviour_count: tuple[int, int] | None = None
    complexity: str | None = None
    style: str | None = None
    custom_rules: list[str] = field(default_factory=list)
    required_keywords: dict[str, list[str]] = field(default_factory=dict)
    occupation_keywords: list[str] = field(default_factory=list)
    goal_themes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return {
            "required_fields": self.required_fields,
            "field_types": self.field_types,
            "age_range": self.age_range,
            "goal_count": self.goal_count,
            "pain_point_count": self.pain_point_count,
            "behaviour_count": self.behaviour_count,
            "complexity": self.complexity,
            "style": self.style,
            "custom_rules": self.custom_rules,
            "required_keywords": self.required_keywords,
            "occupation_keywords": self.occupation_keywords,
            "goal_themes": self.goal_themes,
        }


@dataclass
class FidelityConfig:
    """
    Configuration for fidelity scoring.

    Attributes:
        check_structure: Whether to validate structural constraints.
        check_content: Whether to validate content requirements.
        check_constraints: Whether to validate numeric constraints.
        check_style: Whether to validate style adherence.
        use_llm_judge: Whether to use LLM-as-Judge for style evaluation.
        llm_provider: LLM provider to use for style checking (if enabled).
        llm_model: LLM model to use for style checking (if enabled).
    """

    check_structure: bool = True
    check_content: bool = True
    check_constraints: bool = True
    check_style: bool = True
    use_llm_judge: bool = True
    llm_provider: str = "openai"
    llm_model: str = "gpt-4"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return {
            "check_structure": self.check_structure,
            "check_content": self.check_content,
            "check_constraints": self.check_constraints,
            "check_style": self.check_style,
            "use_llm_judge": self.use_llm_judge,
            "llm_provider": self.llm_provider,
            "llm_model": self.llm_model,
        }


@dataclass
class FidelityReport:
    """
    Complete fidelity assessment for a persona.

    Attributes:
        persona_id: ID of the assessed persona.
        persona_name: Name of the assessed persona.
        overall_score: Aggregate fidelity score (0-1).
        structure_score: Structural fidelity score (0-1).
        content_score: Content fidelity score (0-1).
        constraint_score: Constraint adherence score (0-1).
        style_score: Style adherence score (0-1).
        violations: List of all violations found.
        passed: Whether the persona passed fidelity checks.
        generated_at: Timestamp of assessment.
        details: Additional assessment details.
    """

    persona_id: str
    persona_name: str
    overall_score: float
    structure_score: float
    content_score: float
    constraint_score: float
    style_score: float
    violations: list[Violation] = field(default_factory=list)
    passed: bool = True
    generated_at: str = ""
    details: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Set generated_at timestamp if not provided."""
        if not self.generated_at:
            self.generated_at = datetime.now().isoformat()

    @property
    def critical_violations(self) -> list[Violation]:
        """Get all critical violations."""
        return [v for v in self.violations if v.severity == Severity.CRITICAL]

    @property
    def high_violations(self) -> list[Violation]:
        """Get all high severity violations."""
        return [v for v in self.violations if v.severity == Severity.HIGH]

    @property
    def violation_count(self) -> int:
        """Get total violation count."""
        return len(self.violations)

    @property
    def violation_by_dimension(self) -> dict[str, int]:
        """Get violation counts by dimension."""
        counts: dict[str, int] = {}
        for v in self.violations:
            counts[v.dimension] = counts.get(v.dimension, 0) + 1
        return counts

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return {
            "persona_id": self.persona_id,
            "persona_name": self.persona_name,
            "overall_score": round(self.overall_score, 3),
            "structure_score": round(self.structure_score, 3),
            "content_score": round(self.content_score, 3),
            "constraint_score": round(self.constraint_score, 3),
            "style_score": round(self.style_score, 3),
            "violations": [v.to_dict() for v in self.violations],
            "violation_count": self.violation_count,
            "passed": self.passed,
            "generated_at": self.generated_at,
            "details": self.details,
        }
