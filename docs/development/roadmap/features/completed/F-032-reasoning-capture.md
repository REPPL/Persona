# F-032: Reasoning Capture

## Overview

| Attribute | Value |
|-----------|-------|
| **Milestone** | v0.1.0 |
| **Priority** | P0 (Critical - Default behaviour) |
| **Category** | Observability |

## Problem Statement

Research reproducibility requires complete transparency into LLM decision-making. Users cannot currently:
- See why a persona was generated with specific attributes
- Debug differences between runs
- Audit reasoning for stakeholder review
- Reproduce experiments with full context

## Design Approach

### Three-Layer Reasoning Capture

**1. Request Layer**: Capture what was sent
- Final prompt (after template rendering)
- Model parameters (temperature, max_tokens)
- Provider/model identification

**2. Response Layer**: Capture what was received
- Raw LLM response (before parsing)
- Finish reason
- Token usage (input/output/total)
- Latency metrics

**3. Reasoning Layer**: Extract chain-of-thought
- Delimiter-based extraction (if model provides reasoning)
- Step-by-step breakdown
- Confidence indicators (if available)

### Output Structure

```
outputs/20241215_143022/
├── metadata.json           # Generation metadata
├── reasoning/              # Reasoning capture
│   ├── request.json        # Complete request payload
│   ├── response_raw.json   # Raw LLM response
│   ├── reasoning_trace.md  # Extracted chain-of-thought
│   └── metrics.json        # Token usage, latency, cost
├── personas/
│   └── ...
```

### Extraction Strategy

Use delimiter tags in prompts:
- **Claude**: Uses `<thinking>` tags natively
- **OpenAI/Gemini**: Require `<reasoning>` instruction in prompt

## Implementation Tasks

- [ ] Create `reasoning/` output directory structure
- [ ] Implement request payload capture (pre-LLM call)
- [ ] Implement raw response capture (post-LLM call)
- [ ] Add delimiter-based reasoning extraction
- [ ] Create reasoning trace formatter (Markdown)
- [ ] Create metrics JSON writer (tokens, latency, cost)
- [ ] Update prompt templates with reasoning delimiters
- [ ] Add `--verbose` CLI flag for real-time reasoning display
- [ ] Add `--no-reasoning` flag to suppress reasoning files
- [ ] Update output metadata with reasoning file references
- [ ] Write unit tests for extraction logic
- [ ] Write integration tests

## Success Criteria

- [ ] Every generation produces reasoning trace by default
- [ ] Request/response fully captured in JSON
- [ ] Reasoning trace readable by non-technical users
- [ ] Metrics accurate within 1% of actual API usage
- [ ] `--verbose` shows reasoning in terminal
- [ ] Export suitable for stakeholder audit
- [ ] Test coverage ≥ 80%

## Dependencies

- F-004: Persona generation pipeline
- F-002: LLM provider abstraction
- F-003: Prompt templating (for delimiter tags)
- ADR-0020: Reasoning Capture Architecture

---

## Related Documentation

- [R-009: Reasoning Capture](../../../research/R-009-reasoning-capture.md)
- [ADR-0020: Reasoning Capture Architecture](../../../decisions/adrs/ADR-0020-reasoning-capture-architecture.md)
- [ADR-0011: Multi-Step Workflow](../../../decisions/adrs/ADR-0011-multi-step-workflow.md)
- [Reproducibility](../../../../explanation/reproducibility.md)

