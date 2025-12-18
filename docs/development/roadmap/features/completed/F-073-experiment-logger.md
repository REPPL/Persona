# F-073: Experiment Logger (JSON Lines)

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-007, UC-008 |
| **Milestone** | v0.9.0 |
| **Priority** | P1 |
| **Category** | Logging |

## Problem Statement

Users need detailed logs of experiment execution for debugging, analysis, and reproducibility. JSON Lines format enables easy querying and processing.

## Design Approach

- Log all experiment events to JSON Lines file
- One event per line for easy streaming
- Include timestamps, event types, and payloads
- Support log levels (debug, info, warn, error)
- Enable log rotation for long runs

### Event Schema

```json
{
  "timestamp": "2025-12-14T10:30:00.123Z",
  "level": "info",
  "event": "generation_started",
  "experiment_id": "exp-abc123",
  "run_id": "run-def456",
  "payload": {
    "model": "claude-sonnet-4-5-20250929",
    "data_files": 3,
    "persona_count": 4
  }
}
```

### Event Types

| Event | Description |
|-------|-------------|
| `experiment_started` | Experiment begins |
| `data_loaded` | Input data processed |
| `generation_started` | LLM call initiated |
| `generation_completed` | LLM response received |
| `generation_failed` | LLM call failed |
| `persona_created` | Persona parsed |
| `output_written` | File saved |
| `experiment_completed` | Experiment finished |

### Log File Location

```
experiments/my-experiment/
├── logs/
│   ├── experiment.jsonl    # Main log file
│   └── debug.jsonl         # Debug level only
└── outputs/
    └── ...
```

## Implementation Tasks

- [ ] Create ExperimentLogger class
- [ ] Implement JSON Lines writer
- [ ] Define event types enum
- [ ] Add structured event payloads
- [ ] Implement log levels
- [ ] Add log rotation
- [ ] Create log viewer utility
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] All events logged correctly
- [ ] JSON Lines parseable
- [ ] Log levels work correctly
- [ ] Rotation prevents large files
- [ ] Test coverage ≥ 80%

## Dependencies

- F-006: Experiment management

---

## Related Documentation

- [Milestone v0.9.0](../../milestones/v0.9.0.md)
- [JSON Lines Format](https://jsonlines.org/)
