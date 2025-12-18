"""
Unit tests for evaluation criteria.
"""

import pytest
from persona.core.evaluation.criteria import (
    BATCH_CRITERIA,
    COMPREHENSIVE_CRITERIA,
    DEFAULT_CRITERIA,
    EvaluationCriteria,
)


class TestEvaluationCriteria:
    """Test EvaluationCriteria enum."""

    def test_criteria_values(self):
        """Test that all criteria have correct values."""
        assert EvaluationCriteria.COHERENCE.value == "coherence"
        assert EvaluationCriteria.REALISM.value == "realism"
        assert EvaluationCriteria.USEFULNESS.value == "usefulness"
        assert EvaluationCriteria.DISTINCTIVENESS.value == "distinctiveness"
        assert EvaluationCriteria.COMPLETENESS.value == "completeness"
        assert EvaluationCriteria.SPECIFICITY.value == "specificity"

    def test_criteria_descriptions(self):
        """Test that all criteria have descriptions."""
        for criterion in EvaluationCriteria:
            assert isinstance(criterion.description, str)
            assert len(criterion.description) > 0

    def test_requires_batch(self):
        """Test requires_batch property."""
        assert EvaluationCriteria.DISTINCTIVENESS.requires_batch is True
        assert EvaluationCriteria.COHERENCE.requires_batch is False
        assert EvaluationCriteria.REALISM.requires_batch is False
        assert EvaluationCriteria.USEFULNESS.requires_batch is False
        assert EvaluationCriteria.COMPLETENESS.requires_batch is False
        assert EvaluationCriteria.SPECIFICITY.requires_batch is False

    def test_default_criteria(self):
        """Test default criteria set."""
        assert len(DEFAULT_CRITERIA) == 3
        assert EvaluationCriteria.COHERENCE in DEFAULT_CRITERIA
        assert EvaluationCriteria.REALISM in DEFAULT_CRITERIA
        assert EvaluationCriteria.USEFULNESS in DEFAULT_CRITERIA

    def test_comprehensive_criteria(self):
        """Test comprehensive criteria set."""
        assert len(COMPREHENSIVE_CRITERIA) == 5
        assert EvaluationCriteria.COHERENCE in COMPREHENSIVE_CRITERIA
        assert EvaluationCriteria.REALISM in COMPREHENSIVE_CRITERIA
        assert EvaluationCriteria.USEFULNESS in COMPREHENSIVE_CRITERIA
        assert EvaluationCriteria.COMPLETENESS in COMPREHENSIVE_CRITERIA
        assert EvaluationCriteria.SPECIFICITY in COMPREHENSIVE_CRITERIA

    def test_batch_criteria(self):
        """Test batch criteria set."""
        assert len(BATCH_CRITERIA) == 4
        assert EvaluationCriteria.COHERENCE in BATCH_CRITERIA
        assert EvaluationCriteria.REALISM in BATCH_CRITERIA
        assert EvaluationCriteria.USEFULNESS in BATCH_CRITERIA
        assert EvaluationCriteria.DISTINCTIVENESS in BATCH_CRITERIA

    def test_from_string(self):
        """Test creating criteria from string values."""
        assert EvaluationCriteria("coherence") == EvaluationCriteria.COHERENCE
        assert EvaluationCriteria("realism") == EvaluationCriteria.REALISM
        assert EvaluationCriteria("usefulness") == EvaluationCriteria.USEFULNESS

    def test_invalid_criterion(self):
        """Test that invalid criterion raises error."""
        with pytest.raises(ValueError):
            EvaluationCriteria("invalid")
