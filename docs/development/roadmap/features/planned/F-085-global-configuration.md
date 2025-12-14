# F-085: Global Configuration

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-002, UC-003 |
| **Milestone** | v1.0.0 |
| **Priority** | P1 |
| **Category** | Config |

## Problem Statement

Users need default settings that apply to all experiments without repeating configuration. Global configuration reduces boilerplate and ensures consistency.

## Design Approach

- Global config file (~/.persona/config.yaml)
- Layered configuration (global → project → experiment)
- Environment variable overrides
- Config initialisation command
- Migration from older formats

### Configuration Hierarchy

```
Environment Variables (highest priority)
        ↓
Experiment Config (experiment.yaml)
        ↓
Project Config (.persona/config.yaml)
        ↓
Global Config (~/.persona/config.yaml)
        ↓
Built-in Defaults (lowest priority)
```

### Global Configuration File

```yaml
# ~/.persona/config.yaml

# Default provider and model
defaults:
  provider: anthropic
  model: claude-sonnet-4-5-20250929
  complexity: moderate
  detail_level: standard

# Budget limits
budgets:
  per_run: 5.00
  daily: 25.00
  monthly: 100.00

# Output preferences
output:
  format: json
  include_readme: true
  timestamp_folders: true

# Logging
logging:
  level: info
  format: console  # console, json
  file: ~/.persona/logs/persona.log

# Providers (API keys via env vars)
providers:
  anthropic:
    enabled: true
  openai:
    enabled: true
  google:
    enabled: false

# Telemetry (opt-in)
telemetry:
  enabled: false
```

### CLI Commands

```bash
# Initialise global config
persona config init

# Show effective config
persona config show

# Set a value
persona config set defaults.model gpt-5

# Get a value
persona config get defaults.provider

# Reset to defaults
persona config reset
```

### Configuration Merging

```python
def load_config() -> Config:
    """Load configuration with proper precedence."""
    config = Config()

    # Layer 1: Built-in defaults
    config.merge(DEFAULT_CONFIG)

    # Layer 2: Global config
    if GLOBAL_CONFIG_PATH.exists():
        config.merge(load_yaml(GLOBAL_CONFIG_PATH))

    # Layer 3: Project config
    project_config = find_project_config()
    if project_config:
        config.merge(load_yaml(project_config))

    # Layer 4: Experiment config
    if EXPERIMENT_CONFIG_PATH.exists():
        config.merge(load_yaml(EXPERIMENT_CONFIG_PATH))

    # Layer 5: Environment variables
    config.merge(load_env_vars())

    return config
```

## Implementation Tasks

- [ ] Define configuration schema
- [ ] Implement configuration loader
- [ ] Add layered merging
- [ ] Create `persona config` commands
- [ ] Support environment overrides
- [ ] Add config validation
- [ ] Create migration utility
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Global config works correctly
- [ ] Layering precedence correct
- [ ] Environment overrides work
- [ ] Config commands functional
- [ ] Test coverage ≥ 80%

## Dependencies

- F-012: Experiment configuration
- F-055: Configuration validation

---

## Related Documentation

- [Milestone v1.0.0](../../milestones/v1.0.0.md)
- [Configuration Reference](../../../reference/configuration-reference.md)

