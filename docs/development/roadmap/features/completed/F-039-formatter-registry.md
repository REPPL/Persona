# F-039: Formatter Registry (Plugin System)

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-006, UC-008 |
| **Milestone** | v0.4.0 |
| **Priority** | P2 |
| **Category** | Output |

## Problem Statement

Teams have unique output requirements (internal templates, design tool formats, custom reporting systems). A fixed set of formatters cannot meet all needs. Users need the ability to add custom formatters.

## Design Approach

- Plugin architecture for output formatters
- Registry pattern for format discovery
- Simple interface for custom formatters
- Auto-discovery of installed formatter plugins

### Plugin Interface

```python
from persona.formatters import BaseFormatter, register

@register("my-custom-format")
class MyCustomFormatter(BaseFormatter):
    def format(self, personas: list[Persona]) -> str:
        # Custom formatting logic
        return formatted_output
```

## Implementation Tasks

- [ ] Design formatter plugin interface
- [ ] Implement FormatterRegistry class
- [ ] Add plugin discovery (entry points)
- [ ] Create base formatter abstract class
- [ ] Migrate existing formatters to plugin system
- [ ] Add `--format custom:<name>` CLI option
- [ ] Document plugin development
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Existing formatters work unchanged
- [ ] Custom formatters discoverable via entry points
- [ ] Clear documentation for plugin development
- [ ] Example custom formatter provided
- [ ] Test coverage ≥ 80%

## Dependencies

- F-005: Output formatting

---

## Related Documentation

- [Milestone v0.4.0](../../milestones/v0.4.0.md)
- [F-005: Output Formatting](F-005-output-formatting.md)

