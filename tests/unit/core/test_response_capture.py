"""
Tests for full LLM response capture (F-042).
"""

import json
import pytest
import tempfile
from datetime import datetime
from pathlib import Path

from persona.core.output.response_capture import (
    RequestCapture,
    ResponseCapture,
    ResponseCaptureManager,
    ResponseCaptureStore,
    TokenUsage,
    create_request_capture,
)


@pytest.fixture
def sample_request() -> RequestCapture:
    """Create a sample request capture."""
    return RequestCapture(
        prompt="Generate 3 personas from this data...",
        model="claude-sonnet-4-5",
        provider="anthropic",
        parameters={"temperature": 0.7, "max_tokens": 4096},
    )


@pytest.fixture
def sample_capture(sample_request) -> ResponseCapture:
    """Create a sample response capture."""
    return ResponseCapture(
        raw_response='{"personas": [{"name": "Sarah"}]}',
        parsed_content={"personas": [{"name": "Sarah"}]},
        request=sample_request,
        model="claude-sonnet-4-5",
        provider="anthropic",
        tokens=TokenUsage(input_tokens=1000, output_tokens=500),
        latency_ms=2500,
        provider_metadata={"request_id": "req_123"},
    )


class TestTokenUsage:
    """Tests for TokenUsage dataclass."""

    def test_creation(self):
        """Test token usage creation."""
        usage = TokenUsage(input_tokens=100, output_tokens=50)
        assert usage.input_tokens == 100
        assert usage.output_tokens == 50

    def test_default_values(self):
        """Test default values are zero."""
        usage = TokenUsage()
        assert usage.input_tokens == 0
        assert usage.output_tokens == 0

    def test_total_tokens(self):
        """Test total tokens calculation."""
        usage = TokenUsage(input_tokens=100, output_tokens=50)
        assert usage.total_tokens == 150


class TestRequestCapture:
    """Tests for RequestCapture dataclass."""

    def test_creation(self, sample_request):
        """Test request capture creation."""
        assert sample_request.prompt.startswith("Generate")
        assert sample_request.model == "claude-sonnet-4-5"
        assert sample_request.provider == "anthropic"
        assert sample_request.parameters["temperature"] == 0.7

    def test_timestamp_auto_generated(self):
        """Test timestamp is auto-generated."""
        request = RequestCapture(
            prompt="Test",
            model="test",
            provider="test",
        )
        assert request.timestamp is not None
        # Should be valid ISO format
        datetime.fromisoformat(request.timestamp)


class TestResponseCapture:
    """Tests for ResponseCapture dataclass."""

    def test_creation(self, sample_capture):
        """Test response capture creation."""
        assert sample_capture.model == "claude-sonnet-4-5"
        assert sample_capture.provider == "anthropic"
        assert sample_capture.tokens.total_tokens == 1500
        assert sample_capture.latency_ms == 2500

    def test_default_values(self):
        """Test default values."""
        capture = ResponseCapture(raw_response="test")
        assert capture.tokens.total_tokens == 0
        assert capture.latency_ms == 0
        assert capture.model == ""

    def test_capture_id_auto_generated(self):
        """Test capture ID is auto-generated."""
        capture = ResponseCapture(raw_response="test")
        assert capture.capture_id is not None
        assert len(capture.capture_id) > 0

    def test_to_dict(self, sample_capture):
        """Test conversion to dictionary."""
        data = sample_capture.to_dict()
        assert "capture_id" in data
        assert data["raw_response"] == sample_capture.raw_response
        assert data["model"] == "claude-sonnet-4-5"
        assert data["tokens"]["input"] == 1000
        assert data["tokens"]["output"] == 500
        assert data["tokens"]["total"] == 1500
        assert data["latency_ms"] == 2500
        assert "request" in data
        assert "provider_metadata" in data

    def test_to_dict_without_request(self):
        """Test to_dict without request."""
        capture = ResponseCapture(raw_response="test")
        data = capture.to_dict()
        assert "request" not in data

    def test_from_dict(self, sample_capture):
        """Test creation from dictionary."""
        data = sample_capture.to_dict()
        restored = ResponseCapture.from_dict(data)

        assert restored.raw_response == sample_capture.raw_response
        assert restored.model == sample_capture.model
        assert restored.provider == sample_capture.provider
        assert restored.tokens.input_tokens == sample_capture.tokens.input_tokens
        assert restored.tokens.output_tokens == sample_capture.tokens.output_tokens
        assert restored.latency_ms == sample_capture.latency_ms
        assert restored.request is not None
        assert restored.request.prompt == sample_capture.request.prompt

    def test_from_dict_minimal(self):
        """Test from_dict with minimal data."""
        data = {"raw_response": "test"}
        capture = ResponseCapture.from_dict(data)
        assert capture.raw_response == "test"
        assert capture.tokens.total_tokens == 0

    def test_roundtrip(self, sample_capture):
        """Test to_dict/from_dict roundtrip."""
        data = sample_capture.to_dict()
        restored = ResponseCapture.from_dict(data)
        data2 = restored.to_dict()

        # Compare key fields (capture_id might differ on restore)
        assert data["raw_response"] == data2["raw_response"]
        assert data["model"] == data2["model"]
        assert data["tokens"] == data2["tokens"]


