"""Tests for privacy entities."""

import pytest
from persona.core.privacy.entities import (
    AnonymisationResult,
    AnonymisationStrategy,
    PIIEntity,
    PIIType,
)


class TestPIIEntity:
    """Tests for PIIEntity dataclass."""

    def test_create_entity(self):
        """Test creating a PII entity."""
        entity = PIIEntity(
            type="PERSON",
            text="John Smith",
            start=0,
            end=10,
            score=0.95,
        )

        assert entity.type == "PERSON"
        assert entity.text == "John Smith"
        assert entity.start == 0
        assert entity.end == 10
        assert entity.score == 0.95
        assert entity.metadata is None

    def test_entity_with_metadata(self):
        """Test entity with metadata."""
        entity = PIIEntity(
            type="EMAIL_ADDRESS",
            text="test@example.com",
            start=10,
            end=26,
            score=1.0,
            metadata={"detector": "regex"},
        )

        assert entity.metadata == {"detector": "regex"}

    def test_entity_repr(self):
        """Test entity string representation."""
        entity = PIIEntity(
            type="PERSON",
            text="Jane Doe",
            start=5,
            end=13,
            score=0.87,
        )

        repr_str = repr(entity)
        assert "PIIEntity" in repr_str
        assert "PERSON" in repr_str
        assert "Jane Doe" in repr_str
        assert "0.87" in repr_str

    def test_default_score(self):
        """Test default score is 1.0."""
        entity = PIIEntity(
            type="PERSON",
            text="Test",
            start=0,
            end=4,
        )

        assert entity.score == 1.0


class TestAnonymisationStrategy:
    """Tests for AnonymisationStrategy enum."""

    def test_strategy_values(self):
        """Test strategy enum values."""
        assert AnonymisationStrategy.REDACT.value == "redact"
        assert AnonymisationStrategy.REPLACE.value == "replace"
        assert AnonymisationStrategy.HASH.value == "hash"

    def test_strategy_from_string(self):
        """Test creating strategy from string."""
        assert AnonymisationStrategy("redact") == AnonymisationStrategy.REDACT
        assert AnonymisationStrategy("replace") == AnonymisationStrategy.REPLACE
        assert AnonymisationStrategy("hash") == AnonymisationStrategy.HASH

    def test_invalid_strategy(self):
        """Test invalid strategy raises error."""
        with pytest.raises(ValueError):
            AnonymisationStrategy("invalid")


class TestPIIType:
    """Tests for PIIType enum."""

    def test_common_types(self):
        """Test common PII types exist."""
        assert PIIType.PERSON.value == "PERSON"
        assert PIIType.EMAIL_ADDRESS.value == "EMAIL_ADDRESS"
        assert PIIType.PHONE_NUMBER.value == "PHONE_NUMBER"
        assert PIIType.LOCATION.value == "LOCATION"
        assert PIIType.CREDIT_CARD.value == "CREDIT_CARD"

    def test_type_aliases(self):
        """Test type aliases."""
        # ADDRESS is alias for LOCATION
        assert PIIType.ADDRESS.value == PIIType.LOCATION.value
        # SSN is alias for US_SSN
        assert PIIType.SSN.value == PIIType.US_SSN.value


class TestAnonymisationResult:
    """Tests for AnonymisationResult dataclass."""

    def test_create_result(self):
        """Test creating anonymisation result."""
        entities = [
            PIIEntity(type="PERSON", text="John", start=0, end=4),
            PIIEntity(type="EMAIL_ADDRESS", text="test@ex.com", start=8, end=19),
        ]

        result = AnonymisationResult(
            text="[PERSON] at [EMAIL_ADDRESS]",
            entities=entities,
            strategy=AnonymisationStrategy.REDACT,
            original_length=100,
            anonymised_length=80,
        )

        assert result.text == "[PERSON] at [EMAIL_ADDRESS]"
        assert len(result.entities) == 2
        assert result.strategy == AnonymisationStrategy.REDACT
        assert result.original_length == 100
        assert result.anonymised_length == 80

    def test_entity_count(self):
        """Test entity_count property."""
        entities = [
            PIIEntity(type="PERSON", text="John", start=0, end=4),
            PIIEntity(type="PERSON", text="Jane", start=10, end=14),
        ]

        result = AnonymisationResult(
            text="Test",
            entities=entities,
            strategy=AnonymisationStrategy.REDACT,
            original_length=50,
            anonymised_length=40,
        )

        assert result.entity_count == 2

    def test_entity_types(self):
        """Test entity_types property."""
        entities = [
            PIIEntity(type="PERSON", text="John", start=0, end=4),
            PIIEntity(type="EMAIL_ADDRESS", text="test@ex.com", start=8, end=19),
            PIIEntity(type="PERSON", text="Jane", start=25, end=29),
        ]

        result = AnonymisationResult(
            text="Test",
            entities=entities,
            strategy=AnonymisationStrategy.REDACT,
            original_length=50,
            anonymised_length=40,
        )

        assert result.entity_types == {"PERSON", "EMAIL_ADDRESS"}

    def test_result_repr(self):
        """Test result string representation."""
        entities = [PIIEntity(type="PERSON", text="Test", start=0, end=4)]

        result = AnonymisationResult(
            text="Anonymised",
            entities=entities,
            strategy=AnonymisationStrategy.HASH,
            original_length=100,
            anonymised_length=90,
        )

        repr_str = repr(result)
        assert "AnonymisationResult" in repr_str
        assert "entities=1" in repr_str
        assert "hash" in repr_str
        assert "100->90" in repr_str

    def test_empty_entities(self):
        """Test result with no entities."""
        result = AnonymisationResult(
            text="No PII here",
            entities=[],
            strategy=AnonymisationStrategy.REDACT,
            original_length=11,
            anonymised_length=11,
        )

        assert result.entity_count == 0
        assert result.entity_types == set()
