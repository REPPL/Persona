"""
Dynamic vendor discovery.

This module provides discovery of available LLM vendors through
configuration scanning and endpoint probing.
"""

import os
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import ClassVar

import httpx


class VendorStatus(Enum):
    """Status of a discovered vendor."""

    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    NOT_CONFIGURED = "not_configured"
    ERROR = "error"


@dataclass
class DiscoveryResult:
    """Result of vendor discovery."""

    vendor_id: str
    status: VendorStatus
    source: str  # 'builtin', 'custom', 'ollama'
    name: str = ""
    message: str = ""
    base_url: str | None = None
    response_time_ms: float | None = None
    models: list[str] = field(default_factory=list)


class VendorDiscovery:
    """
    Discover available LLM vendors.

    Scans configuration directories and probes endpoints to determine
    which vendors are available.
    """

    # Built-in vendor probe configurations
    BUILTIN_VENDORS: ClassVar[dict[str, dict]] = {
        "anthropic": {
            "name": "Anthropic",
            "env_var": "ANTHROPIC_API_KEY",
            "base_url": "https://api.anthropic.com",
            "probe_endpoint": "/v1/messages",
            "probe_method": "OPTIONS",
        },
        "openai": {
            "name": "OpenAI",
            "env_var": "OPENAI_API_KEY",
            "base_url": "https://api.openai.com",
            "probe_endpoint": "/v1/models",
            "probe_method": "HEAD",
        },
        "gemini": {
            "name": "Google Gemini",
            "env_var": "GOOGLE_API_KEY",
            "base_url": "https://generativelanguage.googleapis.com",
            "probe_endpoint": "/v1beta/models",
            "probe_method": "HEAD",
        },
    }

    # Ollama default configuration
    OLLAMA_DEFAULT_URL = "http://localhost:11434"

    # Cache TTL in seconds
    CACHE_TTL: ClassVar[int] = 300  # 5 minutes

    def __init__(
        self,
        user_dir: Path | None = None,
        project_dir: Path | None = None,
        cache_enabled: bool = True,
    ) -> None:
        """
        Initialise vendor discovery.

        Args:
            user_dir: Override user vendor directory.
            project_dir: Override project vendor directory.
            cache_enabled: Enable discovery caching.
        """
        from persona.core.config import VendorLoader

        self._user_dir = user_dir or VendorLoader.DEFAULT_USER_DIR
        self._project_dir = project_dir or VendorLoader.DEFAULT_PROJECT_DIR
        self._cache_enabled = cache_enabled
        self._cache: dict[str, tuple[DiscoveryResult, float]] = {}

    def discover_all(self, force_refresh: bool = False) -> list[DiscoveryResult]:
        """
        Discover all available vendors.

        Args:
            force_refresh: Force refresh of cached results.

        Returns:
            List of discovery results for all vendors.
        """
        results = []

        # Discover built-in vendors
        for vendor_id in self.BUILTIN_VENDORS:
            result = self.discover(vendor_id, force_refresh=force_refresh)
            results.append(result)

        # Discover custom vendors
        from persona.core.config import VendorLoader
        loader = VendorLoader(
            user_dir=self._user_dir,
            project_dir=self._project_dir,
        )

        for vendor_id in loader.list_vendors():
            if vendor_id not in self.BUILTIN_VENDORS:
                result = self.discover(vendor_id, force_refresh=force_refresh)
                results.append(result)

        # Discover Ollama
        ollama_result = self.discover_ollama(force_refresh=force_refresh)
        if ollama_result:
            results.append(ollama_result)

        return results

    def discover(self, vendor_id: str, force_refresh: bool = False) -> DiscoveryResult:
        """
        Discover a specific vendor.

        Args:
            vendor_id: Vendor identifier.
            force_refresh: Force refresh of cached result.

        Returns:
            Discovery result for the vendor.
        """
        # Check cache
        if not force_refresh and self._cache_enabled:
            cached = self._get_cached(vendor_id)
            if cached:
                return cached

        # Discover vendor
        if vendor_id in self.BUILTIN_VENDORS:
            result = self._discover_builtin(vendor_id)
        else:
            result = self._discover_custom(vendor_id)

        # Cache result
        if self._cache_enabled:
            self._cache[vendor_id] = (result, time.time())

        return result

    def discover_ollama(self, force_refresh: bool = False) -> DiscoveryResult | None:
        """
        Discover Ollama instance.

        Args:
            force_refresh: Force refresh of cached result.

        Returns:
            Discovery result if Ollama found, None otherwise.
        """
        # Check cache
        if not force_refresh and self._cache_enabled:
            cached = self._get_cached("ollama")
            if cached:
                return cached

        # Check OLLAMA_HOST environment variable
        ollama_url = os.getenv("OLLAMA_HOST", self.OLLAMA_DEFAULT_URL)

        try:
            start_time = time.time()
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{ollama_url}/api/tags")
                response_time = (time.time() - start_time) * 1000

                if response.status_code == 200:
                    data = response.json()
                    models = [m["name"] for m in data.get("models", [])]

                    result = DiscoveryResult(
                        vendor_id="ollama",
                        status=VendorStatus.AVAILABLE,
                        source="ollama",
                        name="Ollama (Local)",
                        message=f"Found {len(models)} models",
                        base_url=ollama_url,
                        response_time_ms=response_time,
                        models=models,
                    )
                else:
                    result = DiscoveryResult(
                        vendor_id="ollama",
                        status=VendorStatus.UNAVAILABLE,
                        source="ollama",
                        name="Ollama (Local)",
                        message=f"HTTP {response.status_code}",
                        base_url=ollama_url,
                    )
        except httpx.ConnectError:
            result = DiscoveryResult(
                vendor_id="ollama",
                status=VendorStatus.UNAVAILABLE,
                source="ollama",
                name="Ollama (Local)",
                message="Not running",
                base_url=ollama_url,
            )
        except Exception as e:
            result = DiscoveryResult(
                vendor_id="ollama",
                status=VendorStatus.ERROR,
                source="ollama",
                name="Ollama (Local)",
                message=str(e),
                base_url=ollama_url,
            )

        # Cache result
        if self._cache_enabled:
            self._cache["ollama"] = (result, time.time())

        return result

    def check_availability(self, vendor_id: str) -> bool:
        """
        Check if a vendor is available.

        Args:
            vendor_id: Vendor identifier.

        Returns:
            True if vendor is available.
        """
        result = self.discover(vendor_id)
        return result.status == VendorStatus.AVAILABLE

    def get_available_vendors(self) -> list[str]:
        """
        Get list of available vendor IDs.

        Returns:
            List of vendor IDs that are available.
        """
        results = self.discover_all()
        return [r.vendor_id for r in results if r.status == VendorStatus.AVAILABLE]

    def clear_cache(self) -> None:
        """Clear the discovery cache."""
        self._cache.clear()

    def _discover_builtin(self, vendor_id: str) -> DiscoveryResult:
        """Discover a built-in vendor."""
        config = self.BUILTIN_VENDORS[vendor_id]

        # Check API key
        api_key = os.getenv(config["env_var"])
        if not api_key:
            return DiscoveryResult(
                vendor_id=vendor_id,
                status=VendorStatus.NOT_CONFIGURED,
                source="builtin",
                name=config["name"],
                message=f"Missing {config['env_var']}",
                base_url=config["base_url"],
            )

        # Probe endpoint (simple connectivity check)
        try:
            start_time = time.time()
            with httpx.Client(timeout=5.0) as client:
                # Just check if we can connect
                response = client.request(
                    config["probe_method"],
                    f"{config['base_url']}{config['probe_endpoint']}",
                    headers={"Authorization": f"Bearer {api_key}"},
                )
                response_time = (time.time() - start_time) * 1000

                # Most APIs return 401/403 without proper auth, but that means they're reachable
                if response.status_code in (200, 401, 403, 404, 405):
                    return DiscoveryResult(
                        vendor_id=vendor_id,
                        status=VendorStatus.AVAILABLE,
                        source="builtin",
                        name=config["name"],
                        message="Configured and reachable",
                        base_url=config["base_url"],
                        response_time_ms=response_time,
                    )
                else:
                    return DiscoveryResult(
                        vendor_id=vendor_id,
                        status=VendorStatus.UNAVAILABLE,
                        source="builtin",
                        name=config["name"],
                        message=f"HTTP {response.status_code}",
                        base_url=config["base_url"],
                        response_time_ms=response_time,
                    )
        except httpx.ConnectError:
            return DiscoveryResult(
                vendor_id=vendor_id,
                status=VendorStatus.UNAVAILABLE,
                source="builtin",
                name=config["name"],
                message="Connection failed",
                base_url=config["base_url"],
            )
        except Exception as e:
            return DiscoveryResult(
                vendor_id=vendor_id,
                status=VendorStatus.ERROR,
                source="builtin",
                name=config["name"],
                message=str(e),
                base_url=config["base_url"],
            )

    def _discover_custom(self, vendor_id: str) -> DiscoveryResult:
        """Discover a custom vendor."""
        from persona.core.config import VendorLoader

        loader = VendorLoader(
            user_dir=self._user_dir,
            project_dir=self._project_dir,
        )

        try:
            config = loader.load(vendor_id)
        except FileNotFoundError:
            return DiscoveryResult(
                vendor_id=vendor_id,
                status=VendorStatus.ERROR,
                source="custom",
                name=vendor_id,
                message="Configuration not found",
            )

        # Check API key
        api_key = os.getenv(config.api_key_env) if config.api_key_env else None
        if config.api_key_env and not api_key:
            return DiscoveryResult(
                vendor_id=vendor_id,
                status=VendorStatus.NOT_CONFIGURED,
                source="custom",
                name=config.name,
                message=f"Missing {config.api_key_env}",
                base_url=config.base_url,
            )

        # Probe endpoint
        try:
            start_time = time.time()
            with httpx.Client(timeout=5.0) as client:
                headers = config.build_headers(api_key or "")
                response = client.get(
                    f"{config.base_url}/models",
                    headers=headers,
                )
                response_time = (time.time() - start_time) * 1000

                if response.status_code in (200, 401, 403, 404, 405):
                    return DiscoveryResult(
                        vendor_id=vendor_id,
                        status=VendorStatus.AVAILABLE,
                        source="custom",
                        name=config.name,
                        message="Reachable",
                        base_url=config.base_url,
                        response_time_ms=response_time,
                    )
                else:
                    return DiscoveryResult(
                        vendor_id=vendor_id,
                        status=VendorStatus.UNAVAILABLE,
                        source="custom",
                        name=config.name,
                        message=f"HTTP {response.status_code}",
                        base_url=config.base_url,
                        response_time_ms=response_time,
                    )
        except httpx.ConnectError:
            return DiscoveryResult(
                vendor_id=vendor_id,
                status=VendorStatus.UNAVAILABLE,
                source="custom",
                name=config.name,
                message="Connection failed",
                base_url=config.base_url,
            )
        except Exception as e:
            return DiscoveryResult(
                vendor_id=vendor_id,
                status=VendorStatus.ERROR,
                source="custom",
                name=config.name,
                message=str(e),
                base_url=config.base_url,
            )

    def _get_cached(self, vendor_id: str) -> DiscoveryResult | None:
        """Get cached result if still valid."""
        if vendor_id not in self._cache:
            return None

        result, timestamp = self._cache[vendor_id]
        if time.time() - timestamp > self.CACHE_TTL:
            return None

        return result
