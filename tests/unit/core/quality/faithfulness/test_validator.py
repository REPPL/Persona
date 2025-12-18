"""Tests for faithfulness validator."""

from unittest.mock import Mock

import pytest
from persona.core.generation.parser import Persona
from persona.core.quality.faithfulness.models import ClaimType
from persona.core.quality.faithfulness.validator import FaithfulnessValidator


class TestFaithfulnessValidator:
    """Tests for FaithfulnessValidator."""

    def test_validator_initialization(self):
        """Test validator initialization."""
        llm = Mock()
        embeddings = Mock()

        validator = FaithfulnessValidator(
            llm_provider=llm,
            embedding_provider=embeddings,
            use_hhem=False,
            support_threshold=0.75,
        )

        assert validator.llm_provider == llm
        assert validator.embedding_provider == embeddings
        assert validator.use_hhem is False
        assert validator.support_threshold == 0.75
        assert validator.extractor is not None
        assert validator.matcher is not None
        assert validator.hhem_classifier is None

    def test_validator_with_hhem_unavailable(self):
        """Test validator with HHEM enabled but unavailable."""
        llm = Mock()
        embeddings = Mock()

        # HHEM will not be available in test environment
        validator = FaithfulnessValidator(
            llm_provider=llm,
            embedding_provider=embeddings,
            use_hhem=True,
        )

        # Should gracefully fall back
        assert (
            validator.hhem_classifier is None
            or not validator.hhem_classifier.is_available()
        )

    def test_set_support_threshold_valid(self):
        """Test setting valid support threshold."""
        llm = Mock()
        embeddings = Mock()
        validator = FaithfulnessValidator(llm, embeddings)

        validator.set_support_threshold(0.8)

        assert validator.support_threshold == 0.8
        assert validator.matcher.support_threshold == 0.8

    def test_set_support_threshold_invalid(self):
        """Test setting invalid support threshold."""
        llm = Mock()
        embeddings = Mock()
        validator = FaithfulnessValidator(llm, embeddings)

        with pytest.raises(ValueError):
            validator.set_support_threshold(1.5)

        with pytest.raises(ValueError):
            validator.set_support_threshold(-0.1)

    def test_enable_hhem(self):
        """Test enabling HHEM classifier."""
        llm = Mock()
        embeddings = Mock()
        validator = FaithfulnessValidator(llm, embeddings, use_hhem=False)

        # Try to enable (will fail in test environment)
        result = validator.enable_hhem()

        # Should return False since HHEM not available
        assert result is False

    def test_disable_hhem(self):
        """Test disabling HHEM classifier."""
        llm = Mock()
        embeddings = Mock()
        validator = FaithfulnessValidator(llm, embeddings, use_hhem=False)

        validator.disable_hhem()

        assert validator.use_hhem is False

    def test_get_hallucination_summary(self):
        """Test hallucination summary generation."""
        from persona.core.quality.faithfulness.models import (
            Claim,
            FaithfulnessReport,
        )

        llm = Mock()
        embeddings = Mock()
        validator = FaithfulnessValidator(llm, embeddings)

        claim1 = Claim(
            text="User is 25 years old",
            source_field="demographics.age",
            claim_type=ClaimType.DEMOGRAPHIC,
        )
        claim2 = Claim(
            text="User likes hiking",
            source_field="preferences",
            claim_type=ClaimType.PREFERENCE,
        )

        report = FaithfulnessReport(
            persona_id="test-1",
            persona_name="Test Person",
            claims=[claim1, claim2],
            matches=[],
            supported_ratio=0.5,
            hallucination_ratio=0.5,
            unsupported_claims=[claim2],
        )

        summary = validator.get_hallucination_summary(report)

        assert summary["total_hallucinations"] == 1
        assert summary["hallucination_rate"] == "50.0%"
        assert summary["faithfulness_score"] == "50.0%"
        assert "by_type" in summary
        assert summary["by_type"]["preference"] == 1
        assert len(summary["examples"]) == 1
        assert summary["examples"][0]["text"] == "User likes hiking"

    def test_get_hallucination_summary_by_type(self):
        """Test hallucination summary groups by type."""
        from persona.core.quality.faithfulness.models import (
            Claim,
            FaithfulnessReport,
        )

        llm = Mock()
        embeddings = Mock()
        validator = FaithfulnessValidator(llm, embeddings)

        claim1 = Claim(
            text="User is 25 years old",
            source_field="demographics.age",
            claim_type=ClaimType.DEMOGRAPHIC,
        )
        claim2 = Claim(
            text="User is a teacher",
            source_field="demographics.occupation",
            claim_type=ClaimType.DEMOGRAPHIC,
        )
        claim3 = Claim(
            text="User likes hiking",
            source_field="preferences",
            claim_type=ClaimType.PREFERENCE,
        )

        report = FaithfulnessReport(
            persona_id="test-1",
            persona_name="Test Person",
            claims=[claim1, claim2, claim3],
            matches=[],
            supported_ratio=0.0,
            hallucination_ratio=1.0,
            unsupported_claims=[claim1, claim2, claim3],
        )

        summary = validator.get_hallucination_summary(report)

        assert summary["by_type"]["demographic"] == 2
        assert summary["by_type"]["preference"] == 1

    def test_validate_batch_all_success(self):
        """Test batch validation with all personas succeeding."""
        from persona.core.embedding.base import (
            BatchEmbeddingResponse,
            EmbeddingResponse,
        )
        from persona.core.providers.base import LLMResponse

        # Mock LLM
        llm = Mock()
        llm.generate.return_value = LLMResponse(
            content="[]",
            model="mock",
        )

        # Mock embeddings
        embeddings = Mock()
        embeddings.embed.return_value = EmbeddingResponse(
            vector=[0.1, 0.2, 0.3],
            model="mock",
            dimensions=3,
        )
        embeddings.embed_batch.return_value = BatchEmbeddingResponse(
            embeddings=[
                EmbeddingResponse(vector=[0.1, 0.2, 0.3], model="mock", dimensions=3)
            ]
        )

        validator = FaithfulnessValidator(llm, embeddings)

        persona1 = Persona(
            id="test-1",
            name="Person 1",
            demographics={"age": "25"},
            goals=[],
            pain_points=[],
        )
        persona2 = Persona(
            id="test-2",
            name="Person 2",
            demographics={"age": "30"},
            goals=[],
            pain_points=[],
        )

        source_data = "Respondents aged 25 and 30."

        reports = validator.validate_batch([persona1, persona2], source_data)

        assert len(reports) == 2
        assert reports[0].persona_id == "test-1"
        assert reports[1].persona_id == "test-2"

    def test_validate_batch_with_failure(self):
        """Test batch validation with one persona failing."""
        llm = Mock()
        embeddings = Mock()

        # Make extractor fail for specific persona
        validator = FaithfulnessValidator(llm, embeddings)
        original_validate = validator.validate

        def mock_validate(persona, source_data):
            if persona.id == "test-2":
                raise RuntimeError("Validation failed")
            return original_validate(persona, source_data)

        validator.validate = Mock(side_effect=mock_validate)

        persona1 = Persona(
            id="test-1",
            name="Person 1",
            demographics={"age": "25"},
            goals=[],
            pain_points=[],
        )
        persona2 = Persona(
            id="test-2",
            name="Person 2",
            demographics={"age": "30"},
            goals=[],
            pain_points=[],
        )

        source_data = "Source data"

        reports = validator.validate_batch([persona1, persona2], source_data)

        assert len(reports) == 2
        # Second report should be minimal error report
        assert reports[1].persona_id == "test-2"
        assert reports[1].hallucination_ratio == 1.0
        assert "error" in reports[1].details

    def test_validate_integration(self):
        """Integration test for full validation flow."""
        from persona.core.embedding.base import (
            BatchEmbeddingResponse,
            EmbeddingResponse,
        )
        from persona.core.providers.base import LLMResponse

        # Mock LLM that returns valid claims
        llm = Mock()
        llm.generate.return_value = LLMResponse(
            content='[{"text": "User is 25", "source_field": "age", "claim_type": "demographic"}]',
            model="mock",
        )

        # Mock embeddings with high similarity
        embeddings = Mock()
        embeddings.embed.return_value = EmbeddingResponse(
            vector=[0.9, 0.1, 0.0],
            model="mock",
            dimensions=3,
        )
        embeddings.embed_batch.return_value = BatchEmbeddingResponse(
            embeddings=[
                EmbeddingResponse(vector=[0.9, 0.1, 0.0], model="mock", dimensions=3)
            ]
        )

        validator = FaithfulnessValidator(llm, embeddings, support_threshold=0.7)

        persona = Persona(
            id="test-1",
            name="Test Person",
            demographics={"age": "25"},
            goals=["Learn Python"],
            pain_points=[],
        )

        source_data = "The respondent is 25 years old."

        report = validator.validate(persona, source_data)

        assert report.persona_id == "test-1"
        assert report.persona_name == "Test Person"
        assert report.total_claims >= 1
        assert report.faithfulness_score >= 0.0
        assert report.faithfulness_score <= 100.0
