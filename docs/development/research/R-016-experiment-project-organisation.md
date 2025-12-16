# R-016: Experiment and Project Organisation Best Practices

Research into state-of-the-art approaches for organising AI/ML experiments and research projects, synthesising lessons from experiment tracking tools, scientific computing, and user research repositories.

## Executive Summary

Effective experiment organisation requires addressing three interconnected concerns: **reproducibility** (can results be recreated?), **discoverability** (can past work be found?), and **lineage** (what produced what?). This research synthesises approaches from MLOps, scientific computing, and qualitative research to define best practices applicable to persona generation workflows.

**Key Finding:** The most successful systems combine structured metadata schemas with flexible tagging, automated capture of environment/parameters, and clear separation between raw artefacts and derived outputs.

**Recommendation:** Implement a hierarchical organisation model with:
1. **Projects** as top-level containers with persistent configuration
2. **Experiments** as parameter variations within projects
3. **Runs** as individual executions with full provenance
4. **Artefacts** with explicit lineage linking outputs to inputs

---

## Current State of the Art (2025)

### Experiment Tracking Landscape

The ML experiment tracking space has matured significantly, with clear patterns emerging from tools serving millions of users.

#### MLflow (Industry Standard)

**Architecture:**
```
MLflow Tracking
├── Experiments (containers)
│   └── Runs (executions)
│       ├── Parameters (inputs)
│       ├── Metrics (outputs)
│       ├── Artefacts (files)
│       └── Tags (metadata)
└── Model Registry (versioning)
```

**Schema Design (SQLite/PostgreSQL):**
```sql
-- Core tables from MLflow schema
experiments (
    experiment_id SERIAL PRIMARY KEY,
    name VARCHAR(256) UNIQUE,
    artifact_location VARCHAR(256),
    lifecycle_stage VARCHAR(32)  -- active/deleted
);

runs (
    run_uuid VARCHAR(32) PRIMARY KEY,
    experiment_id INTEGER REFERENCES experiments,
    start_time BIGINT,
    end_time BIGINT,
    status VARCHAR(9),  -- RUNNING/SCHEDULED/FINISHED/FAILED/KILLED
    source_type VARCHAR(256),
    source_name VARCHAR(500)
);

params (
    run_uuid VARCHAR(32),
    key VARCHAR(250),
    value VARCHAR(8000),
    PRIMARY KEY (run_uuid, key)
);

metrics (
    run_uuid VARCHAR(32),
    key VARCHAR(250),
    value FLOAT,
    timestamp BIGINT,
    step BIGINT,
    PRIMARY KEY (run_uuid, key, timestamp, step)
);

tags (
    run_uuid VARCHAR(32),
    key VARCHAR(250),
    value VARCHAR(5000),
    PRIMARY KEY (run_uuid, key)
);
```

**Key Design Decisions:**
- UUIDs for runs enable distributed generation
- String values for parameters (8KB limit) accommodate JSON serialisation
- Metrics support time-series with step tracking
- Tags provide flexible, unstructured metadata
- Lifecycle stages enable soft delete

#### Weights & Biases (W&B)

**Differentiating Features:**
- Real-time synchronisation with cloud backend
- Rich visualisation and comparison tools
- Artefact versioning with automatic deduplication
- Sweeps for hyperparameter search
- Tables for structured data logging

**Organisation Model:**
```
Entity (organisation/user)
└── Project
    └── Run
        ├── Config (parameters)
        ├── Summary (final metrics)
        ├── History (metric time series)
        ├── Files (artefacts)
        └── Media (images, audio, video)
```

**W&B Artifacts System:**
- Content-addressable storage (SHA-256)
- Lineage tracking: `artifact.use()` and `artifact.log()`
- Automatic versioning with aliases
- Cross-project referencing

#### Comparison: MLflow vs W&B

| Aspect | MLflow | Weights & Biases |
|--------|--------|------------------|
| **Hosting** | Self-hosted or Databricks | Cloud-first (self-hosted available) |
| **Schema** | Fixed, SQL-based | Flexible, document-based |
| **Artefacts** | File system | Content-addressable store |
| **Lineage** | Manual | Automatic with .use()/.log() |
| **Collaboration** | Basic | Rich (comments, reports) |
| **Cost** | Free (open source) | Free tier, paid for teams |
| **Offline** | Full support | Sync-when-connected |

---

### Scientific Computing Best Practices

#### ENCORE Framework (Reproducible Research)

