# ADR-0003: Experiment-Centric Workflow

## Status

Accepted

## Context

UX researchers need:
- Reproducible results
- Comparison across runs
- Clear organisation of work
- Version control friendly structure

## Decision

Organise all persona generation around experiments:
- Self-contained experiment directories
- YAML configuration per experiment
- Timestamped output folders
- Data, config, and outputs together

```
experiments/
└── my-experiment/
    ├── config.yaml
    ├── data/
    └── outputs/
        └── YYYYMMDD_HHMMSS/
```

## Consequences

**Positive:**
- Excellent reproducibility
- Easy to compare runs
- Natural version control
- Self-documenting structure

**Negative:**
- Overhead for simple one-off generation
- Requires user to understand experiment concept

---

## Related Documentation

- [F-006: Experiment Management](../../roadmap/features/planned/F-006-experiment-management.md)
- [UC-002: Manage Experiments](../../../use-cases/briefs/UC-002-manage-experiments.md)
