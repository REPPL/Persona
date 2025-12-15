# F-055: Configuration Validation

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-002, UC-003 |
| **Milestone** | v0.6.0 |
| **Priority** | P1 |
| **Category** | Validation |

## Problem Statement

Invalid configuration causes runtime errors that are difficult to debug. Users need early, clear feedback when configuration is incorrect.

## Design Approach

- Validate configuration at load time
- Use JSON Schema for YAML validation
- Provide detailed error messages with fix suggestions
- Support configuration linting command
- Validate cross-references between configs

### Validation Layers

```
┌─────────────────────────────────────┐
│ Layer 1: Schema Validation          │
│ (Structure, types, required fields) │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│ Layer 2: Semantic Validation        │
│ (Valid values, ranges, patterns)    │
└────────────────┬────────────────────┘
                 ↓
┌─────────────────────────────────────┐
│ Layer 3: Cross-Reference Validation │
│ (Model exists, provider configured) │
└─────────────────────────────────────┘
```

### CLI Interface

```bash
# Validate all configuration
persona config validate

# Validate specific file
persona config validate --file vendors.yaml

# Show detailed validation report
persona config validate --verbose
```

## Implementation Tasks

- [ ] Create JSON schemas for all config types
- [ ] Implement ConfigValidator class
- [ ] Add schema validation layer
- [ ] Add semantic validation layer
- [ ] Add cross-reference validation
- [ ] Create `persona config validate` command
- [ ] Generate helpful error messages
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] All configs validated at load
- [ ] Clear error messages with line numbers
- [ ] Suggestions for common mistakes
- [ ] Cross-reference validation works
- [ ] Test coverage ≥ 80%

## Dependencies

- F-012: Experiment configuration
- F-043: Custom vendor configuration

---

## Related Documentation

- [Milestone v0.6.0](../../milestones/v0.6.0.md)
- [Configuration Reference](../../../reference/configuration-reference.md)

