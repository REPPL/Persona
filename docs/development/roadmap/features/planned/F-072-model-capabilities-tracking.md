# F-072: Model Capabilities Tracking

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-003, UC-004 |
| **Milestone** | v0.8.0 |
| **Priority** | P2 |
| **Category** | Config |

## Problem Statement

Different models have different capabilities (context window, structured output, vision, etc.). Users need this information to select appropriate models for their use case.

## Design Approach

- Track capabilities per model
- Support capability queries
- Warn on capability mismatches
- Suggest alternative models
- Display capabilities in model list

### Capability Categories

```yaml
# models.yaml
claude-sonnet-4-5-20250929:
  capabilities:
    context_window: 200000
    max_output: 8192
    structured_output: true
    vision: true
    function_calling: true
    streaming: true
    extended_thinking: false
    batch_api: true

  strengths:
    - coding
    - analysis
    - instruction_following

  best_for:
    - "Complex persona generation"
    - "Code-related personas"
    - "Technical analysis"
```

### Capability Queries

```bash
# List models with specific capability
persona model list --capability vision
persona model list --capability "context_window>=1000000"

# Check if model supports use case
persona model check gpt-5 --use-case "large dataset"

# Compare capabilities
persona model compare claude-sonnet-4-5 gpt-5 gemini-3.0-pro
```

### Capability Display

```
📋 Model Capabilities: claude-sonnet-4-5-20250929

Context & Output:
  Context window:    200,000 tokens
  Max output:        8,192 tokens
  Extended context:  1M (beta)

Features:
  ✓ Structured output (JSON mode)
  ✓ Vision (image analysis)
  ✓ Function calling
  ✓ Streaming
  ✗ Extended thinking

Best For:
  • Complex persona generation
  • Code-related personas
  • Technical analysis
```

## Implementation Tasks

- [ ] Define capability schema
- [ ] Add capabilities to model configs
- [ ] Create CapabilityChecker class
- [ ] Implement capability queries
- [ ] Add mismatch warnings
- [ ] Implement model comparison
- [ ] Create `persona model compare` command
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] All models have capability data
- [ ] Queries work correctly
- [ ] Warnings shown for mismatches
- [ ] Comparison output clear
- [ ] Test coverage ≥ 80%

## Dependencies

- F-044: Custom model configuration
- F-056: Model availability checking

---

## Related Documentation

- [Milestone v0.8.0](../../milestones/v0.8.0.md)
- [Model Cards](../../../reference/model-cards.md)
- [Configuration Reference](../../../reference/configuration-reference.md)

