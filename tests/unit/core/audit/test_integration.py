"""Integration tests for audit trail (F-123)."""

import tempfile
from pathlib import Path

import pytest

from persona.core.audit import AuditConfig, AuditLogger, AuditTrail


@pytest.fixture
def temp_store_path():
    """Create temporary store path."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


class TestAuditIntegration:
    """Integration tests for complete audit workflow."""

    def test_full_workflow_sqlite(self, temp_store_path):
        """Test complete workflow with SQLite backend."""
        # Configure audit trail
        config = AuditConfig(
            enabled=True,
            store_type="sqlite",
            store_path=temp_store_path,
            retention_days=180,
        )

        # Create logger and log generation
        logger = AuditLogger(config)
        record = logger.log_generation(
            data={"user": "Alice", "age": 25},
            data_path=Path("/data/users.csv"),
            record_count=100,
            data_format="csv",
            provider="anthropic",
            model="claude-sonnet-4",
            parameters={"temperature": 0.7},
            prompt="Generate 3 diverse user personas",
            workflow="default",
            template="standard",
            personas=[
                {"name": "Tech Sarah", "age": 28},
                {"name": "Designer Mike", "age": 35},
                {"name": "Manager Lisa", "age": 42},
            ],
            output_path=Path("/output/personas"),
            persona_count=3,
            generation_time_ms=5432,
            tokens_used={"input": 1234, "output": 567},
        )

        # Verify record was created
        assert record.audit_id is not None
        assert record.input.record_count == 100
        assert record.generation.provider == "anthropic"
        assert record.output.persona_count == 3

        # Query using trail interface
        trail = AuditTrail(config)
        records = trail.query()
        assert len(records) == 1

        # Get specific record
        retrieved = trail.get(record.audit_id)
        assert retrieved is not None
        assert retrieved.audit_id == record.audit_id

        # Export as JSON
        json_export = trail.export(format="json")
        assert record.audit_id in json_export

        # Export as CSV
        csv_export = trail.export(format="csv")
        assert "audit_id" in csv_export
        assert "anthropic" in csv_export

        # Count records
        assert trail.count() == 1

    def test_full_workflow_json(self, temp_store_path):
        """Test complete workflow with JSON backend."""
        # Configure audit trail
        config = AuditConfig(
            enabled=True,
            store_type="json",
            store_path=temp_store_path,
            retention_days=90,
        )

        # Create logger and log generation
        logger = AuditLogger(config)
        record = logger.log_generation(
            data="test data",
            record_count=50,
            provider="openai",
            model="gpt-4",
            prompt="Generate personas",
            personas=["persona1", "persona2"],
            persona_count=2,
            generation_time_ms=3000,
        )

        # Verify record was saved to JSON file
        json_file = temp_store_path / "records" / f"{record.audit_id}.json"
        assert json_file.exists()

        # Query using trail interface
        trail = AuditTrail(config)
        records = trail.query(provider="openai")
        assert len(records) == 1
        assert records[0].generation.model == "gpt-4"

    def test_full_workflow_with_signing(self, temp_store_path):
        """Test complete workflow with record signing."""
        # Configure audit trail with signing
        config = AuditConfig(
            enabled=True,
            store_type="sqlite",
            store_path=temp_store_path,
            sign_records=True,
            signing_key="my-secret-key-123",
        )

        # Create logger and log generation
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

        # Verify signature was added
        assert record.signature is not None
        assert len(record.signature) == 64

        # Verify signature using trail
        trail = AuditTrail(config)
        is_valid, error = trail.verify(record.audit_id)
        assert is_valid is True
        assert error is None

    def test_multiple_generations(self, temp_store_path):
        """Test logging multiple generation sessions."""
        config = AuditConfig(store_path=temp_store_path)
        logger = AuditLogger(config)

        # Log 5 generation sessions
        providers = ["anthropic", "openai", "anthropic", "gemini", "openai"]
        records = []

        for i, provider in enumerate(providers):
            record = logger.log_generation(
                data=f"data-{i}",
                record_count=i + 1,
                provider=provider,
                model=f"model-{i}",
                prompt=f"prompt-{i}",
                personas=f"personas-{i}",
                persona_count=1,
                generation_time_ms=(i + 1) * 1000,
            )
            records.append(record)

        # Query all records
        trail = AuditTrail(config)
        all_records = trail.query()
        assert len(all_records) == 5

        # Filter by provider
        anthropic_records = trail.query(provider="anthropic")
        assert len(anthropic_records) == 2

        openai_records = trail.query(provider="openai")
        assert len(openai_records) == 2

        gemini_records = trail.query(provider="gemini")
        assert len(gemini_records) == 1

    def test_disabled_audit_trail(self, temp_store_path):
        """Test behaviour when audit trail is disabled."""
        config = AuditConfig(
            enabled=False,
            store_path=temp_store_path,
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

        # Should return minimal disabled record
        assert record.audit_id == "disabled"

        # Store should be empty
        trail = AuditTrail(config)
        assert trail.count() == 0

    def test_hash_consistency(self, temp_store_path):
        """Test that hashing is consistent across sessions."""
        config = AuditConfig(store_path=temp_store_path)
        logger1 = AuditLogger(config)

        # Log with first logger
        data = {"key": "value", "number": 123}
        record1 = logger1.log_generation(
            data=data,
            record_count=1,
            provider="test",
            model="test",
            prompt="test prompt",
            personas=["persona1"],
            persona_count=1,
            generation_time_ms=1000,
        )

        # Create new logger
        logger2 = AuditLogger(config)

        # Log with same data
        record2 = logger2.log_generation(
            data=data,
            record_count=1,
            provider="test",
            model="test",
            prompt="test prompt",
            personas=["persona1"],
            persona_count=1,
            generation_time_ms=1000,
        )

        # Hashes should be the same
        assert record1.input.data_hash == record2.input.data_hash
        assert record1.generation.prompt_hash == record2.generation.prompt_hash
        assert record1.output.personas_hash == record2.output.personas_hash

    def test_prune_workflow(self, temp_store_path):
        """Test pruning old records."""
        config = AuditConfig(
            store_path=temp_store_path,
            retention_days=180,
        )

        logger = AuditLogger(config)

        # Log some records
        for i in range(3):
            logger.log_generation(
                data=f"test-{i}",
                record_count=1,
                provider="test",
                model="test",
                prompt="test",
                personas="test",
                persona_count=1,
                generation_time_ms=1000,
            )

        trail = AuditTrail(config)
        assert trail.count() == 3

        # Prune with large retention should keep all records (current)
        deleted = trail.prune(retention_days=365)
        assert deleted == 0
        assert trail.count() == 3

        # Prune with negative days retention (future cutoff - deletes all)
        deleted = trail.prune(retention_days=-1)
        assert deleted == 3
        assert trail.count() == 0
