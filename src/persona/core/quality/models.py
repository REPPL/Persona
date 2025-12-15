"""
Data models for persona quality scoring.

This module provides the core data structures for representing
quality scores and assessment results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class QualityLevel(Enum):
    """Quality level classification based on overall score."""

    EXCELLENT = "excellent"  # 90-100
    GOOD = "good"  # 75-89
    ACCEPTABLE = "acceptable"  # 60-74
    POOR = "poor"  # 40-59
    FAILING = "failing"  # 0-39


@dataclass
class DimensionScore:
    """
    Score for a single quality dimension.

    Attributes:
        dimension: Name of the dimension (e.g., 'completeness').
        score: Raw score from 0-100.
        weight: Weight factor for overall score calculation (0-1).
        issues: List of issues found during evaluation.
        details: Additional evaluation details.
    """

    dimension: str
    score: float
    weight: float
    issues: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)

    @property
    def weighted_score(self) -> float:
        """Calculate weighted contribution to overall score."""
        return self.score * self.weight

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return {
            "dimension": self.dimension,
            "score": round(self.score, 2),
            "weight": self.weight,
            "weighted_contribution": round(self.weighted_score, 2),
            "issues": self.issues,
            "details": self.details,
        }


@dataclass
class QualityScore:
    """
    Complete quality assessment for a single persona.

    Attributes:
        persona_id: ID of the assessed persona.
        persona_name: Name of the assessed persona.
        overall_score: Weighted aggregate score (0-100).
        level: Quality level classification.
        dimensions: Scores for each quality dimension.
        generated_at: Timestamp of assessment.
    """

    persona_id: str
    persona_name: str
    overall_score: float
    level: QualityLevel
    dimensions: dict[str, DimensionScore] = field(default_factory=dict)
    generated_at: str = ""

    def __post_init__(self) -> None:
        """Set generated_at timestamp if not provided."""
        if not self.generated_at:
            self.generated_at = datetime.now().isoformat()

    @property
    def completeness(self) -> DimensionScore | None:
        """Get completeness dimension score."""
        return self.dimensions.get("completeness")

    @property
    def consistency(self) -> DimensionScore | None:
        """Get consistency dimension score."""
        return self.dimensions.get("consistency")

    @property
    def evidence_strength(self) -> DimensionScore | None:
        """Get evidence strength dimension score."""
        return self.dimensions.get("evidence_strength")

    @property
    def distinctiveness(self) -> DimensionScore | None:
        """Get distinctiveness dimension score."""
        return self.dimensions.get("distinctiveness")

    @property
    def realism(self) -> DimensionScore | None:
        """Get realism dimension score."""
        return self.dimensions.get("realism")

    @property
    def all_issues(self) -> list[str]:
        """Get all issues across all dimensions."""
        issues = []
        for dim in self.dimensions.values():
            issues.extend(dim.issues)
        return issues

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return {
            "persona_id": self.persona_id,
            "persona_name": self.persona_name,
            "overall_score": round(self.overall_score, 2),
            "level": self.level.value,
            "dimensions": {k: v.to_dict() for k, v in self.dimensions.items()},
            "generated_at": self.generated_at,
        }


@dataclass
class BatchQualityResult:
    """
    Quality assessment for multiple personas.

    Attributes:
        scores: Individual quality scores for each persona.
        average_score: Mean overall score across all personas.
        average_by_dimension: Mean scores by dimension.
        distinctiveness_matrix: NxN similarity matrix for persona pairs.
        generated_at: Timestamp of assessment.
    """

    scores: list[QualityScore]
    average_score: float
    average_by_dimension: dict[str, float]
    distinctiveness_matrix: list[list[float]] = field(default_factory=list)
    generated_at: str = ""

    def __post_init__(self) -> None:
        """Set generated_at timestamp if not provided."""
        if not self.generated_at:
            self.generated_at = datetime.now().isoformat()

    @property
    def persona_count(self) -> int:
        """Get number of personas assessed."""
        return len(self.scores)

    @property
    def passing_count(self) -> int:
        """Get count of personas with acceptable or better quality."""
        return sum(
            1 for s in self.scores
            if s.level in (QualityLevel.EXCELLENT, QualityLevel.GOOD, QualityLevel.ACCEPTABLE)
        )

    @property
    def failing_count(self) -> int:
        """Get count of personas with poor or failing quality."""
        return sum(
            1 for s in self.scores
            if s.level in (QualityLevel.POOR, QualityLevel.FAILING)
        )

    def get_by_level(self, level: QualityLevel) -> list[QualityScore]:
        """Get all scores with a specific quality level."""
        return [s for s in self.scores if s.level == level]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return {
            "persona_count": len(self.scores),
            "average_score": round(self.average_score, 2),
            "average_by_dimension": {
                k: round(v, 2) for k, v in self.average_by_dimension.items()
            },
            "passing_count": self.passing_count,
            "failing_count": self.failing_count,
            "individual_scores": [s.to_dict() for s in self.scores],
            "distinctiveness_matrix": [
                [round(v, 2) for v in row] for row in self.distinctiveness_matrix
            ],
            "generated_at": self.generated_at,
        }
