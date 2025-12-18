"""Tests for audit trail models (F-123)."""

from pathlib import Path

from persona.core.audit.models import (
    AuditConfig,
    AuditRecord,
    GenerationRecord,
    InputRecord,
    OutputRecord,
    SessionInfo,
)


class TestSessionInfo:
    """Tests for SessionInfo model."""

    def test_capture_current(self):
        """Test capturing current session information."""
        session = SessionInfo.capture_current()

        assert session.user is not None
        assert session.platform is not None
        assert session.python_version is not None
        assert session.python_version.startswith("3.")

    def test_manual_creation(self):
        """Test manual creation of session info."""
        session = SessionInfo(
            user="testuser",
            platform="Linux",
            python_version="3.12.0",
        )

        assert session.user == "testuser"
        assert session.platform == "Linux"
        assert session.python_version == "3.12.0"


class TestInputRecord:
    """Tests for InputRecord model."""

    def test_creation(self):
        """Test creating input record."""
        record = InputRecord(
            data_hash="abc123",
            data_path="/path/to/data.csv",
            record_count=100,
            format="csv",
        )

        assert record.data_hash == "abc123"
        assert record.data_path == "/path/to/data.csv"
        assert record.record_count == 100
        assert record.format == "csv"

    def test_optional_fields(self):
        """Test optional fields can be None."""
        record = InputRecord(
            data_hash="abc123",
            record_count=100,
        )

        assert record.data_hash == "abc123"
        assert record.data_path is None
        assert record.format is None


class TestGenerationRecord:
    """Tests for GenerationRecord model."""

    def test_creation(self):
        """Test creating generation record."""
        record = GenerationRecord(
            provider="anthropic",
            model="claude-sonnet-4",
            parameters={"temperature": 0.7},
            prompt_hash="def456",
            workflow="default",
            template="standard",
        )

        assert record.provider == "anthropic"
        assert record.model == "claude-sonnet-4"
        assert record.parameters == {"temperature": 0.7}
        assert record.prompt_hash == "def456"
        assert record.workflow == "default"
        assert record.template == "standard"

    def test_empty_parameters(self):
        """Test empty parameters default."""
        record = GenerationRecord(
            provider="openai",
            model="gpt-4",
            prompt_hash="abc",
        )

        assert record.parameters == {}


class TestOutputRecord:
    """Tests for OutputRecord model."""

    def test_creation(self):
        """Test creating output record."""
        record = OutputRecord(
            personas_hash="ghi789",
            output_path="/path/to/output",
            persona_count=3,
            generation_time_ms=5000,
            tokens_used={"input": 1000, "output": 500},
        )

        assert record.personas_hash == "ghi789"
        assert record.output_path == "/path/to/output"
        assert record.persona_count == 3
        assert record.generation_time_ms == 5000
        assert record.tokens_used == {"input": 1000, "output": 500}


class TestAuditRecord:
    """Tests for AuditRecord model."""

    def test_creation(self):
        """Test creating complete audit record."""
        session = SessionInfo(
            user="testuser",
            platform="Linux",
            python_version="3.12.0",
        )
        input_rec = InputRecord(
            data_hash="abc",
            record_count=100,
        )
        generation = GenerationRecord(
            provider="anthropic",
            model="claude-sonnet-4",
            prompt_hash="def",
        )
        output = OutputRecord(
            personas_hash="ghi",
            persona_count=3,
            generation_time_ms=5000,
        )

        record = AuditRecord(
            audit_id="test-123",
            tool_version="1.0.0",
            session=session,
            input=input_rec,
            generation=generation,
            output=output,
        )

        assert record.audit_id == "test-123"
        assert record.tool_version == "1.0.0"
        assert record.session == session
        assert record.input == input_rec
        assert record.generation == generation
        assert record.output == output
        assert record.signature is None

    def test_with_signature(self):
        """Test audit record with signature."""
        session = SessionInfo.capture_current()
        input_rec = InputRecord(data_hash="abc", record_count=1)
        generation = GenerationRecord(provider="test", model="test", prompt_hash="def")
        output = OutputRecord(
            personas_hash="ghi", persona_count=1, generation_time_ms=1
        )

        record = AuditRecord(
            audit_id="test-123",
            tool_version="1.0.0",
            session=session,
            input=input_rec,
            generation=generation,
            output=output,
            signature="abc123signature",
        )

        assert record.signature == "abc123signature"

    def test_json_serialization(self):
        """Test JSON serialization of audit record."""
        session = SessionInfo.capture_current()
        input_rec = InputRecord(data_hash="abc", record_count=1)
        generation = GenerationRecord(provider="test", model="test", prompt_hash="def")
        output = OutputRecord(
            personas_hash="ghi", persona_count=1, generation_time_ms=1
        )

        record = AuditRecord(
            audit_id="test-123",
            tool_version="1.0.0",
            session=session,
            input=input_rec,
            generation=generation,
            output=output,
        )

        # Should serialize to JSON
        json_str = record.model_dump_json()
        assert isinstance(json_str, str)
        assert "test-123" in json_str

        # Should deserialize back
        restored = AuditRecord.model_validate_json(json_str)
        assert restored.audit_id == record.audit_id


class TestAuditConfig:
    """Tests for AuditConfig model."""

    def test_defaults(self):
        """Test default configuration values."""
        config = AuditConfig()

        assert config.enabled is True
        assert config.store_type == "sqlite"
        assert config.store_path is None
        assert config.retention_days == 180
        assert config.sign_records is False
        assert config.signing_key is None

    def test_custom_values(self):
        """Test custom configuration values."""
        config = AuditConfig(
            enabled=False,
            store_type="json",
            store_path=Path("/custom/path"),
            retention_days=90,
            sign_records=True,
            signing_key="secret",
        )

        assert config.enabled is False
        assert config.store_type == "json"
        assert config.store_path == Path("/custom/path")
        assert config.retention_days == 90
        assert config.sign_records is True
        assert config.signing_key == "secret"

    def test_get_store_path_custom(self):
        """Test get_store_path with custom path."""
        custom_path = Path("/custom/audit")
        config = AuditConfig(store_path=custom_path)

        assert config.get_store_path() == custom_path

    def test_get_store_path_default(self):
        """Test get_store_path with default platform path."""
        config = AuditConfig()
        path = config.get_store_path()

        # Should use platform data directory
        assert path.name == "audit"
        assert "persona" in str(path)
