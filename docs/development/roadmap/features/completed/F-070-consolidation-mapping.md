# F-070: Consolidation Mapping

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-002, UC-008 |
| **Milestone** | v0.8.0 |
| **Priority** | P2 |
| **Category** | Analysis |

## Problem Statement

When generating personas from multiple models or multiple runs, users need to understand relationships between outputs: which personas are similar, which are unique, and how they might be consolidated.

## Design Approach

- Compare personas across generations
- Calculate similarity scores
- Identify potential merges
- Track lineage across runs
- Visualise relationships

### Similarity Analysis

```python
@dataclass
class PersonaSimilarity:
    persona_a: str
    persona_b: str
    similarity_score: float  # 0.0 to 1.0
    matching_attributes: list[str]
    divergent_attributes: list[str]
    merge_recommendation: bool
```

### Consolidation Map

```
Consolidation Map
═══════════════════════════════════════════════════

Run 1 (Claude)          Run 2 (GPT-5)           Consolidated
─────────────────────────────────────────────────────────────
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│ Tech Lead   │─────────│ Senior Dev  │────────→│ Tech Lead   │
│ Taylor      │  85%    │ Alex        │         │ (merged)    │
└─────────────┘         └─────────────┘         └─────────────┘

┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│ New Grad    │─────────│ Junior Dev  │────────→│ New Grad    │
│ Jordan      │  92%    │ Sam         │         │ (merged)    │
└─────────────┘         └─────────────┘         └─────────────┘

┌─────────────┐                                 ┌─────────────┐
│ Manager     │─────────────────────────────────│ Manager     │
│ Morgan      │  unique                         │ (unique)    │
└─────────────┘                                 └─────────────┘
```

## Implementation Tasks

- [ ] Create ConsolidationMapper class
- [ ] Implement persona similarity calculation
- [ ] Add attribute-level comparison
- [ ] Generate merge recommendations
- [ ] Track persona lineage
- [ ] Create visualisation output
- [ ] Add `persona consolidate` command
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Similarity scores accurate
- [ ] Merge recommendations helpful
- [ ] Lineage tracking works
- [ ] Visualisation clear
- [ ] Test coverage ≥ 80%

## Dependencies

- F-066: Multi-model persona generation
- F-050: Experiment history

---

## Related Documentation

- [Milestone v0.8.0](../../milestones/v0.8.0.md)
- [F-066: Multi-Model Generation](F-066-multi-model-generation.md)
