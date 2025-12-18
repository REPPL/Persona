# F-074: Structured Logging

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-007 |
| **Milestone** | v0.9.0 |
| **Priority** | P1 |
| **Category** | Logging |

## Problem Statement

Traditional text logs are difficult to query and analyse. Structured logging with consistent fields enables filtering, aggregation, and automated processing.

## Design Approach

- Use structlog for structured logging
- Consistent field naming across modules
- Context propagation (experiment_id, run_id)
- Multiple output formats (JSON, console)
- Integration with logging stdlib

### Structured Log Format

```python
import structlog

logger = structlog.get_logger()

logger.info(
    "persona_generated",
    experiment_id="exp-abc123",
    run_id="run-def456",
    persona_index=1,
    persona_name="Jordan",
    tokens_used=8542,
    duration_ms=2340
)
```

### Output Formats

**JSON Output (for processing):**
```json
{
  "event": "persona_generated",
  "experiment_id": "exp-abc123",
  "run_id": "run-def456",
  "persona_index": 1,
  "persona_name": "Jordan",
  "tokens_used": 8542,
  "duration_ms": 2340,
  "timestamp": "2025-12-14T10:30:00.123Z",
  "level": "info"
}
```

**Console Output (for humans):**
```
2025-12-14 10:30:00 [info     ] persona_generated    experiment_id=exp-abc123 persona_name=Jordan tokens_used=8542
```

### Context Binding

```python
# Bind context once
logger = logger.bind(
    experiment_id="exp-abc123",
    run_id="run-def456"
)

# All subsequent logs include context
logger.info("data_loaded", file_count=5)
logger.info("generation_started", model="claude-sonnet-4-5")
```

## Implementation Tasks

- [ ] Integrate structlog
- [ ] Define standard field names
- [ ] Implement context binding
- [ ] Configure JSON processor
- [ ] Configure console processor
- [ ] Add to all modules
- [ ] Create logging configuration
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Structured logs throughout
- [ ] Consistent field naming
- [ ] Context propagation works
- [ ] Multiple output formats
- [ ] Test coverage ≥ 80%

## Dependencies

- None (foundational infrastructure)

---

## Related Documentation

- [Milestone v0.9.0](../../milestones/v0.9.0.md)
- [structlog Documentation](https://www.structlog.org/)
