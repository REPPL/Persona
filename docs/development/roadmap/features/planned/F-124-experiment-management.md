# F-124: Experiment Management System

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-004, UC-007, UC-009 |
| **Milestone** | v1.9.0 |
| **Priority** | P1 |
| **Category** | Research Infrastructure |
| **Status** | Planned |

## Problem Statement

Persona generation for research requires systematic experiment organisation. Currently, users can generate personas and audit individual runs (F-123), but cannot organise related generations into experiments, compare variants, or reproduce past configurations easily. Without experiment management, researchers struggle to track which parameters were tested, what results were obtained, and how to reproduce successful generations.

## Research Foundation

### Research Sources

- **R-016: Experiment & Project Organisation** - State-of-the-art analysis
- **MLflow Tracking** - Industry-standard experiment management schema
- **Weights & Biases** - Cloud-native experiment organisation
- **Cookiecutter Data Science** - Project structure best practices

### Key Findings

From R-016 research:

1. **Hierarchical organisation** (Project → Experiment → Run) scales from individual research to team collaboration
2. **Parameter versioning** enables reproducibility without manual documentation
3. **Variant comparison** accelerates research iteration
4. **Immutable configurations** prevent "works on my machine" issues

### Industry Standards

| Tool | Organisation Model | Key Feature |
|------|-------------------|-------------|
| **MLflow** | Experiment → Runs | SQL-backed, queryable |
| **W&B** | Project → Runs | Real-time sync, sweeps |
| **DVC** | Pipeline stages | Git-integrated |
| **Cookiecutter DS** | Directory structure | Template-based |

## Design Approach

### Hierarchy Model

```
Workspace (default: ~/.persona/)
│
├── Projects
│   ├── project-001/
│   │   ├── project.yaml        # Project configuration
│   │   ├── templates/          # Custom prompt templates
│   │   ├── constraints/        # Validation rules
│   │   └── experiments/
│   │       ├── exp-001/
│   │       │   ├── experiment.yaml
│   │       │   └── runs/
│   │       │       ├── run_20250116_143022/
│   │       │       │   ├── metadata.json
│   │       │       │   ├── input/
│   │       │       │   ├── output/
│   │       │       │   └── metrics/
│   │       │       └── run_20250116_144533/
│   │       └── exp-002/
│   └── project-002/
│
└── config.yaml                 # Global workspace settings
```

### Project Schema

```yaml
# project.yaml
name: "E-commerce User Research"
description: "Personas for checkout flow redesign"
created: 2025-01-15T10:00:00Z
status: active  # active | archived | template

defaults:
  model: gpt-4o-2025-01
  template: default_persona
  temperature: 0.7
  count: 5

constraints:
  age_range: [25, 65]
  required_fields:
    - demographics.occupation
    - goals
    - pain_points
  min_goals: 3

tags:
  team: product-design
  quarter: Q1-2025
  domain: ecommerce

quality:
  auto_validate: true
  min_diversity: 0.6
  max_bias: 0.3
```

### Experiment Schema

```yaml
# experiment.yaml
name: "temperature-comparison"
description: "Compare creativity levels via temperature parameter"
project: ecommerce-research
created: 2025-01-16T09:00:00Z
status: running  # planned | running | completed | failed

hypothesis: "Higher temperature produces more diverse personas"

variants:
  - name: conservative
    parameters:
      temperature: 0.3
  - name: balanced
    parameters:
      temperature: 0.7
  - name: creative
    parameters:
      temperature: 1.0

baseline: balanced  # Control variant for comparison

evaluation:
  metrics:
    - diversity_score
    - consistency_score
    - faithfulness_score
  success_criteria:
    min_diversity: 0.7
  min_runs_per_variant: 5

data_sources:
  - path: data/interviews.csv
    hash: sha256:abc123...
```

### Run Metadata

```json
{
  "run_id": "run_20250116_143022_abc123",
  "experiment_id": "temperature-comparison",
  "project_id": "ecommerce-research",
  "variant": "balanced",
  "status": "completed",
  "timing": {
    "started": "2025-01-16T14:30:22Z",
    "completed": "2025-01-16T14:31:45Z",
    "duration_seconds": 83
  },
  "parameters": {
    "model": "gpt-4o-2025-01",
    "temperature": 0.7,
    "max_tokens": 4096,
    "count": 5
  },
  "inputs": [
    {
      "type": "source_data",
      "path": "input/interviews.csv",
      "hash": "sha256:abc123..."
    },
    {
      "type": "template",
      "name": "default_persona",
      "version": "1.2.0"
    }
  ],
  "outputs": [
    {
      "type": "personas",
      "path": "output/personas.json",
      "hash": "sha256:def456...",
      "count": 5
    }
  ],
  "metrics": {
    "diversity_score": 0.78,
    "consistency_score": 0.92,
    "faithfulness_score": 0.85,
    "bias_score": 0.12
  },
  "environment": {
    "tool_version": "1.8.0",
    "python_version": "3.12.1",
    "platform": "darwin-arm64"
  },
  "audit_id": "audit_xyz789"
}
```

### Python API

