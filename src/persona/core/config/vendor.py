"""
Custom vendor configuration management.

This module provides YAML-based configuration for custom LLM vendors,
supporting enterprise deployments (Azure OpenAI, AWS Bedrock, etc.)
and private LLM endpoints.
"""

import os
import re
from enum import Enum
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator, ConfigDict


class AuthType(str, Enum):
    """Authentication type for vendor API."""

    BEARER = "bearer"  # Authorization: Bearer <token>
    HEADER = "header"  # Custom header with API key
    QUERY = "query"  # API key in query parameter
    NONE = "none"  # No authentication (local models)


class VendorEndpoints(BaseModel):
    """API endpoint configuration for a vendor."""

    model_config = ConfigDict(extra="allow")

    chat: str = "/v1/chat/completions"
    models: str | None = None


class VendorConfig(BaseModel):
    """
    Configuration for a custom LLM vendor.

    Example YAML:
        id: azure-openai
        name: Azure OpenAI
        api_base: https://my-deployment.openai.azure.com
        api_version: 2024-02-15-preview
        auth_type: header
        auth_env: AZURE_OPENAI_API_KEY
        endpoints:
          chat: /openai/deployments/{deployment}/chat/completions
        headers:
          api-key: ${AZURE_OPENAI_API_KEY}
        default_model: gpt-4
        models:
          - gpt-4
          - gpt-4-turbo
    """

    model_config = ConfigDict(extra="allow", use_enum_values=True)

    id: str = Field(..., description="Unique identifier for the vendor")
    name: str = Field(..., description="Human-readable vendor name")
    api_base: str = Field(..., description="Base URL for API calls")
    api_version: str | None = Field(None, description="API version string")
    auth_type: AuthType = Field(AuthType.BEARER, description="Authentication method")
    auth_env: str | None = Field(None, description="Environment variable for auth")
    auth_header: str = Field("Authorization", description="Auth header name")
    endpoints: VendorEndpoints = Field(
        default_factory=VendorEndpoints,
        description="API endpoints",
    )
    headers: dict[str, str] = Field(
        default_factory=dict,
        description="Custom headers to include",
    )
    default_model: str | None = Field(None, description="Default model to use")
    models: list[str] = Field(
        default_factory=list,
        description="Available models for this vendor",
    )
    timeout: int = Field(120, description="Request timeout in seconds")
    request_format: str = Field("openai", description="Request format (openai, anthropic)")
    response_format: str = Field("openai", description="Response format (openai, anthropic)")

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate vendor ID is alphanumeric with hyphens."""
        if not re.match(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$|^[a-z0-9]$", v):
            raise ValueError(
                "Vendor ID must be lowercase alphanumeric with hyphens, "
                "not starting or ending with hyphen"
            )
        return v

    @field_validator("api_base")
    @classmethod
    def validate_api_base(cls, v: str) -> str:
        """Validate API base URL."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("API base must start with http:// or https://")
        return v.rstrip("/")

    def resolve_headers(self) -> dict[str, str]:
        """
        Resolve headers with environment variable substitution.

        Replaces ${VAR_NAME} patterns with environment variable values.

        Returns:
            Dictionary of resolved headers.
        """
        resolved = {}
        pattern = re.compile(r"\$\{([^}]+)\}")

        for key, value in self.headers.items():
            def replace_env(match: re.Match[str]) -> str:
                env_var = match.group(1)
                return os.getenv(env_var, "")

            resolved[key] = pattern.sub(replace_env, value)

        return resolved

    def get_auth_value(self) -> str | None:
        """
        Get the authentication value from environment.

        Returns:
            The API key/token from environment, or None if not set.
        """
        if self.auth_env:
            return os.getenv(self.auth_env)
        return None

    def is_configured(self) -> bool:
        """
        Check if the vendor is properly configured.

        Returns:
            True if authentication is configured or not required.
        """
        if self.auth_type == AuthType.NONE:
            return True
        return bool(self.get_auth_value())

    def build_url(self, endpoint: str, **kwargs: Any) -> str:
        """
        Build full URL for an endpoint.

        Args:
            endpoint: Endpoint path (e.g., 'chat').
            **kwargs: Variables to substitute in the path.

        Returns:
            Full URL with substituted variables.
        """
        # Get endpoint path
        path = getattr(self.endpoints, endpoint, None)
        if path is None:
            path = endpoint

        # Substitute path variables
        for key, value in kwargs.items():
            path = path.replace(f"{{{key}}}", str(value))

        # Add API version if specified
        url = f"{self.api_base}{path}"
        if self.api_version:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}api-version={self.api_version}"

        return url

    def build_headers(self) -> dict[str, str]:
        """
        Build complete headers for API requests.

        Returns:
            Dictionary of headers including authentication.
        """
        headers = {"Content-Type": "application/json"}

        # Add custom headers with env substitution
        headers.update(self.resolve_headers())

        # Add authentication header
        auth_value = self.get_auth_value()
        if auth_value and self.auth_type == AuthType.BEARER:
            headers[self.auth_header] = f"Bearer {auth_value}"
        elif auth_value and self.auth_type == AuthType.HEADER:
            headers[self.auth_header] = auth_value

        return headers

    @classmethod
    def from_yaml(cls, path: Path) -> "VendorConfig":
        """
        Load vendor configuration from a YAML file.

        Args:
            path: Path to the YAML file.

        Returns:
            VendorConfig instance.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            ValueError: If the YAML is invalid.
        """
        if not path.exists():
            raise FileNotFoundError(f"Vendor config not found: {path}")

        with open(path) as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError(f"Invalid vendor config: {path}")

        return cls(**data)

    def to_yaml(self, path: Path) -> None:
        """
        Save vendor configuration to a YAML file.

        Args:
            path: Path to save the YAML file.
        """
        path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict, excluding None values
        data = self.model_dump(mode="json", exclude_none=True)

        with open(path, "w") as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)


