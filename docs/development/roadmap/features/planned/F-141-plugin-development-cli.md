# F-141: Plugin Development CLI

## Overview

| Attribute | Value |
|-----------|-------|
| **Feature ID** | F-141 |
| **Title** | Plugin Development CLI |
| **Priority** | P0 (Critical) |
| **Category** | Developer Experience |
| **Milestone** | [v1.13.0](../../milestones/v1.13.0.md) |
| **Status** | 📋 Planned |
| **Dependencies** | F-107 (Plugin System) |

---

## Problem Statement

Plugin developers currently have to:
- Manually create project structure from scratch
- Guess at required interface implementations
- Install plugins to test them
- Figure out documentation format themselves

This friction reduces plugin ecosystem growth and increases support burden.

---

## Design Approach

Provide comprehensive CLI tooling for the entire plugin development lifecycle.

### Command Structure

```
persona plugin
├── create    # Scaffold new plugin project
├── validate  # Validate plugin implementation
├── test      # Run plugin tests locally
├── docs      # Generate plugin documentation
└── list      # List installed plugins
```

---

## Key Capabilities

### 1. Plugin Scaffolding

Create new plugin projects from templates.

```bash
# Create formatter plugin
persona plugin create my-formatter --type formatter

# Create with custom template
persona plugin create my-loader --type loader --template advanced

# Interactive mode
persona plugin create
```

**Generated Structure:**
```
my-formatter/
├── pyproject.toml
├── README.md
├── src/
│   └── my_formatter/
│       ├── __init__.py
│       ├── formatter.py
│       └── py.typed
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_formatter.py
└── examples/
    └── usage.py
```

**Generated pyproject.toml:**
```toml
[project]
name = "persona-formatter-my-formatter"
version = "0.1.0"
description = "Custom formatter for Persona"
requires-python = ">=3.12"
dependencies = ["persona>=1.13.0"]

[project.entry-points."persona.formatters"]
my_formatter = "my_formatter:MyFormatter"

[project.optional-dependencies]
dev = ["pytest", "pytest-cov", "persona[dev]"]
```

### 2. Plugin Validation

Validate plugin implementation against interface requirements.

```bash
# Validate plugin directory
persona plugin validate ./my-formatter

# Validate installed plugin
persona plugin validate my-formatter

# Verbose output
persona plugin validate ./my-formatter --verbose
```

**Output:**
```
Validating plugin: my-formatter
Type: formatter

Interface Checks
────────────────
✅ Has 'name' attribute
✅ Has 'file_extension' attribute
✅ Has 'format' method
✅ 'format' accepts 'persona' parameter
✅ 'format' returns string

Type Checks
───────────
✅ Type annotations present
✅ Return types specified
⚠️ Missing docstrings (optional)

Smoke Tests
───────────
✅ format() returns valid output
✅ Output is non-empty string

Result: PASSED (2 warnings)
```

### 3. Local Plugin Testing

Test plugins without installation.

```bash
# Run plugin tests
persona plugin test ./my-formatter

# Run with coverage
persona plugin test ./my-formatter --coverage

# Run specific test
persona plugin test ./my-formatter -k test_format
```

**Features:**
- Temporary plugin installation
- Access to `persona.testing` fixtures
- Coverage reporting
- Integration test support

### 4. Documentation Generation

Generate documentation from plugin code.

```bash
# Generate README
persona plugin docs ./my-formatter --output README.md

# Generate API reference
persona plugin docs ./my-formatter --format api --output docs/api.md
```

**Generated Documentation:**
```markdown
# my-formatter

Custom formatter for Persona.

## Installation

```bash
pip install persona-formatter-my-formatter
```

## Usage

```python
from persona import Persona

# The formatter is automatically available
persona.export("output.myfmt")
```

## Configuration

```yaml
formatters:
  my_formatter:
    option1: value1
```

## API Reference

### MyFormatter

**Attributes:**
- `name`: "my_formatter"
- `file_extension`: ".myfmt"

**Methods:**
- `format(persona: dict) -> str`: Format persona to string
```

---

## CLI Commands

```bash
# Scaffolding
persona plugin create NAME --type TYPE [--template TEMPLATE]
persona plugin create NAME --interactive

# Validation
persona plugin validate PATH|NAME [--verbose] [--strict]

# Testing
persona plugin test PATH [--coverage] [-k PATTERN]

# Documentation
persona plugin docs PATH [--output FILE] [--format readme|api]

# Management
persona plugin list [--type TYPE]
persona plugin info NAME
```

---

## Implementation Tasks

### Phase 1: Scaffolding
- [ ] Create template system (Cookiecutter-based)
- [ ] Implement formatter template
- [ ] Implement loader template
- [ ] Implement validator template
- [ ] Implement provider template
- [ ] Implement workflow template
- [ ] Add interactive mode

### Phase 2: Validation
- [ ] Create interface schemas
- [ ] Implement attribute checks
- [ ] Implement method signature checks
- [ ] Implement type annotation checks
- [ ] Add smoke tests
- [ ] Create validation reporter

### Phase 3: Testing
- [ ] Implement temporary installation
- [ ] Integrate with pytest
- [ ] Add coverage support
- [ ] Create integration test harness

### Phase 4: Documentation
- [ ] Implement docstring extraction
- [ ] Create README generator
- [ ] Create API reference generator
- [ ] Add configuration documentation

---

## Success Criteria

- [ ] `persona plugin create` generates working project
- [ ] Generated plugins pass validation out of box
- [ ] `persona plugin validate` catches interface violations
- [ ] `persona plugin test` runs tests without installation
- [ ] `persona plugin docs` generates useful documentation
- [ ] Templates available for all plugin types
- [ ] Test coverage >= 85%

---

## Configuration

```yaml
plugins:
  development:
    templates:
      directory: null  # Use built-in
      custom:
        my_template: ./templates/my_template
    validation:
      strict: false
      smoke_tests: true
    testing:
      coverage_threshold: 80
```

---

## Related Documentation

- [v1.13.0 Milestone](../../milestones/v1.13.0.md)
- [F-107: Plugin System](../completed/F-107-plugin-system.md)
- [F-144: Plugin Testing Utilities](F-144-plugin-testing-utilities.md)
- [R-027: Plugin Development Patterns](../../../research/R-027-plugin-development-patterns.md)
- [ADR-0023: Plugin System Architecture](../../../decisions/adrs/ADR-0023-plugin-system-architecture.md)

---

**Status**: Planned