```python
from persona.core.experiments import Project, Experiment, ExperimentConfig
from persona.core.experiments import RunConfig, Variant

# Create or load project
project = Project.create(
    name="E-commerce Research",
    defaults={"model": "gpt-4o-2025-01", "temperature": 0.7}
)

# Or load existing
project = Project.load("ecommerce-research")

# Create experiment
experiment = project.create_experiment(
    name="temperature-comparison",
    description="Compare creativity via temperature",
    variants=[
        Variant("conservative", temperature=0.3),
        Variant("balanced", temperature=0.7),
        Variant("creative", temperature=1.0),
    ]
)

# Run experiment
for variant in experiment.variants:
    for i in range(5):  # 5 runs per variant
        run = experiment.run(
            variant=variant.name,
            data="data/interviews.csv",
            count=5
        )
        print(f"Run {run.run_id}: {run.metrics}")

# Analyse results
comparison = experiment.compare()
print(comparison.summary())
print(comparison.best_variant)

# Export results
experiment.export("experiment_results.json")
```

### CLI Interface

```bash
# Project management
persona project create "E-commerce Research"
persona project list
persona project show ecommerce-research
persona project use ecommerce-research  # Set as active
persona project archive ecommerce-research

# Experiment management
persona experiment create --name "temp-test" \
    --description "Temperature comparison" \
    --variants variants.yaml

persona experiment list
persona experiment show temp-test
persona experiment status temp-test

# Run experiments
persona experiment run temp-test --variant balanced --count 5
persona experiment run temp-test --all-variants --runs-per-variant 5

# Compare results
persona experiment compare temp-test --metrics diversity,faithfulness
persona experiment compare temp-test --output comparison.md

# Reproduce past runs
persona run reproduce run_20250116_143022
persona run show run_20250116_143022 --format json

# Query runs
persona run list --experiment temp-test --status completed
persona run list --project ecommerce-research --since 2025-01-01
```

### Integration with Existing Features

**F-123 Audit Trail:**
- Runs automatically create audit records
- Audit IDs linked in run metadata
- Combined query: audit + experiment context

**Quality Commands (F-119 to F-122):**
- Quality metrics captured automatically per run
- Experiment-level quality aggregation
- Quality gates for experiment success criteria

### Storage Backend

| Backend | Use Case | Notes |
|---------|----------|-------|
| **File System** | Default, single-user | Project directories, JSON/YAML files |
| **SQLite** | Local, queryable | Single file, SQL queries |
| **PostgreSQL** | Team, enterprise | Multi-user, concurrent access |

Default: File system with SQLite index for queries.

## Implementation Tasks

### Core Infrastructure
- [ ] Create `persona/core/experiments/` module structure
- [ ] Define Project model and schema
- [ ] Define Experiment model and schema
- [ ] Define Run model and metadata schema
- [ ] Define Variant model
- [ ] Implement file-system storage backend
- [ ] Implement SQLite index for queries

### Project Management
- [ ] Implement Project.create() and Project.load()
- [ ] Implement project defaults inheritance
- [ ] Implement project archival
- [ ] Add project-level constraints validation

### Experiment Management
- [ ] Implement Experiment.create() and Experiment.load()
- [ ] Implement variant definition and validation
- [ ] Implement experiment.run() integration with GenerationPipeline
- [ ] Add experiment status tracking

### Run Management
- [ ] Implement Run creation with full metadata capture
- [ ] Implement run reproduction
- [ ] Integrate with F-123 audit trail
- [ ] Capture quality metrics automatically

### Comparison & Analysis
- [ ] Implement variant comparison logic
- [ ] Create comparison report generation
- [ ] Add statistical significance testing
- [ ] Implement best variant selection

### CLI Commands
- [ ] Implement `persona project` command group
- [ ] Implement `persona experiment` command group
- [ ] Extend `persona run` commands
- [ ] Add Rich output formatting

### Documentation & Testing
- [ ] Write unit tests (target: 85% coverage)
- [ ] Write integration tests
- [ ] Add CLI usage examples
- [ ] Update user documentation

## Success Criteria

- [ ] Projects can be created, loaded, and archived
- [ ] Experiments support multiple variants
- [ ] Runs capture full parameters and metrics
- [ ] Past runs can be reproduced from metadata
- [ ] Variants can be compared with statistical summary
- [ ] CLI commands work for all operations
- [ ] Test coverage ≥ 85%
- [ ] Overhead < 10% of generation time

## Dependencies

- **F-123: Generation Audit Trail** - Audit record integration
- **F-119 to F-122: Quality Commands** - Metrics capture

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Schema evolution | Medium | Medium | Versioned schemas, migration scripts |
| Storage growth | Low | Low | Archive/prune old projects |
| Complexity for simple use | Medium | Medium | Smart defaults, single-command usage |
| Concurrent access conflicts | Low | Medium | File locking, SQLite WAL mode |

---

## Related Documentation

- [R-016: Experiment & Project Organisation](../../research/R-016-experiment-project-organisation.md)
- [F-123: Generation Audit Trail](../completed/F-123-generation-audit-trail.md)
- [F-125: Data Lineage & Provenance](./F-125-data-lineage-provenance.md)

---

**Status**: Planned