class VendorLoader:
    """
    Load and manage custom vendor configurations.

    Vendors are loaded from:
    1. User directory: ~/.persona/vendors/
    2. Project directory: .persona/vendors/
    3. Custom paths specified in config

    Example:
        loader = VendorLoader()
        vendors = loader.list_vendors()
        azure = loader.load("azure-openai")
    """

    DEFAULT_USER_DIR = Path.home() / ".persona" / "vendors"
    DEFAULT_PROJECT_DIR = Path(".persona") / "vendors"

    def __init__(
        self,
        user_dir: Path | None = None,
        project_dir: Path | None = None,
        additional_paths: list[Path] | None = None,
    ) -> None:
        """
        Initialise the vendor loader.

        Args:
            user_dir: Override user vendor directory.
            project_dir: Override project vendor directory.
            additional_paths: Additional directories to search.
        """
        self._user_dir = user_dir or self.DEFAULT_USER_DIR
        self._project_dir = project_dir or self.DEFAULT_PROJECT_DIR
        self._additional_paths = additional_paths or []
        self._cache: dict[str, VendorConfig] = {}

    @property
    def search_paths(self) -> list[Path]:
        """Return all vendor search paths in priority order."""
        paths = []

        # Project directory (highest priority)
        if self._project_dir.exists():
            paths.append(self._project_dir)

        # User directory
        if self._user_dir.exists():
            paths.append(self._user_dir)

        # Additional paths
        for path in self._additional_paths:
            if path.exists():
                paths.append(path)

        return paths

    def list_vendors(self, refresh: bool = False) -> list[str]:
        """
        List all available vendor IDs.

        Args:
            refresh: If True, bypass cache.

        Returns:
            List of vendor IDs.
        """
        vendors = set()

        for search_path in self.search_paths:
            for yaml_file in search_path.glob("*.yaml"):
                vendors.add(yaml_file.stem)
            for yml_file in search_path.glob("*.yml"):
                vendors.add(yml_file.stem)

        return sorted(vendors)

    def load(self, vendor_id: str, refresh: bool = False) -> VendorConfig:
        """
        Load a vendor configuration by ID.

        Args:
            vendor_id: The vendor ID to load.
            refresh: If True, bypass cache.

        Returns:
            VendorConfig instance.

        Raises:
            FileNotFoundError: If vendor config not found.
        """
        if not refresh and vendor_id in self._cache:
            return self._cache[vendor_id]

        # Search for the vendor file
        for search_path in self.search_paths:
            for ext in [".yaml", ".yml"]:
                path = search_path / f"{vendor_id}{ext}"
                if path.exists():
                    config = VendorConfig.from_yaml(path)
                    self._cache[vendor_id] = config
                    return config

        raise FileNotFoundError(
            f"Vendor configuration not found: {vendor_id}\n"
            f"Searched paths: {', '.join(str(p) for p in self.search_paths)}"
        )

    def save(self, config: VendorConfig, user_level: bool = True) -> Path:
        """
        Save a vendor configuration.

        Args:
            config: VendorConfig to save.
            user_level: If True, save to user directory; else project directory.

        Returns:
            Path where the config was saved.
        """
        if user_level:
            target_dir = self._user_dir
        else:
            target_dir = self._project_dir

        target_dir.mkdir(parents=True, exist_ok=True)
        path = target_dir / f"{config.id}.yaml"

        config.to_yaml(path)
        self._cache[config.id] = config

        return path

    def delete(self, vendor_id: str) -> bool:
        """
        Delete a vendor configuration.

        Args:
            vendor_id: The vendor ID to delete.

        Returns:
            True if deleted, False if not found.
        """
        for search_path in self.search_paths:
            for ext in [".yaml", ".yml"]:
                path = search_path / f"{vendor_id}{ext}"
                if path.exists():
                    path.unlink()
                    self._cache.pop(vendor_id, None)
                    return True

        return False

    def exists(self, vendor_id: str) -> bool:
        """
        Check if a vendor configuration exists.

        Args:
            vendor_id: The vendor ID to check.

        Returns:
            True if vendor exists.
        """
        return vendor_id in self.list_vendors()

    def clear_cache(self) -> None:
        """Clear the vendor configuration cache."""
        self._cache.clear()

    def get_configured_vendors(self) -> list[str]:
        """
        List vendors that have authentication configured.

        Returns:
            List of configured vendor IDs.
        """
        configured = []
        for vendor_id in self.list_vendors():
            try:
                config = self.load(vendor_id)
                if config.is_configured():
                    configured.append(vendor_id)
            except Exception:
                continue
        return configured
