"""
Global configuration management.

Provides layered configuration with the following precedence (highest to lowest):
1. Environment variables
2. Experiment config
3. Project config (.persona/config.yaml)
4. Global config (~/.persona/config.yaml or %APPDATA%/persona/config.yaml)
5. Built-in defaults
"""

import os
from dataclasses import dataclass, field
from decimal import Decimal
from pathlib import Path
from typing import Any, Optional

import yaml
from pydantic import BaseModel, Field

from persona.core.platform import get_config_dir


# Configuration paths
def get_global_config_path() -> Path:
    """Get path to global configuration file.

    Returns:
        Windows: %APPDATA%/persona/config.yaml
        macOS/Linux: ~/.persona/config.yaml
    """
    return get_config_dir() / "config.yaml"


def get_project_config_path() -> Optional[Path]:
    """Find project configuration file by searching up directory tree."""
    current = Path.cwd()
    while current != current.parent:
        config_path = current / ".persona" / "config.yaml"
        if config_path.exists():
            return config_path
        # Also check for persona.yaml in project root
        alt_path = current / "persona.yaml"
        if alt_path.exists():
            return alt_path
        current = current.parent
    return None


class DefaultsConfig(BaseModel):
    """Default generation settings."""

    provider: str = Field(default="anthropic", description="Default LLM provider")
    model: Optional[str] = Field(default=None, description="Default model (uses provider default if not set)")
    complexity: str = Field(default="moderate", description="Complexity level")
    detail_level: str = Field(default="standard", description="Detail level")
    workflow: str = Field(default="default", description="Default workflow")
    count: int = Field(default=3, description="Default persona count")


class BudgetConfig(BaseModel):
    """Budget limits for cost control."""

    per_run: Optional[Decimal] = Field(default=None, description="Maximum cost per generation run")
    daily: Optional[Decimal] = Field(default=None, description="Daily budget limit")
    monthly: Optional[Decimal] = Field(default=None, description="Monthly budget limit")


class OutputConfig(BaseModel):
    """Output preferences."""

    format: str = Field(default="json", description="Default output format")
    include_readme: bool = Field(default=True, description="Generate README with outputs")
    timestamp_folders: bool = Field(default=True, description="Use timestamped output folders")


class LoggingConfig(BaseModel):
    """Logging configuration."""

    level: str = Field(default="info", description="Log level (debug, info, warning, error)")
    format: str = Field(default="console", description="Log format (console, json)")
    file: Optional[str] = Field(default=None, description="Log file path")


class ProviderSettings(BaseModel):
    """Settings for a provider."""

    enabled: bool = Field(default=True, description="Whether provider is enabled")


class TelemetryConfig(BaseModel):
    """Telemetry settings (opt-in)."""

    enabled: bool = Field(default=False, description="Enable anonymous usage telemetry")


class GlobalConfig(BaseModel):
    """Global Persona configuration."""

    defaults: DefaultsConfig = Field(default_factory=DefaultsConfig)
    budgets: BudgetConfig = Field(default_factory=BudgetConfig)
    output: OutputConfig = Field(default_factory=OutputConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)
    providers: dict[str, ProviderSettings] = Field(default_factory=dict)
    telemetry: TelemetryConfig = Field(default_factory=TelemetryConfig)

    @classmethod
    def get_default(cls) -> "GlobalConfig":
        """Get configuration with all defaults."""
        return cls()