class TestResponseCaptureStore:
    """Tests for ResponseCaptureStore."""

    def test_creation(self):
        """Test store creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ResponseCaptureStore(tmpdir)
            assert store._base_dir.exists()

    def test_save(self, sample_capture):
        """Test saving a capture."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ResponseCaptureStore(tmpdir)
            path = store.save(sample_capture)

            assert path.exists()
            assert path.suffix == ".json"

    def test_load(self, sample_capture):
        """Test loading a capture."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ResponseCaptureStore(tmpdir)
            store.save(sample_capture)

            loaded = store.load(sample_capture.capture_id)
            assert loaded.raw_response == sample_capture.raw_response
            assert loaded.model == sample_capture.model

    def test_load_not_found(self):
        """Test loading non-existent capture."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ResponseCaptureStore(tmpdir)
            with pytest.raises(FileNotFoundError):
                store.load("nonexistent")

    def test_list_captures(self, sample_capture):
        """Test listing captures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ResponseCaptureStore(tmpdir)

            # Save multiple captures
            capture1 = ResponseCapture(raw_response="test1")
            capture2 = ResponseCapture(raw_response="test2")
            store.save(capture1)
            store.save(capture2)

            captures = store.list_captures()
            assert len(captures) == 2

    def test_delete(self, sample_capture):
        """Test deleting a capture."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ResponseCaptureStore(tmpdir)
            store.save(sample_capture)

            # Verify exists
            assert len(store.list_captures()) == 1

            # Delete
            result = store.delete(sample_capture.capture_id)
            assert result is True
            assert len(store.list_captures()) == 0

    def test_delete_not_found(self):
        """Test deleting non-existent capture."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ResponseCaptureStore(tmpdir)
            result = store.delete("nonexistent")
            assert result is False


class TestResponseCaptureManager:
    """Tests for ResponseCaptureManager."""

    def test_creation(self):
        """Test manager creation."""
        manager = ResponseCaptureManager()
        assert manager.enabled is True

    def test_enabled_property(self):
        """Test enabled property."""
        manager = ResponseCaptureManager(enabled=False)
        assert manager.enabled is False

        manager.enabled = True
        assert manager.enabled is True

    def test_capture(self):
        """Test capturing a response."""
        manager = ResponseCaptureManager()
        capture = manager.capture(
            raw_response="test response",
            model="test-model",
            provider="test-provider",
            input_tokens=100,
            output_tokens=50,
            latency_ms=1000,
        )

        assert capture.raw_response == "test response"
        assert capture.model == "test-model"
        assert capture.tokens.total_tokens == 150

    def test_capture_with_request(self, sample_request):
        """Test capturing with request."""
        manager = ResponseCaptureManager()
        capture = manager.capture(
            raw_response="test",
            request=sample_request,
        )

        assert capture.request is not None
        assert capture.request.prompt == sample_request.prompt

    def test_capture_stored_in_session(self):
        """Test captures stored in session."""
        manager = ResponseCaptureManager()
        manager.capture(raw_response="test1")
        manager.capture(raw_response="test2")

        captures = manager.get_session_captures()
        assert len(captures) == 2

    def test_capture_not_stored_when_disabled(self):
        """Test captures not stored when disabled."""
        manager = ResponseCaptureManager(enabled=False)
        manager.capture(raw_response="test")

        captures = manager.get_session_captures()
        assert len(captures) == 0

    def test_save(self, sample_capture):
        """Test saving a capture."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ResponseCaptureStore(tmpdir)
            manager = ResponseCaptureManager(store=store)

            path = manager.save(sample_capture)
            assert path is not None
            assert path.exists()

    def test_save_disabled(self, sample_capture):
        """Test save returns None when disabled."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ResponseCaptureStore(tmpdir)
            manager = ResponseCaptureManager(store=store, enabled=False)

            path = manager.save(sample_capture)
            assert path is None

    def test_save_all(self):
        """Test saving all session captures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ResponseCaptureStore(tmpdir)
            manager = ResponseCaptureManager(store=store)

            manager.capture(raw_response="test1")
            manager.capture(raw_response="test2")

            paths = manager.save_all()
            assert len(paths) == 2

            # Session should be cleared
            assert len(manager.get_session_captures()) == 0

    def test_load_for_replay(self, sample_capture):
        """Test loading capture for replay."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ResponseCaptureStore(tmpdir)
            manager = ResponseCaptureManager(store=store)

            manager.save(sample_capture)
            loaded = manager.load_for_replay(sample_capture.capture_id)

            assert loaded.raw_response == sample_capture.raw_response

    def test_list_available(self):
        """Test listing available captures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ResponseCaptureStore(tmpdir)
            manager = ResponseCaptureManager(store=store)

            capture = manager.capture(raw_response="test")
            manager.save(capture)

            available = manager.list_available()
            assert len(available) == 1

    def test_clear_session(self):
        """Test clearing session without saving."""
        manager = ResponseCaptureManager()
        manager.capture(raw_response="test1")
        manager.capture(raw_response="test2")

        assert len(manager.get_session_captures()) == 2

        manager.clear_session()
        assert len(manager.get_session_captures()) == 0


