"""Tests for SQLite audit store (F-123)."""

import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from persona.core.audit.models import (
    AuditRecord,
    GenerationRecord,
    InputRecord,
    OutputRecord,
    SessionInfo,
)
from persona.core.audit.sqlite_store import SqliteStore


@pytest.fixture
def temp_store_path():
    """Create temporary store path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def store(temp_store_path):
    """Create SQLite store."""
    return SqliteStore(temp_store_path)


@pytest.fixture
def sample_record():
    """Create sample audit record."""
    session = SessionInfo(user="test", platform="Linux", python_version="3.12.0")
    input_rec = InputRecord(data_hash="abc123", record_count=100)
    generation = GenerationRecord(
        provider="anthropic", model="claude-sonnet-4", prompt_hash="def456"
    )
    output = OutputRecord(
        personas_hash="ghi789", persona_count=3, generation_time_ms=5000
    )

    return AuditRecord(
        audit_id="test-record-1",
        tool_version="1.0.0",
        session=session,
        input=input_rec,
        generation=generation,
        output=output,
    )


class TestSqliteStore:
    """Tests for SqliteStore."""

    def test_initialization(self, temp_store_path):
        """Test store initialization creates database."""
        store = SqliteStore(temp_store_path)

        assert store.db_path.exists()
        assert store.db_path.name == "audit.db"

    def test_save_and_get(self, store, sample_record):
        """Test saving and retrieving a record."""
        store.save(sample_record)

        retrieved = store.get(sample_record.audit_id)
        assert retrieved is not None
        assert retrieved.audit_id == sample_record.audit_id
        assert retrieved.tool_version == sample_record.tool_version

    def test_get_nonexistent(self, store):
        """Test retrieving nonexistent record."""
        result = store.get("nonexistent-id")
        assert result is None

    def test_save_duplicate_replaces(self, store, sample_record):
        """Test saving duplicate record replaces original."""
        store.save(sample_record)

        # Modify and save again
        sample_record.tool_version = "2.0.0"
        store.save(sample_record)

        retrieved = store.get(sample_record.audit_id)
        assert retrieved.tool_version == "2.0.0"

    def test_list_all(self, store, sample_record):
        """Test listing all records."""
        # Save multiple records
        store.save(sample_record)

        record2 = sample_record.model_copy(deep=True)
        record2.audit_id = "test-record-2"
        store.save(record2)

        records = store.list()
        assert len(records) == 2

    def test_list_with_date_filter(self, store):
        """Test listing records with date filtering."""
        now = datetime.utcnow()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)

        # Create record with timestamp
        session = SessionInfo(user="test", platform="Linux", python_version="3.12.0")
        input_rec = InputRecord(data_hash="abc", record_count=1)
        generation = GenerationRecord(
            provider="test", model="test", prompt_hash="def"
        )
        output = OutputRecord(personas_hash="ghi", persona_count=1, generation_time_ms=1)

        record = AuditRecord(
            audit_id="test-1",
            timestamp=now,
            tool_version="1.0.0",
            session=session,
            input=input_rec,
            generation=generation,
            output=output,
        )
        store.save(record)

        # Test start_date filter
        records = store.list(start_date=yesterday)
        assert len(records) == 1

        records = store.list(start_date=tomorrow)
        assert len(records) == 0

        # Test end_date filter
        records = store.list(end_date=tomorrow)
        assert len(records) == 1

        records = store.list(end_date=yesterday)
        assert len(records) == 0

    def test_list_with_provider_filter(self, store, sample_record):
        """Test listing records with provider filtering."""
        store.save(sample_record)

        # Create record with different provider
        record2 = sample_record.model_copy(deep=True)
        record2.audit_id = "test-record-2"
        record2.generation.provider = "openai"
        store.save(record2)

        # Filter by anthropic
        records = store.list(provider="anthropic")
        assert len(records) == 1
        assert records[0].generation.provider == "anthropic"

        # Filter by openai
        records = store.list(provider="openai")
        assert len(records) == 1
        assert records[0].generation.provider == "openai"

    def test_list_with_model_filter(self, store, sample_record):
        """Test listing records with model filtering."""
        store.save(sample_record)

        records = store.list(model="claude-sonnet-4")
        assert len(records) == 1

        records = store.list(model="gpt-4")
        assert len(records) == 0

    def test_list_with_limit(self, store, sample_record):
        """Test listing records with limit."""
        # Save 5 records
        for i in range(5):
            record = sample_record.model_copy(deep=True)
            record.audit_id = f"test-record-{i}"
            store.save(record)

        records = store.list(limit=3)
        assert len(records) == 3

    def test_delete_existing(self, store, sample_record):
        """Test deleting existing record."""
        store.save(sample_record)

        result = store.delete(sample_record.audit_id)
        assert result is True

        # Verify deleted
        retrieved = store.get(sample_record.audit_id)
        assert retrieved is None

    def test_delete_nonexistent(self, store):
        """Test deleting nonexistent record."""
        result = store.delete("nonexistent-id")
        assert result is False

    def test_prune(self, store):
        """Test pruning old records."""
        now = datetime.utcnow()
        old_date = now - timedelta(days=200)

        # Create old record
        session = SessionInfo(user="test", platform="Linux", python_version="3.12.0")
        input_rec = InputRecord(data_hash="abc", record_count=1)
        generation = GenerationRecord(
            provider="test", model="test", prompt_hash="def"
        )
        output = OutputRecord(personas_hash="ghi", persona_count=1, generation_time_ms=1)

        old_record = AuditRecord(
            audit_id="old-record",
            timestamp=old_date,
            tool_version="1.0.0",
            session=session,
            input=input_rec,
            generation=generation,
            output=output,
        )
        store.save(old_record)

        # Create new record
        new_record = old_record.model_copy(deep=True)
        new_record.audit_id = "new-record"
        new_record.timestamp = now
        store.save(new_record)

        # Prune records older than 180 days
        cutoff = now - timedelta(days=180)
        deleted_count = store.prune(cutoff)

        assert deleted_count == 1

        # Verify old record deleted
        assert store.get("old-record") is None
        assert store.get("new-record") is not None

    def test_count(self, store, sample_record):
        """Test counting records."""
        assert store.count() == 0

        store.save(sample_record)
        assert store.count() == 1

        record2 = sample_record.model_copy(deep=True)
        record2.audit_id = "test-record-2"
        store.save(record2)
        assert store.count() == 2
