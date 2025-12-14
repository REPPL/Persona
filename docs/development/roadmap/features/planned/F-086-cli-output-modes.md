# F-086: CLI Output Modes

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001, UC-002, UC-003 |
| **Milestone** | v0.3.0 |
| **Priority** | P1 |
| **Category** | CLI |

## Problem Statement

Users need control over CLI output for different contexts: accessibility (colour blindness), CI/CD pipelines (machine-readable), and scripting (minimal output). Currently all output uses Rich formatting with no alternatives.

## Design Approach

- Global flags affecting all command output
- Respect environment variables (NO_COLOR standard)
- JSON output for machine parsing
- Quiet mode for scripting
- Verbose mode for debugging

### Global Flags

```bash
# Disable colour output
persona --no-color check
NO_COLOR=1 persona check

# JSON output (machine-readable)
persona check --json
persona cost --json
persona experiment list --json

# Quiet mode (minimal output)
persona --quiet generate --from data.csv
persona -q check

# Verbose mode (debug info)
persona -v generate --from data.csv
persona -vv check  # Extra verbose
```

### NO_COLOR Standard

Following [no-color.org](https://no-color.org/):

```python
import os
from rich.console import Console

def get_console() -> Console:
    """Get console with colour settings from environment."""
    no_color = os.environ.get("NO_COLOR") is not None
    return Console(no_color=no_color, width=min(100, Console().width))
```

### JSON Output Format

```json
{
  "command": "check",
  "version": "0.2.0",
  "success": true,
  "data": {
    "installation": "ok",
    "providers": {
      "anthropic": {"configured": false, "env_var": "ANTHROPIC_API_KEY"},
      "openai": {"configured": false, "env_var": "OPENAI_API_KEY"},
      "gemini": {"configured": false, "env_var": "GOOGLE_API_KEY"}
    }
  }
}
```

### Verbosity Levels

| Level | Flag | Output |
|-------|------|--------|
| Quiet | `-q`, `--quiet` | Errors and final result only |
| Normal | (default) | Standard output |
| Verbose | `-v`, `--verbose` | Additional context |
| Debug | `-vv` | Full debug information |

## Implementation Tasks

- [x] Add `--no-color` global flag
- [x] Respect NO_COLOR environment variable
- [x] Add `--json` flag to `check` command
- [x] Add `--quiet` global flag
- [x] Create shared console module (`persona.ui.console`)
- [ ] Add `--json` flag to `cost` command
- [ ] Add `--json` flag to `experiment list`
- [ ] Add `--verbose` flag
- [ ] Implement verbosity levels throughout CLI
- [ ] Write unit tests
- [ ] Write integration tests
- [ ] Update CLI documentation

## Success Criteria

- [ ] NO_COLOR environment variable respected
- [ ] `--no-color` disables all colour output
- [ ] `--json` produces valid, parseable JSON
- [ ] `--quiet` reduces output to minimum
- [ ] Flags work with all commands
- [ ] Test coverage ≥ 80%

## Dependencies

- F-008: CLI interface (Typer)
- F-016: Interactive Rich UI

---

## Related Documentation

- [Milestone v0.3.0](../../milestones/v0.3.0.md)
- [NO_COLOR Standard](https://no-color.org/)
- [CLI Reference](../../../reference/cli-reference.md)
