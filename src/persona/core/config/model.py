"""
Custom model configuration management.

This module provides YAML-based configuration for custom LLM models,
supporting fine-tuned models, new model releases, and custom deployments.
"""

import re
from decimal import Decimal
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator


class ModelCapabilities(BaseModel):
    """Model capability flags."""

    model_config = ConfigDict(extra="allow")

    structured_output: bool = Field(True, description="Supports structured JSON output")
    vision: bool = Field(False, description="Supports image input")
    function_calling: bool = Field(True, description="Supports function/tool calling")
    streaming: bool = Field(True, description="Supports streaming responses")


class ModelPricing(BaseModel):
    """Model pricing per million tokens."""

    model_config = ConfigDict(extra="allow")

    input: Decimal = Field(Decimal("0.0"), description="Price per 1M input tokens")
    output: Decimal = Field(Decimal("0.0"), description="Price per 1M output tokens")
    currency: str = Field("USD", description="Pricing currency")

    @field_validator("input", "output", mode="before")
    @classmethod
    def coerce_to_decimal(cls, v: Any) -> Decimal:
        """Coerce input to Decimal."""
        if isinstance(v, Decimal):
            return v
        return Decimal(str(v))


class ModelConfig(BaseModel):
    """
    Configuration for a custom LLM model.

    Example YAML:
        id: my-finetuned-gpt4
        name: Fine-tuned GPT-4 for Personas
        provider: azure-openai
        base_model: gpt-4
        context_window: 128000
        max_output: 8192
        pricing:
          input: 5.00
          output: 15.00
        capabilities:
          structured_output: true
          vision: false
    """

    model_config = ConfigDict(extra="allow", use_enum_values=True)

    id: str = Field(..., description="Unique model identifier")
    name: str = Field(..., description="Human-readable model name")
    provider: str = Field(..., description="Provider ID (built-in or custom vendor)")
    base_model: str | None = Field(None, description="Base model ID (for inheritance)")
    context_window: int = Field(128000, description="Maximum context window in tokens")
    max_output: int = Field(4096, description="Maximum output tokens")
    pricing: ModelPricing = Field(
        default_factory=ModelPricing,
        description="Pricing per million tokens",
    )
    capabilities: ModelCapabilities = Field(
        default_factory=ModelCapabilities,
        description="Model capabilities",
    )
    deployment_id: str | None = Field(
        None, description="Deployment ID (for Azure etc.)"
    )
    description: str | None = Field(None, description="Model description")

    @field_validator("id")
    @classmethod
    def validate_id(cls, v: str) -> str:
        """Validate model ID format."""
        if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$", v):
            raise ValueError(
                "Model ID must be alphanumeric with dots, underscores, or hyphens, "
                "not starting or ending with punctuation"
            )
        return v

    @field_validator("context_window", "max_output")
    @classmethod
    def validate_positive(cls, v: int) -> int:
        """Validate positive integer values."""
        if v <= 0:
            raise ValueError("Value must be positive")
        return v

    def get_effective_model_id(self) -> str:
        """
        Get the model ID to use for API calls.

        Returns deployment_id if set, otherwise the model id.
        """
        return self.deployment_id or self.id

    @classmethod
    def from_yaml(cls, path: Path) -> "ModelConfig":
        """
        Load model configuration from a YAML file.

        Args:
            path: Path to the YAML file.

        Returns:
            ModelConfig instance.

        Raises:
            FileNotFoundError: If the file doesn't exist.
            ValueError: If the YAML is invalid.
        """
        if not path.exists():
            raise FileNotFoundError(f"Model config not found: {path}")

        with open(path) as f:
            data = yaml.safe_load(f)

        if not isinstance(data, dict):
            raise ValueError(f"Invalid model config: {path}")

        return cls(**data)

    def to_yaml(self, path: Path) -> None:
        """
        Save model configuration to a YAML file.

        Args:
            path: Path to save the YAML file.
        """
        path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict, handling Decimal conversion
        data = self.model_dump(mode="json", exclude_none=True)

        with open(path, "w") as f:
            yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)


