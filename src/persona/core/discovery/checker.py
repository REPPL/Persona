"""
Model availability checking (F-056).

Provides model availability verification before generation,
deprecation warnings, and alternative suggestions.
"""

import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ModelStatus(Enum):
    """Status of a model's availability."""

    AVAILABLE = "available"
    DEPRECATED = "deprecated"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


@dataclass
class ModelAvailability:
    """Result of model availability check."""

    model: str
    provider: str
    status: ModelStatus
    checked_at: datetime = field(default_factory=datetime.now)
    message: str | None = None
    deprecation_date: str | None = None
    replacement: str | None = None
    alternatives: list[str] = field(default_factory=list)

    @property
    def is_available(self) -> bool:
        """Check if model is available for use."""
        return self.status in (ModelStatus.AVAILABLE, ModelStatus.DEPRECATED)

    @property
    def is_deprecated(self) -> bool:
        """Check if model is deprecated."""
        return self.status == ModelStatus.DEPRECATED

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model": self.model,
            "provider": self.provider,
            "status": self.status.value,
            "checked_at": self.checked_at.isoformat(),
            "message": self.message,
            "deprecation_date": self.deprecation_date,
            "replacement": self.replacement,
            "alternatives": self.alternatives,
        }


# Known deprecated models with replacements
DEPRECATED_MODELS: dict[str, dict[str, str]] = {
    # Anthropic
    "claude-2.0": {
        "replacement": "claude-3-5-sonnet-20241022",
        "date": "2024-12-01",
    },
    "claude-2.1": {
        "replacement": "claude-3-5-sonnet-20241022",
        "date": "2024-12-01",
    },
    "claude-instant-1.2": {
        "replacement": "claude-3-5-haiku-20241022",
        "date": "2024-12-01",
    },
    # OpenAI
    "gpt-3.5-turbo-0301": {
        "replacement": "gpt-4o-mini",
        "date": "2024-06-13",
    },
    "gpt-4-0314": {
        "replacement": "gpt-4o",
        "date": "2024-06-13",
    },
    "gpt-4-32k": {
        "replacement": "gpt-4o",
        "date": "2024-06-13",
    },
    # Google/Gemini
    "gemini-pro": {
        "replacement": "gemini-1.5-pro",
        "date": "2024-09-01",
    },
}

# Model alternatives by capability
MODEL_ALTERNATIVES: dict[str, list[str]] = {
    "anthropic": [
        "claude-sonnet-4-20250514",
        "claude-3-5-sonnet-20241022",
        "claude-3-5-haiku-20241022",
    ],
    "openai": [
        "gpt-4o",
        "gpt-4o-mini",
        "gpt-4-turbo",
    ],
    "gemini": [
        "gemini-1.5-pro",
        "gemini-1.5-flash",
        "gemini-2.0-flash-exp",
    ],
}