The ENCORE principles from computational science provide a foundational framework:

1. **E**xecutable - Code runs without modification
2. **N**on-proprietary - Open formats and tools
3. **C**omplete - All dependencies documented
4. **O**pen - Accessible to reviewers
5. **R**eliable - Consistent results across runs
6. **E**xplicit - Clear documentation of process

**Implementation Checklist:**
- [ ] Version control for code (Git)
- [ ] Pinned dependency versions (requirements.txt, poetry.lock)
- [ ] Environment capture (conda.yaml, Dockerfile)
- [ ] Random seed documentation
- [ ] Hardware specification (GPU, RAM)
- [ ] Execution timestamps and duration

#### "Good Enough Practices in Scientific Computing" (Wilson et al.)

Key recommendations from this influential paper:

**Data Management:**
- Save raw data as read-only
- Create derived data programmatically
- Record all processing steps
- Use standard formats (CSV, JSON, Parquet)

**Project Organisation:**
```
project/
├── data/
│   ├── raw/           # Immutable input data
│   └── processed/     # Derived data (can regenerate)
├── src/               # Source code
├── notebooks/         # Exploration (numbered)
├── results/           # Output artefacts
├── docs/              # Documentation
├── environment.yml    # Dependencies
└── README.md          # Project overview
```

**Naming Conventions:**
- Dates in ISO format: `YYYY-MM-DD`
- Avoid spaces and special characters
- Use descriptive, consistent prefixes
- Include version/run identifiers

#### Cookiecutter Data Science (v2, 2024)

The de facto standard template for ML/data science projects:

```
├── LICENSE
├── Makefile           # CLI entry points
├── README.md
├── data/
│   ├── external/      # Third-party data
│   ├── interim/       # Intermediate transforms
│   ├── processed/     # Final datasets
│   └── raw/           # Immutable originals
├── docs/
├── models/            # Trained/serialised models
├── notebooks/         # Jupyter notebooks (numbered)
├── references/        # Data dictionaries, papers
├── reports/
│   └── figures/       # Generated graphics
├── pyproject.toml
└── src/
    ├── __init__.py
    ├── config.py
    ├── dataset.py
    ├── features.py
    ├── modeling/
    └── plots.py
```

**Key Principles:**
1. **Immutable raw data** - Never modify, only read
2. **Numbered notebooks** - `01_explore.ipynb`, `02_clean.ipynb`
3. **Pipeline as code** - `make data` regenerates processed data
4. **Separation of concerns** - Source code vs notebooks vs configs

---

### User Research Repositories

Persona generation serves user research workflows. Understanding how researchers organise qualitative data informs our approach.

#### Dovetail (Industry Standard)

**Data Model:**
```
Workspace
└── Project
    ├── Data (interviews, surveys, notes)
    │   └── Highlights (tagged excerpts)
    ├── Insights (synthesised findings)
    │   └── Evidence (linked highlights)
    ├── Tags (hierarchical taxonomy)
    └── Charts (visualisations)
```

**Key Features:**
- Automatic transcription with speaker labels
- Pattern detection across highlights
- Evidence-linked insights
- Stakeholder sharing with permissions

#### EnjoyHQ

**Organisation Approach:**
- Properties (custom metadata fields)
- Projects (research initiatives)
- Stories (synthesised narratives)
- Collections (curated groupings)

**Insight-Evidence Model:**
```
Insight: "Users struggle with onboarding"
└── Evidence:
    ├── Interview #23, timestamp 14:32
    ├── Survey response #456
    └── Support ticket #789
```

#### Qualitative Analysis Tools (ATLAS.ti, NVivo)

**Document-Code-Memo Model:**
```
Documents (primary data)
    │
    ├── Codes (tags/categories)
    │   └── Code Groups (hierarchies)
    │
    └── Memos (researcher notes)
        └── Linked to documents/codes
```

**Grounded Theory Support:**
- Open coding (initial labels)
- Axial coding (relationships)
- Selective coding (core categories)
- Theoretical saturation tracking

---

### Data Lineage and Provenance

#### Key Concepts

**Provenance Types:**
1. **Data provenance** - Where did this data come from?
2. **Process provenance** - What transformations were applied?
3. **Agent provenance** - Who/what performed the transformation?

**Lineage Granularity:**
- **Coarse-grained** - Dataset to dataset
- **Fine-grained** - Column/row level
- **Schema-level** - Type transformations

#### W3C PROV Standard

