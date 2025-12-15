# F-015: CLI Core Commands

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Cases** | UC-001, UC-002, UC-003 |
| **Milestone** | v0.1.0 |
| **Priority** | P0 |
| **Category** | CLI |

## Problem Statement

Users need a consistent, discoverable set of CLI commands to interact with persona generation. The command structure must be intuitive, support common workflows, and provide clear feedback.

## Design Approach

- Verb-noun command structure (e.g., `create experiment`)
- Consistent flag naming across commands
- Required arguments positional, optional via flags
- Clear error messages with suggestions
- Exit codes following conventions (0=success, 1=error)

## Implementation Tasks

- [ ] Implement `persona check` command
- [ ] Implement `persona create experiment` command
- [ ] Implement `persona list experiments` command
- [ ] Implement `persona show experiment <name>` command
- [ ] Implement `persona delete experiment <name>` command
- [ ] Implement `persona generate --from <source>` command
- [ ] Add `--verbose` flag for all commands
- [ ] Add `--quiet` flag for scriptable output
- [ ] Implement proper exit codes
- [ ] Write integration tests for all commands

## Success Criteria

- [ ] All documented commands implemented
- [ ] Commands discoverable via `--help`
- [ ] Error messages include suggested fixes
- [ ] Exit codes usable in scripts
- [ ] Test coverage ≥ 80%

## Command Reference

| Command | Arguments | Description |
|---------|-----------|-------------|
| `check` | none | Verify installation and configuration |
| `create experiment` | `<name>` | Create new experiment directory |
| `list experiments` | none | List all experiments |
| `show experiment` | `<name>` | Display experiment details |
| `delete experiment` | `<name>` | Remove experiment |
| `generate` | `--from <source>` | Generate personas from data |

## Dependencies

- F-008: CLI interface (provides framework)
- F-006: Experiment management (experiment commands)

---

## Related Documentation

- [F-008: CLI Interface](F-008-cli-interface.md)
- [UC-001: Generate Personas](../../../../use-cases/briefs/UC-001-generate-personas.md)
- [UC-002: Manage Experiments](../../../../use-cases/briefs/UC-002-manage-experiments.md)
- [ADR-0005: CLI Framework](../../../../decisions/adrs/ADR-0005-cli-framework.md)

