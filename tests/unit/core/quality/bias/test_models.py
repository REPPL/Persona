"""Tests for bias detection models."""

import pytest

from persona.core.quality.bias.models import (
    BiasCategory,
    BiasConfig,
    BiasFinding,
    BiasReport,
    Severity,
)


class TestBiasConfig:
    """Tests for BiasConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = BiasConfig()

        assert "lexicon" in config.methods
        assert "embedding" in config.methods
        assert "llm" in config.methods
        assert "gender" in config.categories
        assert config.threshold == 0.3
        assert config.lexicon == "holisticbias"

    def test_custom_config(self):
        """Test custom configuration."""
        config = BiasConfig(
            methods=["lexicon"],
            categories=["gender", "age"],
            threshold=0.5,
        )

        assert config.methods == ["lexicon"]
        assert config.categories == ["gender", "age"]
        assert config.threshold == 0.5

    def test_invalid_method(self):
        """Test that invalid method raises error."""
        with pytest.raises(ValueError, match="Invalid method"):
            BiasConfig(methods=["invalid"])

    def test_invalid_category(self):
        """Test that invalid category raises error."""
        with pytest.raises(ValueError, match="Invalid category"):
            BiasConfig(categories=["invalid"])


class TestBiasFinding:
    """Tests for BiasFinding."""

    def test_finding_creation(self):
        """Test creating a bias finding."""
        finding = BiasFinding(
            category=BiasCategory.GENDER,
            description="Gender stereotype detected",
            evidence="She is very emotional",
            severity=Severity.MEDIUM,
            method="lexicon",
            confidence=0.8,
        )

        assert finding.category == BiasCategory.GENDER
        assert finding.description == "Gender stereotype detected"
        assert finding.evidence == "She is very emotional"
        assert finding.severity == Severity.MEDIUM
        assert finding.method == "lexicon"
        assert finding.confidence == 0.8

    def test_finding_to_dict(self):
        """Test converting finding to dictionary."""
        finding = BiasFinding(
            category=BiasCategory.RACIAL,
            description="Racial bias",
            evidence="Test evidence",
            severity=Severity.HIGH,
            method="llm",
            confidence=0.9,
            context="test context",
        )

        result = finding.to_dict()

        assert result["category"] == "racial"
        assert result["description"] == "Racial bias"
        assert result["evidence"] == "Test evidence"
        assert result["severity"] == "high"
        assert result["method"] == "llm"
        assert result["confidence"] == 0.9
        assert result["context"] == "test context"


class TestBiasReport:
    """Tests for BiasReport."""

    def test_empty_report(self):
        """Test creating empty bias report."""
        report = BiasReport(
            persona_id="test-1",
            persona_name="Test Persona",
            overall_score=0.0,
            findings=[],
            category_scores={},
            methods_used=["lexicon"],
        )

        assert report.persona_id == "test-1"
        assert report.persona_name == "Test Persona"
        assert report.overall_score == 0.0
        assert len(report.findings) == 0
        assert not report.has_bias
        assert report.high_severity_count == 0
        assert report.medium_severity_count == 0
        assert report.low_severity_count == 0

    def test_report_with_findings(self):
        """Test report with bias findings."""
        findings = [
            BiasFinding(
                category=BiasCategory.GENDER,
                description="Gender bias",
                evidence="Evidence 1",
                severity=Severity.HIGH,
                method="lexicon",
                confidence=0.9,
            ),
            BiasFinding(
                category=BiasCategory.AGE,
                description="Age bias",
                evidence="Evidence 2",
                severity=Severity.MEDIUM,
                method="embedding",
                confidence=0.7,
            ),
            BiasFinding(
                category=BiasCategory.GENDER,
                description="Another gender bias",
                evidence="Evidence 3",
                severity=Severity.LOW,
                method="llm",
                confidence=0.5,
            ),
        ]

        report = BiasReport(
            persona_id="test-2",
            persona_name="Biased Persona",
            overall_score=0.65,
            findings=findings,
            category_scores={"gender": 0.7, "age": 0.4},
            methods_used=["lexicon", "embedding", "llm"],
        )

        assert report.has_bias
        assert len(report.findings) == 3
        assert report.high_severity_count == 1
        assert report.medium_severity_count == 1
        assert report.low_severity_count == 1

    def test_get_findings_by_category(self):
        """Test filtering findings by category."""
        findings = [
            BiasFinding(
                category=BiasCategory.GENDER,
                description="Gender bias 1",
                evidence="Evidence 1",
                severity=Severity.MEDIUM,
                method="lexicon",
                confidence=0.8,
            ),
            BiasFinding(
                category=BiasCategory.AGE,
                description="Age bias",
                evidence="Evidence 2",
                severity=Severity.LOW,
                method="embedding",
                confidence=0.6,
            ),
            BiasFinding(
                category=BiasCategory.GENDER,
                description="Gender bias 2",
                evidence="Evidence 3",
                severity=Severity.HIGH,
                method="llm",
                confidence=0.9,
            ),
        ]

        report = BiasReport(
            persona_id="test-3",
            persona_name="Test",
            overall_score=0.5,
            findings=findings,
            category_scores={},
            methods_used=["lexicon"],
        )

        gender_findings = report.get_findings_by_category(BiasCategory.GENDER)
        age_findings = report.get_findings_by_category(BiasCategory.AGE)

        assert len(gender_findings) == 2
        assert len(age_findings) == 1

    def test_get_findings_by_severity(self):
        """Test filtering findings by severity."""
        findings = [
            BiasFinding(
                category=BiasCategory.PROFESSIONAL,
                description="Bias 1",
                evidence="Evidence 1",
                severity=Severity.HIGH,
                method="lexicon",
                confidence=0.9,
            ),
            BiasFinding(
                category=BiasCategory.PROFESSIONAL,
                description="Bias 2",
                evidence="Evidence 2",
                severity=Severity.HIGH,
                method="embedding",
                confidence=0.8,
            ),
            BiasFinding(
                category=BiasCategory.PROFESSIONAL,
                description="Bias 3",
                evidence="Evidence 3",
                severity=Severity.MEDIUM,
                method="llm",
                confidence=0.7,
            ),
        ]

        report = BiasReport(
            persona_id="test-4",
            persona_name="Test",
            overall_score=0.6,
            findings=findings,
            category_scores={},
            methods_used=["all"],
        )

        high_findings = report.get_findings_by_severity(Severity.HIGH)
        medium_findings = report.get_findings_by_severity(Severity.MEDIUM)
        low_findings = report.get_findings_by_severity(Severity.LOW)

        assert len(high_findings) == 2
        assert len(medium_findings) == 1
        assert len(low_findings) == 0

    def test_report_to_dict(self):
        """Test converting report to dictionary."""
        finding = BiasFinding(
            category=BiasCategory.GENDER,
            description="Test bias",
            evidence="Test evidence",
            severity=Severity.MEDIUM,
            method="lexicon",
            confidence=0.8,
        )

        report = BiasReport(
            persona_id="test-5",
            persona_name="Test Persona",
            overall_score=0.45,
            findings=[finding],
            category_scores={"gender": 0.45},
            methods_used=["lexicon"],
        )

        result = report.to_dict()

        assert result["persona_id"] == "test-5"
        assert result["persona_name"] == "Test Persona"
        assert result["overall_score"] == 0.45
        assert result["has_bias"] is True
        assert result["total_findings"] == 1
        assert result["high_severity_count"] == 0
        assert result["medium_severity_count"] == 1
        assert result["low_severity_count"] == 0
        assert "gender" in result["category_scores"]
        assert len(result["findings"]) == 1
        assert result["methods_used"] == ["lexicon"]
