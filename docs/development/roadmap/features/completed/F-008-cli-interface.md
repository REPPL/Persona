# F-008: CLI Interface

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Cases** | UC-001, UC-002, UC-003 |
| **Milestone** | v0.1.0 |
| **Priority** | P0 |
| **Category** | CLI |

## Problem Statement

Users need a simple, scriptable CLI to interact with persona generation.

## Design Approach

- Typer for CLI framework
- Rich for beautiful output
- Structured command groups
- Consistent error handling

## Implementation Tasks

- [ ] Set up Typer application
- [ ] Implement generate command
- [ ] Implement experiment commands:
  - [ ] create
  - [ ] list
  - [ ] show
  - [ ] delete
- [ ] Implement check command
- [ ] Add Rich progress bars
- [ ] Add --help for all commands
- [ ] Write CLI integration tests

## Success Criteria

- [ ] All commands work as documented
- [ ] --help shows useful information
- [ ] Errors displayed clearly with suggestions
- [ ] Progress feedback during long operations
- [ ] Test coverage ≥ 80%

## Command Structure

```
persona
├── generate           # Generate personas
│   └── --from         # Data source (experiment/file/folder)
├── create experiment  # Create new experiment
├── list experiments   # List all experiments
├── show experiment    # Show experiment details
├── delete experiment  # Delete experiment
└── check              # System health check
```

---

## Related Documentation

- [All Use Cases](../../../../use-cases/)
- [ADR-0005: CLI Framework](../../../../decisions/adrs/ADR-0005-cli-framework.md)