The W3C PROV-DM (Provenance Data Model) defines:

```
Entity (data artefacts)
    │
    ├── wasGeneratedBy → Activity
    │
    └── wasDerivedFrom → Entity

Activity (processes)
    │
    ├── used → Entity
    │
    └── wasAssociatedWith → Agent

Agent (actors/systems)
```

**Example Provenance Chain:**
```
persona_batch_001.json
    wasGeneratedBy → generation_run_xyz
    wasDerivedFrom → interview_transcripts.txt

generation_run_xyz
    used → interview_transcripts.txt
    used → template_v2.jinja2
    wasAssociatedWith → gpt-4o-2025-01
```

#### Implementation Approaches

**Option 1: Embedded Metadata**
```json
{
  "persona": { ... },
  "_provenance": {
    "generated_by": "persona-cli v1.7.0",
    "timestamp": "2025-01-15T10:30:00Z",
    "source_hash": "sha256:abc123...",
    "model": "gpt-4o-2025-01",
    "template": "default_v2.jinja2",
    "parameters": {
      "temperature": 0.7,
      "max_tokens": 4096
    }
  }
}
```

**Option 2: Separate Manifest**
```yaml
# manifest.yaml
artefacts:
  - id: persona_batch_001
    type: persona_set
    generated: 2025-01-15T10:30:00Z
    sources:
      - id: interviews_raw
        hash: sha256:abc123
    generator:
      tool: persona-cli
      version: 1.7.0
      parameters:
        model: gpt-4o-2025-01
        template: default_v2
```

**Option 3: Graph Database**
For complex lineage with many relationships, graph storage enables flexible querying:
```cypher
CREATE (input:Data {hash: "abc123", type: "transcript"})
CREATE (output:Data {hash: "def456", type: "persona"})
CREATE (run:Run {id: "run_001", timestamp: datetime()})
CREATE (output)-[:GENERATED_BY]->(run)
CREATE (run)-[:USED]->(input)
```

---

## Synthesis: Best Practices for Persona Generation

### Recommended Organisation Model

Based on the research, here's a hierarchical model suited to persona generation:

```
Persona Workspace
│
├── Projects (research initiatives)
│   ├── metadata.yaml
│   ├── templates/           # Custom prompt templates
│   └── constraints/         # Validation rules
│
├── Experiments (parameter variations)
│   ├── config.yaml          # Experiment configuration
│   └── runs/                # Individual executions
│
├── Runs (individual generations)
│   ├── run_metadata.json    # Parameters, timing, model
│   ├── input/               # Source data (immutable copies)
│   ├── output/              # Generated personas
│   └── audit/               # Quality metrics, logs
│
├── Artefacts (versioned outputs)
│   ├── personas/            # Approved personas
│   ├── reports/             # Analysis outputs
│   └── manifests/           # Lineage records
│
└── Analysis (cross-run insights)
    ├── comparisons/         # A/B test results
    └── meta-analysis/       # Aggregated findings
```

### Core Principles

1. **Immutable Inputs**
   - Raw data is never modified after import
   - Create versioned copies for experiments
   - Hash inputs for integrity verification

2. **Reproducible Runs**
   - Capture all parameters (model, template, temperature)
   - Record environment (tool version, dependencies)
   - Store random seeds for deterministic replay

3. **Explicit Lineage**
   - Every output links to its inputs
   - Track both data and code versions
   - Support "time travel" queries

4. **Flexible Metadata**
   - Required fields (core schema)
   - Optional tags (user-defined)
   - Extensible without schema changes

5. **Quality Integration**
   - Metrics captured at generation time
   - Validation results stored with runs
   - Audit trails for compliance

### Schema Design

**Project Configuration:**
```yaml
# project.yaml
name: "E-commerce User Research"
description: "Personas for checkout flow redesign"
created: 2025-01-15
status: active

defaults:
  model: gpt-4o-2025-01
  template: ecommerce_v1

constraints:
  age_range: [25, 65]
  required_fields:
    - demographics.occupation
    - goals
    - pain_points

tags:
  - team: product-design
  - sprint: Q1-2025
```

**Experiment Configuration:**
```yaml
# experiment.yaml
name: "temperature-comparison"
description: "Compare temperature 0.3 vs 0.7 vs 1.0"
project: ecommerce-personas
created: 2025-01-16

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

evaluation:
  metrics: [diversity, consistency, faithfulness]
  min_runs_per_variant: 5
```

