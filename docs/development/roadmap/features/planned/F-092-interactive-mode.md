# F-092: Interactive Mode Flag

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Cases** | UC-001, UC-002, UC-003 |
| **Milestone** | v1.0.0 |
| **Priority** | P1 |
| **Category** | CLI |

## Problem Statement

Users running Persona commands often need to make multiple decisions (provider, model, output format, count). Currently, all options must be specified as command-line flags, which:

- Requires memorising flag names
- Makes typos likely for complex option values
- Provides no guidance for new users
- Cannot show dynamic choices (e.g., available models)

An interactive mode would guide users through choices with arrow-key navigation, autocomplete, and validation.

## Design Approach

- Add global `--interactive` / `-i` flag to all commands
- Use questionary library for prompts (ADR-0022)
- Each command implements an interactive workflow
- Non-interactive flags take precedence over interactive choices
- Fall back to defaults in non-TTY environments

## Implementation Tasks

- [ ] Add `--interactive` / `-i` global flag to Typer app
- [ ] Create `src/persona/cli/interactive.py` module
- [ ] Implement interactive workflow for `generate` command
- [ ] Implement interactive workflow for `experiment create` command
- [ ] Implement interactive workflow for `config` command
- [ ] Add TTY detection (skip interactive in pipes)
- [ ] Add questionary to dependencies
- [ ] Write unit tests for interactive prompts
- [ ] Document interactive mode in help text

## Success Criteria

- [ ] `persona generate -i` launches interactive wizard
- [ ] Arrow keys navigate selection menus
- [ ] Tab completes file paths
- [ ] Non-TTY environments skip interactive prompts
- [ ] Flags override interactive choices
- [ ] Test coverage ≥ 80%

## Interactive Workflows

### Generate Command

```
persona generate -i

? Select LLM provider: (Use arrow keys)
 > Anthropic (Claude)
   OpenAI (GPT)
   Google (Gemini)

? Select model:
 > Claude Sonnet 4 (recommended)
   Claude Opus 4.5
   Claude Haiku 3.5

? Number of personas: 3

? Data file or directory: [autocomplete] ./data/

? Output format:
 > JSON (recommended)
   Markdown
   YAML

? Enable reasoning capture? (Y/n)

Generating 3 personas from ./data/ using claude-sonnet-4...
```

### Config Command

```
persona config -i

? Select provider to configure: (Use arrow keys)
 > anthropic
   openai
   gemini

? API key: [hidden input]

? Default model: claude-sonnet-4

Configuration saved.
```

## Dependencies

- F-008: CLI interface (provides CLI framework)
- F-016: Interactive Rich UI (provides output components)
- ADR-0022: Interactive CLI library (questionary)

---

## Related Documentation

- [ADR-0022: Interactive CLI Library Selection](../../../decisions/adrs/ADR-0022-interactive-cli-library.md)
- [F-016: Interactive Rich UI](../completed/F-016-interactive-rich-ui.md)
- [F-093: TUI Configuration Editor](./F-093-tui-config-editor.md)
- [R-011: Interactive CLI Libraries](../../research/R-011-interactive-cli-libraries.md)
