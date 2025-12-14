# F-006: Experiment Management

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-002 |
| **Milestone** | v0.1.0 |
| **Priority** | P0 |
| **Category** | Experiments |

## Problem Statement

Users need to organise generation runs into experiments for reproducibility and comparison of results.

## Design Approach

- Experiment directory structure
- YAML configuration per experiment
- Timestamped output folders
- Experiment listing and status

## Implementation Tasks

- [ ] Create ExperimentManager class
- [ ] Define experiment config schema
- [ ] Implement create experiment flow (interactive)
- [ ] Implement list experiments
- [ ] Implement show experiment
- [ ] Implement delete experiment (with confirmation)
- [ ] Add experiment validation
- [ ] Write unit tests

## Success Criteria

- [ ] Experiments created with correct structure
- [ ] Configuration persisted in YAML
- [ ] Multiple generation runs organised by timestamp
- [ ] Listing shows all experiments with status
- [ ] Test coverage ≥ 80%

## Experiment Structure

```
experiments/
└── my-experiment/
    ├── config.yaml       # Experiment settings
    ├── data/             # Input data files
    ├── outputs/          # Generation outputs
    │   └── YYYYMMDD_HHMMSS/
    └── README.md         # Auto-generated docs
```

---

## Related Documentation

- [UC-002: Manage Experiments](../../../../use-cases/briefs/UC-002-manage-experiments.md)
- [ADR-0003: Experiment-Centric Workflow](../../../decisions/adrs/ADR-0003-experiment-centric-workflow.md)
