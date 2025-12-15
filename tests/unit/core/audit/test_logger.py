"""Tests for audit logger (F-123)."""

import tempfile
from pathlib import Path

import pytest

from persona.core.audit.logger import AuditLogger
from persona.core.audit.models import AuditConfig


@pytest.fixture
def temp_store_path():
    """Create temporary store path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def logger(temp_store_path):
    """Create audit logger with temporary storage."""
    config = AuditConfig(store_path=temp_store_path)
    return AuditLogger(config)


class TestAuditLogger:
    """Tests for AuditLogger."""

    def test_initialization(self):
        """Test logger initialization."""
        logger = AuditLogger()

        assert logger.config is not None
        assert logger.config.enabled is True
        assert logger._session_info is not None

    def test_hash_data_string(self):
        """Test hashing string data."""
        data = "test data"
        hash_result = AuditLogger.hash_data(data)

        assert isinstance(hash_result, str)
        assert len(hash_result) == 64  # SHA-256 hex digest

    def test_hash_data_bytes(self):
        """Test hashing bytes data."""
        data = b"test data"
        hash_result = AuditLogger.hash_data(data)

        assert isinstance(hash_result, str)
        assert len(hash_result) == 64

    def test_hash_data_dict(self):
        """Test hashing dictionary data."""
        data = {"key": "value", "number": 123}
        hash_result = AuditLogger.hash_data(data)

        assert isinstance(hash_result, str)
        assert len(hash_result) == 64

    def test_hash_data_deterministic(self):
        """Test hashing is deterministic."""
        data = {"key": "value"}

        hash1 = AuditLogger.hash_data(data)
        hash2 = AuditLogger.hash_data(data)

        assert hash1 == hash2

    def test_hash_data_dict_order_independent(self):
        """Test hashing is order-independent for dicts."""
        data1 = {"a": 1, "b": 2}
        data2 = {"b": 2, "a": 1}

        hash1 = AuditLogger.hash_data(data1)
        hash2 = AuditLogger.hash_data(data2)

        assert hash1 == hash2

    def test_log_generation_basic(self, logger):
        """Test logging a basic generation session."""
        record = logger.log_generation(
            data={"test": "data"},
            record_count=10,
            provider="anthropic",
            model="claude-sonnet-4",
            prompt="Generate personas",
            personas=[{"name": "Test"}],
            persona_count=1,
            generation_time_ms=5000,
        )

        assert record.audit_id is not None
        assert record.tool_version is not None
        assert record.input.data_hash != ""
        assert record.input.record_count == 10
        assert record.generation.provider == "anthropic"
        assert record.generation.model == "claude-sonnet-4"
        assert record.generation.prompt_hash != ""
        assert record.output.personas_hash != ""
        assert record.output.persona_count == 1
        assert record.output.generation_time_ms == 5000

    def test_log_generation_with_paths(self, logger):
        """Test logging with file paths."""
        record = logger.log_generation(
            data="test",
            data_path=Path("/path/to/data.csv"),
            record_count=100,
            provider="openai",
            model="gpt-4",
            prompt="test",
            personas="test",
            output_path=Path("/path/to/output"),
            persona_count=3,
            generation_time_ms=10000,
        )

        assert record.input.data_path == "/path/to/data.csv"
        assert record.output.output_path == "/path/to/output"

    def test_log_generation_with_workflow(self, logger):
        """Test logging with workflow and template."""
        record = logger.log_generation(
            data="test",
            record_count=1,
            provider="test",
            model="test",
            prompt="test",
            workflow="custom",
            template="advanced",
            personas="test",
            persona_count=1,
            generation_time_ms=1000,
        )

        assert record.generation.workflow == "custom"
        assert record.generation.template == "advanced"

    def test_log_generation_with_parameters(self, logger):
        """Test logging with generation parameters."""
        params = {"temperature": 0.7, "max_tokens": 2000}

        record = logger.log_generation(
            data="test",
            record_count=1,
            provider="test",
            model="test",
            parameters=params,
            prompt="test",
            personas="test",
            persona_count=1,
            generation_time_ms=1000,
        )

        assert record.generation.parameters == params

    def test_log_generation_with_tokens(self, logger):
        """Test logging with token usage."""
        tokens = {"input": 1000, "output": 500}

        record = logger.log_generation(
            data="test",
            record_count=1,
            provider="test",
            model="test",
            prompt="test",
            personas="test",
            persona_count=1,
            generation_time_ms=1000,
            tokens_used=tokens,
        )

        assert record.output.tokens_used == tokens

    def test_log_generation_saves_to_store(self, logger):
        """Test logging saves record to store."""
        record = logger.log_generation(
            data="test",
            record_count=1,
            provider="test",
            model="test",
            prompt="test",
            personas="test",
            persona_count=1,
            generation_time_ms=1000,
        )

        # Should be retrievable from store
        retrieved = logger.get_record(record.audit_id)
        assert retrieved is not None
        assert retrieved.audit_id == record.audit_id

    def test_log_generation_disabled(self, temp_store_path):
        """Test logging when disabled."""
        config = AuditConfig(enabled=False, store_path=temp_store_path)
        logger = AuditLogger(config)

        record = logger.log_generation(
            data="test",
            record_count=1,
            provider="test",
            model="test",
            prompt="test",
            personas="test",
            persona_count=1,
            generation_time_ms=1000,
        )

        # Should return minimal record
        assert record.audit_id == "disabled"

    def test_log_generation_with_signing(self, temp_store_path):
        """Test logging with record signing."""
        config = AuditConfig(
            store_path=temp_store_path,
            sign_records=True,
            signing_key="test-secret-key",
        )
        logger = AuditLogger(config)

        record = logger.log_generation(
            data="test",
            record_count=1,
            provider="test",
            model="test",
            prompt="test",
            personas="test",
            persona_count=1,
            generation_time_ms=1000,
        )

        assert record.signature is not None
        assert len(record.signature) == 64

    def test_get_record(self, logger):
        """Test retrieving a record."""
        # Log a record
        record = logger.log_generation(
            data="test",
            record_count=1,
            provider="test",
            model="test",
            prompt="test",
            personas="test",
            persona_count=1,
            generation_time_ms=1000,
        )

        # Retrieve it
        retrieved = logger.get_record(record.audit_id)
        assert retrieved is not None
        assert retrieved.audit_id == record.audit_id

    def test_list_records(self, logger):
        """Test listing records."""
        # Log multiple records
        for i in range(3):
            logger.log_generation(
                data=f"test{i}",
                record_count=1,
                provider="test",
                model="test",
                prompt="test",
                personas="test",
                persona_count=1,
                generation_time_ms=1000,
            )

        records = logger.list_records()
        assert len(records) == 3

    def test_list_records_with_filters(self, logger):
        """Test listing records with filters."""
        # Log records with different providers
        logger.log_generation(
            data="test1",
            record_count=1,
            provider="anthropic",
            model="claude",
            prompt="test",
            personas="test",
            persona_count=1,
            generation_time_ms=1000,
        )

        logger.log_generation(
            data="test2",
            record_count=1,
            provider="openai",
            model="gpt-4",
            prompt="test",
            personas="test",
            persona_count=1,
            generation_time_ms=1000,
        )

        # Filter by provider
        records = logger.list_records(provider="anthropic")
        assert len(records) == 1
        assert records[0].generation.provider == "anthropic"

    def test_prune_old_records(self, logger):
        """Test pruning old records."""
        # Log a record
        logger.log_generation(
            data="test",
            record_count=1,
            provider="test",
            model="test",
            prompt="test",
            personas="test",
            persona_count=1,
            generation_time_ms=1000,
        )

        # Prune with 0 day retention (delete everything)
        deleted_count = logger.prune_old_records(retention_days=0)
        assert deleted_count >= 0

    def test_store_lazy_initialization(self, temp_store_path):
        """Test store is lazily initialized."""
        config = AuditConfig(store_path=temp_store_path)
        logger = AuditLogger(config)

        assert logger._store is None

        # Access store
        _ = logger.store

        assert logger._store is not None

    def test_sqlite_store_creation(self, temp_store_path):
        """Test SQLite store is created by default."""
        config = AuditConfig(store_type="sqlite", store_path=temp_store_path)
        logger = AuditLogger(config)

        store = logger.store
        assert store.__class__.__name__ == "SqliteStore"

    def test_json_store_creation(self, temp_store_path):
        """Test JSON store creation."""
        config = AuditConfig(store_type="json", store_path=temp_store_path)
        logger = AuditLogger(config)

        store = logger.store
        assert store.__class__.__name__ == "JsonStore"
