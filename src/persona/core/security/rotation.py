"""
API key rotation and management (F-052).

Provides automatic key rotation on authentication failures,
support for multiple keys per provider, and key health monitoring.
"""

import os
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from persona.core.security.keys import SecureString


class KeyStatus(Enum):
    """Status of an API key."""

    ACTIVE = "active"
    FAILED = "failed"
    EXPIRED = "expired"
    RATE_LIMITED = "rate_limited"
    UNKNOWN = "unknown"


@dataclass
class KeyHealth:
    """Health information for an API key."""

    key_id: str
    status: KeyStatus
    last_used: datetime | None = None
    last_success: datetime | None = None
    last_failure: datetime | None = None
    failure_count: int = 0
    success_count: int = 0
    failure_reason: str | None = None

    @property
    def is_healthy(self) -> bool:
        """Check if the key is healthy for use."""
        return self.status in (KeyStatus.ACTIVE, KeyStatus.UNKNOWN)

    @property
    def success_rate(self) -> float:
        """Calculate the success rate."""
        total = self.success_count + self.failure_count
        if total == 0:
            return 1.0
        return self.success_count / total

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialisation."""
        return {
            "key_id": self.key_id,
            "status": self.status.value,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "last_success": self.last_success.isoformat()
            if self.last_success
            else None,
            "last_failure": self.last_failure.isoformat()
            if self.last_failure
            else None,
            "failure_count": self.failure_count,
            "success_count": self.success_count,
            "failure_reason": self.failure_reason,
            "success_rate": self.success_rate,
        }


@dataclass
class KeyConfig:
    """Configuration for a provider's API keys."""

    provider: str
    keys: list[SecureString] = field(default_factory=list)
    env_vars: list[str] = field(default_factory=list)
    rotation_enabled: bool = True
    max_retries: int = 2
    failure_threshold: int = 3  # Failures before marking key as failed

    def __post_init__(self) -> None:
        """Load keys from environment variables."""
        for env_var in self.env_vars:
            value = os.environ.get(env_var)
            if value:
                self.keys.append(SecureString(value))


