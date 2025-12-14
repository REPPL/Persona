# F-093: TUI Configuration Editor

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Cases** | UC-001 |
| **Milestone** | v1.0.0 |
| **Priority** | P2 |
| **Category** | CLI |

## Problem Statement

Editing Persona configuration requires manually editing YAML files or remembering multiple `config set` commands. Users need:

- Visual overview of all configuration options
- Inline editing without leaving the terminal
- Validation before saving
- Easy navigation between settings

A form-based TUI editor provides these capabilities.

## Design Approach

- Use questionary's `form()` for multi-field input
- Group settings by category (providers, defaults, output)
- Validate on submit, show errors inline
- Support both global and experiment-specific config
- Preview changes before saving

## Implementation Tasks

- [ ] Create `persona config edit` command
- [ ] Implement form layout with questionary
- [ ] Group settings: Providers, Defaults, Output, Logging
- [ ] Add validation for each field type
- [ ] Implement preview/diff before save
- [ ] Add "Reset to defaults" option
- [ ] Handle nested configuration (provider-specific settings)
- [ ] Write unit tests for config editor
- [ ] Document config editing workflow

## Success Criteria

- [ ] `persona config edit` opens form-based editor
- [ ] All configuration options accessible
- [ ] Invalid values rejected with helpful messages
- [ ] Changes preview shown before save
- [ ] Experiment-specific config supported
- [ ] Test coverage ≥ 80%

## Editor Layout

```
persona config edit --interactive

┌─ Persona Configuration ─────────────────────────────────────────┐
│                                                                 │
│ Provider Settings                                               │
│ ─────────────────                                               │
│ Default Provider:    ▾ [anthropic]                             │
│ Default Model:       ▾ [claude-sonnet-4-20250514]              │
│                                                                 │
│ Output Settings                                                 │
│ ──────────────                                                  │
│ Default Format:      ▾ [json]                                  │
│ Persona Count:       [3     ]                                  │
│ Include Reasoning:   [x] Yes                                   │
│                                                                 │
│ Advanced                                                        │
│ ────────                                                        │
│ Temperature:         [0.7   ]                                  │
│ Max Tokens:          [4096  ]                                  │
│                                                                 │
│   [Save]        [Cancel]        [Reset Defaults]               │
└─────────────────────────────────────────────────────────────────┘
```

## Configuration Sections

| Section | Fields |
|---------|--------|
| **Provider** | Default provider, API keys (masked), models |
| **Output** | Format, directory, timestamping |
| **Generation** | Persona count, temperature, reasoning |
| **Logging** | Level, format, file path |

## Dependencies

- F-092: Interactive mode flag (provides `-i` flag)
- F-085: Global configuration (provides config schema)
- ADR-0022: Interactive CLI library (questionary)

---

## Related Documentation

- [F-092: Interactive Mode Flag](./F-092-interactive-mode.md)
- [F-085: Global Configuration](./F-085-global-configuration.md)
- [ADR-0022: Interactive CLI Library Selection](../../../decisions/adrs/ADR-0022-interactive-cli-library.md)
- [Configuration Reference](../../../../reference/configuration-reference.md)