class ModelLoader:
    """
    Load and manage custom model configurations.

    Models are loaded from:
    1. User directory: ~/.persona/models/
    2. Project directory: .persona/models/
    3. Custom paths specified in config

    Example:
        loader = ModelLoader()
        models = loader.list_models()
        model = loader.load("my-finetuned-gpt4")
    """

    DEFAULT_USER_DIR = Path.home() / ".persona" / "models"
    DEFAULT_PROJECT_DIR = Path(".persona") / "models"

    def __init__(
        self,
        user_dir: Path | None = None,
        project_dir: Path | None = None,
        additional_paths: list[Path] | None = None,
    ) -> None:
        """
        Initialise the model loader.

        Args:
            user_dir: Override user model directory.
            project_dir: Override project model directory.
            additional_paths: Additional directories to search.
        """
        self._user_dir = user_dir or self.DEFAULT_USER_DIR
        self._project_dir = project_dir or self.DEFAULT_PROJECT_DIR
        self._additional_paths = additional_paths or []
        self._cache: dict[str, ModelConfig] = {}

    @property
    def search_paths(self) -> list[Path]:
        """Return all model search paths in priority order."""
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

    def list_models(self, provider: str | None = None) -> list[str]:
        """
        List all available model IDs.

        Args:
            provider: Filter by provider if specified.

        Returns:
            List of model IDs.
        """
        models = set()

        for search_path in self.search_paths:
            for yaml_file in search_path.glob("*.yaml"):
                try:
                    config = ModelConfig.from_yaml(yaml_file)
                    if provider is None or config.provider == provider:
                        models.add(config.id)
                except Exception:
                    continue
            for yml_file in search_path.glob("*.yml"):
                try:
                    config = ModelConfig.from_yaml(yml_file)
                    if provider is None or config.provider == provider:
                        models.add(config.id)
                except Exception:
                    continue

        return sorted(models)

    def load(self, model_id: str, refresh: bool = False) -> ModelConfig:
        """
        Load a model configuration by ID.

        Args:
            model_id: The model ID to load.
            refresh: If True, bypass cache.

        Returns:
            ModelConfig instance.

        Raises:
            FileNotFoundError: If model config not found.
        """
        if not refresh and model_id in self._cache:
            return self._cache[model_id]

        # Search for the model file
        for search_path in self.search_paths:
            for ext in [".yaml", ".yml"]:
                # Try direct filename match
                path = search_path / f"{model_id}{ext}"
                if path.exists():
                    config = ModelConfig.from_yaml(path)
                    if config.id == model_id:
                        self._cache[model_id] = config
                        return config

                # Search all files for matching ID
                for yaml_file in search_path.glob(f"*{ext}"):
                    try:
                        config = ModelConfig.from_yaml(yaml_file)
                        if config.id == model_id:
                            self._cache[model_id] = config
                            return config
                    except Exception:
                        continue

        raise FileNotFoundError(
            f"Model configuration not found: {model_id}\n"
            f"Searched paths: {', '.join(str(p) for p in self.search_paths)}"
        )

    def save(self, config: ModelConfig, user_level: bool = True) -> Path:
        """
        Save a model configuration.

        Args:
            config: ModelConfig to save.
            user_level: If True, save to user directory; else project directory.

        Returns:
            Path where the config was saved.
        """
        if user_level:
            target_dir = self._user_dir
        else:
            target_dir = self._project_dir

        target_dir.mkdir(parents=True, exist_ok=True)
        # Use sanitised filename
        filename = config.id.replace("/", "-").replace(":", "-")
        path = target_dir / f"{filename}.yaml"

        config.to_yaml(path)
        self._cache[config.id] = config

        return path

    def delete(self, model_id: str) -> bool:
        """
        Delete a model configuration.

        Args:
            model_id: The model ID to delete.

        Returns:
            True if deleted, False if not found.
        """
        for search_path in self.search_paths:
            for ext in [".yaml", ".yml"]:
                # Try direct filename
                filename = model_id.replace("/", "-").replace(":", "-")
                path = search_path / f"{filename}{ext}"
                if path.exists():
                    path.unlink()
                    self._cache.pop(model_id, None)
                    return True

                # Search all files
                for yaml_file in search_path.glob(f"*{ext}"):
                    try:
                        config = ModelConfig.from_yaml(yaml_file)
                        if config.id == model_id:
                            yaml_file.unlink()
                            self._cache.pop(model_id, None)
                            return True
                    except Exception:
                        continue

        return False

    def exists(self, model_id: str) -> bool:
        """
        Check if a model configuration exists.

        Args:
            model_id: The model ID to check.

        Returns:
            True if model exists.
        """
        try:
            self.load(model_id)
            return True
        except FileNotFoundError:
            return False

    def clear_cache(self) -> None:
        """Clear the model configuration cache."""
        self._cache.clear()

    def list_by_provider(self) -> dict[str, list[str]]:
        """
        List models grouped by provider.

        Returns:
            Dictionary mapping provider names to model IDs.
        """
        by_provider: dict[str, list[str]] = {}

        for search_path in self.search_paths:
            for ext in [".yaml", ".yml"]:
                for yaml_file in search_path.glob(f"*{ext}"):
                    try:
                        config = ModelConfig.from_yaml(yaml_file)
                        if config.provider not in by_provider:
                            by_provider[config.provider] = []
                        if config.id not in by_provider[config.provider]:
                            by_provider[config.provider].append(config.id)
                    except Exception:
                        continue

        return by_provider


def get_builtin_models() -> dict[str, list[str]]:
    """
    Get built-in models from the provider implementations.

    Returns:
        Dictionary mapping provider names to model lists.
    """
    from persona.core.providers import ProviderFactory

    result = {}
    for provider_name in ProviderFactory.list_builtin_providers():
        try:
            provider = ProviderFactory.create(provider_name)
            result[provider_name] = provider.available_models
        except Exception:
            result[provider_name] = []

    return result


def get_all_models(include_custom: bool = True) -> dict[str, list[str]]:
    """
    Get all available models (built-in and custom).

    Args:
        include_custom: Whether to include custom models.

    Returns:
        Dictionary mapping provider names to model lists.
    """
    result = get_builtin_models()

    if include_custom:
        loader = ModelLoader()
        custom = loader.list_by_provider()
        for provider, models in custom.items():
            if provider in result:
                # Add custom models that aren't already in the list
                for model in models:
                    if model not in result[provider]:
                        result[provider].append(model)
            else:
                result[provider] = models

    return result