**Run Metadata:**
```json
{
  "run_id": "run_20250116_143022_abc123",
  "experiment_id": "temperature-comparison",
  "variant": "balanced",
  "status": "completed",
  "timing": {
    "started": "2025-01-16T14:30:22Z",
    "completed": "2025-01-16T14:31:45Z",
    "duration_seconds": 83
  },
  "inputs": {
    "source_data": {
      "path": "input/interviews.txt",
      "hash": "sha256:abc123def456..."
    },
    "template": {
      "name": "ecommerce_v1",
      "version": "1.2.0"
    }
  },
  "parameters": {
    "model": "gpt-4o-2025-01",
    "temperature": 0.7,
    "max_tokens": 4096,
    "count": 5
  },
  "outputs": {
    "personas": {
      "path": "output/personas.json",
      "hash": "sha256:789xyz...",
      "count": 5
    }
  },
  "metrics": {
    "diversity_score": 0.78,
    "consistency_score": 0.92,
    "faithfulness_score": 0.85,
    "bias_score": 0.12
  },
  "environment": {
    "tool": "persona-cli",
    "version": "1.7.0",
    "python": "3.12.1"
  }
}
```

### CLI Integration

**Proposed Commands:**
```bash
# Project management
persona project create "E-commerce Research"
persona project list
persona project use ecommerce-research

# Experiment management
persona experiment create --name "temp-test" --variants variants.yaml
persona experiment run --variant balanced --count 5
persona experiment compare --metrics diversity,faithfulness

# Run management
persona run list --experiment temp-test --status completed
persona run show run_20250116_143022
persona run reproduce run_20250116_143022  # Re-run with same params

# Artefact management
persona artefact export --run run_20250116_143022 --format json
persona artefact lineage personas_batch_001.json  # Show provenance
```

---

## Recommendations for Persona

### Immediate (v1.8.0 Scope)

1. **Extend Audit Trail**
   - Already have `core/audit/` from v1.7.0
   - Add experiment/project context to audit records
   - Enable querying by project/experiment

2. **Add Run Metadata**
   - Capture full parameter set at generation time
   - Include environment information
   - Store input hashes for verification

3. **Implement Basic Lineage**
   - Link outputs to inputs via manifest
   - Track template versions
   - Support lineage queries

### Future (v1.9.0+)

1. **Full Experiment Management**
   - Project and experiment hierarchies
   - Variant comparison workflows
   - A/B testing support

2. **Advanced Lineage**
   - Graph-based provenance store
   - Cross-project lineage queries
   - Time-travel debugging

3. **Integration Points**
   - MLflow export (for ML teams)
   - W&B integration (optional)
   - OpenTelemetry tracing

---

## Sources

### Experiment Tracking

- [MLflow Documentation](https://mlflow.org/docs/latest/index.html)
- [MLflow Database Schema](https://github.com/mlflow/mlflow/blob/master/mlflow/store/db_migrations/versions/)
- [Weights & Biases Documentation](https://docs.wandb.ai/)
- [W&B Artifacts Guide](https://docs.wandb.ai/guides/artifacts)

### Scientific Computing

- [Good Enough Practices in Scientific Computing](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1005510) (Wilson et al., PLOS 2017)
- [ENCORE Reproducibility Framework](https://arxiv.org/abs/1801.02973)
- [Cookiecutter Data Science](https://cookiecutter-data-science.drivendata.org/) (v2, 2024)

### Data Lineage

- [W3C PROV Data Model](https://www.w3.org/TR/prov-dm/)
- [OpenLineage Specification](https://openlineage.io/)
- [Apache Atlas](https://atlas.apache.org/)

### User Research

- [Dovetail User Research Platform](https://dovetail.com/)
- [EnjoyHQ](https://www.enjoyhq.com/)
- [ATLAS.ti Qualitative Analysis](https://atlasti.com/)
- [NVivo](https://lumivero.com/products/nvivo/)

### Database Design

- [MLflow SQLite Schema](https://github.com/mlflow/mlflow/blob/master/mlflow/store/tracking/dbmodels/models.py)
- [W&B Backend Architecture](https://wandb.ai/site/research)

---

## Related Documentation

- [F-123: Generation Audit Trail](../roadmap/features/completed/F-123-generation-audit-trail.md) - Existing audit implementation
- [R-015: Quality Metrics Taxonomy](./R-015-quality-metrics-taxonomy.md) - Metrics for run evaluation

---

**Status**: Complete
