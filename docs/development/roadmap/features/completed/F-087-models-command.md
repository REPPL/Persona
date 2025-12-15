# F-087: Models Command

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-002 |
| **Milestone** | v1.0.0 |
| **Priority** | P2 |
| **Category** | CLI |

## Problem Statement

Users need to discover available models and their pricing before running `persona cost`. Currently `persona cost` shows all models with pricing, but there's no dedicated way to browse models without providing token counts.

## Design Approach

- Dedicated `persona models` command for model discovery
- Filter by provider
- Show pricing and recommendations
- Highlight configured providers

### Command Interface

```bash
# List all models
persona models

# Filter by provider
persona models --provider anthropic
persona models -p openai

# Show detailed info
persona models --verbose
```

### Output Format

```
anthropic Models:
  claude-opus-4           $15.00/$75.00 per M tokens   (best quality)
  claude-sonnet-4         $3.00/$15.00 per M tokens    (balanced) ✓ default
  claude-3-5-haiku        $1.00/$5.00 per M tokens     (fast/cheap)

openai Models:
  gpt-4o                  $2.50/$10.00 per M tokens
  gpt-4o-mini             $0.15/$0.60 per M tokens     (recommended)
  o1                      $15.00/$60.00 per M tokens   (reasoning)

gemini Models:
  gemini-2.0-flash        $0.10/$0.40 per M tokens     (fast)
  gemini-1.5-pro          $1.25/$5.00 per M tokens

Legend: Input/Output price per million tokens
✓ = default model for provider
```

### JSON Output

```json
{
  "command": "models",
  "version": "0.3.0",
  "providers": {
    "anthropic": {
      "configured": true,
      "models": [
        {
          "name": "claude-sonnet-4",
          "input_price": 3.00,
          "output_price": 15.00,
          "default": true,
          "tags": ["balanced"]
        }
      ]
    }
  }
}
```

## Implementation Tasks

- [x] Create `models` command in CLI
- [x] Add provider filtering option
- [x] Show pricing from cost module
- [x] Indicate default models
- [x] Mark configured providers
- [x] Add `--json` output support
- [x] Write unit tests
- [x] Update CLI reference docs

## Success Criteria

- [x] `persona models` lists all available models
- [x] `--provider` filters by provider
- [x] Pricing displayed clearly
- [x] Default models indicated
- [x] JSON output works
- [x] Test coverage ≥ 80%

## Dependencies

- F-008: CLI interface (Typer)
- F-086: CLI output modes (for `--json`)
- F-017: Cost estimation (for pricing data)

---

## Related Documentation

- [Milestone v1.0.0](../../milestones/v1.0.0.md)
- [CLI Reference](../../../../reference/cli-reference.md)
- [F-086: CLI Output Modes](./F-086-cli-output-modes.md)

---

**Status**: ✅ Complete
