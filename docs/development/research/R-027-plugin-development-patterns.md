# R-027: Plugin Development Patterns

## Executive Summary

This research analyses best practices for plugin systems in Python CLI applications, focusing on developer experience, discoverability, and safety. The current Persona plugin system uses Python entry points but lacks comprehensive developer guidance. Recommended approach: enhance the plugin API with a development CLI, template scaffolding, validation framework, and comprehensive documentation.

---

## Research Context

| Attribute | Value |
|-----------|-------|
| **ID** | R-027 |
| **Category** | Developer Experience |
| **Status** | Complete |
| **Priority** | P2 |
| **Informs** | v1.13.0 Plugin Development CLI, Plugin documentation |

---

## Problem Statement

Persona's plugin system (F-107) supports extension via entry points, but:
- No CLI tools for plugin scaffolding
- Limited validation of plugin interfaces
- No testing utilities for plugin developers
- Minimal documentation and examples
- No versioning/compatibility checking

For a healthy plugin ecosystem, developers need better tooling and guidance.

---

## State of the Art Analysis

### Plugin Architecture Patterns

#### 1. Entry Points (Current)

```python
# pyproject.toml
[project.entry-points."persona.formatters"]
my_formatter = "my_plugin:MyFormatter"
```

**Pros:**
- Standard Python mechanism
- Lazy loading
- Namespace isolation

**Cons:**
- Requires package installation
- No runtime discovery
- Limited metadata

#### 2. Hook-Based Plugins (pluggy)

```python
import pluggy

hookspec = pluggy.HookspecMarker("persona")
hookimpl = pluggy.HookimplMarker("persona")

class PersonaSpec:
    @hookspec
    def format_persona(self, persona: dict, format: str) -> str:
        """Format a persona for output."""

class MyPlugin:
    @hookimpl
    def format_persona(self, persona: dict, format: str) -> str:
        return json.dumps(persona, indent=2)
```

**Pros:**
- Rich hook specification
- Multiple implementations per hook
- Call ordering control

**Cons:**
- Additional dependency
- Learning curve

#### 3. Protocol-Based Plugins

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class FormatterPlugin(Protocol):
    name: str
    file_extension: str

    def format(self, persona: dict) -> str: ...
    def parse(self, content: str) -> dict: ...
```

**Pros:**
- Type-safe
- IDE support
- Runtime validation

**Cons:**
- Python 3.8+ only
- Structural typing limitations

#### 4. Abstract Base Class Plugins

```python
from abc import ABC, abstractmethod

