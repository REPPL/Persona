# Experiments

User experiments directory.

## Structure

Each experiment is a self-contained directory:

```
experiments/
└── my-experiment/
    ├── config.yaml       # Experiment configuration
    ├── data/             # Input data files
    ├── outputs/          # Generated outputs
    │   └── YYYYMMDD_HHMMSS/
    └── README.md         # Auto-generated documentation
```

## Creating an Experiment

```bash
persona create experiment
```

## Listing Experiments

```bash
persona list experiments
```

## Sample Experiment

*Sample experiments will be added during v0.1.0 implementation.*

---

## Related Documentation

- [Getting Started](../docs/tutorials/01-getting-started.md)
- [UC-002: Manage Experiments](../docs/use-cases/briefs/UC-002-manage-experiments.md)
