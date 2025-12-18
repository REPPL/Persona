# R-006: YAML Configuration & Validation

## Executive Summary

Pydantic v2 with **pydantic-yaml** provides the ideal configuration management stack: YAML for human-readable configs, Pydantic for validation and type safety. The key patterns are domain-specific configuration classes, strict validation with `extra="forbid"`, and environment variable integration via `pydantic-settings`. This approach ensures configuration errors are caught early with clear, actionable error messages.

## Current State of the Art (2025)

### Industry Standards

YAML configuration with Pydantic validation is the de facto standard for Python applications:
- **YAML** - Human-readable, supports comments, version-controllable
- **Pydantic** - Type validation, default values, clear errors
- **Environment Variables** - Secrets (API keys) separate from config files

**Key Principle:** Validate configuration at load time, not at use time. Fail fast with helpful errors.

### Academic Research

No significant academic research specific to configuration validation. Best practices derive from software engineering principles (fail-fast, separation of concerns).

### Open Source Ecosystem

| Library | Purpose | Features |
|---------|---------|----------|
| **pydantic** | Core validation | Types, validators, serialisation |
| **pydantic-settings** | Env var loading | .env files, nested settings |
| **pydantic-yaml** | YAML I/O | Load/dump YAML with Pydantic |
| **PyYAML** | YAML parsing | Base YAML library |
| **strictyaml** | Safe YAML | Type-safe YAML subset |

## Alternatives Analysis

| Option | Pros | Cons | Recommendation |
|--------|------|------|----------------|
| **Pydantic + PyYAML** | Flexible, widely used | Manual integration | **Recommended** |
| **pydantic-yaml** | Convenient helpers | Extra dependency | Consider |
| **strictyaml** | Type-safe subset | Less flexible | Consider for critical configs |
| **TOML** | Simpler syntax | Less expressive | Not for complex configs |
| **JSON** | Native Python | No comments, verbose | Avoid for configs |

## Recommendation

### Primary Approach

Use **Pydantic v2 + PyYAML** with domain-specific configuration classes:

#### Configuration Schema

```python
# src/persona/core/config/schemas.py
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Literal
from pathlib import Path

class VendorConfig(BaseModel):
    """Configuration for an LLM vendor."""
    name: str
    api_base: str
    models: list[str]

    model_config = {"extra": "forbid"}

class ModelConfig(BaseModel):
    """Configuration for a specific model."""
    name: str
    vendor: str
    context_window: int = Field(ge=1000)
    max_output: int = Field(ge=100)
    pricing: "PricingConfig"

    model_config = {"extra": "forbid"}

class PricingConfig(BaseModel):
    """Token pricing configuration."""
    input_per_1k: float = Field(ge=0)
    output_per_1k: float = Field(ge=0)
    currency: str = "USD"

class ExperimentConfig(BaseModel):
    """Experiment configuration from config.yaml."""
    vendor: str
    model: str
    persona_count: int = Field(ge=1, le=20, default=5)
    temperature: float = Field(ge=0, le=2, default=0.7)
    max_tokens: int = Field(ge=100, le=16000, default=4000)
    prompt_template: str = "default"

    model_config = {"extra": "forbid"}

    @field_validator("vendor")
    @classmethod
    def validate_vendor(cls, v: str) -> str:
        valid_vendors = ["openai", "anthropic", "gemini"]
        if v not in valid_vendors:
            raise ValueError(f"Vendor must be one of: {valid_vendors}")
        return v
```

#### Loading Configuration

```python
# src/persona/core/config/loader.py
from pathlib import Path
import yaml
from .schemas import ExperimentConfig, VendorConfig

class ConfigLoader:
    def load_experiment(self, path: Path) -> ExperimentConfig:
        """Load and validate experiment configuration."""
        with open(path / "config.yaml") as f:
            data = yaml.safe_load(f)

        try:
            return ExperimentConfig.model_validate(data)
        except ValidationError as e:
            raise ConfigurationError(
                f"Invalid experiment configuration in {path}:\n{e}"
            )

    def load_vendor(self, vendor_name: str) -> VendorConfig:
        """Load vendor configuration from bundled configs."""
        config_path = self.config_dir / "vendors" / f"{vendor_name}.yaml"
        with open(config_path) as f:
            data = yaml.safe_load(f)
        return VendorConfig.model_validate(data)
```

#### Environment Variables

```python
# src/persona/core/config/settings.py
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings from environment variables."""

    # API Keys (from environment)
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    google_ai_api_key: Optional[str] = None

    # Defaults
    default_vendor: str = "openai"
    experiments_dir: str = "experiments"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"  # Allow extra env vars
    }

# Singleton instance
settings = Settings()
```

### Configuration File Examples

**Experiment Config (experiments/my-experiment/config.yaml):**

```yaml
# Persona generation configuration
vendor: openai
model: gpt-4o

# Generation settings
persona_count: 5
temperature: 0.7
max_tokens: 4000

# Prompt template
prompt_template: research-personas
```

**Vendor Config (config/vendors/openai.yaml):**

```yaml
name: openai
api_base: https://api.openai.com/v1
models:
  - gpt-4o
  - gpt-4o-mini
  - gpt-4-turbo
```

### Validation Best Practices

1. **Use `extra="forbid"`** - Catch typos in config files
2. **Provide defaults** - Sensible defaults reduce required config
3. **Validate ranges** - Use `Field(ge=..., le=...)` for numeric bounds
4. **Custom validators** - Business logic validation with `@field_validator`
5. **Clear error messages** - Pydantic provides these automatically

### Rationale

1. **Type Safety** - Catch configuration errors at load time
2. **Documentation** - Pydantic models serve as config documentation
3. **IDE Support** - Autocomplete and type checking
4. **Serialisation** - Easy conversion to/from YAML, JSON
5. **Extensibility** - Easy to add new configuration fields

## Impact on Existing Decisions

### ADR Updates Required

**ADR-0006 (YAML Configuration)** should be updated to:
- Specify Pydantic as validation layer
- Document `extra="forbid"` pattern
- Add environment variable handling

### Feature Spec Updates

**F-006 (Experiment Management)** should specify:
- ExperimentConfig schema
- Validation error display

**F-011 (Experiment Configuration)** should specify:
- Full config.yaml schema
- Default values

## Sources

- [Pydantic YAML Configuration Guide](https://betterprogramming.pub/validating-yaml-configs-made-easy-with-pydantic-594522612db5)
- [Pydantic Settings Documentation](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [How to Validate Config YAML with Pydantic](https://www.sarahglasmacher.com/how-to-validate-config-yaml-pydantic/)
- [Simple Guide to Pydantic + YAML](https://medium.com/@jonathan_b/a-simple-guide-to-configure-your-python-project-with-pydantic-and-a-yaml-file-bef76888f366)
- [Leveraging Pydantic for Validation](https://medium.com/datamindedbe/leveraging-pydantic-for-validation-daf2d51e0627)

---

## Related Documentation

- [ADR-0006: YAML Configuration](../decisions/adrs/ADR-0006-yaml-configuration.md)
- [F-006: Experiment Management](../roadmap/features/completed/F-006-experiment-management.md)
- [F-012: Experiment Configuration](../roadmap/features/completed/F-012-experiment-configuration.md)
