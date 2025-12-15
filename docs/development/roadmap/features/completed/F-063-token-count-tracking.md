# F-063: Token Count Tracking

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-003, UC-007 |
| **Milestone** | v0.7.0 |
| **Priority** | P1 |
| **Category** | LLM |

## Problem Statement

Users need to understand token usage for cost management and context planning. Token counts should be tracked, displayed, and stored in metadata.

## Design Approach

- Count tokens before and after LLM calls
- Use provider-specific tokenisers
- Store token metrics in metadata
- Display token usage summary
- Track cumulative usage

### Token Metrics

```python
@dataclass
class TokenUsage:
    input_tokens: int      # Tokens sent to LLM
    output_tokens: int     # Tokens received from LLM
    total_tokens: int      # Sum of above
    model: str             # Model used
    timestamp: datetime    # When call was made
```

### Metadata Output

```json
{
  "token_usage": {
    "total_input_tokens": 45230,
    "total_output_tokens": 8750,
    "total_tokens": 53980,
    "breakdown_by_step": [
      {
        "step": "persona_generation",
        "input": 42000,
        "output": 7500
      },
      {
        "step": "summary_generation",
        "input": 3230,
        "output": 1250
      }
    ]
  }
}
```

### CLI Display

```
Token Usage Summary
───────────────────────────────
Input tokens:   45,230
Output tokens:   8,750
Total tokens:   53,980
───────────────────────────────
Estimated cost: $0.42
```

## Implementation Tasks

- [ ] Create TokenCounter class
- [ ] Integrate provider-specific tokenisers
- [ ] Track tokens per LLM call
- [ ] Aggregate token usage
- [ ] Add token metadata to output
- [ ] Create token usage display
- [ ] Link to cost estimation
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Accurate token counts per provider
- [ ] Token usage in metadata
- [ ] Clear usage display
- [ ] Breakdown by workflow step
- [ ] Test coverage ≥ 80%

## Dependencies

- F-002: LLM provider abstraction
- F-007: Cost estimation

---

## Related Documentation

- [Milestone v0.7.0](../../milestones/v0.7.0.md)
- [F-007: Cost Estimation](F-007-cost-estimation.md)

