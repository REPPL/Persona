# F-056: Model Availability Checking

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-003 |
| **Milestone** | v0.6.0 |
| **Priority** | P2 |
| **Category** | Validation |

## Problem Statement

Users may configure models that don't exist, are deprecated, or aren't available in their region. Early detection prevents wasted time and confusing errors.

## Design Approach

- Check model availability before generation
- Query provider APIs for model lists
- Warn about deprecated models
- Suggest alternatives for unavailable models
- Cache availability status

### Availability Check Flow

```
User Selects Model
        ↓
Check Local Cache
        ↓
[Cache Valid] → Return Cached Status
        ↓
[Cache Expired] → Query Provider API
        ↓
Update Cache → Return Status
        ↓
[Available] → Continue
[Unavailable] → Suggest Alternatives
[Deprecated] → Warn + Continue
```

### CLI Interface

```bash
# Check if model is available
persona model check claude-sonnet-4-5-20250929

# List available models for provider
persona model list --provider anthropic

# Show deprecated models
persona model list --show-deprecated
```

## Implementation Tasks

- [ ] Create ModelChecker class
- [ ] Implement provider API queries
- [ ] Add availability caching with TTL
- [ ] Implement deprecation detection
- [ ] Add alternative suggestions
- [ ] Create `persona model check` command
- [ ] Create `persona model list` command
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Unavailable models detected before generation
- [ ] Deprecated models show warnings
- [ ] Alternatives suggested for unavailable models
- [ ] Offline mode works with cache
- [ ] Test coverage ≥ 80%

## Dependencies

- F-002: LLM provider abstraction
- F-048: Dynamic model discovery

---

## Related Documentation

- [Milestone v0.6.0](../../milestones/v0.6.0.md)
- [Model Cards](../../../reference/model-cards.md)

