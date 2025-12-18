# F-075: Progress Tracking with Rich

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001, UC-002 |
| **Milestone** | v0.9.0 |
| **Priority** | P2 |
| **Category** | Logging |

## Problem Statement

Long-running operations (data loading, generation, export) leave users uncertain about progress. Visual feedback improves user experience and helps identify stalls.

## Design Approach

- Use Rich library for progress bars
- Show multi-step workflow progress
- Display ETA and elapsed time
- Support nested progress (steps within steps)
- Graceful fallback for non-TTY

### Progress Display

```
Generating Personas ━━━━━━━━━━━━━━━━━━━━━━ 67% 0:01:23 ETA: 0:00:42

Steps:
  ✓ Loading data (3 files)
  ✓ Validating configuration
  → Generating personas (2/3)
    ├─ Persona 1: Jordan ✓
    ├─ Persona 2: Alex ✓
    └─ Persona 3: Taylor ...
  ○ Writing output
  ○ Generating README
```

### Progress API

```python
from persona.ui import ProgressTracker

async with ProgressTracker() as progress:
    # Add tasks
    load_task = progress.add_task("Loading data", total=3)
    gen_task = progress.add_task("Generating personas", total=5)

    # Update progress
    progress.update(load_task, advance=1, description="Loading file 1")

    # Nested progress
    with progress.subtask(gen_task, "Persona 1"):
        # ... generation work
        pass
```

### Non-TTY Fallback

```
[INFO] Loading data... (1/3)
[INFO] Loading data... (2/3)
[INFO] Loading data... (3/3)
[INFO] Generating personas... (1/5)
```

## Implementation Tasks

- [ ] Integrate Rich progress
- [ ] Create ProgressTracker class
- [ ] Implement multi-step display
- [ ] Add nested progress support
- [ ] Calculate ETA
- [ ] Implement non-TTY fallback
- [ ] Add to all long operations
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Progress shown for all long ops
- [ ] ETA reasonably accurate
- [ ] Nested progress works
- [ ] Non-TTY fallback works
- [ ] Test coverage ≥ 80%

## Dependencies

- None (UI enhancement)

---

## Related Documentation

- [Milestone v0.9.0](../../milestones/v0.9.0.md)
- [Rich Progress](https://rich.readthedocs.io/en/latest/progress.html)
