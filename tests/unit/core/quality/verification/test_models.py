"""Tests for verification data models."""

import pytest
from datetime import datetime

from persona.core.quality.verification.models import (
    AttributeAgreement,
    ConsistencyMetrics,
    VerificationConfig,
    VerificationReport,
)


class TestVerificationConfig:
    """Tests for VerificationConfig."""

    def test_basic_config(self):
        """Test basic configuration creation."""
        config = VerificationConfig(
            models=["model1", "model2"],
            samples_per_model=3,
            voting_strategy="majority",
        )

        assert config.models == ["model1", "model2"]
        assert config.samples_per_model == 3
        assert config.voting_strategy == "majority"
        assert config.consistency_threshold == 0.7  # default

    def test_config_validation_no_models(self):
        """Test that config requires at least one model."""
        with pytest.raises(ValueError, match="At least one model"):
            VerificationConfig(models=[])

    def test_config_validation_invalid_samples(self):
        """Test that samples_per_model must be positive."""
        with pytest.raises(ValueError, match="samples_per_model must be at least 1"):
            VerificationConfig(models=["model1"], samples_per_model=0)

    def test_config_validation_invalid_threshold(self):
        """Test that threshold must be between 0 and 1."""
        with pytest.raises(ValueError, match="threshold must be between 0 and 1"):
            VerificationConfig(models=["model1"], consistency_threshold=1.5)

    def test_config_validation_invalid_strategy(self):
        """Test that voting strategy must be valid."""
        with pytest.raises(ValueError, match="voting_strategy must be one of"):
            VerificationConfig(models=["model1"], voting_strategy="invalid")

    def test_config_to_dict(self):
        """Test configuration serialization."""
        config = VerificationConfig(
            models=["model1", "model2"],
            samples_per_model=5,
            voting_strategy="unanimous",
            consistency_threshold=0.8,
        )

        data = config.to_dict()

        assert data["models"] == ["model1", "model2"]
        assert data["samples_per_model"] == 5
        assert data["voting_strategy"] == "unanimous"
        assert data["consistency_threshold"] == 0.8


class TestConsistencyMetrics:
    """Tests for ConsistencyMetrics."""

    def test_basic_metrics(self):
        """Test basic metrics creation."""
        metrics = ConsistencyMetrics(
            attribute_agreement=0.8,
            semantic_consistency=0.7,
            factual_convergence=0.9,
        )

        assert metrics.attribute_agreement == 0.8
        assert metrics.semantic_consistency == 0.7
        assert metrics.factual_convergence == 0.9

    def test_confidence_score_calculation(self):
        """Test automatic confidence score calculation."""
        metrics = ConsistencyMetrics(
            attribute_agreement=0.8,
            semantic_consistency=0.6,
            factual_convergence=0.7,
        )

        # Default weights: 0.4, 0.3, 0.3
        expected = (0.8 * 0.4) + (0.6 * 0.3) + (0.7 * 0.3)
        assert abs(metrics.confidence_score - expected) < 0.001

    def test_custom_weights(self):
        """Test metrics with custom weights."""
        weights = {
            "attribute_agreement": 0.5,
            "semantic_consistency": 0.25,
            "factual_convergence": 0.25,
        }

        metrics = ConsistencyMetrics(
            attribute_agreement=0.8,
            semantic_consistency=0.6,
            factual_convergence=0.4,
            weights=weights,
        )

        expected = (0.8 * 0.5) + (0.6 * 0.25) + (0.4 * 0.25)
        assert abs(metrics.confidence_score - expected) < 0.001

    def test_metrics_to_dict(self):
        """Test metrics serialization."""
        metrics = ConsistencyMetrics(
            attribute_agreement=0.75,
            semantic_consistency=0.85,
            factual_convergence=0.65,
        )

        data = metrics.to_dict()

        assert data["attribute_agreement"] == 0.75
        assert data["semantic_consistency"] == 0.85
        assert data["factual_convergence"] == 0.65
        assert "confidence_score" in data
        assert "weights" in data


class TestAttributeAgreement:
    """Tests for AttributeAgreement."""

    def test_basic_agreement(self):
        """Test basic attribute agreement."""
        agreement = AttributeAgreement(
            attribute="name",
            present_count=3,
            total_count=5,
        )

        assert agreement.attribute == "name"
        assert agreement.present_count == 3
        assert agreement.total_count == 5
        assert agreement.agreement_score == 0.6

    def test_is_agreed_majority(self):
        """Test majority agreement detection."""
        agreement = AttributeAgreement(
            attribute="goals",
            present_count=4,
            total_count=5,
        )

        assert agreement.is_agreed is True

    def test_is_agreed_minority(self):
        """Test minority agreement detection."""
        agreement = AttributeAgreement(
            attribute="quotes",
            present_count=2,
            total_count=5,
        )

        assert agreement.is_agreed is False

    def test_agreement_to_dict(self):
        """Test agreement serialization."""
        agreement = AttributeAgreement(
            attribute="demographics",
            present_count=3,
            total_count=4,
            values=[{"age": 30}, {"age": 35}, {"age": 40}],
        )

        data = agreement.to_dict()

        assert data["attribute"] == "demographics"
        assert data["present_count"] == 3
        assert data["total_count"] == 4
        assert data["agreement_score"] == 0.75
        assert data["is_agreed"] is True


