# ADR-0027: Data Lineage Implementation

## Status

Accepted

## Context

Persona v1.9.0 needed comprehensive data lineage tracking for:
- Reproducibility (recreate any persona from its origins)
- Audit compliance (EU AI Act Article 19)
- Debugging (trace issues to source data)
- Research transparency (document methodology)

The implementation needed to:
- Track entities, activities, and agents
- Support querying lineage forwards and backwards
- Export in standard formats
- Not significantly impact performance

## Decision

Implement data lineage using the **W3C PROV data model** with SQLite storage:

### Core Concepts

| PROV Concept | Persona Mapping |
|--------------|-----------------|
| **Entity** | Data files, personas, prompts, responses |
| **Activity** | Generation runs, validation, export |
| **Agent** | LLM models, users, Persona tool |
| **wasGeneratedBy** | Persona ← Activity |
| **used** | Activity → Entity |
| **wasAssociatedWith** | Activity ↔ Agent |
| **wasDerivedFrom** | Persona ← Source data |

### Schema Design

```sql
-- Entities (things that exist)
CREATE TABLE entities (
    id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,  -- input_file, persona, prompt, etc.
    name TEXT,
    attributes JSON,
    content_hash TEXT,  -- SHA-256 for integrity
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Activities (things that happen)
CREATE TABLE activities (
    id TEXT PRIMARY KEY,
    activity_type TEXT NOT NULL,  -- generation, validation, export
    started_at TIMESTAMP,
    ended_at TIMESTAMP,
    attributes JSON
);

-- Agents (who/what performed activities)
CREATE TABLE agents (
    id TEXT PRIMARY KEY,
    agent_type TEXT NOT NULL,  -- llm_model, user, system
    name TEXT,
    attributes JSON
);

-- Relationships
CREATE TABLE used (
    activity_id TEXT REFERENCES activities(id),
    entity_id TEXT REFERENCES entities(id),
    PRIMARY KEY (activity_id, entity_id)
);

CREATE TABLE was_generated_by (
    entity_id TEXT REFERENCES entities(id),
    activity_id TEXT REFERENCES activities(id),
    PRIMARY KEY (entity_id, activity_id)
);

CREATE TABLE was_associated_with (
    activity_id TEXT REFERENCES activities(id),
    agent_id TEXT REFERENCES agents(id),
    role TEXT,
    PRIMARY KEY (activity_id, agent_id)
);

CREATE TABLE was_derived_from (
    derived_id TEXT REFERENCES entities(id),
    source_id TEXT REFERENCES entities(id),
    PRIMARY KEY (derived_id, source_id)
);
```

### API Design

```python
class LineageStore:
    def register_entity(
        self,
        entity_type: str,
        name: str,
        content: bytes | None = None,
        attributes: dict | None = None
    ) -> str:
        """Register an entity and return its ID."""
        entity_id = f"ent-{uuid4().hex[:12]}"
        content_hash = hashlib.sha256(content).hexdigest() if content else None
        # Store in database
        return entity_id

    def record_activity(
        self,
        activity_type: str,
        used: list[str],
        generated: list[str],
        agent: str,
        attributes: dict | None = None
    ) -> str:
        """Record an activity with its relationships."""
        activity_id = f"act-{uuid4().hex[:12]}"
        # Store activity and relationships
        return activity_id

    def trace(
        self,
        entity_id: str,
        direction: str = "up"  # "up", "down", "both"
    ) -> LineageGraph:
        """Trace lineage for an entity."""
        # Query relationships recursively
        return graph
```

### CLI Commands

```bash
# List tracked entities
persona lineage list

# Show entity details
persona lineage show ent-abc123

# Trace lineage upward (sources)
persona lineage trace ent-abc123 --direction up

# Trace lineage downward (derivatives)
persona lineage trace ent-abc123 --direction down

# Verify entity integrity
persona lineage verify ent-abc123

# Export as PROV-JSON
persona lineage export --format prov-json --output lineage.json
```

## Consequences

**Positive:**
- Full traceability from output to input
- Standard format (W3C PROV) for interoperability
- Efficient querying (SQLite, indexed)
- Integrity verification via content hashes
- Supports regulatory compliance

**Negative:**
- Storage overhead (~1KB per tracked entity)
- Write latency for lineage recording
- Complexity in maintaining relationships
- Large lineage graphs for complex workflows

## Alternatives Considered

### Simple Event Log

**Description:** Append-only log of all operations.
**Pros:** Simple, fast writes, easily auditable.
**Cons:** No relationship structure, difficult to query lineage.
**Why Not Chosen:** Lineage queries are a core requirement.

### Neo4j Graph Database

**Description:** Use graph database for relationship storage.
**Pros:** Native graph queries, scalable, visualisation tools.
**Cons:** External dependency, operational complexity.
**Why Not Chosen:** Overkill for single-user tool; SQLite sufficient.

### JSON Files

**Description:** Store lineage as JSON files per entity.
**Pros:** Simple, portable, human-readable.
**Cons:** Inefficient queries, relationship duplication.
**Why Not Chosen:** Query performance unacceptable for complex graphs.

### Git-Based Tracking

**Description:** Use git commits to track lineage.
**Pros:** Built-in history, diff support, widely understood.
**Cons:** Not designed for structured relationships, overhead.
**Why Not Chosen:** Doesn't model PROV concepts well.

## Implementation Details

### Automatic Lineage Capture

Lineage is captured automatically during generation:

```python
@contextmanager
def track_generation(self, data_files: list[Path]):
    """Context manager for automatic lineage tracking."""
    # Register input entities
    input_ids = [
        self.lineage.register_entity(
            "input_file",
            f.name,
            content=f.read_bytes()
        )
        for f in data_files
    ]

    # Create activity
    activity_id = self.lineage.start_activity("generation")

    try:
        yield activity_id
    finally:
        # Record relationships when generation completes
        for input_id in input_ids:
            self.lineage.record_used(activity_id, input_id)
```

### PROV-JSON Export

```python
def export_prov_json(self, entity_id: str | None = None) -> dict:
    """Export lineage as W3C PROV-JSON."""
    graph = self.trace(entity_id) if entity_id else self.get_all()

    return {
        "prefix": {
            "persona": "https://persona.dev/prov/",
            "prov": "http://www.w3.org/ns/prov#"
        },
        "entity": {e.id: e.to_prov() for e in graph.entities},
        "activity": {a.id: a.to_prov() for a in graph.activities},
        "agent": {a.id: a.to_prov() for a in graph.agents},
        "wasGeneratedBy": [...],
        "used": [...],
        "wasAssociatedWith": [...],
        "wasDerivedFrom": [...]
    }
```

### Integrity Verification

```python
def verify_entity(self, entity_id: str) -> VerificationResult:
    """Verify entity integrity against stored hash."""
    entity = self.get_entity(entity_id)
    if not entity.content_hash:
        return VerificationResult(status="no_hash")

    current_hash = compute_hash(entity.path)
    if current_hash == entity.content_hash:
        return VerificationResult(status="verified")
    else:
        return VerificationResult(
            status="modified",
            expected=entity.content_hash,
            actual=current_hash
        )
```

---

## Related Documentation

- [F-125: Data Lineage & Provenance](../../roadmap/features/completed/F-125-data-lineage-provenance.md)
- [F-123: Generation Audit Trail](../../roadmap/features/completed/F-123-generation-audit-trail.md)
- [W3C PROV Data Model](https://www.w3.org/TR/prov-dm/)
- [PROV-JSON Specification](https://www.w3.org/Submission/prov-json/)
