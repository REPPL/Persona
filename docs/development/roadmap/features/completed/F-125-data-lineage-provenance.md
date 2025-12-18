# F-125: Data Lineage & Provenance Tracking

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-004, UC-007, UC-008 |
| **Milestone** | v1.9.0 |
| **Priority** | P2 |
| **Category** | Research Infrastructure |
| **Status** | Complete |

## Problem Statement

Generated personas derive from input data through transformations. Users need to trace outputs back to their sources ("where did this persona come from?"), understand transformation chains ("what processing was applied?"), and verify data integrity ("has anything been tampered with?"). Without lineage tracking, debugging generation issues, ensuring reproducibility, and meeting audit requirements becomes difficult.

## Research Foundation

### Research Sources

- **R-016: Experiment & Project Organisation** - Lineage architecture patterns
- **W3C PROV Data Model** - Standard provenance vocabulary
- **OpenLineage Specification** - Open standard for data lineage
- **MLflow/W&B Artifacts** - Practical lineage implementations

### Key Findings

From R-016 research:

1. **W3C PROV** defines three core concepts: Entity (data), Activity (process), Agent (actor)
2. **Content-addressable storage** (hashing) enables automatic deduplication and integrity verification
3. **Lineage granularity** ranges from coarse (dataset-to-dataset) to fine (row/column level)
4. **Implicit vs explicit capture**: Automatic lineage (from tool integration) vs manual annotation

### W3C PROV Model

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

## Design Approach

### Lineage Components

| Component | Description | Example |
|-----------|-------------|---------|
| **Entity** | Data artefact | Interview transcript, persona JSON |
| **Activity** | Transformation | Generation run, quality check |
| **Agent** | Actor/system | persona-cli, GPT-4o model |
| **Derivation** | Output-input link | Persona derived from transcript |

### Entity Model

```python
@dataclass
class LineageEntity:
    """Represents a data artefact in the lineage graph."""
    entity_id: str              # Unique identifier
    entity_type: str            # source_data, template, persona, report
    hash: str                   # SHA-256 content hash
    path: str | None            # File path if applicable
    created: datetime           # When entity was created
    metadata: dict              # Type-specific metadata

    # Lineage relationships
    derived_from: list[str]     # Parent entity IDs
    generated_by: str | None    # Activity ID that created this
```

### Activity Model

```python
@dataclass
class LineageActivity:
    """Represents a transformation/process."""
    activity_id: str            # Unique identifier
    activity_type: str          # generation, validation, comparison
    started: datetime
    ended: datetime | None
    status: str                 # running, completed, failed

    # Relationships
    used: list[str]             # Input entity IDs
    generated: list[str]        # Output entity IDs
    agent: str                  # Agent ID

    # Context
    parameters: dict            # Activity parameters
    run_id: str | None          # Link to experiment run
    audit_id: str | None        # Link to audit record
```

### Agent Model

```python
@dataclass
class LineageAgent:
    """Represents an actor or system."""
    agent_id: str               # Unique identifier
    agent_type: str             # tool, model, user
    name: str                   # e.g., "persona-cli", "gpt-4o-2025-01"
    version: str | None         # Version if applicable
    metadata: dict              # Agent-specific attributes
```

### Lineage Record Schema