class TestVerificationReport:
    """Tests for VerificationReport."""

    def test_basic_report(self):
        """Test basic report creation."""
        config = VerificationConfig(models=["model1", "model2"])
        metrics = ConsistencyMetrics(
            attribute_agreement=0.8,
            semantic_consistency=0.7,
            factual_convergence=0.9,
        )

        report = VerificationReport(
            persona_id="test-persona",
            config=config,
            consistency_score=0.8,
            metrics=metrics,
        )

        assert report.persona_id == "test-persona"
        assert report.consistency_score == 0.8
        assert report.passed is True  # above threshold

    def test_report_passed_threshold(self):
        """Test pass/fail determination."""
        config = VerificationConfig(
            models=["model1"],
            consistency_threshold=0.75,
        )

        # Above threshold
        report1 = VerificationReport(
            persona_id="pass",
            config=config,
            consistency_score=0.8,
        )
        assert report1.passed is True

        # Below threshold
        report2 = VerificationReport(
            persona_id="fail",
            config=config,
            consistency_score=0.6,
        )
        assert report2.passed is False

    def test_get_consensus_persona(self):
        """Test consensus persona retrieval."""
        config = VerificationConfig(models=["model1"])
        consensus = {"name": "Test Persona", "goals": ["Goal 1"]}

        report = VerificationReport(
            persona_id="test",
            config=config,
            consistency_score=0.8,
            consensus_persona=consensus,
        )

        assert report.get_consensus_persona() == consensus

    def test_get_agreement_details(self):
        """Test agreement details extraction."""
        config = VerificationConfig(models=["model1", "model2"])
        model_outputs = {
            "model1": {"name": "Alice", "age": 30},
            "model2": {"name": "Alice", "occupation": "Engineer"},
        }

        report = VerificationReport(
            persona_id="test",
            config=config,
            consistency_score=0.8,
            model_outputs=model_outputs,
        )

        details = report.get_agreement_details()

        assert "name" in details
        assert details["name"].present_count == 2
        assert details["name"].is_agreed is True

        assert "age" in details
        assert details["age"].present_count == 1
        assert details["age"].is_agreed is False

    def test_report_to_dict(self):
        """Test report serialization."""
        config = VerificationConfig(models=["model1"])
        metrics = ConsistencyMetrics(
            attribute_agreement=0.8,
            semantic_consistency=0.7,
            factual_convergence=0.9,
        )

        report = VerificationReport(
            persona_id="test",
            config=config,
            consistency_score=0.8,
            agreed_attributes=["name", "goals"],
            disputed_attributes=["quotes"],
            metrics=metrics,
        )

        data = report.to_dict()

        assert data["persona_id"] == "test"
        assert data["consistency_score"] == 0.8
        assert data["agreed_attributes"] == ["name", "goals"]
        assert data["disputed_attributes"] == ["quotes"]
        assert data["passed"] is True
        assert "metrics" in data
        assert "timestamp" in data

    def test_report_to_markdown(self):
        """Test markdown report generation."""
        config = VerificationConfig(
            models=["model1", "model2"],
            samples_per_model=3,
            voting_strategy="majority",
        )
        metrics = ConsistencyMetrics(
            attribute_agreement=0.85,
            semantic_consistency=0.75,
            factual_convergence=0.90,
        )

        report = VerificationReport(
            persona_id="test-persona",
            config=config,
            consistency_score=0.83,
            agreed_attributes=["name", "goals", "demographics"],
            disputed_attributes=["quotes"],
            metrics=metrics,
            consensus_persona={"name": "Test", "goals": ["Goal 1"]},
        )

        markdown = report.to_markdown()

        # Check key sections exist
        assert "# Verification Report: test-persona" in markdown
        assert "✅ PASSED" in markdown or "PASSED" in markdown
        assert "Consistency Score" in markdown
        assert "83" in markdown  # Check score appears somewhere
        assert "## Configuration" in markdown
        assert "## Consistency Metrics" in markdown
        assert "## Agreed Attributes" in markdown
        assert "## Disputed Attributes" in markdown
        assert "## Consensus Persona" in markdown
        assert "model1, model2" in markdown