class ModelChecker:
    """
    Checks model availability before generation.

    Queries provider APIs to verify model accessibility,
    warns about deprecated models, and suggests alternatives.

    Example:
        checker = ModelChecker()
        availability = checker.check("claude-sonnet-4-20250514", "anthropic")
        if not availability.is_available:
            print(f"Model unavailable: {availability.message}")
        if availability.is_deprecated:
            print(f"Warning: Use {availability.replacement} instead")
    """

    # Cache TTL in seconds
    CACHE_TTL = 300  # 5 minutes

    def __init__(self) -> None:
        """Initialise the model checker."""
        self._cache: dict[str, tuple[ModelAvailability, float]] = {}
        self._model_discovery = None  # Lazy load

    def check(
        self,
        model: str,
        provider: str,
        force_refresh: bool = False,
    ) -> ModelAvailability:
        """
        Check if a model is available.

        Args:
            model: Model name/ID.
            provider: Provider name.
            force_refresh: Bypass cache.

        Returns:
            ModelAvailability with status and details.
        """
        cache_key = f"{provider}:{model}"

        # Check cache
        if not force_refresh and cache_key in self._cache:
            availability, cached_at = self._cache[cache_key]
            if time.monotonic() - cached_at < self.CACHE_TTL:
                return availability

        # Check for known deprecations first
        if model in DEPRECATED_MODELS:
            deprecated_info = DEPRECATED_MODELS[model]
            availability = ModelAvailability(
                model=model,
                provider=provider,
                status=ModelStatus.DEPRECATED,
                message=f"Model is deprecated as of {deprecated_info['date']}",
                deprecation_date=deprecated_info["date"],
                replacement=deprecated_info["replacement"],
                alternatives=self._get_alternatives(provider),
            )
            self._cache[cache_key] = (availability, time.monotonic())
            return availability

        # Try to verify with model discovery
        availability = self._check_with_discovery(model, provider)

        # Cache result
        self._cache[cache_key] = (availability, time.monotonic())
        return availability

    def check_multiple(
        self,
        models: list[tuple[str, str]],
        force_refresh: bool = False,
    ) -> dict[str, ModelAvailability]:
        """
        Check multiple models at once.

        Args:
            models: List of (model, provider) tuples.
            force_refresh: Bypass cache.

        Returns:
            Dictionary mapping "provider:model" to availability.
        """
        results = {}
        for model, provider in models:
            key = f"{provider}:{model}"
            results[key] = self.check(model, provider, force_refresh)
        return results

    def get_alternatives(
        self,
        model: str,
        provider: str,
        count: int = 3,
    ) -> list[str]:
        """
        Get alternative models for an unavailable/deprecated model.

        Args:
            model: Original model name.
            provider: Provider name.
            count: Maximum alternatives to return.

        Returns:
            List of alternative model names.
        """
        # Check for specific replacement
        if model in DEPRECATED_MODELS:
            replacement = DEPRECATED_MODELS[model].get("replacement")
            if replacement:
                return [replacement]

        # Return provider alternatives
        return self._get_alternatives(provider)[:count]

    def is_deprecated(self, model: str) -> bool:
        """
        Quick check if a model is deprecated.

        Args:
            model: Model name.

        Returns:
            True if model is known to be deprecated.
        """
        return model in DEPRECATED_MODELS

    def get_deprecation_info(self, model: str) -> dict[str, str] | None:
        """
        Get deprecation information for a model.

        Args:
            model: Model name.

        Returns:
            Deprecation info dict or None.
        """
        return DEPRECATED_MODELS.get(model)

    def suggest_model(self, provider: str, capability: str = "general") -> str | None:
        """
        Suggest a model for a provider.

        Args:
            provider: Provider name.
            capability: Required capability (not yet used).

        Returns:
            Suggested model name or None.
        """
        alternatives = MODEL_ALTERNATIVES.get(provider.lower(), [])
        return alternatives[0] if alternatives else None

    def clear_cache(self) -> None:
        """Clear the availability cache."""
        self._cache.clear()

    def get_cached_status(self, model: str, provider: str) -> ModelAvailability | None:
        """
        Get cached status without refreshing.

        Args:
            model: Model name.
            provider: Provider name.

        Returns:
            Cached availability or None.
        """
        cache_key = f"{provider}:{model}"
        if cache_key in self._cache:
            availability, _ = self._cache[cache_key]
            return availability
        return None

    def _check_with_discovery(self, model: str, provider: str) -> ModelAvailability:
        """Check model using discovery system."""
        try:
            # Lazy load model discovery
            if self._model_discovery is None:
                from persona.core.discovery.model import ModelDiscovery

                self._model_discovery = ModelDiscovery()

            # Try to discover available models
            discovered = self._model_discovery.discover(provider)

            if discovered.status == "available":
                # Check if model is in discovered list
                model_found = any(
                    m.get("id") == model or m.get("name") == model
                    for m in discovered.models
                )

                if model_found:
                    return ModelAvailability(
                        model=model,
                        provider=provider,
                        status=ModelStatus.AVAILABLE,
                        message="Model verified as available",
                    )
                else:
                    return ModelAvailability(
                        model=model,
                        provider=provider,
                        status=ModelStatus.UNAVAILABLE,
                        message=f"Model not found in {provider}'s available models",
                        alternatives=self._get_alternatives(provider),
                    )
            else:
                # Provider not available - assume model is OK
                return ModelAvailability(
                    model=model,
                    provider=provider,
                    status=ModelStatus.UNKNOWN,
                    message="Could not verify model availability (provider unreachable)",
                )

        except Exception as e:
            # Assume model is OK on error
            return ModelAvailability(
                model=model,
                provider=provider,
                status=ModelStatus.UNKNOWN,
                message=f"Could not verify: {e}",
            )

    def _get_alternatives(self, provider: str) -> list[str]:
        """Get alternatives for a provider."""
        return MODEL_ALTERNATIVES.get(provider.lower(), [])


def check_model(model: str, provider: str) -> ModelAvailability:
    """
    Convenience function to check model availability.

    Args:
        model: Model name.
        provider: Provider name.

    Returns:
        ModelAvailability result.
    """
    checker = ModelChecker()
    return checker.check(model, provider)


def warn_if_deprecated(model: str, provider: str) -> str | None:
    """
    Check if model is deprecated and return warning message.

    Args:
        model: Model name.
        provider: Provider name.

    Returns:
        Warning message or None.
    """
    checker = ModelChecker()
    availability = checker.check(model, provider)

    if availability.is_deprecated:
        msg = f"Warning: Model '{model}' is deprecated"
        if availability.deprecation_date:
            msg += f" as of {availability.deprecation_date}"
        if availability.replacement:
            msg += f". Consider using '{availability.replacement}' instead"
        return msg

    return None
