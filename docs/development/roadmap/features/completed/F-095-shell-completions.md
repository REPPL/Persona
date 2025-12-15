# F-095: Shell Completions

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Cases** | UC-001, UC-002, UC-003 |
| **Milestone** | v1.0.0 |
| **Priority** | P3 |
| **Category** | CLI |

## Problem Statement

Users must type full command names, option flags, and argument values. This leads to:

- Slower command entry
- Typos in long option names
- Difficulty discovering available commands
- No help for valid argument values

Shell completions enable Tab completion for commands, options, and arguments.

## Design Approach

- Use Typer's built-in completion support
- Generate completions for bash, zsh, fish, PowerShell
- Add custom completers for dynamic values (models, providers)
- Support file path completion for data arguments
- Include completion installation command

## Implementation Tasks

- [x] Enable Typer's completion generation
- [x] Create installation command: `persona --install-completion`
- [x] Add custom completer for `--provider` (anthropic, openai, gemini)
- [x] Add custom completer for `--model` (dynamic per provider)
- [x] Add custom completer for `--format` (json, markdown, yaml)
- [x] Add file path completion for `--from` argument
- [x] Test completions in bash, zsh, fish
- [x] Document shell completion setup
- [x] Add completion to installation guide

## Success Criteria

- [x] Tab completes command names
- [x] Tab completes option flags
- [x] Tab completes known option values
- [x] File paths complete for data arguments
- [x] Works in bash, zsh, fish, PowerShell
- [x] Installation documented and tested

## Completion Examples

### Command Completion

```bash
$ persona gen<TAB>
$ persona generate

$ persona exp<TAB>
$ persona experiment
```

### Option Completion

```bash
$ persona generate --<TAB>
--from       --provider   --model      --count
--format     --output     --verbose    --help

$ persona generate --pro<TAB>
$ persona generate --provider
```

### Value Completion

```bash
$ persona generate --provider <TAB>
anthropic    openai    gemini

$ persona generate --provider anthropic --model <TAB>
claude-sonnet-4-20250514    claude-opus-4-5-20251101    claude-haiku-3-5-20241022

$ persona generate --format <TAB>
json    markdown    yaml
```

### Path Completion

```bash
$ persona generate --from ./da<TAB>
$ persona generate --from ./data/

$ persona generate --from ./data/inter<TAB>
$ persona generate --from ./data/interviews.csv
```

## Shell Setup

### Bash

```bash
# Add to ~/.bashrc
eval "$(persona --show-completion bash)"

# Or install permanently
persona --install-completion bash
```

### Zsh

```bash
# Add to ~/.zshrc
eval "$(persona --show-completion zsh)"

# Or install permanently
persona --install-completion zsh
```

### Fish

```fish
# Install permanently
persona --install-completion fish
```

### PowerShell

```powershell
# Add to $PROFILE
persona --show-completion powershell | Out-String | Invoke-Expression

# Or install permanently
persona --install-completion powershell
```

## Custom Completers

```python
# src/persona/cli/completers.py

from typing import Iterator

def complete_provider(incomplete: str) -> Iterator[str]:
    """Complete provider names."""
    providers = ["anthropic", "openai", "gemini"]
    for p in providers:
        if p.startswith(incomplete):
            yield p

def complete_model(ctx, incomplete: str) -> Iterator[str]:
    """Complete model names based on selected provider."""
    provider = ctx.params.get("provider", "anthropic")
    models = get_models_for_provider(provider)
    for m in models:
        if m.id.startswith(incomplete):
            yield m.id

def complete_format(incomplete: str) -> Iterator[str]:
    """Complete output format names."""
    formats = ["json", "markdown", "yaml"]
    for f in formats:
        if f.startswith(incomplete):
            yield f
```

## Dependencies

- F-008: CLI interface (provides Typer app)
- F-011: Multi-provider LLM support (provides model lists)

---

## Related Documentation

- [F-008: CLI Interface](./F-008-cli-interface.md)
- [ADR-0005: Typer + Rich CLI Framework](../../../decisions/adrs/ADR-0005-cli-framework.md)
- [CLI Reference](../../../../../reference/cli-reference.md)

---

**Status**: Complete
