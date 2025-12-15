# F-062: Context Window Awareness

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-003, UC-004 |
| **Milestone** | v0.7.0 |
| **Priority** | P0 |
| **Category** | LLM |

## Problem Statement

LLMs have context window limits. Exceeding these limits causes failures or truncated outputs. Users need warnings before hitting limits and strategies for handling large datasets.

## Design Approach

- Track token count during generation
- Warn when approaching context limit
- Suggest chunking strategies for large data
- Support automatic data chunking
- Reserve space for output tokens

### Context Budget

```
┌─────────────────────────────────────────┐
│           Total Context Window          │
│              (e.g., 200K)               │
├─────────────────────────────────────────┤
│ System Prompt │  Input Data  │ Reserved │
│   (~2-5K)     │  (variable)  │ for Output│
│               │              │  (~10-20K)│
└─────────────────────────────────────────┘
```

### Warning Thresholds

| Usage | Level | Action |
|-------|-------|--------|
| < 70% | Green | Continue |
| 70-85% | Yellow | Warning displayed |
| 85-95% | Orange | Strong warning + suggestions |
| > 95% | Red | Block or require confirmation |

### CLI Output

```
⚠️  Context Usage Warning
   Model: claude-sonnet-4-5-20250929 (200K context)
   Current usage: 172,000 tokens (86%)

   Breakdown:
   - System prompt: 3,200 tokens
   - Input data: 153,800 tokens
   - Reserved for output: 15,000 tokens

   Suggestions:
   1. Use a larger context model (claude-sonnet supports 1M beta)
   2. Split data into multiple runs
   3. Summarise input data first
```

## Implementation Tasks

- [ ] Create ContextManager class
- [ ] Implement token counting per provider
- [ ] Add warning threshold system
- [ ] Create budget visualisation
- [ ] Implement output reservation
- [ ] Add chunking suggestions
- [ ] Support automatic data chunking
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Warnings displayed before limit exceeded
- [ ] Token counts accurate per provider
- [ ] Clear suggestions for large datasets
- [ ] Auto-chunking works correctly
- [ ] Test coverage ≥ 80%

## Dependencies

- F-002: LLM provider abstraction
- F-063: Token count tracking

---

## Related Documentation

- [Milestone v0.7.0](../../milestones/v0.7.0.md)
- [Model Cards](../../../reference/model-cards.md)

