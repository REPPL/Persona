"""
Dynamic model discovery.

This module provides discovery of available models through
API queries and configuration merging.
"""

import os
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar

import httpx


class ModelStatus(Enum):
    """Status of a discovered model."""

    AVAILABLE = "available"
    DEPRECATED = "deprecated"
    UNAVAILABLE = "unavailable"
    UNKNOWN = "unknown"


@dataclass
class ModelDiscoveryResult:
    """Result of model discovery."""

    model_id: str
    status: ModelStatus
    provider: str
    source: str  # 'api', 'builtin', 'custom'
    name: str = ""
    context_window: int | None = None
    deprecation_message: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ModelDiscovery:
    """
    Discover available models from vendors.

    Queries vendor APIs and merges with custom model configurations.
    """

    # Known deprecated models
    DEPRECATED_MODELS: ClassVar[dict[str, str]] = {
        "gpt-4-0314": "Deprecated. Use gpt-4 instead.",
        "gpt-4-32k-0314": "Deprecated. Use gpt-4-32k instead.",
        "gpt-3.5-turbo-0301": "Deprecated. Use gpt-3.5-turbo instead.",
        "claude-2": "Deprecated. Use claude-3 models instead.",
        "claude-instant-1": "Deprecated. Use claude-3-haiku instead.",
    }

    # Cache TTL in seconds
    CACHE_TTL: ClassVar[int] = 600  # 10 minutes

    def __init__(
        self,
        user_dir: Path | None = None,
        project_dir: Path | None = None,
        cache_enabled: bool = True,
    ) -> None:
        """
        Initialise model discovery.

        Args:
            user_dir: Override user model directory.
            project_dir: Override project model directory.
            cache_enabled: Enable discovery caching.
        """
        from persona.core.config import ModelLoader

        self._user_dir = user_dir or ModelLoader.DEFAULT_USER_DIR
        self._project_dir = project_dir or ModelLoader.DEFAULT_PROJECT_DIR
        self._cache_enabled = cache_enabled
        self._cache: dict[str, tuple[list[ModelDiscoveryResult], float]] = {}

    def discover_all(
        self,
        provider: str | None = None,
        force_refresh: bool = False,
    ) -> list[ModelDiscoveryResult]:
        """
        Discover all available models.

        Args:
            provider: Filter by provider.
            force_refresh: Force refresh of cached results.

        Returns:
            List of discovery results for all models.
        """
        results = []

        # Get built-in models
        builtin_results = self._discover_builtin_models(provider)
        results.extend(builtin_results)

        # Get custom models
        custom_results = self._discover_custom_models(provider)
        results.extend(custom_results)

        # Query APIs if configured
        if not provider or provider == "openai":
            api_results = self._query_openai_models(force_refresh)
            results.extend(api_results)

        if not provider or provider == "ollama":
            from persona.core.discovery.vendor import VendorDiscovery

            vendor_discovery = VendorDiscovery()
            ollama_result = vendor_discovery.discover_ollama()
            if ollama_result and ollama_result.models:
                for model_name in ollama_result.models:
                    results.append(
                        ModelDiscoveryResult(
                            model_id=model_name,
                            status=ModelStatus.AVAILABLE,
                            provider="ollama",
                            source="api",
                            name=model_name,
                        )
                    )

        return results

    def discover(
        self,
        model_id: str,
        provider: str | None = None,
    ) -> ModelDiscoveryResult | None:
        """
        Discover a specific model.

        Args:
            model_id: Model identifier.
            provider: Provider hint.

        Returns:
            Discovery result if found, None otherwise.
        """
        # Check deprecation
        if model_id in self.DEPRECATED_MODELS:
            return ModelDiscoveryResult(
                model_id=model_id,
                status=ModelStatus.DEPRECATED,
                provider=provider or "unknown",
                source="builtin",
                deprecation_message=self.DEPRECATED_MODELS[model_id],
            )

        # Check custom models first
        from persona.core.config import ModelLoader

        loader = ModelLoader(
            user_dir=self._user_dir,
            project_dir=self._project_dir,
        )

        if loader.exists(model_id):
            config = loader.load(model_id)
            return ModelDiscoveryResult(
                model_id=model_id,
                status=ModelStatus.AVAILABLE,
                provider=config.provider,
                source="custom",
                name=config.name,
                context_window=config.context_window,
            )

        # Check built-in pricing data
        from persona.core.cost import PricingData

        pricing = PricingData.get_pricing(model_id, provider)
        if pricing:
            return ModelDiscoveryResult(
                model_id=model_id,
                status=ModelStatus.AVAILABLE,
                provider=pricing.provider,
                source="builtin",
                name=pricing.description,
                context_window=pricing.context_window,
            )

        return None

    def check_model(
        self, model_id: str, provider: str | None = None
    ) -> tuple[bool, str]:
        """
        Check if a model is available and usable.

        Args:
            model_id: Model identifier.
            provider: Provider hint.

        Returns:
            Tuple of (is_available, message).
        """
        result = self.discover(model_id, provider)

        if not result:
            return False, f"Model '{model_id}' not found"

        if result.status == ModelStatus.DEPRECATED:
            return True, f"Warning: {result.deprecation_message}"

        if result.status == ModelStatus.AVAILABLE:
            return True, f"Model '{model_id}' is available ({result.provider})"

        return False, f"Model '{model_id}' is {result.status.value}"

    def get_available_models(
        self,
        provider: str | None = None,
    ) -> list[str]:
        """
        Get list of available model IDs.

        Args:
            provider: Filter by provider.

        Returns:
            List of available model IDs.
        """
        results = self.discover_all(provider=provider)
        return list(
            set(
                r.model_id
                for r in results
                if r.status in (ModelStatus.AVAILABLE, ModelStatus.DEPRECATED)
            )
        )

    def get_deprecated_models(self) -> list[ModelDiscoveryResult]:
        """
        Get list of deprecated models.

        Returns:
            List of deprecated model results.
        """
        return [
            ModelDiscoveryResult(
                model_id=model_id,
                status=ModelStatus.DEPRECATED,
                provider="unknown",
                source="builtin",
                deprecation_message=message,
            )
            for model_id, message in self.DEPRECATED_MODELS.items()
        ]

    def clear_cache(self) -> None:
        """Clear the discovery cache."""
        self._cache.clear()

    def _discover_builtin_models(
        self,
        provider: str | None = None,
    ) -> list[ModelDiscoveryResult]:
        """Discover models from built-in pricing data."""
        from persona.core.cost import PricingData

        results = []
        for pricing in PricingData.list_models(provider=provider):
            status = ModelStatus.AVAILABLE
            deprecation_msg = None

            if pricing.model in self.DEPRECATED_MODELS:
                status = ModelStatus.DEPRECATED
                deprecation_msg = self.DEPRECATED_MODELS[pricing.model]

            results.append(
                ModelDiscoveryResult(
                    model_id=pricing.model,
                    status=status,
                    provider=pricing.provider,
                    source="builtin",
                    name=pricing.description,
                    context_window=pricing.context_window,
                    deprecation_message=deprecation_msg,
                )
            )

        return results

    def _discover_custom_models(
        self,
        provider: str | None = None,
    ) -> list[ModelDiscoveryResult]:
        """Discover custom model configurations."""
        from persona.core.config import ModelLoader

        loader = ModelLoader(
            user_dir=self._user_dir,
            project_dir=self._project_dir,
        )

        results = []
        for model_id in loader.list_models(provider=provider):
            try:
                config = loader.load(model_id)
                results.append(
                    ModelDiscoveryResult(
                        model_id=model_id,
                        status=ModelStatus.AVAILABLE,
                        provider=config.provider,
                        source="custom",
                        name=config.name,
                        context_window=config.context_window,
                    )
                )
            except Exception:
                continue

        return results

    def _query_openai_models(
        self, force_refresh: bool = False
    ) -> list[ModelDiscoveryResult]:
        """Query OpenAI API for available models."""
        cache_key = "openai_api"

        # Check cache
        if not force_refresh and self._cache_enabled and cache_key in self._cache:
            results, timestamp = self._cache[cache_key]
            if time.time() - timestamp < self.CACHE_TTL:
                return results

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return []

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                )

                if response.status_code != 200:
                    return []

                data = response.json()
                results = []

                for model in data.get("data", []):
                    model_id = model.get("id", "")
                    # Filter to only include chat models
                    if not any(prefix in model_id for prefix in ["gpt-", "o1-"]):
                        continue

                    status = ModelStatus.AVAILABLE
                    deprecation_msg = None
                    if model_id in self.DEPRECATED_MODELS:
                        status = ModelStatus.DEPRECATED
                        deprecation_msg = self.DEPRECATED_MODELS[model_id]

                    results.append(
                        ModelDiscoveryResult(
                            model_id=model_id,
                            status=status,
                            provider="openai",
                            source="api",
                            name=model_id,
                            deprecation_message=deprecation_msg,
                            metadata={"owned_by": model.get("owned_by", "")},
                        )
                    )

                # Cache results
                if self._cache_enabled:
                    self._cache[cache_key] = (results, time.time())

                return results

        except Exception:
            return []
