# F-013: Timestamped Output Folders

## Overview

| Attribute | Value |
|-----------|-------|
| **Milestone** | v0.1.0 |
| **Priority** | P0 |
| **Category** | Output |

## Problem Statement

Each persona generation run must produce distinctly identifiable outputs. Without automatic timestamping, outputs may overwrite previous runs, making it impossible to compare results, track experiments, or reproduce specific generations.

## Design Approach

- Create timestamp-based folder for each generation run
- Use ISO 8601-inspired format (YYYYMMDD_HHMMSS)
- Store all run artifacts within timestamped folder
- Support custom output directory via CLI flag
- Enable easy identification and chronological sorting

## Implementation Tasks

- [ ] Define timestamped folder naming convention
- [ ] Implement folder creation utility
- [ ] Add --output CLI flag for custom base directory
- [ ] Create folder structure within timestamped output
- [ ] Handle timezone considerations (UTC vs local)
- [ ] Add collision detection (same-second runs)
- [ ] Write unit tests

## Success Criteria

- [ ] Each run creates unique timestamped folder
- [ ] Folders sort chronologically in file system
- [ ] Custom output directories work correctly
- [ ] No collisions on rapid successive runs
- [ ] Test coverage ≥ 80%

## Folder Structure

```
outputs/
├── 20241215_143022/
│   ├── metadata.json
│   ├── reasoning/
│   └── personas/
├── 20241215_150145/
│   └── ...
└── 20241216_091230/
    └── ...
```

## Dependencies

- F-005: Output formatting (provides output structure)

---

## Related Documentation

- [F-005: Output Formatting](F-005-output-formatting.md)
- [ADR-0009: Timestamped Output Organisation](../../../../decisions/adrs/ADR-0009-timestamped-output.md)

