"""
Evaluation criteria for persona quality assessment.

This module defines the criteria used by LLM judges to evaluate
persona quality. Each criterion measures a specific aspect of
persona usefulness and believability.
"""

from enum import Enum


class EvaluationCriteria(str, Enum):
    """
    Criteria for evaluating persona quality.

    Each criterion measures a specific aspect of persona quality,
    scored from 0.0 to 1.0 by an LLM judge.
    """

    COHERENCE = "coherence"
    """Internal consistency: Do demographics, goals, behaviours, and quotes fit together?"""

    REALISM = "realism"
    """Believability: Could this be a real person with plausible details?"""

    USEFULNESS = "usefulness"
    """Design value: Would this persona help designers make better decisions?"""

    DISTINCTIVENESS = "distinctiveness"
    """Uniqueness: Is this meaningfully different from other personas? (Batch evaluation only)"""

    COMPLETENESS = "completeness"
    """Coverage: Are all expected attributes present with sufficient detail?"""

    SPECIFICITY = "specificity"
    """Concreteness: Are details specific rather than generic?"""

    @property
    def description(self) -> str:
        """Get human-readable description of the criterion."""
        descriptions = {
            self.COHERENCE: "Do demographics, goals, behaviours, and quotes fit together logically?",
            self.REALISM: "Could this be a believable real person? Are details plausible?",
            self.USEFULNESS: "Would this persona help designers make better decisions?",
            self.DISTINCTIVENESS: "Is this persona meaningfully different from others in the set?",
            self.COMPLETENESS: "Are all expected attributes present with sufficient detail?",
            self.SPECIFICITY: "Are details specific and concrete rather than generic?",
        }
        return descriptions[self]

    @property
    def requires_batch(self) -> bool:
        """Check if this criterion requires batch context for evaluation."""
        return self == self.DISTINCTIVENESS


# Default criteria sets
DEFAULT_CRITERIA = [
    EvaluationCriteria.COHERENCE,
    EvaluationCriteria.REALISM,
    EvaluationCriteria.USEFULNESS,
]

COMPREHENSIVE_CRITERIA = [
    EvaluationCriteria.COHERENCE,
    EvaluationCriteria.REALISM,
    EvaluationCriteria.USEFULNESS,
    EvaluationCriteria.COMPLETENESS,
    EvaluationCriteria.SPECIFICITY,
]

BATCH_CRITERIA = [
    EvaluationCriteria.COHERENCE,
    EvaluationCriteria.REALISM,
    EvaluationCriteria.USEFULNESS,
    EvaluationCriteria.DISTINCTIVENESS,
]