class TestCreateRequestCapture:
    """Tests for create_request_capture helper."""

    def test_basic_creation(self):
        """Test basic request capture creation."""
        request = create_request_capture(
            prompt="Test prompt",
            model="test-model",
            provider="test-provider",
        )

        assert request.prompt == "Test prompt"
        assert request.model == "test-model"
        assert request.provider == "test-provider"
        assert request.parameters == {}

    def test_with_parameters(self):
        """Test creation with parameters."""
        request = create_request_capture(
            prompt="Test",
            model="test",
            provider="test",
            temperature=0.7,
            max_tokens=1000,
        )

        assert request.parameters["temperature"] == 0.7
        assert request.parameters["max_tokens"] == 1000


class TestResponseCaptureEdgeCases:
    """Tests for edge cases in response capture."""

    def test_empty_raw_response(self):
        """Test capture with empty response."""
        capture = ResponseCapture(raw_response="")
        assert capture.raw_response == ""

    def test_large_response(self):
        """Test capture with large response."""
        large_response = "x" * 100000
        capture = ResponseCapture(raw_response=large_response)
        assert len(capture.raw_response) == 100000

    def test_unicode_response(self):
        """Test capture with unicode response."""
        unicode_response = '{"name": "日本語テスト", "emoji": "🎉"}'
        capture = ResponseCapture(raw_response=unicode_response)
        assert capture.raw_response == unicode_response

    def test_json_serialization_of_complex_content(self):
        """Test serialization of complex parsed content."""
        complex_content = {
            "nested": {"deep": {"value": [1, 2, 3]}},
            "list": [{"a": 1}, {"b": 2}],
        }
        capture = ResponseCapture(
            raw_response="test",
            parsed_content=complex_content,
        )

        data = capture.to_dict()
        assert data["parsed_content"] == complex_content

    def test_store_handles_special_characters_in_id(self):
        """Test store handles various capture IDs."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store = ResponseCaptureStore(tmpdir)

            # Capture ID with underscores and numbers
            capture = ResponseCapture(
                raw_response="test",
            )
            # Override with known ID
            capture.capture_id = "20251214_103000_123456"

            path = store.save(capture)
            loaded = store.load(capture.capture_id)
            assert loaded.raw_response == "test"