class BaseFormatter(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def file_extension(self) -> str: ...

    @abstractmethod
    def format(self, persona: dict) -> str: ...
```

**Pros:**
- Clear contract
- IDE support
- Registration hooks

**Cons:**
- Inheritance required
- Less flexible

### Developer Experience Patterns

#### 1. CLI Scaffolding

```bash
# Create new plugin project
persona plugin create my-formatter

# Creates:
# my-formatter/
# ├── pyproject.toml
# ├── src/
# │   └── my_formatter/
# │       ├── __init__.py
# │       └── formatter.py
# └── tests/
#     └── test_formatter.py
```

#### 2. Plugin Validation

```python
class PluginValidator:
    def validate(self, plugin: Any) -> ValidationResult:
        errors = []

        # Check required attributes
        if not hasattr(plugin, "name"):
            errors.append("Plugin must have 'name' attribute")

        # Check required methods
        if not callable(getattr(plugin, "format", None)):
            errors.append("Plugin must have 'format' method")

        # Check method signatures
        sig = inspect.signature(plugin.format)
        if "persona" not in sig.parameters:
            errors.append("format() must accept 'persona' parameter")

        return ValidationResult(valid=len(errors) == 0, errors=errors)
```

#### 3. Testing Utilities

```python
# persona/testing/plugin.py

class PluginTestCase:
    """Base test case for plugin testing."""

    def assert_valid_formatter(self, formatter: BaseFormatter) -> None:
        """Assert formatter implements required interface."""
        assert hasattr(formatter, "name")
        assert hasattr(formatter, "file_extension")
        assert callable(formatter.format)

        # Test with sample persona
        result = formatter.format(self.sample_persona)
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.fixture
    def sample_persona(self) -> dict:
        """Provide sample persona for testing."""
        return {
            "name": "Test User",
            "demographics": {"age": 30},
            "behaviours": ["testing"]
        }
```

#### 4. Compatibility Matrix

```python
@dataclass
class PluginMetadata:
    name: str
    version: str
    persona_version_min: str
    persona_version_max: str | None
    python_version_min: str

    def is_compatible(self, persona_version: str) -> bool:
        return (
            version.parse(persona_version) >= version.parse(self.persona_version_min)
            and (
                self.persona_version_max is None
                or version.parse(persona_version) <= version.parse(self.persona_version_max)
            )
        )
```

### Plugin Categories

| Category | Interface | Example |
|----------|-----------|---------|
| **Formatters** | `format(persona) -> str` | YAML, TOML, custom formats |
| **Loaders** | `load(path) -> list[dict]` | CSV, Excel, API sources |
| **Validators** | `validate(persona) -> Result` | Custom validation rules |
| **Providers** | `generate(prompt) -> str` | Custom LLM integrations |
| **Workflows** | `execute(context) -> Result` | Custom generation pipelines |

---

## Plugin Development Workflow

### Ideal Developer Experience

```
┌─────────────────────────────────────────────────────────────┐
│                 Plugin Development Workflow                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Scaffold                                                 │
│     persona plugin create my-plugin --type formatter        │
│                                                              │
│  2. Develop                                                  │
│     - Implement interface                                    │
│     - Use testing utilities                                  │
│     - Reference examples                                     │
│                                                              │
│  3. Validate                                                 │
│     persona plugin validate ./my-plugin                     │
│                                                              │
│  4. Test                                                     │
│     persona plugin test ./my-plugin                         │
│                                                              │
│  5. Package                                                  │
│     persona plugin build ./my-plugin                        │
│                                                              │
│  6. Publish                                                  │
│     pip install ./my-plugin                                 │
│     # or: twine upload dist/*                               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Evaluation Matrix

| Pattern | DX | Safety | Flexibility | Adoption |
|---------|-------|--------|-------------|----------|
| Entry points only | ⚠️ | ⚠️ | ✅ | ⚠️ |
| + CLI scaffolding | ✅ | ⚠️ | ✅ | ✅ |
| + Validation | ✅ | ✅ | ✅ | ✅ |
| + Testing utils | ✅ | ✅ | ✅ | ✅ |
| + Compatibility | ✅ | ✅ | ⚠️ | ⚠️ |

---

## Recommendation

### Primary: Enhanced Plugin DX

Extend the existing entry point system with comprehensive developer tooling.

### CLI Commands

```bash
# Create plugin from template
persona plugin create <name> --type <formatter|loader|validator|provider|workflow>

# Validate plugin implementation
persona plugin validate <path>

# Run plugin tests
persona plugin test <path>

# Build plugin package
persona plugin build <path>

# List installed plugins
persona plugin list

# Show plugin info
persona plugin info <name>
```

### Template Structure

```
my-plugin/
├── pyproject.toml              # Package configuration
├── README.md                   # Plugin documentation
├── src/
│   └── my_plugin/
│       ├── __init__.py
│       ├── plugin.py           # Main plugin implementation
│       └── py.typed            # PEP 561 marker
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Fixtures from persona.testing
│   └── test_plugin.py          # Plugin tests
└── examples/
    └── usage.py                # Usage examples
```

### Validation Framework

```python
class PluginValidator:
    def __init__(self, plugin_type: str):
        self.plugin_type = plugin_type
        self.schema = self._load_schema(plugin_type)

    def validate(self, plugin: Any) -> ValidationResult:
        checks = [
            self._check_required_attributes,
            self._check_method_signatures,
            self._check_type_annotations,
            self._check_metadata,
            self._run_smoke_test,
        ]

        errors = []
        warnings = []

        for check in checks:
            result = check(plugin)
            errors.extend(result.errors)
            warnings.extend(result.warnings)

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
```

### Testing Utilities

```python
# persona/testing/__init__.py

from persona.testing.fixtures import (
    sample_persona,
    sample_personas,
    sample_input_data,
    mock_provider,
)

from persona.testing.assertions import (
    assert_valid_persona,
    assert_valid_formatter,
    assert_valid_loader,
)

from persona.testing.plugin import (
    PluginTestCase,
    validate_plugin,
)

__all__ = [
    "sample_persona",
    "sample_personas",
    "sample_input_data",
    "mock_provider",
    "assert_valid_persona",
    "assert_valid_formatter",
    "assert_valid_loader",
    "PluginTestCase",
    "validate_plugin",
]
```

### Configuration

```yaml
plugins:
  discovery:
    enabled: true
    namespaces:
      - persona.formatters
      - persona.loaders
      - persona.validators
      - persona.providers
      - persona.workflows

  validation:
    strict: false  # Warn vs error on issues
    check_compatibility: true

  development:
    templates_dir: null  # Use built-in templates
    scaffold_tests: true
    scaffold_examples: true
```

---

## Documentation Structure

```
docs/
├── plugins/
│   ├── README.md               # Plugin overview
│   ├── getting-started.md      # Quick start guide
│   ├── types/
│   │   ├── formatters.md       # Formatter plugin guide
│   │   ├── loaders.md          # Loader plugin guide
│   │   ├── validators.md       # Validator plugin guide
│   │   ├── providers.md        # Provider plugin guide
│   │   └── workflows.md        # Workflow plugin guide
│   ├── reference/
│   │   ├── api.md              # Plugin API reference
│   │   └── testing.md          # Testing utilities reference
│   └── examples/
│       ├── yaml-formatter/     # Example formatter
│       └── csv-loader/         # Example loader
```

---

## Implementation Priority

1. **CLI scaffolding** - `persona plugin create`
2. **Validation framework** - `persona plugin validate`
3. **Testing utilities** - `persona.testing` module
4. **Documentation** - Comprehensive plugin guides
5. **Examples** - Reference implementations

---

## References

1. [Python Entry Points Specification](https://packaging.python.org/en/latest/specifications/entry-points/)
2. [pluggy Documentation](https://pluggy.readthedocs.io/)
3. [pytest Plugin Development](https://docs.pytest.org/en/stable/how-to/writing_plugins.html)
4. [Click Plugin Development](https://click.palletsprojects.com/en/8.1.x/plugins/)
5. [Cookiecutter](https://cookiecutter.readthedocs.io/)

---

## Related Documentation

- [F-107: Plugin System](../roadmap/features/completed/F-107-plugin-system.md)
- [ADR-0023: Plugin System Architecture](../decisions/adrs/ADR-0023-plugin-system-architecture.md)
- [Plugin Guide](../../guides/plugins/)

---

**Status**: Complete
