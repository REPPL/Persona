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

- Use questionary's `select()` and form inputs for multi-field input
- Group settings by category (defaults, budgets, output, logging)
- Validate on submit, show errors inline
- Support both global and project-specific config
- Preview changes before saving

## Implementation Tasks

- [x] Create `persona config edit` command
- [x] Implement form layout with questionary
- [x] Group settings: Defaults, Budgets, Output, Logging
- [x] Add validation for each field type
- [x] Implement preview/diff before save
- [x] Add "Reset to defaults" option
- [x] Handle project vs global configuration
- [x] Write unit tests for config editor
- [x] Document config editing workflow

## Success Criteria

- [x] `persona config edit` opens form-based editor
- [x] All configuration options accessible
- [x] Invalid values rejected with helpful messages
- [x] Changes preview shown before save
- [x] Project-specific config supported (`--project` flag)
- [x] Test coverage ≥ 80%

## Implementation Details

### ConfigEditor Class

The `ConfigEditor` class in `src/persona/ui/interactive.py` provides:

- **Section selection**: Users can edit specific sections (defaults, budgets, output, logging) or all at once
- **Current config display**: Shows current values before editing
- **Section-specific editing**: Each section has appropriate prompts and validation
- **Reset functionality**: Reset all settings to defaults
- **Change preview**: Shows pending changes before applying

### CLI Command

```bash
# Edit global config
persona config edit

# Edit specific section
persona config edit defaults
persona config edit budgets

# Edit project config
persona config edit --project
```

### Editor Flow

```
persona config edit

[Current Configuration displayed]

? Select section to edit:
  > Provider & Model Defaults
    Budget Limits
    Output Preferences
    Logging Settings
    All sections
    Reset to defaults

[Section-specific prompts with current values as defaults]

Changes to apply:
  defaults.provider: openai
  defaults.count: 5

? Apply these changes? (Y/n)

✓ Set defaults.provider = openai
✓ Set defaults.count = 5

Configuration saved!
```

## Configuration Sections

| Section | Fields |
|---------|--------|
| **Defaults** | Provider, model, count, complexity, detail_level |
| **Budgets** | Per-run limit, daily limit, monthly limit |
| **Output** | Format, include_readme, timestamp_folders |
| **Logging** | Level, format |

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
