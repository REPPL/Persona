"""Tests for faithfulness models."""

import pytest

from persona.core.quality.faithfulness.models import (
    Claim,
    ClaimType,
    FaithfulnessReport,
    SourceMatch,
)


class TestClaimType:
    """Tests for ClaimType enum."""

    def test_claim_type_values(self):
        """Test claim type enum values."""
        assert ClaimType.FACTUAL.value == "factual"
        assert ClaimType.OPINION.value == "opinion"
        assert ClaimType.PREFERENCE.value == "preference"
        assert ClaimType.BEHAVIOUR.value == "behaviour"
        assert ClaimType.QUOTE.value == "quote"
        assert ClaimType.DEMOGRAPHIC.value == "demographic"
        assert ClaimType.GOAL.value == "goal"
        assert ClaimType.PAIN_POINT.value == "pain_point"


class TestClaim:
    """Tests for Claim dataclass."""

    def test_claim_creation(self):
        """Test basic claim creation."""
        claim = Claim(
            text="User is 25 years old",
            source_field="demographics.age",
            claim_type=ClaimType.DEMOGRAPHIC,
        )

        assert claim.text == "User is 25 years old"
        assert claim.source_field == "demographics.age"
        assert claim.claim_type == ClaimType.DEMOGRAPHIC
        assert claim.context == ""

    def test_claim_with_context(self):
        """Test claim with context."""
        claim = Claim(
            text="User is 25 years old",
            source_field="demographics.age",
            claim_type=ClaimType.DEMOGRAPHIC,
            context="Age: 25",
        )

        assert claim.context == "Age: 25"

    def test_claim_to_dict(self):
        """Test claim serialisation."""
        claim = Claim(
            text="User is 25 years old",
            source_field="demographics.age",
            claim_type=ClaimType.DEMOGRAPHIC,
            context="Age: 25",
        )

        result = claim.to_dict()

        assert result["text"] == "User is 25 years old"
        assert result["source_field"] == "demographics.age"
        assert result["claim_type"] == "demographic"
        assert result["context"] == "Age: 25"


class TestSourceMatch:
    """Tests for SourceMatch dataclass."""

    def test_source_match_creation(self):
        """Test basic source match creation."""
        claim = Claim(
            text="User is 25 years old",
            source_field="demographics.age",
            claim_type=ClaimType.DEMOGRAPHIC,
        )

        match = SourceMatch(
            claim=claim,
            source_text="Respondent aged 25",
            similarity_score=0.85,
            is_supported=True,
        )

        assert match.claim == claim
        assert match.source_text == "Respondent aged 25"
        assert match.similarity_score == 0.85
        assert match.is_supported is True
        assert match.evidence_type == "inferred"

    def test_source_match_with_evidence_type(self):
        """Test source match with custom evidence type."""
        claim = Claim(
            text="User is 25 years old",
            source_field="demographics.age",
            claim_type=ClaimType.DEMOGRAPHIC,
        )

        match = SourceMatch(
            claim=claim,
            source_text="Age: 25",
            similarity_score=0.95,
            is_supported=True,
            evidence_type="direct",
        )

        assert match.evidence_type == "direct"

    def test_source_match_unsupported(self):
        """Test unsupported source match."""
        claim = Claim(
            text="User is 25 years old",
            source_field="demographics.age",
            claim_type=ClaimType.DEMOGRAPHIC,
        )

        match = SourceMatch(
            claim=claim,
            source_text="No age information",
            similarity_score=0.2,
            is_supported=False,
            evidence_type="unsupported",
        )

        assert match.is_supported is False
        assert match.evidence_type == "unsupported"

    def test_source_match_to_dict(self):
        """Test source match serialisation."""
        claim = Claim(
            text="User is 25 years old",
            source_field="demographics.age",
            claim_type=ClaimType.DEMOGRAPHIC,
        )

        match = SourceMatch(
            claim=claim,
            source_text="Age: 25",
            similarity_score=0.8567,
            is_supported=True,
            evidence_type="direct",
        )

        result = match.to_dict()

        assert "claim" in result
        assert result["source_text"] == "Age: 25"
        assert result["similarity_score"] == 0.857  # Rounded to 3 decimals
        assert result["is_supported"] is True
        assert result["evidence_type"] == "direct"