```json
{
  "lineage_version": "1.0.0",
  "entities": {
    "ent_abc123": {
      "entity_id": "ent_abc123",
      "entity_type": "source_data",
      "hash": "sha256:abc123def456...",
      "path": "data/interviews.csv",
      "created": "2025-01-15T10:00:00Z",
      "metadata": {
        "format": "csv",
        "rows": 50,
        "columns": ["id", "transcript", "date"]
      },
      "derived_from": [],
      "generated_by": null
    },
    "ent_def456": {
      "entity_id": "ent_def456",
      "entity_type": "persona_set",
      "hash": "sha256:def456ghi789...",
      "path": "output/personas.json",
      "created": "2025-01-16T14:31:45Z",
      "metadata": {
        "count": 5,
        "quality_score": 0.87
      },
      "derived_from": ["ent_abc123", "ent_template_v2"],
      "generated_by": "act_run_001"
    }
  },
  "activities": {
    "act_run_001": {
      "activity_id": "act_run_001",
      "activity_type": "generation",
      "started": "2025-01-16T14:30:22Z",
      "ended": "2025-01-16T14:31:45Z",
      "status": "completed",
      "used": ["ent_abc123", "ent_template_v2"],
      "generated": ["ent_def456"],
      "agent": "agent_persona_cli",
      "parameters": {
        "model": "gpt-4o-2025-01",
        "temperature": 0.7,
        "count": 5
      },
      "run_id": "run_20250116_143022",
      "audit_id": "audit_xyz789"
    }
  },
  "agents": {
    "agent_persona_cli": {
      "agent_id": "agent_persona_cli",
      "agent_type": "tool",
      "name": "persona-cli",
      "version": "1.8.0",
      "metadata": {}
    },
    "agent_gpt4o": {
      "agent_id": "agent_gpt4o",
      "agent_type": "model",
      "name": "gpt-4o-2025-01",
      "version": "2025-01",
      "metadata": {
        "provider": "openai"
      }
    }
  }
}
```

### Python API

```python
from persona.core.lineage import LineageGraph, LineageQuery

# Automatic lineage capture during generation
# (integrated with GenerationPipeline)
result = pipeline.generate(data, count=5)
print(f"Output lineage: {result.lineage}")

# Query lineage
graph = LineageGraph.load("~/.persona/lineage/")

# Trace backwards: What produced this persona?
ancestors = graph.ancestors("ent_def456")
for entity in ancestors:
    print(f"- {entity.entity_type}: {entity.path}")

# Trace forwards: What was derived from this data?
descendants = graph.descendants("ent_abc123")
for entity in descendants:
    print(f"- {entity.entity_type}: {entity.path}")

# Find all entities from a specific activity
outputs = graph.generated_by("act_run_001")

# Query by type and time range
personas = graph.query(
    entity_type="persona_set",
    created_after="2025-01-01",
    created_before="2025-02-01"
)

# Verify integrity
verification = graph.verify("ent_def456")
print(f"Hash matches: {verification.hash_valid}")
print(f"Source exists: {verification.sources_exist}")

# Export lineage for a specific output
lineage_export = graph.export_subgraph(
    root="ent_def456",
    depth=3,  # How many levels of ancestors
    format="prov-json"  # W3C PROV-JSON format
)
```

### CLI Interface

```bash
# View lineage for an artefact
persona lineage show output/personas.json

# Trace ancestors (what produced this?)
persona lineage trace output/personas.json --direction up

# Trace descendants (what was derived?)
persona lineage trace data/interviews.csv --direction down

# Verify integrity
persona lineage verify output/personas.json
# Output:
# ✓ Hash: sha256:def456... (valid)
# ✓ Source: data/interviews.csv (exists, hash valid)
# ✓ Template: default_v2.jinja2 (exists)
# ✓ Activity: act_run_001 (audit verified)

# Export lineage graph
persona lineage export output/personas.json \
    --format prov-json \
    --output lineage-report.json

# Visualise lineage (requires graphviz)
persona lineage graph output/personas.json --output lineage.png

# Query lineage
persona lineage query --type persona_set --since 2025-01-01

# Show activity details
persona lineage activity act_run_001
```

### Storage Backend

**Primary: JSON-based graph storage**

```
~/.persona/lineage/
├── entities/
│   ├── ent_abc123.json
│   └── ent_def456.json
├── activities/
│   └── act_run_001.json
├── agents/
│   └── agent_persona_cli.json
└── index.sqlite  # For queries
```

**Alternative: SQLite graph**

For larger deployments, store lineage in SQLite with proper indexing:

```sql
CREATE TABLE entities (
    entity_id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    hash TEXT NOT NULL,
    path TEXT,
    created TIMESTAMP,
    metadata JSON
);

CREATE TABLE derivations (
    child_id TEXT REFERENCES entities,
    parent_id TEXT REFERENCES entities,
    PRIMARY KEY (child_id, parent_id)
);

CREATE TABLE activities (
    activity_id TEXT PRIMARY KEY,
    activity_type TEXT NOT NULL,
    started TIMESTAMP,
    ended TIMESTAMP,
    status TEXT,
    agent_id TEXT,
    parameters JSON,
    run_id TEXT,
    audit_id TEXT
);

CREATE INDEX idx_entities_type ON entities(entity_type);
CREATE INDEX idx_entities_created ON entities(created);
CREATE INDEX idx_activities_type ON activities(activity_type);
```

### Integration Points

**F-123 Audit Trail:**
- Activities link to audit records via `audit_id`
- Combined query: lineage + audit for full provenance

**F-124 Experiment Management:**
- Activities link to runs via `run_id`
- Experiment-level lineage aggregation

**Quality Commands:**
- Quality checks recorded as activities
- Quality scores in entity metadata

### Content-Addressable Storage

```python
def compute_entity_hash(path: Path) -> str:
    """Compute SHA-256 hash for content addressing."""
    hasher = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return f"sha256:{hasher.hexdigest()}"

def verify_entity(entity: LineageEntity) -> bool:
    """Verify entity content matches stored hash."""
    if entity.path is None:
        return True  # No file to verify
    current_hash = compute_entity_hash(entity.path)
    return current_hash == entity.hash
```

## Implementation Tasks

### Core Infrastructure
- [ ] Create `persona/core/lineage/` module structure
- [ ] Define LineageEntity model
- [ ] Define LineageActivity model
- [ ] Define LineageAgent model
- [ ] Implement LineageGraph class

### Storage
- [ ] Implement JSON file storage backend
- [ ] Implement SQLite storage backend
- [ ] Add index for efficient queries
- [ ] Implement content hashing

### Capture
- [ ] Integrate lineage capture with GenerationPipeline
- [ ] Capture template entities
- [ ] Capture model agents automatically
- [ ] Link to F-123 audit records
- [ ] Link to F-124 experiment runs

### Query & Traversal
- [ ] Implement ancestor traversal (upstream)
- [ ] Implement descendant traversal (downstream)
- [ ] Implement query by type, time, hash
- [ ] Add subgraph extraction

### Verification
- [ ] Implement hash verification
- [ ] Implement source existence check
- [ ] Add chain verification (all ancestors)
- [ ] Report verification results

### CLI Commands
- [ ] Implement `persona lineage show`
- [ ] Implement `persona lineage trace`
- [ ] Implement `persona lineage verify`
- [ ] Implement `persona lineage export`
- [ ] Implement `persona lineage query`
- [ ] Add graph visualisation (optional)

### Export Formats
- [ ] Implement PROV-JSON export
- [ ] Implement simple JSON export
- [ ] Consider PROV-N, PROV-XML (optional)

### Documentation & Testing
- [ ] Write unit tests (target: 85% coverage)
- [ ] Write integration tests
- [ ] Add CLI usage examples
- [ ] Document PROV compliance

## Success Criteria

- [ ] All generation operations captured automatically
- [ ] Lineage traces from output to all inputs
- [ ] Hash verification detects tampering
- [ ] PROV-JSON export validates against schema
- [ ] Query by type, time range, and hash works
- [ ] CLI commands functional for all operations
- [ ] Test coverage ≥ 85%
- [ ] Lineage capture overhead < 5%

## Dependencies

- **F-123: Generation Audit Trail** - Audit record integration
- **F-124: Experiment Management** - Run context integration

## Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Storage growth from hashes | Medium | Low | Deduplicate identical content |
| Performance of graph traversal | Low | Medium | SQLite indexing, caching |
| File moves break lineage | Medium | Medium | Track by hash, not just path |
| Complex graph visualisation | Low | Low | Simple text output as fallback |

---

## Related Documentation

- [R-016: Experiment & Project Organisation](../../../research/R-016-experiment-project-organisation.md)
- [F-123: Generation Audit Trail](../completed/F-123-generation-audit-trail.md)
- [F-124: Experiment Management](./F-124-experiment-management.md)
- [W3C PROV-DM](https://www.w3.org/TR/prov-dm/)

---

**Status**: Complete
