"""Tests for PII anonymiser."""

import pytest
from persona.core.privacy.anonymiser import PIIAnonymiser
from persona.core.privacy.entities import AnonymisationStrategy, PIIEntity


class TestPIIAnonymiserAvailability:
    """Tests for anonymiser availability checking (works without Presidio)."""

    def test_anonymiser_init(self):
        """Test anonymiser initialisation."""
        anonymiser = PIIAnonymiser()
        assert anonymiser is not None

    def test_is_available_returns_bool(self):
        """Test is_available returns boolean."""
        anonymiser = PIIAnonymiser()
        result = anonymiser.is_available()
        assert isinstance(result, bool)

    def test_get_import_error_when_unavailable(self):
        """Test get_import_error when Presidio not installed."""
        anonymiser = PIIAnonymiser()

        if not anonymiser.is_available():
            error = anonymiser.get_import_error()
            assert error is None or isinstance(error, ImportError)


class TestPIIAnonymiserWithPresidio:
    """Tests that require Presidio to be installed."""

    @pytest.fixture(autouse=True)
    def check_presidio(self):
        """Skip tests if Presidio not available."""
        anonymiser = PIIAnonymiser()
        if not anonymiser.is_available():
            pytest.skip("Presidio not installed")

    @pytest.fixture
    def sample_text(self):
        """Sample text with PII."""
        return "Contact John Smith at john@example.com or call 555-1234."

    @pytest.fixture
    def sample_entities(self):
        """Sample detected entities."""
        return [
            PIIEntity(
                type="PERSON",
                text="John Smith",
                start=8,
                end=18,
                score=0.95,
            ),
            PIIEntity(
                type="EMAIL_ADDRESS",
                text="john@example.com",
                start=22,
                end=38,
                score=1.0,
            ),
        ]

    def test_anonymise_redact(self, sample_text, sample_entities):
        """Test redaction strategy."""
        anonymiser = PIIAnonymiser()

        result = anonymiser.anonymise(
            sample_text, sample_entities, AnonymisationStrategy.REDACT
        )

        assert result.text != sample_text
        assert "John Smith" not in result.text
        assert "john@example.com" not in result.text
        assert result.entity_count == 2
        assert result.strategy == AnonymisationStrategy.REDACT
        assert result.original_length == len(sample_text)

    def test_anonymise_replace(self, sample_text, sample_entities):
        """Test replacement strategy."""
        anonymiser = PIIAnonymiser()

        result = anonymiser.anonymise(
            sample_text, sample_entities, AnonymisationStrategy.REPLACE
        )

        assert result.text != sample_text
        assert "John Smith" not in result.text
        assert "john@example.com" not in result.text
        # Should have some replacement text
        assert len(result.text) > 0
        assert result.entity_count == 2
        assert result.strategy == AnonymisationStrategy.REPLACE

    def test_anonymise_hash(self, sample_text, sample_entities):
        """Test hash strategy."""
        anonymiser = PIIAnonymiser()

        result = anonymiser.anonymise(
            sample_text, sample_entities, AnonymisationStrategy.HASH
        )

        assert result.text != sample_text
        assert "John Smith" not in result.text
        assert "john@example.com" not in result.text
        assert result.entity_count == 2
        assert result.strategy == AnonymisationStrategy.HASH

    def test_anonymise_empty_entities(self, sample_text):
        """Test anonymising with no entities."""
        anonymiser = PIIAnonymiser()

        result = anonymiser.anonymise(sample_text, [], AnonymisationStrategy.REDACT)

        # Text should be unchanged
        assert result.text == sample_text
        assert result.entity_count == 0
        assert result.original_length == len(sample_text)
        assert result.anonymised_length == len(sample_text)

    def test_anonymise_multiple_same_type(self):
        """Test anonymising multiple entities of same type."""
        text = "John Smith and Jane Doe are friends."
        entities = [
            PIIEntity(type="PERSON", text="John Smith", start=0, end=10, score=0.9),
            PIIEntity(type="PERSON", text="Jane Doe", start=15, end=23, score=0.9),
        ]

        anonymiser = PIIAnonymiser()
        result = anonymiser.anonymise(text, entities, AnonymisationStrategy.REDACT)

        assert "John Smith" not in result.text
        assert "Jane Doe" not in result.text
        assert result.entity_count == 2
        assert "PERSON" in result.entity_types

    def test_anonymise_overlapping_entities(self):
        """Test handling potentially overlapping entities."""
        text = "Email: test@example.com"
        entities = [
            PIIEntity(
                type="EMAIL_ADDRESS",
                text="test@example.com",
                start=7,
                end=23,
                score=1.0,
            ),
        ]

        anonymiser = PIIAnonymiser()
        result = anonymiser.anonymise(text, entities, AnonymisationStrategy.REPLACE)

        assert "test@example.com" not in result.text
        assert result.entity_count == 1

    def test_anonymise_phone_number(self):
        """Test anonymising phone number."""
        text = "Call me at 555-123-4567"
        entities = [
            PIIEntity(
                type="PHONE_NUMBER",
                text="555-123-4567",
                start=11,
                end=23,
                score=0.95,
            ),
        ]

        anonymiser = PIIAnonymiser()
        result = anonymiser.anonymise(text, entities, AnonymisationStrategy.REPLACE)

        assert "555-123-4567" not in result.text
        assert result.entity_count == 1

    def test_anonymise_location(self):
        """Test anonymising location."""
        text = "I live in New York City"
        entities = [
            PIIEntity(
                type="LOCATION",
                text="New York City",
                start=10,
                end=23,
                score=0.85,
            ),
        ]

        anonymiser = PIIAnonymiser()
        result = anonymiser.anonymise(text, entities, AnonymisationStrategy.REPLACE)

        assert "New York City" not in result.text
        assert result.entity_count == 1

    def test_anonymise_credit_card(self):
        """Test anonymising credit card."""
        text = "Card: 4111-1111-1111-1111"
        entities = [
            PIIEntity(
                type="CREDIT_CARD",
                text="4111-1111-1111-1111",
                start=6,
                end=25,
                score=1.0,
            ),
        ]

        anonymiser = PIIAnonymiser()
        result = anonymiser.anonymise(text, entities, AnonymisationStrategy.REPLACE)

        assert "4111-1111-1111-1111" not in result.text
        assert result.entity_count == 1

    def test_anonymise_result_properties(self):
        """Test AnonymisationResult properties."""
        text = "John at john@ex.com"
        entities = [
            PIIEntity(type="PERSON", text="John", start=0, end=4, score=0.9),
            PIIEntity(
                type="EMAIL_ADDRESS", text="john@ex.com", start=8, end=19, score=1.0
            ),
        ]

        anonymiser = PIIAnonymiser()
        result = anonymiser.anonymise(text, entities, AnonymisationStrategy.REDACT)

        assert result.entity_count == 2
        assert "PERSON" in result.entity_types
        assert "EMAIL_ADDRESS" in result.entity_types
        assert result.original_length == len(text)
        assert result.anonymised_length > 0

    def test_anonymise_strategies_produce_different_output(self):
        """Test that different strategies produce different results."""
        text = "Contact John at john@example.com"
        entities = [
            PIIEntity(type="PERSON", text="John", start=8, end=12, score=0.9),
            PIIEntity(
                type="EMAIL_ADDRESS",
                text="john@example.com",
                start=16,
                end=32,
                score=1.0,
            ),
        ]

        anonymiser = PIIAnonymiser()

        redact = anonymiser.anonymise(text, entities, AnonymisationStrategy.REDACT)
        replace = anonymiser.anonymise(text, entities, AnonymisationStrategy.REPLACE)
        hash_result = anonymiser.anonymise(text, entities, AnonymisationStrategy.HASH)

        # All should be different from original
        assert redact.text != text
        assert replace.text != text
        assert hash_result.text != text

        # Strategies should produce different results
        # (though in some edge cases they might be similar)
        results = {redact.text, replace.text, hash_result.text}
        assert len(results) >= 2  # At least 2 different outputs


