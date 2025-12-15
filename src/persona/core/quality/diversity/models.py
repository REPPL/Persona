"""
Data models for lexical diversity analysis.

This module provides the core data structures for diversity configuration,
individual reports, and batch analysis results.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class InterpretationLevel(Enum):
    """Interpretation levels for MTLD scores."""

    POOR = "poor"  # < 30
    BELOW_AVERAGE = "below_average"  # 30-50
    AVERAGE = "average"  # 50-70
    GOOD = "good"  # 70-100
    EXCELLENT = "excellent"  # > 100


@dataclass
class DiversityConfig:
    """
    Configuration for lexical diversity analysis.

    Attributes:
        mattr_window_size: Window size for MATTR calculation (default: 50).
        mtld_threshold: TTR threshold for MTLD factor completion (default: 0.72).
        min_tokens: Minimum tokens required for reliable analysis (default: 50).
    """

    mattr_window_size: int = 50
    mtld_threshold: float = 0.72
    min_tokens: int = 50

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return {
            "mattr_window_size": self.mattr_window_size,
            "mtld_threshold": self.mtld_threshold,
            "min_tokens": self.min_tokens,
        }


@dataclass
class DiversityReport:
    """
    Lexical diversity report for a single persona.

    Attributes:
        persona_id: ID of the analysed persona.
        persona_name: Name of the analysed persona.
        total_tokens: Total number of tokens.
        unique_tokens: Number of unique tokens.
        ttr: Type-Token Ratio (0-1).
        mattr: Moving-Average Type-Token Ratio (0-1).
        mtld: Measure of Textual Lexical Diversity.
        hapax_ratio: Ratio of words appearing exactly once (0-1).
        interpretation: Interpretation level based on MTLD.
        token_frequency: Frequency distribution of tokens.
        generated_at: Timestamp of analysis.
    """

    persona_id: str
    persona_name: str
    total_tokens: int
    unique_tokens: int
    ttr: float
    mattr: float
    mtld: float
    hapax_ratio: float
    interpretation: InterpretationLevel
    token_frequency: dict[str, int] = field(default_factory=dict)
    generated_at: str = ""

    def __post_init__(self) -> None:
        """Set generated_at timestamp if not provided."""
        if not self.generated_at:
            self.generated_at = datetime.now().isoformat()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return {
            "persona_id": self.persona_id,
            "persona_name": self.persona_name,
            "total_tokens": self.total_tokens,
            "unique_tokens": self.unique_tokens,
            "ttr": round(self.ttr, 4),
            "mattr": round(self.mattr, 4),
            "mtld": round(self.mtld, 2),
            "hapax_ratio": round(self.hapax_ratio, 4),
            "interpretation": self.interpretation.value,
            "top_tokens": dict(
                sorted(
                    self.token_frequency.items(),
                    key=lambda x: x[1],
                    reverse=True,
                )[:10]
            ),
            "generated_at": self.generated_at,
        }


@dataclass
class BatchDiversityReport:
    """
    Lexical diversity analysis for multiple personas.

    Attributes:
        reports: Individual diversity reports for each persona.
        average_ttr: Mean TTR across all personas.
        average_mattr: Mean MATTR across all personas.
        average_mtld: Mean MTLD across all personas.
        average_hapax_ratio: Mean hapax ratio across all personas.
        generated_at: Timestamp of analysis.
    """

    reports: list[DiversityReport]
    average_ttr: float
    average_mattr: float
    average_mtld: float
    average_hapax_ratio: float
    generated_at: str = ""

    def __post_init__(self) -> None:
        """Set generated_at timestamp if not provided."""
        if not self.generated_at:
            self.generated_at = datetime.now().isoformat()

    @property
    def persona_count(self) -> int:
        """Get number of personas analysed."""
        return len(self.reports)

    def get_by_interpretation(
        self, level: InterpretationLevel
    ) -> list[DiversityReport]:
        """Get all reports with a specific interpretation level."""
        return [r for r in self.reports if r.interpretation == level]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return {
            "persona_count": len(self.reports),
            "average_ttr": round(self.average_ttr, 4),
            "average_mattr": round(self.average_mattr, 4),
            "average_mtld": round(self.average_mtld, 2),
            "average_hapax_ratio": round(self.average_hapax_ratio, 4),
            "individual_reports": [r.to_dict() for r in self.reports],
            "generated_at": self.generated_at,
        }
