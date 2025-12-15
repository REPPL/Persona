# F-050: Experiment History Command

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-002, UC-007 |
| **Milestone** | v0.5.0 |
| **Priority** | P2 |
| **Category** | CLI |

## Problem Statement

Users run multiple generations from the same experiment with different parameters. They need to track which outputs came from which runs and compare results over time.

## Design Approach

- Track all generation runs per experiment
- Store run metadata (parameters, timestamp, cost)
- Diff between runs
- Navigate run outputs
- Aggregate statistics

### History Output

```
$ persona experiment history my-experiment

Run History for: my-experiment

| Run | Timestamp           | Model           | Personas | Cost   | Status |
|-----|---------------------|-----------------|----------|--------|--------|
| #5  | 2025-12-14 10:30:00 | claude-sonnet-4.5 | 3      | $0.45  | ✓      |
| #4  | 2025-12-13 15:22:00 | gpt-5           | 3        | $0.62  | ✓      |
| #3  | 2025-12-13 14:10:00 | claude-sonnet-4.5 | 5      | $0.72  | ✓      |
| #2  | 2025-12-12 09:45:00 | gemini-3.0-pro  | 3        | $0.18  | ✓      |
| #1  | 2025-12-11 16:30:00 | claude-sonnet-4.5 | 3      | $0.41  | ✓      |

Total: 5 runs, 17 personas, $2.38
```

## Implementation Tasks

- [ ] Create RunHistory class
- [ ] Store run metadata in experiment
- [ ] Implement `persona experiment history` command
- [ ] Add `--diff` flag for run comparison
- [ ] Add `--open` to navigate to run output
- [ ] Add `--stats` for aggregate statistics
- [ ] Add `--last N` to filter recent runs
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] All runs tracked with metadata
- [ ] History displays correctly
- [ ] Diff highlights changes
- [ ] Navigation to outputs works
- [ ] Test coverage ≥ 80%

## Dependencies

- F-006: Experiment management
- F-013: Timestamped output folders

---

## Related Documentation

- [Milestone v0.5.0](../../milestones/v0.5.0.md)
- [CLI Reference](../../../../reference/cli-reference.md)