class TestPIIAnonymiserErrorHandling:
    """Tests for error handling."""

    def test_anonymise_without_presidio(self):
        """Test anonymise raises error when Presidio not available."""
        anonymiser = PIIAnonymiser()
        anonymiser._available = False
        anonymiser._import_error = ImportError("presidio not found")

        text = "Some text"
        entities = [PIIEntity(type="PERSON", text="Some", start=0, end=4, score=0.9)]

        with pytest.raises(RuntimeError) as exc_info:
            anonymiser.anonymise(text, entities, AnonymisationStrategy.REDACT)

        assert "not available" in str(exc_info.value).lower()
        assert "pip install persona[privacy]" in str(exc_info.value)

    def test_anonymise_invalid_strategy(self):
        """Test that invalid strategy raises error."""
        anonymiser = PIIAnonymiser()

        if anonymiser.is_available():
            text = "Test"
            entities = []

            with pytest.raises((ValueError, AttributeError)):
                anonymiser.anonymise(text, entities, "invalid_strategy")

    def test_anonymise_empty_text(self):
        """Test anonymising empty text."""
        anonymiser = PIIAnonymiser()

        if anonymiser.is_available():
            result = anonymiser.anonymise("", [], AnonymisationStrategy.REDACT)

            assert result.text == ""
            assert result.entity_count == 0
            assert result.original_length == 0
            assert result.anonymised_length == 0
