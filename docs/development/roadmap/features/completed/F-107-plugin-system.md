# F-107: Plugin System

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001, UC-006 |
| **Milestone** | v1.2.0 |
| **Priority** | P1 |
| **Category** | Core |

## Problem Statement

Persona needs extensibility to support:
- Custom output formatters beyond built-in JSON/Markdown/Text
- Additional data loaders for proprietary formats
- Third-party LLM providers not included in core
- Custom validators for domain-specific requirements

Without a plugin architecture, users must fork the codebase to add extensions.

## Design Approach

Entry point-based plugin discovery system with unified registry architecture:

1. **PluginRegistry base class** - Generic registry for all plugin types
2. **Entry point groups** - Standard Python entry points for discovery
3. **PluginManager** - Central orchestrator for all registries
4. **CLI interface** - Commands for listing, inspecting, and managing plugins

### Plugin Types

| Type | Entry Point Group | Description |
|------|-------------------|-------------|
| Formatter | `persona.formatters` | Output format converters |
| Loader | `persona.loaders` | Data file readers |
| Provider | `persona.providers` | LLM API integrations |
| Validator | `persona.validators` | Persona validation rules |
| Workflow | `persona.workflows` | Generation workflows |

### Plugin Registration

```python
# Via entry points (pyproject.toml)
[project.entry-points."persona.formatters"]
html = "my_package:HTMLFormatter"

# Via code (built-in plugins)
registry.register(
    name="json",
    plugin_class=JSONFormatter,
    description="JSON format",
    builtin=True,
)
```

### CLI Commands

```bash
# List all plugins
persona plugin list
persona plugin list --type formatter

# Get plugin info
persona plugin info json --type formatter

# Show summary
persona plugin summary

# Verify plugins load correctly
persona plugin check

# Reload all plugins
persona plugin reload
```

## Implementation

### Module Structure

```
src/persona/core/plugins/
├── __init__.py           # Public API exports
├── base.py               # PluginInfo, PluginRegistry, PluginType
├── discovery.py          # Entry point discovery
├── exceptions.py         # Plugin-specific exceptions
├── manager.py            # PluginManager orchestrator
└── registries.py         # Concrete registry implementations
```

### Key Components

**PluginInfo dataclass**: Metadata about a registered plugin including name, description, type, version, and status.

**PluginRegistry[T]**: Generic base class with methods for register, unregister, get, list, enable/disable.

**PluginManager**: Central coordinator that holds all registries and provides unified access.

**Entry point discovery**: Uses `importlib.metadata` to discover plugins from installed packages.

### Concrete Registries

- **FormatterPluginRegistry**: Built-in json, markdown, text formatters
- **LoaderPluginRegistry**: Built-in csv, json, yaml, markdown, text, html, org loaders
- **ProviderPluginRegistry**: Built-in openai, anthropic, gemini providers
- **ValidatorPluginRegistry**: Built-in persona validator

## Success Criteria

- [x] PluginRegistry base class with generic type support
- [x] Entry point discovery via importlib.metadata
- [x] PluginManager orchestrating all registries
- [x] CLI commands: list, info, summary, check, reload
- [x] Built-in plugins registered as formatters, loaders, providers, validators
- [x] pyproject.toml entry point groups defined
- [x] Unit tests (33 tests, 100% pass)
- [x] Backward compatible with existing API

## Dependencies

- F-039: Formatter registry (pattern to extend)
- F-043: Custom vendor configuration (provider registry)

---

## Related Documentation

- [Milestone: v1.2.0](../../milestones/v1.2.0.md)
- [Manual Tests: Plugin System](../../../../../tests/manual/plugin_system_test_script.md)

---

**Status**: Complete
