# F-076: Metadata Recording (Comprehensive)

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-002, UC-007 |
| **Milestone** | v0.9.0 |
| **Priority** | P1 |
| **Category** | Logging |

## Problem Statement

For reproducibility and auditing, users need comprehensive metadata about how personas were generated: configuration, environment, timing, costs, and more.

## Design Approach

- Record all generation parameters
- Capture environment information
- Track timing and performance
- Store in standardised format
- Include in all output directories

### Metadata Schema

```json
{
  "metadata_version": "1.0",
  "generation": {
    "experiment_id": "exp-abc123",
    "run_id": "run-def456",
    "timestamp_start": "2025-12-14T10:30:00Z",
    "timestamp_end": "2025-12-14T10:32:15Z",
    "duration_seconds": 135
  },
  "configuration": {
    "model": "claude-sonnet-4-5-20250929",
    "provider": "anthropic",
    "persona_count": 3,
    "complexity": "moderate",
    "detail_level": "detailed"
  },
  "data_sources": {
    "files": [...],
    "total_tokens": 45230
  },
  "environment": {
    "persona_version": "0.9.0",
    "python_version": "3.12.0",
    "platform": "darwin",
    "timezone": "UTC"
  },
  "costs": {
    "input_tokens": 45230,
    "output_tokens": 8750,
    "total_cost_usd": 0.42
  },
  "checksums": {
    "config": "sha256:abc123...",
    "data": "sha256:def456...",
    "output": "sha256:ghi789..."
  }
}
```

### Metadata Location

```
outputs/2025-12-14_103000/
├── metadata.json           # Full metadata
├── personas/
│   └── ...
├── README.md
└── experiment.jsonl
```

## Implementation Tasks

- [ ] Define metadata schema
- [ ] Create MetadataRecorder class
- [ ] Capture configuration
- [ ] Capture environment info
- [ ] Track timing
- [ ] Calculate checksums
- [ ] Write metadata on completion
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] All fields populated
- [ ] Metadata in every output
- [ ] Checksums enable verification
- [ ] Schema versioned for compatibility
- [ ] Test coverage ≥ 80%

## Dependencies

- F-006: Experiment management
- F-063: Token count tracking

---

## Related Documentation

- [Milestone v0.9.0](../../milestones/v0.9.0.md)
- [Persona Schema](../../../../reference/persona-schema.md)