class TestFaithfulnessReport:
    """Tests for FaithfulnessReport dataclass."""

    def test_faithfulness_report_creation(self):
        """Test basic report creation."""
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

        match1 = SourceMatch(
            claim=claim1,
            source_text="Age: 25",
            similarity_score=0.9,
            is_supported=True,
        )
        match2 = SourceMatch(
            claim=claim2,
            source_text="No preference data",
            similarity_score=0.1,
            is_supported=False,
        )

        report = FaithfulnessReport(
            persona_id="test-1",
            persona_name="Test Person",
            claims=[claim1, claim2],
            matches=[match1, match2],
            supported_ratio=0.5,
            hallucination_ratio=0.5,
            unsupported_claims=[claim2],
        )

        assert report.persona_id == "test-1"
        assert report.persona_name == "Test Person"
        assert report.total_claims == 2
        assert report.supported_count == 1
        assert report.unsupported_count == 1
        assert report.supported_ratio == 0.5
        assert report.hallucination_ratio == 0.5

    def test_faithfulness_score(self):
        """Test faithfulness score calculation."""
        report = FaithfulnessReport(
            persona_id="test-1",
            persona_name="Test Person",
            claims=[],
            matches=[],
            supported_ratio=0.75,
            hallucination_ratio=0.25,
        )

        assert report.faithfulness_score == 75.0

    def test_get_claims_by_type(self):
        """Test filtering claims by type."""
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
        claim3 = Claim(
            text="User is a teacher",
            source_field="demographics.occupation",
            claim_type=ClaimType.DEMOGRAPHIC,
        )

        report = FaithfulnessReport(
            persona_id="test-1",
            persona_name="Test Person",
            claims=[claim1, claim2, claim3],
            matches=[],
            supported_ratio=1.0,
            hallucination_ratio=0.0,
        )

        demographics = report.get_claims_by_type(ClaimType.DEMOGRAPHIC)
        preferences = report.get_claims_by_type(ClaimType.PREFERENCE)

        assert len(demographics) == 2
        assert len(preferences) == 1
        assert claim1 in demographics
        assert claim3 in demographics
        assert claim2 in preferences

    def test_get_unsupported_by_type(self):
        """Test filtering unsupported claims by type."""
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
            supported_ratio=0.0,
            hallucination_ratio=1.0,
            unsupported_claims=[claim1, claim2],
        )

        demographics = report.get_unsupported_by_type(ClaimType.DEMOGRAPHIC)
        preferences = report.get_unsupported_by_type(ClaimType.PREFERENCE)

        assert len(demographics) == 1
        assert len(preferences) == 1

    def test_report_to_dict(self):
        """Test report serialisation."""
        claim = Claim(
            text="User is 25 years old",
            source_field="demographics.age",
            claim_type=ClaimType.DEMOGRAPHIC,
        )

        match = SourceMatch(
            claim=claim,
            source_text="Age: 25",
            similarity_score=0.9,
            is_supported=True,
        )

        report = FaithfulnessReport(
            persona_id="test-1",
            persona_name="Test Person",
            claims=[claim],
            matches=[match],
            supported_ratio=1.0,
            hallucination_ratio=0.0,
            details={"test": True},
        )

        result = report.to_dict()

        assert result["persona_id"] == "test-1"
        assert result["persona_name"] == "Test Person"
        assert result["total_claims"] == 1
        assert result["supported_count"] == 1
        assert result["unsupported_count"] == 0
        assert result["supported_ratio"] == 1.0
        assert result["hallucination_ratio"] == 0.0
        assert result["faithfulness_score"] == 100.0
        assert len(result["claims"]) == 1
        assert len(result["matches"]) == 1
        assert result["details"]["test"] is True
