# R-032: Persona Evolution & Versioning

## Executive Summary

This research analyses approaches for tracking persona changes over time, enabling version history, diff comparison, and evolution tracking. As personas are refined through multiple iterations, version control becomes essential for research reproducibility and audit trails. Recommended approach: Git-inspired versioning with content-addressable storage and semantic diff capabilities.

---

## Research Context

| Attribute | Value |
|-----------|-------|
| **ID** | R-032 |
| **Category** | Research Workflows |
| **Status** | Complete |
| **Priority** | P3 |
| **Informs** | Future persona versioning features |

---

## Problem Statement

Research workflows require tracking persona evolution:
- How did this persona change over iterations?
- What was the persona like before this edit?
- Can we revert to a previous version?
- How do different generation parameters affect results?
- What changes were made and why?

Current personas are point-in-time snapshots without history.

---

## State of the Art Analysis

### Versioning Models

| Model | Description | Granularity |
|-------|-------------|-------------|
| **Git-style** | Content-addressable, commits | Fine |
| **Document DB** | Revision IDs, branches | Medium |
| **Event sourcing** | Append-only events | Very fine |
| **Snapshot-based** | Periodic full copies | Coarse |

### Git-Style Versioning

```python
@dataclass
class PersonaVersion:
    id: str  # SHA-256 of content
    content: dict
    parent_id: str | None
    timestamp: datetime
    message: str
    author: str
    metadata: dict

class PersonaRepository:
    def commit(
        self,
        persona: dict,
        message: str,
        parent: str | None = None
    ) -> PersonaVersion:
        content_hash = self._hash_content(persona)
        version = PersonaVersion(
            id=content_hash,
            content=persona,
            parent_id=parent,
            timestamp=datetime.now(),
            message=message,
            author=self._get_author()
        )
        self._store(version)
        return version

    def get(self, version_id: str) -> PersonaVersion:
        return self._load(version_id)

    def history(self, head: str) -> list[PersonaVersion]:
        versions = []
        current = head
        while current:
            version = self.get(current)
            versions.append(version)
            current = version.parent_id
        return versions
```

### Diff Capabilities

**Structural Diff:**
```python
def diff_personas(old: dict, new: dict) -> PersonaDiff:
    changes = []

    # Added fields
    for key in set(new.keys()) - set(old.keys()):
        changes.append(Change(type="added", path=key, value=new[key]))

    # Removed fields
    for key in set(old.keys()) - set(new.keys()):
        changes.append(Change(type="removed", path=key, value=old[key]))

    # Modified fields
    for key in set(old.keys()) & set(new.keys()):
        if old[key] != new[key]:
            changes.append(Change(
                type="modified",
                path=key,
                old_value=old[key],
                new_value=new[key]
            ))

    return PersonaDiff(changes=changes)
```

**Semantic Diff:**
```python
class SemanticDiff:
    def __init__(self, encoder: SentenceEncoder):
        self.encoder = encoder

    def diff(self, old: dict, new: dict) -> SemanticDiffResult:
        old_text = self._to_text(old)
        new_text = self._to_text(new)

        old_embedding = self.encoder.encode(old_text)
        new_embedding = self.encoder.encode(new_text)

        similarity = cosine_similarity(old_embedding, new_embedding)

        return SemanticDiffResult(
            similarity=similarity,
            significant_changes=similarity < 0.9,
            structural_diff=self._structural_diff(old, new)
        )
```

### Branching Model

```
main
 │
 ├── v1 (initial generation)
 │
 ├── v2 (refined demographics)
 │    │
 │    └── experiment/variant-a (alternative goals)
 │
 └── v3 (final version)
```

### Storage Options

| Storage | Performance | Deduplication | Query |
|---------|-------------|---------------|-------|
| SQLite | ✅ | ❌ | ✅ |
| Git repo | ⚠️ | ✅ | ⚠️ |
| Object store | ✅ | ✅ | ⚠️ |
| Document DB | ✅ | ⚠️ | ✅ |

---

## Recommended Approach

### Hybrid Version System

```
┌─────────────────────────────────────────────────────────────┐
│                 Persona Version System                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Content    │───▶│   Version    │───▶│    Index     │  │
│  │    Store     │    │    Graph     │    │   (SQLite)   │  │
│  │  (objects/)  │    │  (refs/)     │    │              │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
│  Content Store: SHA-256 addressed JSON blobs                │
│  Version Graph: Parent-child relationships                   │
│  Index: Fast queries, search, metadata                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### CLI Commands

```bash
# Create version
persona version commit PERSONA_ID -m "Refined demographics"

# View history
persona version log PERSONA_ID

# Show diff
persona version diff PERSONA_ID v1 v2

# Revert to version
persona version checkout PERSONA_ID v1

# Create branch
persona version branch PERSONA_ID experiment/new-approach

# Merge changes
persona version merge experiment/new-approach main
```

### Output Examples

**Version Log:**
```
Persona: customer-sarah
══════════════════════════════════════════════════════════════

v3 (HEAD, main) - 2025-01-15 14:30
  Finalised persona for research study
  Author: researcher@example.com

v2 - 2025-01-15 10:15
  Refined demographics based on interview data
  Author: researcher@example.com

v1 - 2025-01-14 16:45
  Initial generation from survey data
  Author: ai/claude-sonnet-4-20250514
```

**Diff Output:**
```
Comparing v1 → v2

Demographics
────────────
- age: 28
+ age: 32
- location: "London"
+ location: "Manchester"

Goals (modified)
────────────────
~ "Save time on daily tasks"
  → "Save time on work-related tasks"
+ "Improve work-life balance" (added)

Semantic similarity: 87%
```

### Data Model

```python
@dataclass
class PersonaVersion:
    id: str  # Content hash
    persona_id: str  # Logical persona identifier
    content: dict
    parent_ids: list[str]  # Support merges
    timestamp: datetime
    message: str
    author: str
    generation_config: dict | None  # If AI-generated
    lineage_id: str | None  # Link to data lineage

@dataclass
class PersonaRef:
    name: str  # e.g., "main", "experiment/v2"
    version_id: str
    persona_id: str

@dataclass
class PersonaDiff:
    old_version: str
    new_version: str
    changes: list[Change]
    semantic_similarity: float
```

---

## Evaluation Matrix

| Feature | Git-style | Document DB | Event Source |
|---------|-----------|-------------|--------------|
| Fine-grained history | ✅ | ⚠️ | ✅ |
| Easy rollback | ✅ | ✅ | ⚠️ |
| Branching | ✅ | ⚠️ | ❌ |
| Deduplication | ✅ | ❌ | ⚠️ |
| Query performance | ⚠️ | ✅ | ⚠️ |
| Complexity | ⚠️ | ✅ | ⚠️ |

---

## Recommendation

Implement Git-inspired versioning with:
1. Content-addressable storage
2. Parent-child version graph
3. SQLite index for queries
4. Semantic diff capabilities
5. Branch/merge support

---

## References

1. [Git Internals](https://git-scm.com/book/en/v2/Git-Internals-Plumbing-and-Porcelain)
2. [Event Sourcing](https://martinfowler.com/eaaDev/EventSourcing.html)
3. [Content-Addressable Storage](https://en.wikipedia.org/wiki/Content-addressable_storage)
4. [JSON Patch RFC 6902](https://tools.ietf.org/html/rfc6902)

---

## Related Documentation

- [F-125: Data Lineage & Provenance](../roadmap/features/completed/F-125-data-lineage-provenance.md)
- [ADR-0027: Data Lineage Implementation](../decisions/adrs/ADR-0027-data-lineage-implementation.md)

---

**Status**: Complete