class KeyManager:
    """
    Manages API keys for providers with automatic rotation.

    Supports multiple keys per provider, automatic failover on
    authentication errors, and key health monitoring.

    Example:
        >>> manager = KeyManager()
        >>> manager.register_provider("anthropic", ["ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY_BACKUP"])
        >>> key = manager.get_key("anthropic")
        >>> # Use key...
        >>> manager.mark_success("anthropic", key)
        >>> # Or on failure:
        >>> manager.mark_failure("anthropic", key, "401 Unauthorized")
        >>> next_key = manager.get_key("anthropic")  # Returns backup key
    """

    # Default environment variables for built-in providers
    DEFAULT_ENV_VARS: dict[str, list[str]] = {
        "anthropic": ["ANTHROPIC_API_KEY", "ANTHROPIC_API_KEY_BACKUP"],
        "openai": ["OPENAI_API_KEY", "OPENAI_API_KEY_BACKUP"],
        "gemini": ["GOOGLE_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY_BACKUP"],
    }

    def __init__(self) -> None:
        """Initialise the key manager."""
        self._configs: dict[str, KeyConfig] = {}
        self._health: dict[
            str, dict[str, KeyHealth]
        ] = {}  # provider -> key_id -> health
        self._current_index: dict[str, int] = {}  # provider -> current key index
        self._on_rotation_callbacks: list[Callable[[str, str, str], None]] = []

        # Auto-register default providers
        for provider, env_vars in self.DEFAULT_ENV_VARS.items():
            self.register_provider(provider, env_vars)

    def register_provider(
        self,
        provider: str,
        env_vars: list[str] | None = None,
        keys: list[str] | None = None,
        rotation_enabled: bool = True,
        max_retries: int = 2,
    ) -> None:
        """
        Register a provider with its API keys.

        Args:
            provider: Provider name.
            env_vars: Environment variable names to load keys from.
            keys: Direct key values (use with caution).
            rotation_enabled: Whether to enable automatic rotation.
            max_retries: Maximum rotation retries.
        """
        config = KeyConfig(
            provider=provider,
            env_vars=env_vars or [],
            rotation_enabled=rotation_enabled,
            max_retries=max_retries,
        )

        # Add direct keys if provided
        if keys:
            for key in keys:
                config.keys.append(SecureString(key))

        self._configs[provider] = config
        self._health[provider] = {}
        self._current_index[provider] = 0

        # Initialise health for each key
        for i, key in enumerate(config.keys):
            key_id = f"{provider}_key_{i}"
            self._health[provider][key_id] = KeyHealth(
                key_id=key_id,
                status=KeyStatus.UNKNOWN,
            )

    def get_key(self, provider: str) -> SecureString | None:
        """
        Get the current active key for a provider.

        Returns the first healthy key, rotating if necessary.

        Args:
            provider: Provider name.

        Returns:
            SecureString containing the API key, or None if no keys available.
        """
        if provider not in self._configs:
            # Try default env var
            env_var = self.DEFAULT_ENV_VARS.get(
                provider, [f"{provider.upper()}_API_KEY"]
            )[0]
            value = os.environ.get(env_var)
            if value:
                return SecureString(value)
            return None

        config = self._configs[provider]
        if not config.keys:
            return None

        # Find first healthy key starting from current index
        start_index = self._current_index.get(provider, 0)
        for offset in range(len(config.keys)):
            index = (start_index + offset) % len(config.keys)
            key_id = f"{provider}_key_{index}"
            health = self._health[provider].get(key_id)

            if health is None or health.is_healthy:
                self._current_index[provider] = index
                return config.keys[index]

        # No healthy keys - return first key anyway (let caller handle error)
        return config.keys[0] if config.keys else None

    def get_key_value(self, provider: str) -> str | None:
        """
        Get the current API key value as a string.

        Args:
            provider: Provider name.

        Returns:
            The API key string, or None if not available.
        """
        key = self.get_key(provider)
        return key.get_value() if key else None

    def mark_success(self, provider: str, key: SecureString | str) -> None:
        """
        Mark a key as successfully used.

        Args:
            provider: Provider name.
            key: The key that was used.
        """
        key_id = self._find_key_id(provider, key)
        if key_id and provider in self._health:
            health = self._health[provider].get(key_id)
            if health:
                health.status = KeyStatus.ACTIVE
                health.last_used = datetime.now()
                health.last_success = datetime.now()
                health.success_count += 1

    def mark_failure(
        self,
        provider: str,
        key: SecureString | str,
        reason: str,
        is_auth_failure: bool = False,
    ) -> SecureString | None:
        """
        Mark a key as failed and optionally rotate to next key.

        Args:
            provider: Provider name.
            key: The key that failed.
            reason: Failure reason.
            is_auth_failure: Whether this is an authentication failure (401/403).

        Returns:
            Next available key if rotation occurred, None otherwise.
        """
        key_id = self._find_key_id(provider, key)
        if key_id and provider in self._health:
            health = self._health[provider].get(key_id)
            if health:
                health.last_used = datetime.now()
                health.last_failure = datetime.now()
                health.failure_count += 1
                health.failure_reason = reason

                # Mark as failed if auth failure or threshold exceeded
                config = self._configs.get(provider)
                if is_auth_failure or (
                    config and health.failure_count >= config.failure_threshold
                ):
                    health.status = KeyStatus.FAILED

                    # Attempt rotation
                    if config and config.rotation_enabled:
                        return self._rotate_key(provider, key_id, reason)

        return None

    def mark_rate_limited(
        self,
        provider: str,
        key: SecureString | str,
        retry_after: float | None = None,
    ) -> None:
        """
        Mark a key as rate limited.

        Args:
            provider: Provider name.
            key: The key that was rate limited.
            retry_after: Seconds until rate limit resets.
        """
        key_id = self._find_key_id(provider, key)
        if key_id and provider in self._health:
            health = self._health[provider].get(key_id)
            if health:
                health.status = KeyStatus.RATE_LIMITED
                health.last_used = datetime.now()
                health.failure_reason = f"Rate limited (retry after {retry_after}s)"

    def get_health(self, provider: str) -> list[KeyHealth]:
        """
        Get health information for all keys of a provider.

        Args:
            provider: Provider name.

        Returns:
            List of KeyHealth objects.
        """
        if provider not in self._health:
            return []
        return list(self._health[provider].values())

    def get_health_summary(self, provider: str) -> dict[str, Any]:
        """
        Get a summary of key health for a provider.

        Args:
            provider: Provider name.

        Returns:
            Dictionary with health summary.
        """
        health_list = self.get_health(provider)
        if not health_list:
            return {
                "provider": provider,
                "total_keys": 0,
                "healthy_keys": 0,
                "status": "not configured",
            }

        healthy = sum(1 for h in health_list if h.is_healthy)
        return {
            "provider": provider,
            "total_keys": len(health_list),
            "healthy_keys": healthy,
            "status": "healthy" if healthy > 0 else "degraded",
            "keys": [h.to_dict() for h in health_list],
        }

    def has_backup_keys(self, provider: str) -> bool:
        """
        Check if a provider has backup keys configured.

        Args:
            provider: Provider name.

        Returns:
            True if backup keys are available.
        """
        config = self._configs.get(provider)
        if not config:
            return False
        return len(config.keys) > 1

    def on_rotation(self, callback: Callable[[str, str, str], None]) -> None:
        """
        Register a callback for key rotation events.

        Args:
            callback: Function(provider, old_key_id, new_key_id).
        """
        self._on_rotation_callbacks.append(callback)

    def _find_key_id(self, provider: str, key: SecureString | str) -> str | None:
        """Find the key ID for a given key."""
        if provider not in self._configs:
            return None

        key_value = key.get_value() if isinstance(key, SecureString) else key
        config = self._configs[provider]

        for i, stored_key in enumerate(config.keys):
            if stored_key.get_value() == key_value:
                return f"{provider}_key_{i}"

        return None

    def _rotate_key(
        self, provider: str, failed_key_id: str, reason: str
    ) -> SecureString | None:
        """Rotate to the next available key."""
        config = self._configs.get(provider)
        if not config or len(config.keys) <= 1:
            return None

        # Find next healthy key
        current_index = self._current_index.get(provider, 0)
        for offset in range(1, len(config.keys)):
            next_index = (current_index + offset) % len(config.keys)
            next_key_id = f"{provider}_key_{next_index}"
            health = self._health[provider].get(next_key_id)

            if health is None or health.is_healthy:
                self._current_index[provider] = next_index

                # Notify callbacks
                for callback in self._on_rotation_callbacks:
                    try:
                        callback(provider, failed_key_id, next_key_id)
                    except Exception:
                        pass

                return config.keys[next_index]

        return None

    def reset_key_health(self, provider: str, key_index: int | None = None) -> None:
        """
        Reset health status for keys.

        Args:
            provider: Provider name.
            key_index: Specific key index, or None for all keys.
        """
        if provider not in self._health:
            return

        if key_index is not None:
            key_id = f"{provider}_key_{key_index}"
            if key_id in self._health[provider]:
                self._health[provider][key_id] = KeyHealth(
                    key_id=key_id,
                    status=KeyStatus.UNKNOWN,
                )
        else:
            config = self._configs.get(provider)
            if config:
                for i in range(len(config.keys)):
                    key_id = f"{provider}_key_{i}"
                    self._health[provider][key_id] = KeyHealth(
                        key_id=key_id,
                        status=KeyStatus.UNKNOWN,
                    )
            self._current_index[provider] = 0
