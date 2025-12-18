"""Tests for audit trail interface (F-123)."""

import tempfile
from pathlib import Path

import pytest
from persona.core.audit.models import AuditConfig
from persona.core.audit.trail import AuditTrail


@pytest.fixture
def temp_store_path():
    """Create temporary store path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def trail(temp_store_path):
    """Create audit trail with temporary storage."""
    config = AuditConfig(store_path=temp_store_path)
    return AuditTrail(config)


@pytest.fixture
def trail_with_signing(temp_store_path):
    """Create audit trail with signing enabled."""
    config = AuditConfig(
        store_path=temp_store_path,
        sign_records=True,
        signing_key="test-secret-key",
    )
    return AuditTrail(config)


class TestAuditTrail:
    """Tests for AuditTrail."""

    def test_initialization(self):
        """Test trail initialization."""
        trail = AuditTrail()

        assert trail.config is not None
        assert trail.logger is not None

    def test_query_empty(self, trail):
        """Test querying empty trail."""
        records = trail.query()
        assert len(records) == 0

    def test_query_with_records(self, trail):
        """Test querying with records."""
        # Log some records
        trail.logger.log_generation(
            data="test",
            record_count=1,
            provider="test",
            model="test",
            prompt="test",
            personas="test",
            persona_count=1,
            generation_time_ms=1000,
        )

        records = trail.query()
        assert len(records) == 1

    def test_query_with_filters(self, trail):
        """Test querying with filters."""
        # Log records with different providers
        trail.logger.log_generation(
            data="test1",
            record_count=1,
            provider="anthropic",
            model="claude",
            prompt="test",
            personas="test",
            persona_count=1,
            generation_time_ms=1000,
        )

        trail.logger.log_generation(
            data="test2",
            record_count=1,
            provider="openai",
            model="gpt-4",
            prompt="test",
            personas="test",
            persona_count=1,
            generation_time_ms=1000,
        )

        # Query by provider
        records = trail.query(provider="anthropic")
        assert len(records) == 1
        assert records[0].generation.provider == "anthropic"

    def test_get_existing_record(self, trail):
        """Test getting an existing record."""
        # Log a record
        record = trail.logger.log_generation(
            data="test",
            record_count=1,
            provider="test",
            model="test",
            prompt="test",
            personas="test",
            persona_count=1,
            generation_time_ms=1000,
        )

        # Get it
        retrieved = trail.get(record.audit_id)
        assert retrieved is not None
        assert retrieved.audit_id == record.audit_id

    def test_get_nonexistent_record(self, trail):
        """Test getting a nonexistent record."""
        result = trail.get("nonexistent-id")
        assert result is None

    def test_verify_unsigned_record(self, trail):
        """Test verifying an unsigned record."""
        # Log record without signing
        record = trail.logger.log_generation(
            data="test",
            record_count=1,
            provider="test",
            model="test",
            prompt="test",
            personas="test",
            persona_count=1,
            generation_time_ms=1000,
        )

        is_valid, error = trail.verify(record.audit_id)
        assert is_valid is False
        assert error == "Record is not signed"

    def test_verify_signed_record(self, trail_with_signing):
        """Test verifying a signed record."""
        # Log record with signing
        record = trail_with_signing.logger.log_generation(
            data="test",
            record_count=1,
            provider="test",
            model="test",
            prompt="test",
            personas="test",
            persona_count=1,
            generation_time_ms=1000,
        )

        is_valid, error = trail_with_signing.verify(record.audit_id)
        assert is_valid is True
        assert error is None

    def test_verify_nonexistent_record(self, trail):
        """Test verifying a nonexistent record."""
        is_valid, error = trail.verify("nonexistent-id")
        assert is_valid is False
        assert error == "Record not found"

    def test_export_json(self, trail):
        """Test exporting as JSON."""
        # Log some records
        trail.logger.log_generation(
            data="test",
            record_count=1,
            provider="test",
            model="test",
            prompt="test",
            personas="test",
            persona_count=1,
            generation_time_ms=1000,
        )

        result = trail.export(format="json")
        assert isinstance(result, str)
        assert result.startswith("[")
        assert "test" in result

    def test_export_jsonl(self, trail):
        """Test exporting as JSON Lines."""
        # Log some records
        trail.logger.log_generation(
            data="test",
            record_count=1,
            provider="test",
            model="test",
            prompt="test",
            personas="test",
            persona_count=1,
            generation_time_ms=1000,
        )

        result = trail.export(format="jsonl")
        assert isinstance(result, str)
        assert "\n" not in result or result.count("\n") == result.count("{")

    def test_export_csv(self, trail):
        """Test exporting as CSV."""
        # Log some records
        trail.logger.log_generation(
            data="test",
            record_count=1,
            provider="test",
            model="test",
            prompt="test",
            personas="test",
            persona_count=1,
            generation_time_ms=1000,
        )

        result = trail.export(format="csv")
        assert isinstance(result, str)
        assert "audit_id" in result
        assert "provider" in result

    def test_export_to_file(self, trail, temp_store_path):
        """Test exporting to file."""
        # Log some records
        trail.logger.log_generation(
            data="test",
            record_count=1,
            provider="test",
            model="test",
            prompt="test",
            personas="test",
            persona_count=1,
            generation_time_ms=1000,
        )

        output_path = temp_store_path / "export.json"
        trail.export(format="json", output_path=output_path)

        assert output_path.exists()
        content = output_path.read_text()
        assert "test" in content

    def test_export_with_filters(self, trail):
        """Test exporting with filters."""
        # Log records with different providers
        trail.logger.log_generation(
            data="test1",
            record_count=1,
            provider="anthropic",
            model="claude",
            prompt="test",
            personas="test",
            persona_count=1,
            generation_time_ms=1000,
        )

        trail.logger.log_generation(
            data="test2",
            record_count=1,
            provider="openai",
            model="gpt-4",
            prompt="test",
            personas="test",
            persona_count=1,
            generation_time_ms=1000,
        )

        # Export only anthropic
        result = trail.export(format="json", provider="anthropic")
        assert "anthropic" in result
        assert "openai" not in result

    def test_export_invalid_format(self, trail):
        """Test exporting with invalid format."""
        with pytest.raises(ValueError, match="Unknown format"):
            trail.export(format="xml")

    def test_prune(self, trail):
        """Test pruning records."""
        # Log a record
        trail.logger.log_generation(
            data="test",
            record_count=1,
            provider="test",
            model="test",
            prompt="test",
            personas="test",
            persona_count=1,
            generation_time_ms=1000,
        )

        # Prune with 0 day retention
        deleted_count = trail.prune(retention_days=0)
        assert deleted_count >= 0

    def test_count(self, trail):
        """Test counting records."""
        assert trail.count() == 0

        # Log some records
        trail.logger.log_generation(
            data="test1",
            record_count=1,
            provider="test",
            model="test",
            prompt="test",
            personas="test",
            persona_count=1,
            generation_time_ms=1000,
        )

        assert trail.count() == 1

        trail.logger.log_generation(
            data="test2",
            record_count=1,
            provider="test",
            model="test",
            prompt="test",
            personas="test",
            persona_count=1,
            generation_time_ms=1000,
        )

        assert trail.count() == 2

    def test_csv_export_format(self, trail):
        """Test CSV export has correct columns."""
        # Log a record
        trail.logger.log_generation(
            data="test",
            record_count=1,
            provider="anthropic",
            model="claude-sonnet-4",
            prompt="test prompt",
            personas=[{"name": "Test"}],
            persona_count=1,
            generation_time_ms=5000,
        )

        csv_output = trail.export(format="csv")
        lines = csv_output.strip().split("\n")

        # Check header
        assert "audit_id" in lines[0]
        assert "provider" in lines[0]
        assert "model" in lines[0]

        # Check data row exists
        assert len(lines) >= 2

    def test_export_empty_records(self, trail):
        """Test exporting when no records exist."""
        result = trail.export(format="json")
        assert result == "[]"
