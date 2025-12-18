"""Tests for AcademicValidator orchestrator."""

import pytest
from persona.core.generation.parser import Persona
from persona.core.quality.academic.validator import (
    AcademicValidator,
    validate_persona,
    validate_personas,
)


class TestAcademicValidator:
    """Tests for AcademicValidator."""

    @pytest.fixture
    def validator(self):
        """Create an academic validator."""
        return AcademicValidator()

    @pytest.fixture
    def sample_persona(self):
        """Create a sample persona."""
        return Persona(
            id="p1",
            name="Sarah",
            demographics={"age": "32", "occupation": "software engineer"},
            goals=["Build scalable systems"],
            pain_points=["Technical debt"],
        )

    @pytest.fixture
    def source_data(self):
        """Create sample source data."""
        return """
        Sarah is a 32-year-old software engineer who loves building scalable systems.
        She struggles with technical debt and legacy code.
        """

    def test_validate_with_rouge_only(self, validator, sample_persona, source_data):
        """Test validation with only ROUGE-L metric."""
        report = validator.validate(
            sample_persona, source_data=source_data, metrics=["rouge_l"]
        )

        assert report.persona_id == "p1"
        assert report.persona_name == "Sarah"
        assert report.has_rouge_l
        assert not report.has_bertscore
        assert not report.has_gpt_similarity
        assert not report.has_geval
        assert "rouge_l" in report.metrics_used

    def test_validate_missing_source_data(self, validator, sample_persona):
        """Test validation fails when source data required but missing."""
        with pytest.raises(ValueError, match="require source_data"):
            validator.validate(sample_persona, metrics=["rouge_l"])

    def test_validate_geval_without_source(self, validator, sample_persona):
        """Test G-eval can run without source data."""
        report = validator.validate(sample_persona, metrics=["geval"])

        # G-eval doesn't require source data
        assert report.persona_id == "p1"
        assert "geval" in report.metrics_used

    def test_validate_batch(self, validator, source_data):
        """Test batch validation."""
        personas = [
            Persona(id="p1", name="Sarah", goals=["Goal 1"]),
            Persona(id="p2", name="John", goals=["Goal 2"]),
        ]

        batch_report = validator.validate_batch(
            personas, source_data=source_data, metrics=["rouge_l"]
        )

        assert batch_report.persona_count == 2
        assert len(batch_report.reports) == 2
        assert batch_report.average_overall >= 0

    def test_validate_batch_empty_list(self, validator):
        """Test batch validation with empty persona list."""
        with pytest.raises(ValueError, match="At least one persona"):
            validator.validate_batch([])

    def test_overall_score_calculation(self, validator, sample_persona, source_data):
        """Test overall score is calculated from available metrics."""
        report = validator.validate(
            sample_persona, source_data=source_data, metrics=["rouge_l"]
        )

        # Overall score should be computed
        assert report.overall_score > 0
        # Should match ROUGE-L F-measure scaled to 0-100
        if report.rouge_l:
            expected = report.rouge_l.fmeasure * 100
            assert report.overall_score == pytest.approx(expected, rel=0.01)

    def test_to_dict_serialization(self, validator, sample_persona, source_data):
        """Test report serialisation to dict."""
        report = validator.validate(
            sample_persona, source_data=source_data, metrics=["rouge_l"]
        )

        result = report.to_dict()

        assert isinstance(result, dict)
        assert result["persona_id"] == "p1"
        assert result["persona_name"] == "Sarah"
        assert "overall_score" in result
        assert "metrics_used" in result
        assert "generated_at" in result
        assert "rouge_l" in result


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @pytest.fixture
    def sample_persona(self):
        """Create a sample persona."""
        return Persona(id="p1", name="Test", goals=["Goal"])

    def test_validate_persona_function(self, sample_persona):
        """Test validate_persona convenience function."""
        report = validate_persona(sample_persona, metrics=["geval"])

        assert report.persona_id == "p1"
        assert "geval" in report.metrics_used

    def test_validate_personas_function(self, sample_persona):
        """Test validate_personas convenience function."""
        personas = [sample_persona]

        batch_report = validate_personas(personas, metrics=["geval"])

        assert batch_report.persona_count == 1
        assert len(batch_report.reports) == 1


class TestMetricSkipping:
    """Tests for graceful metric skipping when libraries unavailable."""

    @pytest.fixture
    def validator(self):
        """Create an academic validator."""
        return AcademicValidator()

    @pytest.fixture
    def sample_persona(self):
        """Create a sample persona."""
        return Persona(id="p1", name="Test", goals=["Goal"])

    def test_skip_metric_on_import_error(self, validator, sample_persona):
        """Test that metrics are skipped gracefully if library missing."""
        # This test validates the try/except logic in validator
        # In real scenarios with missing libraries, the metric would return None

        source_data = "Test source"

        # Should not crash even if some metrics fail
        report = validator.validate(
            sample_persona,
            source_data=source_data,
            metrics=["rouge_l", "bertscore"],
        )

        # Report should still be created
        assert report.persona_id == "p1"
        # At least one metric should work (or both might be None if libs missing)
        assert report.metrics_used is not None
