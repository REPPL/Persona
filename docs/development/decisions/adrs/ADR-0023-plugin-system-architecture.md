# ADR-0023: Plugin System Architecture

## Status

Accepted

## Context

Persona v1.2.0 needed an extensibility mechanism allowing users and third parties to:
- Add custom output formatters
- Add custom data loaders
- Add custom LLM providers
- Add custom validators
- Add custom workflows

The extension mechanism needed to:
- Work without modifying Persona's core code
- Be discoverable at runtime
- Follow Python ecosystem conventions
- Support both installed packages and local development

## Decision

Implement a plugin system using **Python entry points** (setuptools entry_points specification):

### Plugin Categories

```python
# pyproject.toml entry point groups
[project.entry-points."persona.formatters"]
my_formatter = "my_package:MyFormatter"

[project.entry-points."persona.loaders"]
my_loader = "my_package:MyLoader"

[project.entry-points."persona.providers"]
my_provider = "my_package:MyProvider"

[project.entry-points."persona.validators"]
my_validator = "my_package:MyValidator"

[project.entry-points."persona.workflows"]
my_workflow = "my_package:MyWorkflow"
```

### Discovery Mechanism

```python
from importlib.metadata import entry_points

def discover_plugins(group: str) -> dict[str, type]:
    """Discover all plugins in a group."""
    plugins = {}
    eps = entry_points(group=f"persona.{group}")
    for ep in eps:
        try:
            plugins[ep.name] = ep.load()
        except Exception as e:
            logger.warning(f"Failed to load plugin {ep.name}: {e}")
    return plugins
```

### Plugin Base Classes

Each category has an abstract base class:

```python
class FormatterPlugin(ABC):
    @abstractmethod
    def format(self, personas: list[Persona]) -> str: ...

class LoaderPlugin(ABC):
    @abstractmethod
    def load(self, path: Path) -> LoadedData: ...

class ProviderPlugin(LLMProvider):
    # Inherits from existing provider interface
    pass

class ValidatorPlugin(ABC):
    @abstractmethod
    def validate(self, persona: Persona) -> list[ValidationIssue]: ...

class WorkflowPlugin(ABC):
    @abstractmethod
    def execute(self, config: WorkflowConfig) -> list[Persona]: ...
```

## Consequences

**Positive:**
- Standard Python pattern (familiar to developers)
- Automatic discovery (no registration code needed)
- Namespace isolation (plugins can have any package structure)
- Pip-installable (easy distribution)
- Local development supported (editable installs)

**Negative:**
- Requires package installation (can't just drop a file)
- Entry point changes need reinstall
- No runtime plugin loading/unloading
- Error handling needed for malformed plugins

## Alternatives Considered

### File-Based Discovery

**Description:** Scan a plugins directory for Python files.
**Pros:** Simple, no installation needed.
**Cons:** Security risks, no dependency management, non-standard.
**Why Not Chosen:** Security and maintainability concerns.

### Decorator Registration

**Description:** Use decorators to register plugins at import time.
**Pros:** Explicit, easy to understand.
**Cons:** Requires import of all potential plugins, circular import risks.
**Why Not Chosen:** Entry points handle discovery better.

### Configuration-Based

**Description:** List plugins in configuration file.
**Pros:** Explicit control over what's loaded.
**Cons:** Manual maintenance, doesn't leverage Python packaging.
**Why Not Chosen:** Entry points are more Pythonic.

### Namespace Packages

**Description:** Use namespace packages (persona_plugins.formatters).
**Pros:** Structured, discoverable.
**Cons:** More complex packaging, still needs discovery mechanism.
**Why Not Chosen:** Entry points are simpler and sufficient.

## Implementation Details

### Plugin Loading Order

1. Built-in plugins loaded first
2. Installed plugins discovered via entry points
3. Name conflicts: installed plugins override built-ins (with warning)

### Error Handling

```python
def safe_load_plugin(ep: EntryPoint) -> type | None:
    """Load plugin with error handling."""
    try:
        plugin_class = ep.load()
        if not issubclass(plugin_class, expected_base):
            logger.warning(f"Plugin {ep.name} does not inherit from {expected_base}")
            return None
        return plugin_class
    except ImportError as e:
        logger.warning(f"Plugin {ep.name} has missing dependencies: {e}")
        return None
    except Exception as e:
        logger.error(f"Failed to load plugin {ep.name}: {e}")
        return None
```

### Plugin CLI

```bash
# List installed plugins
persona plugin list

# Show plugin details
persona plugin show my_formatter

# Verify plugin compatibility
persona plugin verify my_package
```

---

## Related Documentation

- [F-107: Plugin System](../../roadmap/features/completed/F-107-plugin-system.md)
- [Python Entry Points Specification](https://packaging.python.org/en/latest/specifications/entry-points/)
- [ADR-0013: Formatter Registry Pattern](./ADR-0013-formatter-registry.md)
