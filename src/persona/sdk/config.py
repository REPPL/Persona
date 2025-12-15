"""
SDK configuration management.

This module provides configuration loading from multiple sources:
- Constructor arguments (highest priority)
- Environment variables (PERSONA_*)
- Configuration file (~/.persona/config.yaml)
- Defaults (lowest priority)
"""

import os
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator

from persona.sdk.exceptions import ConfigurationError


class SDKConfig(BaseModel):
    """
    SDK configuration with multiple loading sources.

    Configuration priority (highest to lowest):
    1. Constructor arguments
    2. Environment variables (PERSONA_*)
    3. Config file (~/.persona/config.yaml)
    4. Defaults

    Example:
        # Load from defaults
        config = SDKConfig.from_defaults()

        # Load from environment
        config = SDKConfig.from_environment()

        # Load from file
        config = SDKConfig.from_file("~/.persona/config.yaml")

        # Override specific values
        config = SDKConfig(
            default_provider="openai",
            default_count=5,
        )
    """

    default_provider: str = Field(
        default="anthropic",
        description="Default LLM provider",
    )
    default_model: str | None = Field(
        default=None,
        description="Default model identifier",
    )
    default_count: int = Field(
        default=3,
        ge=1,
        le=20,
        description="Default number of personas",
    )
    default_complexity: str = Field(
        default="moderate",
        description="Default complexity level",
    )
    default_detail_level: str = Field(
        default="standard",
        description="Default detail level",
    )
    default_temperature: float = Field(
        default=0.7,
        ge=0.0,
        le=2.0,
        description="Default sampling temperature",
    )
    config_file_path: str | None = Field(
        default=None,
        description="Path to configuration file",
    )

    @field_validator("default_provider")
    @classmethod
    def validate_provider(cls, v: str) -> str:
        """Validate provider name."""
        valid = {"anthropic", "openai", "gemini"}
        if v not in valid:
            raise ValueError(f"Invalid provider: {v}. Must be one of: {valid}")
        return v

    @field_validator("default_complexity")
    @classmethod
    def validate_complexity(cls, v: str) -> str:
        """Validate complexity level."""
        valid = {"simple", "moderate", "complex"}
        if v not in valid:
            raise ValueError(f"Invalid complexity: {v}. Must be one of: {valid}")
        return v

    @field_validator("default_detail_level")
    @classmethod
    def validate_detail_level(cls, v: str) -> str:
        """Validate detail level."""
        valid = {"minimal", "standard", "detailed"}
        if v not in valid:
            raise ValueError(f"Invalid detail_level: {v}. Must be one of: {valid}")
        return v

    @classmethod
    def from_defaults(cls) -> "SDKConfig":
        """
        Create configuration with default values.

        Returns:
            SDKConfig with all defaults.
        """
        return cls()

    @classmethod
    def from_environment(cls) -> "SDKConfig":
        """
        Create configuration from environment variables.

        Reads from PERSONA_* environment variables:
        - PERSONA_PROVIDER
        - PERSONA_MODEL
        - PERSONA_COUNT
        - PERSONA_COMPLEXITY
        - PERSONA_DETAIL_LEVEL
        - PERSONA_TEMPERATURE

        Returns:
            SDKConfig loaded from environment.

        Example:
            # With PERSONA_PROVIDER=openai set
            config = SDKConfig.from_environment()
            assert config.default_provider == "openai"
        """
        env_values = {}

        # Map environment variables to config fields
        env_mapping = {
            "PERSONA_PROVIDER": "default_provider",
            "PERSONA_MODEL": "default_model",
            "PERSONA_COUNT": ("default_count", int),
            "PERSONA_COMPLEXITY": "default_complexity",
            "PERSONA_DETAIL_LEVEL": "default_detail_level",
            "PERSONA_TEMPERATURE": ("default_temperature", float),
        }

        for env_var, field_info in env_mapping.items():
            value = os.getenv(env_var)
            if value is not None:
                if isinstance(field_info, tuple):
                    field_name, converter = field_info
                    try:
                        env_values[field_name] = converter(value)
                    except ValueError as e:
                        raise ConfigurationError(
                            f"Invalid value for {env_var}: {value}",
                            field=env_var,
                            value=value,
                        ) from e
                else:
                    env_values[field_info] = value

        return cls(**env_values)

    @classmethod
    def from_file(cls, path: str | Path) -> "SDKConfig":
        """
        Create configuration from YAML file.

        Args:
            path: Path to YAML configuration file.

        Returns:
            SDKConfig loaded from file.

        Raises:
            ConfigurationError: If file is invalid or not found.

        Example:
            config = SDKConfig.from_file("~/.persona/config.yaml")
        """
        path = Path(path).expanduser()

        if not path.exists():
            raise ConfigurationError(
                f"Configuration file not found: {path}",
                field="config_file_path",
                value=str(path),
            )

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise ConfigurationError(
                f"Invalid YAML in configuration file: {e}",
                field="config_file_path",
                value=str(path),
            ) from e
        except Exception as e:
            raise ConfigurationError(
                f"Failed to read configuration file: {e}",
                field="config_file_path",
                value=str(path),
            ) from e

        if not isinstance(data, dict):
            raise ConfigurationError(
                "Configuration file must contain a YAML object",
                field="config_file_path",
                value=str(path),
            )

        # Extract SDK section if present
        sdk_config = data.get("sdk", data)

        # Add path to config
        sdk_config["config_file_path"] = str(path)

        try:
            return cls(**sdk_config)
        except Exception as e:
            raise ConfigurationError(
                f"Invalid configuration: {e}",
                field="config_file_path",
                value=str(path),
            ) from e

    @classmethod
    def from_sources(
        cls,
        config_file: str | Path | None = None,
        use_environment: bool = True,
        **overrides: Any,
    ) -> "SDKConfig":
        """
        Create configuration from multiple sources.

        Priority (highest to lowest):
        1. overrides (keyword arguments)
        2. Environment variables
        3. Configuration file
        4. Defaults

        Args:
            config_file: Optional path to configuration file.
            use_environment: Whether to load from environment variables.
            **overrides: Explicit overrides for configuration values.

        Returns:
            SDKConfig merged from all sources.

        Example:
            config = SDKConfig.from_sources(
                config_file="~/.persona/config.yaml",
                default_provider="openai",  # Override
            )
        """
        # Start with defaults
        values = cls().model_dump()

        # Load from file if provided
        if config_file is not None:
            file_config = cls.from_file(config_file)
            values.update(file_config.model_dump())

        # Load from environment
        if use_environment:
            env_config = cls.from_environment()
            values.update(
                {k: v for k, v in env_config.model_dump().items() if v is not None}
            )

        # Apply overrides
        values.update(overrides)

        return cls(**values)

    def to_file(self, path: str | Path) -> None:
        """
        Save configuration to YAML file.

        Args:
            path: Path to save configuration file.

        Example:
            config = SDKConfig(default_provider="openai")
            config.to_file("~/.persona/config.yaml")
        """
        path = Path(path).expanduser()
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "sdk": self.model_dump(exclude={"config_file_path"}, exclude_none=True)
        }

        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)

    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.model_dump(exclude_none=True)
