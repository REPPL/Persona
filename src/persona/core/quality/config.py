"""
Configuration for persona quality scoring.

This module provides configurable thresholds and weights
for quality assessment.
"""

from dataclasses import dataclass, field


@dataclass
class QualityConfig:
    """
    Configuration for quality scoring.

    Attributes:
        weights: Weight for each dimension (must sum to 1.0).
        required_fields: Fields that must be present.
        expected_fields: Fields that should be populated.
        min_goals: Minimum number of goals expected.
        min_pain_points: Minimum number of pain points expected.
        min_behaviours: Minimum number of behaviours expected.
        min_quotes: Minimum number of quotes expected.
        max_similarity_threshold: Maximum similarity before personas are too alike.
        excellent_threshold: Minimum score for 'excellent' level.
        good_threshold: Minimum score for 'good' level.
        acceptable_threshold: Minimum score for 'acceptable' level.
        poor_threshold: Minimum score for 'poor' level.
    """

    # Dimension weights (must sum to 1.0)
    weights: dict[str, float] = field(default_factory=lambda: {
        "completeness": 0.25,
        "consistency": 0.20,
        "evidence_strength": 0.25,
        "distinctiveness": 0.15,
        "realism": 0.15,
    })

    # Completeness thresholds
    required_fields: list[str] = field(default_factory=lambda: ["id", "name"])
    expected_fields: list[str] = field(default_factory=lambda: [
        "demographics", "goals", "pain_points", "behaviours", "quotes"
    ])
    min_goals: int = 2
    min_pain_points: int = 1
    min_behaviours: int = 1
    min_quotes: int = 1

    # Evidence thresholds
    min_evidence_coverage: float = 0.5  # 50% of attributes should have evidence

    # Distinctiveness thresholds
    max_similarity_threshold: float = 0.70  # >70% similar is too similar

    # Score level thresholds
    excellent_threshold: int = 90
    good_threshold: int = 75
    acceptable_threshold: int = 60
    poor_threshold: int = 40

    def validate(self) -> list[str]:
        """
        Validate configuration.

        Returns:
            List of validation errors (empty if valid).
        """
        errors = []

        # Check weights sum to 1.0
        weight_sum = sum(self.weights.values())
        if abs(weight_sum - 1.0) > 0.01:
            errors.append(f"Weights must sum to 1.0, got {weight_sum}")

        # Check thresholds are ordered correctly
        if not (self.excellent_threshold > self.good_threshold >
                self.acceptable_threshold > self.poor_threshold):
            errors.append("Thresholds must be in descending order")

        # Check numeric ranges
        if not 0 <= self.min_evidence_coverage <= 1:
            errors.append("min_evidence_coverage must be between 0 and 1")

        if not 0 <= self.max_similarity_threshold <= 1:
            errors.append("max_similarity_threshold must be between 0 and 1")

        return errors

    @classmethod
    def strict(cls) -> "QualityConfig":
        """Create strict configuration with higher thresholds."""
        return cls(
            min_goals=3,
            min_pain_points=2,
            min_behaviours=2,
            min_quotes=2,
            min_evidence_coverage=0.7,
            max_similarity_threshold=0.50,
            excellent_threshold=95,
            good_threshold=85,
            acceptable_threshold=70,
            poor_threshold=50,
        )

    @classmethod
    def lenient(cls) -> "QualityConfig":
        """Create lenient configuration with lower thresholds."""
        return cls(
            min_goals=1,
            min_pain_points=1,
            min_behaviours=0,
            min_quotes=0,
            min_evidence_coverage=0.3,
            max_similarity_threshold=0.80,
            excellent_threshold=85,
            good_threshold=70,
            acceptable_threshold=50,
            poor_threshold=30,
        )
