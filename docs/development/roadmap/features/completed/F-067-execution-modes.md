# F-067: Parallel/Sequential/Consensus Modes

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-004, UC-008 |
| **Milestone** | v0.8.0 |
| **Priority** | P1 |
| **Category** | Generation |

## Problem Statement

When using multiple models, users need different execution strategies: parallel for speed, sequential for dependencies, consensus for reliability.

## Design Approach

- **Parallel**: Run all models simultaneously, combine results
- **Sequential**: Run models in order, pass context forward
- **Consensus**: Generate independently, find agreement

### Execution Modes

| Mode | Description | Use Case |
|------|-------------|----------|
| `parallel` | All models run simultaneously | Speed, comparison |
| `sequential` | Models run in order | Refinement chains |
| `consensus` | Generate then merge agreements | High reliability |

### Parallel Mode

```
┌─────────────┐
│ Input Data  │
└──────┬──────┘
       │
       ├────────────────┬────────────────┐
       ↓                ↓                ↓
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│   Model A   │  │   Model B   │  │   Model C   │
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┴────────────────┘
                        ↓
               ┌─────────────┐
               │   Combine   │
               └─────────────┘
```

### Consensus Mode

```
Step 1: Independent Generation
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│  Personas A │  │  Personas B │  │  Personas C │
│ (3 personas)│  │ (3 personas)│  │ (3 personas)│
└──────┬──────┘  └──────┬──────┘  └──────┬──────┘
       │                │                │
       └────────────────┴────────────────┘
                        ↓
Step 2: Find Agreement
┌───────────────────────────────────────────────┐
│  Cluster similar personas across models       │
│  Identify consensus characteristics           │
│  Flag divergent traits                        │
└───────────────────────────────────────────────┘
                        ↓
Step 3: Output Consensus Personas
┌───────────────────────────────────────────────┐
│  3 consensus personas with confidence scores  │
│  Per-model variations noted                   │
└───────────────────────────────────────────────┘
```

## Implementation Tasks

- [ ] Create ExecutionStrategy base class
- [ ] Implement ParallelStrategy
- [ ] Implement SequentialStrategy
- [ ] Implement ConsensusStrategy
- [ ] Add result combination logic
- [ ] Implement consensus clustering
- [ ] Add divergence detection
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] All three modes work correctly
- [ ] Parallel achieves speedup
- [ ] Sequential passes context
- [ ] Consensus identifies agreement
- [ ] Test coverage ≥ 80%

## Dependencies

- F-066: Multi-model persona generation
- F-088: Async support

---

## Related Documentation

- [Milestone v0.8.0](../../milestones/v0.8.0.md)
- [F-066: Multi-Model Generation](F-066-multi-model-generation.md)
