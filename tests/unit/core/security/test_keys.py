"""Tests for API key protection (F-051)."""

import logging
import pytest

from persona.core.security.keys import (
    SecureString,
    mask_api_key,
    redact_api_keys,
    KeyMaskingFilter,
    format_key_for_display,
)


class TestMaskApiKey:
    """Tests for mask_api_key function."""

    def test_masks_anthropic_key(self):
        """Masks Anthropic API key correctly."""
        key = "sk-ant-api03-abc123xyz789def456ghi"
        masked = mask_api_key(key)
        assert masked.startswith("sk-ant-")
        assert "***" in masked
        assert not "abc123" in masked

    def test_masks_openai_key(self):
        """Masks OpenAI API key correctly."""
        key = "sk-proj-abc123xyz789def456"
        masked = mask_api_key(key)
        assert masked.startswith("sk-proj")
        assert "***" in masked

    def test_masks_short_key(self):
        """Masks short keys entirely."""
        key = "short"
        masked = mask_api_key(key)
        assert masked == "*****"

    def test_handles_none(self):
        """Handles None key."""
        assert mask_api_key(None) == "<not set>"

    def test_handles_empty_string(self):
        """Handles empty string."""
        assert mask_api_key("") == "<not set>"

    def test_custom_prefix_suffix(self):
        """Respects custom prefix/suffix lengths."""
        key = "abcdefghijklmnopqrstuvwxyz"
        masked = mask_api_key(key, show_prefix=3, show_suffix=3)
        assert masked.startswith("abc")
        assert masked.endswith("xyz")

    def test_no_suffix(self):
        """Handles zero suffix length."""
        key = "abcdefghijklmnop"
        masked = mask_api_key(key, show_prefix=4, show_suffix=0)
        assert masked.startswith("abcd")
        assert masked.endswith("...")


class TestRedactApiKeys:
    """Tests for redact_api_keys function."""

    def test_redacts_anthropic_key(self):
        """Redacts Anthropic key from text."""
        text = "Using key sk-ant-api03-abc123xyz789def456ghi for API calls"
        redacted = redact_api_keys(text)
        assert "abc123" not in redacted
        assert "sk-ant-" in redacted

    def test_redacts_openai_key(self):
        """Redacts OpenAI key from text."""
        text = "OpenAI key: sk-abc123xyz789def456ghijklmnop"
        redacted = redact_api_keys(text)
        assert "abc123xyz789" not in redacted

    def test_redacts_multiple_keys(self):
        """Redacts multiple keys in text."""
        text = "Keys: sk-ant-api03-key1234567890 and sk-otherkey123456789012"
        redacted = redact_api_keys(text)
        assert "key1234567890" not in redacted

    def test_preserves_non_key_text(self):
        """Preserves non-key text."""
        text = "Normal text without any keys"
        assert redact_api_keys(text) == text

    def test_handles_empty(self):
        """Handles empty string."""
        assert redact_api_keys("") == ""

    def test_handles_none(self):
        """Handles None."""
        assert redact_api_keys(None) is None


class TestSecureString:
    """Tests for SecureString class."""

    def test_stores_value(self):
        """Stores and retrieves value."""
        secret = SecureString("my-secret-key")
        assert secret.get_value() == "my-secret-key"

    def test_str_redacts(self):
        """String representation is redacted."""
        secret = SecureString("my-secret-key")
        assert "my-secret-key" not in str(secret)
        assert "REDACTED" in str(secret)

    def test_repr_redacts(self):
        """Repr is redacted."""
        secret = SecureString("my-secret-key")
        assert "my-secret-key" not in repr(secret)
        assert "REDACTED" in repr(secret)

    def test_get_masked(self):
        """Returns masked version."""
        secret = SecureString("sk-ant-api03-abc123xyz789def456")
        masked = secret.get_masked()
        assert "***" in masked
        assert "abc123xyz" not in masked

    def test_equality(self):
        """Equality comparison works."""
        s1 = SecureString("same-key")
        s2 = SecureString("same-key")
        s3 = SecureString("different-key")
        assert s1 == s2
        assert s1 != s3

    def test_hash(self):
        """Can be used in sets/dicts."""
        s1 = SecureString("key1")
        s2 = SecureString("key1")
        assert hash(s1) == hash(s2)
        assert {s1, s2} == {s1}

    def test_bool(self):
        """Bool conversion works."""
        assert bool(SecureString("value"))
        assert not bool(SecureString(""))

    def test_len(self):
        """Length returns value length."""
        assert len(SecureString("12345")) == 5

    def test_rejects_non_string(self):
        """Rejects non-string values."""
        with pytest.raises(TypeError):
            SecureString(12345)


class TestKeyMaskingFilter:
    """Tests for KeyMaskingFilter logging filter."""

    def test_masks_keys_in_log_message(self):
        """Masks keys in log messages."""
        filter = KeyMaskingFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Using key sk-ant-api03-abc123xyz789def456",
            args=(),
            exc_info=None,
        )
        filter.filter(record)
        assert "abc123xyz789" not in record.msg

    def test_masks_keys_in_args(self):
        """Masks keys in log arguments."""
        filter = KeyMaskingFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Key is %s",
            args=("sk-ant-api03-abc123xyz789def456",),
            exc_info=None,
        )
        filter.filter(record)
        assert "abc123xyz789" not in str(record.args)

    def test_masks_keys_in_dict_args(self):
        """Masks keys in dictionary arguments."""
        filter = KeyMaskingFilter()
        # Create record with empty args first, then set dict args manually
        # (LogRecord's constructor validates args in a way that breaks with dicts)
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Key is %(key)s",
            args=None,
            exc_info=None,
        )
        # Manually set dict args after construction
        record.args = {"key": "sk-ant-api03-abc123xyz789def456"}
        filter.filter(record)
        assert "abc123xyz789" not in str(record.args)

    def test_always_returns_true(self):
        """Always allows log record through."""
        filter = KeyMaskingFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg="Normal message",
            args=(),
            exc_info=None,
        )
        assert filter.filter(record) is True


class TestFormatKeyForDisplay:
    """Tests for format_key_for_display function."""

    def test_formats_string_key(self):
        """Formats string key."""
        result = format_key_for_display("sk-abc123xyz789")
        assert "API Key:" in result
        assert "***" in result

    def test_formats_secure_string(self):
        """Formats SecureString."""
        secret = SecureString("sk-abc123xyz789")
        result = format_key_for_display(secret)
        assert "API Key:" in result
        assert "***" in result

    def test_handles_none(self):
        """Handles None."""
        result = format_key_for_display(None)
        assert "<not configured>" in result

    def test_custom_label(self):
        """Uses custom label."""
        result = format_key_for_display("key123", label="Custom Key")
        assert "Custom Key:" in result
