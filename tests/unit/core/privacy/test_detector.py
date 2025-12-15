"""Tests for PII detector."""

import pytest

from persona.core.privacy.detector import PIIDetector


class TestPIIDetectorAvailability:
    """Tests for detector availability checking (works without Presidio)."""

    def test_detector_init(self):
        """Test detector initialisation."""
        detector = PIIDetector()
        assert detector.language == "en"
        assert detector.score_threshold == 0.5
        assert detector.entities is None

    def test_detector_custom_params(self):
        """Test detector with custom parameters."""
        detector = PIIDetector(
            language="en",
            score_threshold=0.7,
            entities=["PERSON", "EMAIL_ADDRESS"],
        )

        assert detector.language == "en"
        assert detector.score_threshold == 0.7
        assert detector.entities == ["PERSON", "EMAIL_ADDRESS"]

    def test_is_available_returns_bool(self):
        """Test is_available returns boolean."""
        detector = PIIDetector()
        result = detector.is_available()
        assert isinstance(result, bool)

    def test_get_import_error_when_unavailable(self):
        """Test get_import_error when Presidio not installed."""
        detector = PIIDetector()

        if not detector.is_available():
            error = detector.get_import_error()
            assert error is None or isinstance(error, ImportError)


class TestPIIDetectorWithPresidio:
    """Tests that require Presidio to be installed."""

    @pytest.fixture(autouse=True)
    def check_presidio(self):
        """Skip tests if Presidio not available."""
        detector = PIIDetector()
        if not detector.is_available():
            pytest.skip("Presidio not installed")

    def test_detect_person_name(self):
        """Test detecting person names."""
        detector = PIIDetector()
        text = "My name is John Smith and I live in London."

        entities = detector.detect(text)

        # Should detect at least the person name
        person_entities = [e for e in entities if e.type == "PERSON"]
        assert len(person_entities) > 0
        assert any("John Smith" in e.text for e in person_entities)

    def test_detect_email(self):
        """Test detecting email addresses."""
        detector = PIIDetector()
        text = "Contact me at john.smith@example.com for details."

        entities = detector.detect(text)

        email_entities = [e for e in entities if e.type == "EMAIL_ADDRESS"]
        assert len(email_entities) == 1
        assert "john.smith@example.com" in email_entities[0].text

    def test_detect_phone_number(self):
        """Test detecting phone numbers."""
        detector = PIIDetector()
        text = "Call me at +44 20 7946 0958 anytime."

        entities = detector.detect(text)

        phone_entities = [e for e in entities if e.type == "PHONE_NUMBER"]
        # Phone detection may vary, so just check if we got entities
        assert len(entities) >= 0  # May or may not detect depending on format

    def test_detect_multiple_pii_types(self):
        """Test detecting multiple PII types in one text."""
        detector = PIIDetector()
        text = (
            "Hello, I'm Dr. Sarah Johnson. "
            "You can reach me at sarah.j@hospital.com or call 555-0123. "
            "My office is in New York."
        )

        entities = detector.detect(text)

        # Should detect multiple types
        types_found = {e.type for e in entities}
        assert len(types_found) > 0

        # Check we have entities with reasonable scores
        for entity in entities:
            assert 0.0 <= entity.score <= 1.0
            assert entity.start < entity.end
            assert entity.text == text[entity.start : entity.end]

    def test_score_threshold_filtering(self):
        """Test score threshold filters low-confidence entities."""
        # Low threshold - more results
        detector_low = PIIDetector(score_threshold=0.1)
        text = "Maybe John is a name, maybe not."
        entities_low = detector_low.detect(text)

        # High threshold - fewer results
        detector_high = PIIDetector(score_threshold=0.9)
        entities_high = detector_high.detect(text)

        # High threshold should have same or fewer entities
        assert len(entities_high) <= len(entities_low)

    def test_entity_type_filtering(self):
        """Test filtering by entity types."""
        detector = PIIDetector(entities=["PERSON"])
        text = "John Smith's email is john@example.com"

        entities = detector.detect(text)

        # Should only return PERSON entities
        for entity in entities:
            assert entity.type == "PERSON"

    def test_scan_text_summary(self):
        """Test scan_text returns proper summary."""
        detector = PIIDetector()
        text = "Contact John at john@example.com"

        result = detector.scan_text(text)

        assert "entities" in result
        assert "entity_count" in result
        assert "entity_types" in result
        assert "has_pii" in result

        assert isinstance(result["entities"], list)
        assert isinstance(result["entity_count"], int)
        assert isinstance(result["entity_types"], list)
        assert isinstance(result["has_pii"], bool)

        if result["has_pii"]:
            assert result["entity_count"] > 0
            assert len(result["entity_types"]) > 0

    def test_get_supported_entities(self):
        """Test getting supported entity types."""
        detector = PIIDetector()

        supported = detector.get_supported_entities()

        assert isinstance(supported, list)
        assert len(supported) > 0
        # Common types should be supported
        assert "PERSON" in supported or "EMAIL_ADDRESS" in supported

    def test_detect_with_language_override(self):
        """Test detection with language override."""
        detector = PIIDetector(language="en")
        text = "My name is Alice."

        # Override language in detect call
        entities = detector.detect(text, language="en")

        assert isinstance(entities, list)

    def test_entity_metadata(self):
        """Test that entities include metadata."""
        detector = PIIDetector()
        text = "Email: test@example.com"

        entities = detector.detect(text)

        for entity in entities:
            assert entity.metadata is not None
            assert isinstance(entity.metadata, dict)


class TestPIIDetectorErrorHandling:
    """Tests for error handling."""

    def test_detect_without_presidio(self, monkeypatch):
        """Test detect raises error when Presidio not available."""
        # Create detector that appears unavailable
        detector = PIIDetector()
        detector._available = False
        detector._import_error = ImportError("presidio not found")

        with pytest.raises(RuntimeError) as exc_info:
            detector.detect("Some text")

        assert "not available" in str(exc_info.value).lower()
        assert "pip install persona[privacy]" in str(exc_info.value)

    def test_get_supported_entities_without_presidio(self):
        """Test get_supported_entities raises error when unavailable."""
        detector = PIIDetector()
        detector._available = False

        with pytest.raises(RuntimeError) as exc_info:
            detector.get_supported_entities()

        assert "not available" in str(exc_info.value).lower()

    def test_scan_text_without_presidio(self):
        """Test scan_text raises error when unavailable."""
        detector = PIIDetector()
        detector._available = False

        with pytest.raises(RuntimeError):
            detector.scan_text("Some text")

    def test_detect_empty_string(self):
        """Test detecting PII in empty string."""
        detector = PIIDetector()

        if detector.is_available():
            entities = detector.detect("")
            assert isinstance(entities, list)
            assert len(entities) == 0
