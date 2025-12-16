"""Model configuration loader for LLM parameters.

Loads model-specific parameters from YAML configuration files.
Supports per-model defaults for temperature, max_tokens, and other settings.
"""

from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel


def get_config_dir() -> Path:
    """Get the config directory path.

    Searches in order:
    1. Project-level config/ directory
    2. Package-level config/ directory
    """
    # Try relative to current working directory first
    cwd_config = Path("config")
    if cwd_config.exists():
        return cwd_config

    # Fall back to relative to this file (package config)
    return Path(__file__).parent.parent.parent.parent / "config"


class ModelParams(BaseModel):
    """Parameters for a single model.

    Attributes:
        name: Model identifier (e.g., 'gpt-4o', 'claude-sonnet-4.5')
        provider: Provider name (openai, anthropic, gemini, ollama)
        description: Human-readable description of the model
        max_tokens: Maximum tokens to generate
        temperature: Sampling temperature (0.0-2.0)
        top_p: Nucleus sampling parameter
        context_window: Maximum context window size
    """

    name: str = ""
    provider: str = ""
    description: str = ""
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 1.0
    context_window: int = 128000


def load_model_config(provider: str, model_name: str) -> ModelParams:
    """Load configuration for a specific model.

    Args:
        provider: Provider name (openai, anthropic, gemini, ollama).
        model_name: Model identifier.

    Returns:
        ModelParams for the model with loaded or default values.
    """
    config_dir = get_config_dir()
    provider_dir = config_dir / "models" / provider

    if not provider_dir.exists():
        return ModelParams(name=model_name, provider=provider)

    # Try exact model name match
    for yaml_file in provider_dir.glob("*.yaml"):
        if yaml_file.name in ("README.md", "defaults.yaml"):
            continue

        try:
            with open(yaml_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}

            # Check if this config matches the model
            config_name = data.get("name", yaml_file.stem)
            # Match exact name or base name (e.g., llama3 matches llama3:8b)
            if config_name == model_name or yaml_file.stem == model_name.split(":")[0]:
                params = data.get("parameters", {})
                return ModelParams(
                    name=data.get("name", model_name),
                    provider=data.get("provider", provider),
                    description=data.get("description", ""),
                    max_tokens=params.get("max_tokens", 4096),
                    temperature=params.get("temperature", 0.7),
                    top_p=params.get("top_p", 1.0),
                    context_window=params.get("context_window", 128000),
                )
        except Exception:
            continue

    # Try defaults.yaml for the provider (especially useful for Ollama)
    defaults_file = provider_dir / "defaults.yaml"
    if defaults_file.exists():
        try:
            with open(defaults_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            params = data.get("parameters", {})
            return ModelParams(
                name=model_name,
                provider=provider,
                max_tokens=params.get("max_tokens", 4096),
                temperature=params.get("temperature", 0.7),
                top_p=params.get("top_p", 1.0),
                context_window=params.get("context_window", 128000),
            )
        except Exception:
            pass

    # Return defaults
    return ModelParams(name=model_name, provider=provider)


def get_model_params(provider: str, model_id: str) -> ModelParams:
    """Get parameters for a specific model (convenience wrapper).

    Args:
        provider: Provider name (openai, anthropic, gemini, ollama).
        model_id: Model identifier.

    Returns:
        ModelParams for the model.
    """
    return load_model_config(provider, model_id)


def get_default_model(provider: str) -> str:
    """Get the default model for a provider from config/models/default.yaml.

    Args:
        provider: Provider name (openai, anthropic, gemini, ollama).

    Returns:
        Default model name for the provider.
    """
    config_dir = get_config_dir()
    defaults_file = config_dir / "models" / "default.yaml"

    # Fallback defaults if file not found
    fallback_defaults = {
        "openai": "gpt-4o",
        "anthropic": "claude-sonnet-4-20250514",
        "gemini": "gemini-2.5-flash",
        "ollama": "llama3:8b",
    }

    if defaults_file.exists():
        try:
            with open(defaults_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            defaults = data.get("defaults", {})
            return defaults.get(provider, fallback_defaults.get(provider, ""))
        except Exception:
            pass

    return fallback_defaults.get(provider, "")


def list_configured_models(provider: Optional[str] = None) -> list[dict]:
    """List all models with configuration files.

    Args:
        provider: Optional provider to filter by.

    Returns:
        List of model configuration dictionaries.
    """
    config_dir = get_config_dir()
    models_dir = config_dir / "models"

    if not models_dir.exists():
        return []

    models = []
    providers = [provider] if provider else ["openai", "anthropic", "gemini", "ollama"]

    for prov in providers:
        provider_dir = models_dir / prov
        if not provider_dir.exists():
            continue

        for yaml_file in provider_dir.glob("*.yaml"):
            if yaml_file.name in ("defaults.yaml",):
                continue

            try:
                with open(yaml_file, "r", encoding="utf-8") as f:
                    data = yaml.safe_load(f) or {}

                models.append({
                    "name": data.get("name", yaml_file.stem),
                    "provider": prov,
                    "description": data.get("description", ""),
                    "file": str(yaml_file),
                })
            except Exception:
                continue

    return models
