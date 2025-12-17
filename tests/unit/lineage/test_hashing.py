"""Tests for lineage hashing utilities."""

import tempfile
from pathlib import Path

import pytest

from persona.core.lineage.hashing import (
    extract_digest,
    hash_content,
    hash_dict,
    hash_file,
    hash_persona,
    is_valid_hash,
    verify_file_hash,
    verify_hash,
)


class TestHashContent:
    """Tests for hash_content function."""

    def test_hash_string(self):
        """Test hashing a string."""
        result = hash_content("hello world")
        assert result.startswith("sha256:")
        assert len(result) == 71  # sha256: + 64 hex chars

    def test_hash_bytes(self):
        """Test hashing bytes."""
        result = hash_content(b"hello world")
        assert result.startswith("sha256:")

    def test_same_content_same_hash(self):
        """Test same content produces same hash."""
        hash1 = hash_content("test content")
        hash2 = hash_content("test content")
        assert hash1 == hash2

    def test_different_content_different_hash(self):
        """Test different content produces different hash."""
        hash1 = hash_content("content a")
        hash2 = hash_content("content b")
        assert hash1 != hash2

    def test_string_and_bytes_equivalent(self):
        """Test string and bytes hash to same value."""
        hash1 = hash_content("hello")
        hash2 = hash_content(b"hello")
        assert hash1 == hash2


class TestHashFile:
    """Tests for hash_file function."""

    def test_hash_file(self):
        """Test hashing a file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("file content")
            temp_path = Path(f.name)

        try:
            result = hash_file(temp_path)
            assert result.startswith("sha256:")
        finally:
            temp_path.unlink()

    def test_hash_file_matches_content(self):
        """Test file hash matches content hash."""
        content = "test file content"
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            file_hash = hash_file(temp_path)
            content_hash = hash_content(content)
            assert file_hash == content_hash
        finally:
            temp_path.unlink()

    def test_hash_nonexistent_file_raises(self):
        """Test hashing non-existent file raises error."""
        with pytest.raises(FileNotFoundError):
            hash_file("/nonexistent/path/file.txt")


class TestHashDict:
    """Tests for hash_dict function."""

    def test_hash_dict(self):
        """Test hashing a dictionary."""
        result = hash_dict({"key": "value"})
        assert result.startswith("sha256:")

    def test_same_dict_same_hash(self):
        """Test same dictionary produces same hash."""
        hash1 = hash_dict({"a": 1, "b": 2})
        hash2 = hash_dict({"a": 1, "b": 2})
        assert hash1 == hash2

    def test_key_order_independent(self):
        """Test dictionary hash is key order independent."""
        hash1 = hash_dict({"a": 1, "b": 2})
        hash2 = hash_dict({"b": 2, "a": 1})
        assert hash1 == hash2

    def test_different_dict_different_hash(self):
        """Test different dictionaries produce different hashes."""
        hash1 = hash_dict({"a": 1})
        hash2 = hash_dict({"a": 2})
        assert hash1 != hash2


class TestHashPersona:
    """Tests for hash_persona function."""

    def test_hash_persona(self):
        """Test hashing a persona."""
        persona = {
            "name": "Alice",
            "background": "Engineer",
            "goals": ["Learn new skills"],
        }
        result = hash_persona(persona)
        assert result.startswith("sha256:")

    def test_ignores_metadata(self):
        """Test that non-content fields are ignored."""
        persona1 = {"name": "Alice", "id": "123"}
        persona2 = {"name": "Alice", "id": "456"}
        # id is not in content_keys, so both should hash the same
        hash1 = hash_persona(persona1)
        hash2 = hash_persona(persona2)
        assert hash1 == hash2

    def test_content_changes_hash(self):
        """Test that content changes affect hash."""
        persona1 = {"name": "Alice"}
        persona2 = {"name": "Bob"}
        hash1 = hash_persona(persona1)
        hash2 = hash_persona(persona2)
        assert hash1 != hash2


class TestVerifyHash:
    """Tests for verification functions."""

    def test_verify_hash_matches(self):
        """Test verification passes for matching hash."""
        content = "test content"
        h = hash_content(content)
        assert verify_hash(content, h) is True

    def test_verify_hash_mismatch(self):
        """Test verification fails for mismatched hash."""
        assert verify_hash("content", "sha256:wronghash") is False

    def test_verify_file_hash_matches(self):
        """Test file verification passes for matching hash."""
        content = "file content"
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write(content)
            temp_path = Path(f.name)

        try:
            h = hash_file(temp_path)
            assert verify_file_hash(temp_path, h) is True
        finally:
            temp_path.unlink()

    def test_verify_file_hash_mismatch(self):
        """Test file verification fails for wrong hash."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("content")
            temp_path = Path(f.name)

        try:
            assert verify_file_hash(temp_path, "sha256:wronghash") is False
        finally:
            temp_path.unlink()


class TestExtractDigest:
    """Tests for extract_digest function."""

    def test_extract_digest(self):
        """Test extracting digest from hash string."""
        h = hash_content("test")
        digest = extract_digest(h)
        assert not digest.startswith("sha256:")
        assert len(digest) == 64

    def test_extract_digest_invalid_format(self):
        """Test extracting from invalid format raises."""
        with pytest.raises(ValueError):
            extract_digest("md5:abc123")


class TestIsValidHash:
    """Tests for is_valid_hash function."""

    def test_valid_hash(self):
        """Test valid hash returns True."""
        h = hash_content("test")
        assert is_valid_hash(h) is True

    def test_invalid_prefix(self):
        """Test invalid prefix returns False."""
        assert is_valid_hash("md5:abc123") is False

    def test_invalid_length(self):
        """Test invalid length returns False."""
        assert is_valid_hash("sha256:abc123") is False

    def test_invalid_hex(self):
        """Test invalid hex characters returns False."""
        # 64 chars but contains 'g'
        invalid = "sha256:" + "g" * 64
        assert is_valid_hash(invalid) is False
