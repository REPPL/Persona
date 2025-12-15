"""
Data models for bias and stereotype detection.

This module defines data structures for representing bias detection
configuration, findings, and reports.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class BiasCategory(Enum):
    """Categories of bias that can be detected."""

    GENDER = "gender"  # Gender-based stereotypes
    RACIAL = "racial"  # Race and ethnicity stereotypes
    AGE = "age"  # Age-based stereotypes
    PROFESSIONAL = "professional"  # Occupation-based stereotypes
    INTERSECTIONAL = "intersectional"  # Multiple overlapping biases


class Severity(Enum):
    """Severity level of a bias finding."""

    LOW = "low"  # Minor stereotype or implicit bias
    MEDIUM = "medium"  # Clear stereotype present
    HIGH = "high"  # Harmful or strong stereotype


@dataclass
class BiasConfig:
    """
    Configuration for bias detection.

    Attributes:
        methods: Detection methods to use (lexicon, embedding, llm).
        categories: Bias categories to check for.
        threshold: Confidence threshold for reporting findings (0-1).
        lexicon: Lexicon to use for pattern matching.
        embedding_model: Sentence transformer model for WEAT analysis.
        weat_effect_threshold: WEAT effect size threshold for reporting.
    """

    methods: list[str] = field(
        default_factory=lambda: ["lexicon", "embedding", "llm"]
    )
    categories: list[str] = field(
        default_factory=lambda: ["gender", "racial", "age", "professional"]
    )
    threshold: float = 0.3
    lexicon: str = "holisticbias"
    embedding_model: str = "all-MiniLM-L6-v2"
    weat_effect_threshold: float = 0.5

    def __post_init__(self) -> None:
        """Validate configuration."""
        valid_methods = {"lexicon", "embedding", "llm"}
        for method in self.methods:
            if method not in valid_methods:
                raise ValueError(
                    f"Invalid method '{method}'. "
                    f"Must be one of: {', '.join(valid_methods)}"
                )

        valid_categories = {"gender", "racial", "age", "professional", "intersectional"}
        for category in self.categories:
            if category not in valid_categories:
                raise ValueError(
                    f"Invalid category '{category}'. "
                    f"Must be one of: {', '.join(valid_categories)}"
                )


@dataclass
class BiasFinding:
    """
    A single bias or stereotype finding.

    Attributes:
        category: Category of bias detected.
        description: Human-readable description of the bias.
        evidence: Specific text that exhibits the bias.
        severity: Severity level of the finding.
        method: Detection method that found this bias.
        confidence: Confidence score (0-1).
        context: Additional context from the persona.
    """

    category: BiasCategory
    description: str
    evidence: str
    severity: Severity
    method: str
    confidence: float
    context: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return {
            "category": self.category.value,
            "description": self.description,
            "evidence": self.evidence,
            "severity": self.severity.value,
            "method": self.method,
            "confidence": round(self.confidence, 3),
            "context": self.context,
        }


@dataclass
class BiasReport:
    """
    Complete bias detection report for a persona.

    Attributes:
        persona_id: ID of the evaluated persona.
        persona_name: Name of the evaluated persona.
        overall_score: Overall bias score (0=no bias, 1=high bias).
        findings: List of detected bias findings.
        category_scores: Bias scores by category (0-1).
        methods_used: Detection methods that were applied.
        generated_at: Timestamp of report generation.
    """

    persona_id: str
    persona_name: str | None
    overall_score: float
    findings: list[BiasFinding]
    category_scores: dict[str, float]
    methods_used: list[str]
    generated_at: str = ""

    def __post_init__(self) -> None:
        """Set generated_at timestamp if not provided."""
        if not self.generated_at:
            self.generated_at = datetime.now().isoformat()

    @property
    def has_bias(self) -> bool:
        """Check if any bias was detected."""
        return len(self.findings) > 0

    @property
    def high_severity_count(self) -> int:
        """Count of high-severity findings."""
        return sum(1 for f in self.findings if f.severity == Severity.HIGH)

    @property
    def medium_severity_count(self) -> int:
        """Count of medium-severity findings."""
        return sum(1 for f in self.findings if f.severity == Severity.MEDIUM)

    @property
    def low_severity_count(self) -> int:
        """Count of low-severity findings."""
        return sum(1 for f in self.findings if f.severity == Severity.LOW)

    def get_findings_by_category(self, category: BiasCategory) -> list[BiasFinding]:
        """Get all findings for a specific category."""
        return [f for f in self.findings if f.category == category]

    def get_findings_by_severity(self, severity: Severity) -> list[BiasFinding]:
        """Get all findings at a specific severity level."""
        return [f for f in self.findings if f.severity == severity]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return {
            "persona_id": self.persona_id,
            "persona_name": self.persona_name,
            "overall_score": round(self.overall_score, 3),
            "has_bias": self.has_bias,
            "total_findings": len(self.findings),
            "high_severity_count": self.high_severity_count,
            "medium_severity_count": self.medium_severity_count,
            "low_severity_count": self.low_severity_count,
            "category_scores": {
                k: round(v, 3) for k, v in self.category_scores.items()
            },
            "findings": [f.to_dict() for f in self.findings],
            "methods_used": self.methods_used,
            "generated_at": self.generated_at,
        }
