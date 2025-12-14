"""Tests for API key rotation (F-052)."""

import os
import pytest
from unittest.mock import patch

from persona.core.security.rotation import (
    KeyManager,
    KeyStatus,
    KeyHealth,
    KeyConfig,
)
from persona.core.security.keys import SecureString


class TestKeyHealth:
    """Tests for KeyHealth dataclass."""

    def test_is_healthy_active(self):
        """Active status is healthy."""
        health = KeyHealth(key_id="test", status=KeyStatus.ACTIVE)
        assert health.is_healthy

    def test_is_healthy_unknown(self):
        """Unknown status is healthy (assumed OK)."""
        health = KeyHealth(key_id="test", status=KeyStatus.UNKNOWN)
        assert health.is_healthy

    def test_is_not_healthy_failed(self):
        """Failed status is not healthy."""
        health = KeyHealth(key_id="test", status=KeyStatus.FAILED)
        assert not health.is_healthy

    def test_is_not_healthy_rate_limited(self):
        """Rate limited status is not healthy."""
        health = KeyHealth(key_id="test", status=KeyStatus.RATE_LIMITED)
        assert not health.is_healthy

    def test_success_rate_calculation(self):
        """Calculates success rate correctly."""
        health = KeyHealth(
            key_id="test",
            status=KeyStatus.ACTIVE,
            success_count=8,
            failure_count=2,
        )
        assert health.success_rate == 0.8

    def test_success_rate_no_requests(self):
        """Success rate is 1.0 with no requests."""
        health = KeyHealth(key_id="test", status=KeyStatus.UNKNOWN)
        assert health.success_rate == 1.0

    def test_to_dict(self):
        """Converts to dictionary."""
        health = KeyHealth(key_id="test", status=KeyStatus.ACTIVE)
        data = health.to_dict()
        assert data["key_id"] == "test"
        assert data["status"] == "active"


class TestKeyConfig:
    """Tests for KeyConfig dataclass."""

    def test_loads_from_env_vars(self):
        """Loads keys from environment variables."""
        with patch.dict(os.environ, {"TEST_KEY": "secret123"}):
            config = KeyConfig(
                provider="test",
                env_vars=["TEST_KEY"],
            )
            assert len(config.keys) == 1
            assert config.keys[0].get_value() == "secret123"

    def test_ignores_missing_env_vars(self):
        """Ignores missing environment variables."""
        config = KeyConfig(
            provider="test",
            env_vars=["NONEXISTENT_KEY"],
        )
        assert len(config.keys) == 0


class TestKeyManager:
    """Tests for KeyManager class."""

    def test_get_key_from_env(self):
        """Gets key from environment variable."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            manager = KeyManager()
            key = manager.get_key("anthropic")
            assert key is not None
            assert key.get_value() == "test-key"

    def test_get_key_value(self):
        """Gets key value as string."""
        with patch.dict(os.environ, {"OPENAI_API_KEY": "openai-key"}):
            manager = KeyManager()
            value = manager.get_key_value("openai")
            assert value == "openai-key"

    def test_get_key_none_when_not_configured(self):
        """Returns None when no key configured."""
        with patch.dict(os.environ, {}, clear=True):
            manager = KeyManager()
            manager._configs.clear()  # Clear default registrations
            key = manager.get_key("nonexistent")
            assert key is None

    def test_register_provider(self):
        """Registers custom provider."""
        manager = KeyManager()
        manager.register_provider(
            "custom",
            keys=["key1", "key2"],
        )
        key = manager.get_key("custom")
        assert key is not None
        assert key.get_value() == "key1"

    def test_mark_success(self):
        """Marks key as successful."""
        manager = KeyManager()
        manager.register_provider("test", keys=["testkey"])
        key = manager.get_key("test")
        manager.mark_success("test", key)

        health = manager.get_health("test")
        assert len(health) == 1
        assert health[0].status == KeyStatus.ACTIVE
        assert health[0].success_count == 1

    def test_mark_failure_rotates_key(self):
        """Rotates to backup on failure."""
        manager = KeyManager()
        manager.register_provider(
            "test",
            keys=["primary", "backup"],
            rotation_enabled=True,
        )

        primary_key = manager.get_key("test")
        assert primary_key.get_value() == "primary"

        # Mark as auth failure - should rotate
        next_key = manager.mark_failure(
            "test",
            primary_key,
            "401 Unauthorized",
            is_auth_failure=True,
        )

        assert next_key is not None
        assert next_key.get_value() == "backup"

    def test_mark_failure_threshold(self):
        """Rotates after failure threshold."""
        manager = KeyManager()
        manager.register_provider(
            "test",
            keys=["key1", "key2"],
            rotation_enabled=True,
        )
        manager._configs["test"].failure_threshold = 2

        key = manager.get_key("test")

        # First failure - no rotation
        manager.mark_failure("test", key, "error1")
        current = manager.get_key("test")
        assert current.get_value() == "key1"

        # Second failure - should rotate
        manager.mark_failure("test", key, "error2")
        current = manager.get_key("test")
        assert current.get_value() == "key2"

    def test_mark_rate_limited(self):
        """Marks key as rate limited."""
        manager = KeyManager()
        manager.register_provider("test", keys=["testkey"])
        key = manager.get_key("test")

        manager.mark_rate_limited("test", key, retry_after=30)

        health = manager.get_health("test")
        assert health[0].status == KeyStatus.RATE_LIMITED

    def test_has_backup_keys(self):
        """Checks for backup keys."""
        manager = KeyManager()
        manager.register_provider("single", keys=["only"])
        manager.register_provider("multiple", keys=["one", "two"])

        assert not manager.has_backup_keys("single")
        assert manager.has_backup_keys("multiple")

    def test_get_health_summary(self):
        """Gets health summary."""
        manager = KeyManager()
        manager.register_provider("test", keys=["key1", "key2"])

        summary = manager.get_health_summary("test")
        assert summary["provider"] == "test"
        assert summary["total_keys"] == 2
        assert summary["healthy_keys"] == 2

    def test_reset_key_health(self):
        """Resets key health."""
        manager = KeyManager()
        manager.register_provider("test", keys=["testkey"])
        key = manager.get_key("test")
        manager.mark_success("test", key)

        health = manager.get_health("test")
        assert health[0].success_count == 1

        manager.reset_key_health("test")
        health = manager.get_health("test")
        assert health[0].success_count == 0

    def test_on_rotation_callback(self):
        """Calls rotation callback."""
        manager = KeyManager()
        manager.register_provider("test", keys=["key1", "key2"])

        rotations = []
        manager.on_rotation(lambda p, old, new: rotations.append((p, old, new)))

        key = manager.get_key("test")
        manager.mark_failure("test", key, "error", is_auth_failure=True)

        assert len(rotations) == 1
        assert rotations[0][0] == "test"
