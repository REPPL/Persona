"""Tests for audit record signing (F-123)."""

import pytest
from persona.core.audit.models import (
    AuditRecord,
    GenerationRecord,
    InputRecord,
    OutputRecord,
    SessionInfo,
)
from persona.core.audit.signing import sign_record, verify_signature


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


class TestSigning:
    """Tests for HMAC-SHA256 signing."""

    def test_sign_record(self, sample_record):
        """Test signing a record."""
        signing_key = "test-secret-key"
        signature = sign_record(sample_record, signing_key)

        assert isinstance(signature, str)
        assert len(signature) == 64  # SHA-256 produces 64 hex characters

    def test_sign_deterministic(self, sample_record):
        """Test signing is deterministic."""
        signing_key = "test-secret-key"

        sig1 = sign_record(sample_record, signing_key)
        sig2 = sign_record(sample_record, signing_key)

        assert sig1 == sig2

    def test_sign_different_keys(self, sample_record):
        """Test different keys produce different signatures."""
        sig1 = sign_record(sample_record, "key1")
        sig2 = sign_record(sample_record, "key2")

        assert sig1 != sig2

    def test_sign_different_records(self):
        """Test different records produce different signatures."""
        session = SessionInfo(user="test", platform="Linux", python_version="3.12.0")
        input_rec = InputRecord(data_hash="abc", record_count=1)
        generation = GenerationRecord(provider="test", model="test", prompt_hash="def")
        output = OutputRecord(
            personas_hash="ghi", persona_count=1, generation_time_ms=1
        )

        record1 = AuditRecord(
            audit_id="test-1",
            tool_version="1.0.0",
            session=session,
            input=input_rec,
            generation=generation,
            output=output,
        )

        record2 = AuditRecord(
            audit_id="test-2",
            tool_version="1.0.0",
            session=session,
            input=input_rec,
            generation=generation,
            output=output,
        )

        signing_key = "test-key"
        sig1 = sign_record(record1, signing_key)
        sig2 = sign_record(record2, signing_key)

        assert sig1 != sig2

    def test_verify_valid_signature(self, sample_record):
        """Test verifying a valid signature."""
        signing_key = "test-secret-key"

        # Sign record
        signature = sign_record(sample_record, signing_key)
        sample_record.signature = signature

        # Verify
        is_valid = verify_signature(sample_record, signing_key)
        assert is_valid is True

    def test_verify_invalid_signature(self, sample_record):
        """Test verifying an invalid signature."""
        signing_key = "test-secret-key"

        # Set wrong signature
        sample_record.signature = "invalid-signature"

        # Verify
        is_valid = verify_signature(sample_record, signing_key)
        assert is_valid is False

    def test_verify_wrong_key(self, sample_record):
        """Test verifying with wrong key."""
        # Sign with one key
        signature = sign_record(sample_record, "key1")
        sample_record.signature = signature

        # Verify with different key
        is_valid = verify_signature(sample_record, "key2")
        assert is_valid is False

    def test_verify_no_signature(self, sample_record):
        """Test verifying record without signature."""
        signing_key = "test-secret-key"

        is_valid = verify_signature(sample_record, signing_key)
        assert is_valid is False

    def test_verify_tampered_record(self, sample_record):
        """Test verifying tampered record."""
        signing_key = "test-secret-key"

        # Sign record
        signature = sign_record(sample_record, signing_key)
        sample_record.signature = signature

        # Tamper with record
        sample_record.output.persona_count = 999

        # Verify should fail
        is_valid = verify_signature(sample_record, signing_key)
        assert is_valid is False

    def test_signature_excludes_signature_field(self, sample_record):
        """Test that signature field itself is excluded from signing."""
        signing_key = "test-secret-key"

        # Sign record
        sig1 = sign_record(sample_record, signing_key)

        # Add signature and sign again
        sample_record.signature = sig1
        sig2 = sign_record(sample_record, signing_key)

        # Signatures should be the same (signature field excluded)
        assert sig1 == sig2
