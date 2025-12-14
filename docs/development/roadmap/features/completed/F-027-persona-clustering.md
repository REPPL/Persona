# F-027: Persona Clustering

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-006 |
| **Milestone** | v0.7.0 |
| **Priority** | P2 |
| **Category** | Analysis |

## Problem Statement

Large datasets may yield many similar personas. Automatic clustering helps identify redundant personas and suggests consolidation, reducing cognitive load for stakeholders while ensuring coverage.

## Design Approach

- Use embedding similarity to group related personas
- Visualise clusters in terminal
- Suggest consolidation candidates
- Preserve diversity while reducing redundancy
- Support manual cluster adjustment

## Implementation Tasks

- [ ] Implement persona embedding generation
- [ ] Build clustering algorithm (k-means or HDBSCAN)
- [ ] Create `persona cluster` CLI command
- [ ] Visualise clusters with Rich tree/table
- [ ] Generate consolidation suggestions
- [ ] Add similarity threshold configuration
- [ ] Support manual cluster assignment
- [ ] Export cluster report
- [ ] Write unit tests

## Success Criteria

- [ ] Similar personas grouped correctly
- [ ] Cluster visualisation intuitive
- [ ] Consolidation suggestions actionable
- [ ] Diversity preserved (no over-consolidation)
- [ ] Works with 50+ personas efficiently
- [ ] Test coverage ≥ 80%

## Dependencies

- F-004: Persona generation
- F-020: Batch processing
- Embedding model for similarity

---

## Related Documentation

- [UC-006: Process Large Datasets](../../../../use-cases/briefs/UC-006-large-datasets.md)
- [F-020: Batch Data Processing](F-020-batch-data-processing.md)
- [F-021: Persona Comparison](F-021-persona-comparison.md)

