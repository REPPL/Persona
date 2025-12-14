# F-082: Built-in Help System

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001 |
| **Milestone** | v1.0.0 |
| **Priority** | P1 |
| **Category** | Docs |

## Problem Statement

Users need immediate access to help without leaving the terminal. A comprehensive built-in help system reduces friction and improves discoverability.

## Design Approach

- Rich help text for all commands
- Examples in help output
- Topic-based help (`persona help topics`)
- Interactive help mode
- Links to documentation

### Help Levels

| Command | Description |
|---------|-------------|
| `persona --help` | Top-level overview |
| `persona generate --help` | Command-specific help |
| `persona help` | Interactive help browser |
| `persona help topics` | List help topics |
| `persona help <topic>` | Topic-specific help |

### Help Topics

```
$ persona help topics

Available Help Topics:
  quickstart     Getting started with Persona
  configuration  Configuring Persona
  providers      LLM provider setup
  experiments    Managing experiments
  generation     Generating personas
  output         Output formats and options
  costs          Understanding costs
  troubleshoot   Common issues and solutions
```

### Rich Help Output

```
$ persona generate --help

 Usage: persona generate [OPTIONS]

 Generate personas from your data.

╭─ Required ─────────────────────────────────────────────╮
│ --from PATH  Data source file or directory [required]  │
╰────────────────────────────────────────────────────────╯
╭─ Generation Options ───────────────────────────────────╮
│ --count INT         Number of personas (default: 3)    │
│ --complexity TEXT   simple, moderate, complex          │
│ --detail TEXT       minimal, standard, detailed        │
╰────────────────────────────────────────────────────────╯
╭─ Model Options ────────────────────────────────────────╮
│ --provider TEXT     anthropic, openai, google          │
│ --model TEXT        Model identifier                   │
╰────────────────────────────────────────────────────────╯

 Examples:
   persona generate --from data.csv
   persona generate --from ./interviews/ --count 5
   persona generate --from data.csv --model gpt-5

 See 'persona help generation' for more details.
```

## Implementation Tasks

- [ ] Enhance Typer help strings
- [ ] Add examples to all commands
- [ ] Create help topics system
- [ ] Implement `persona help` command
- [ ] Add interactive help browser
- [ ] Link to online documentation
- [ ] Add man page generation
- [ ] Write help content
- [ ] Test help accessibility

## Success Criteria

- [ ] All commands have rich help
- [ ] Examples for common tasks
- [ ] Help topics comprehensive
- [ ] Interactive mode works
- [ ] Help text accurate

## Dependencies

- F-008: CLI interface (Typer)

---

## Related Documentation

- [Milestone v1.0.0](../../milestones/v1.0.0.md)
- [CLI Reference](../../../reference/cli-reference.md)