@dataclass
class ConfigManager:
    """Manages layered configuration loading and merging."""

    _global_config: Optional[GlobalConfig] = field(default=None, init=False)
    _project_config: Optional[dict[str, Any]] = field(default=None, init=False)
    _effective_config: Optional[GlobalConfig] = field(default=None, init=False)

    def load_global(self) -> GlobalConfig:
        """Load global configuration file."""
        path = get_global_config_path()
        if path.exists():
            try:
                with open(path) as f:
                    data = yaml.safe_load(f) or {}
                return GlobalConfig.model_validate(data)
            except Exception:
                return GlobalConfig.get_default()
        return GlobalConfig.get_default()

    def load_project(self) -> dict[str, Any]:
        """Load project configuration file."""
        path = get_project_config_path()
        if path and path.exists():
            try:
                with open(path) as f:
                    return yaml.safe_load(f) or {}
            except Exception:
                return {}
        return {}

    def load_env_overrides(self) -> dict[str, Any]:
        """Load configuration from environment variables.

        Environment variable format: PERSONA_<SECTION>_<KEY>
        Example: PERSONA_DEFAULTS_PROVIDER=openai
        """
        overrides: dict[str, Any] = {}

        env_mappings = {
            "PERSONA_DEFAULTS_PROVIDER": ("defaults", "provider"),
            "PERSONA_DEFAULTS_MODEL": ("defaults", "model"),
            "PERSONA_DEFAULTS_COMPLEXITY": ("defaults", "complexity"),
            "PERSONA_DEFAULTS_DETAIL_LEVEL": ("defaults", "detail_level"),
            "PERSONA_DEFAULTS_WORKFLOW": ("defaults", "workflow"),
            "PERSONA_DEFAULTS_COUNT": ("defaults", "count"),
            "PERSONA_BUDGET_PER_RUN": ("budgets", "per_run"),
            "PERSONA_BUDGET_DAILY": ("budgets", "daily"),
            "PERSONA_BUDGET_MONTHLY": ("budgets", "monthly"),
            "PERSONA_OUTPUT_FORMAT": ("output", "format"),
            "PERSONA_LOGGING_LEVEL": ("logging", "level"),
        }

        for env_var, (section, key) in env_mappings.items():
            value = os.environ.get(env_var)
            if value is not None:
                if section not in overrides:
                    overrides[section] = {}
                # Convert types as needed
                if key == "count":
                    overrides[section][key] = int(value)
                elif key in ("per_run", "daily", "monthly"):
                    overrides[section][key] = Decimal(value)
                else:
                    overrides[section][key] = value

        return overrides

    def _merge_dict(self, base: dict, override: dict) -> dict:
        """Deep merge two dictionaries."""
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_dict(result[key], value)
            else:
                result[key] = value
        return result

    def load(self) -> GlobalConfig:
        """Load effective configuration with all layers merged."""
        # Start with defaults
        config_dict = GlobalConfig.get_default().model_dump()

        # Layer 2: Global config
        global_config = self.load_global()
        config_dict = self._merge_dict(config_dict, global_config.model_dump(exclude_none=True))

        # Layer 3: Project config
        project_config = self.load_project()
        if project_config:
            config_dict = self._merge_dict(config_dict, project_config)

        # Layer 4: Environment overrides
        env_config = self.load_env_overrides()
        if env_config:
            config_dict = self._merge_dict(config_dict, env_config)

        self._effective_config = GlobalConfig.model_validate(config_dict)
        return self._effective_config

    def get_value(self, path: str) -> Any:
        """Get a configuration value by dot-notation path.

        Example: get_value("defaults.provider") -> "anthropic"
        """
        config = self.load()
        parts = path.split(".")
        value: Any = config.model_dump()

        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                raise KeyError(f"Configuration key not found: {path}")

        return value

    def set_value(self, path: str, value: Any, *, user_level: bool = True) -> Path:
        """Set a configuration value.

        Args:
            path: Dot-notation path (e.g., "defaults.provider")
            value: Value to set
            user_level: If True, save to global config. If False, save to project config.

        Returns:
            Path to the modified configuration file.
        """
        if user_level:
            config_path = get_global_config_path()
        else:
            config_path = get_project_config_path()
            if not config_path:
                config_path = Path.cwd() / ".persona" / "config.yaml"

        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing config or create empty
        if config_path.exists():
            with open(config_path) as f:
                config_data = yaml.safe_load(f) or {}
        else:
            config_data = {}

        # Navigate to parent and set value
        parts = path.split(".")
        current = config_data
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        current[parts[-1]] = value

        # Save
        with open(config_path, "w") as f:
            yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)

        return config_path

    def reset(self, *, user_level: bool = True) -> Optional[Path]:
        """Reset configuration to defaults.

        Args:
            user_level: If True, reset global config. If False, reset project config.

        Returns:
            Path to the removed configuration file, or None if it didn't exist.
        """
        if user_level:
            config_path = get_global_config_path()
        else:
            config_path = get_project_config_path()

        if config_path and config_path.exists():
            config_path.unlink()
            return config_path
        return None

    def init_global(self, *, force: bool = False) -> Path:
        """Initialise global configuration file with defaults.

        Args:
            force: Overwrite existing configuration.

        Returns:
            Path to the created configuration file.

        Raises:
            FileExistsError: If configuration exists and force is False.
        """
        config_path = get_global_config_path()

        if config_path.exists() and not force:
            raise FileExistsError(f"Configuration already exists: {config_path}")

        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Generate default config with comments
        default_content = """# Persona Global Configuration
# See: https://github.com/REPPL/Persona

# Default generation settings
defaults:
  provider: anthropic
  # model: claude-sonnet-4-20250514  # Uses provider default if not set
  complexity: moderate
  detail_level: standard
  workflow: default
  count: 3

# Budget limits (optional)
# budgets:
#   per_run: 5.00
#   daily: 25.00
#   monthly: 100.00

# Output preferences
output:
  format: json
  include_readme: true
  timestamp_folders: true

# Logging configuration
logging:
  level: info
  format: console  # console or json
  # file: ~/.persona/logs/persona.log

# Provider settings (API keys via environment variables)
# providers:
#   anthropic:
#     enabled: true
#   openai:
#     enabled: true
#   google:
#     enabled: false

# Telemetry (opt-in, disabled by default)
telemetry:
  enabled: false
"""

        config_path.write_text(default_content)
        return config_path


# Module-level instance for convenience
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global config manager instance."""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def get_config() -> GlobalConfig:
    """Get the effective configuration."""
    return get_config_manager().load()
