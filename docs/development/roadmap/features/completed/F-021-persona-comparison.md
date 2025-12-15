# F-021: Persona Comparison

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-004 |
| **Milestone** | v0.3.0 |
| **Priority** | P1 |
| **Category** | Analysis |

## Problem Statement

Researchers need to compare personas generated with different settings (models, temperatures, prompts) or from different datasets. Currently there's no mechanism to view differences side-by-side or quantify similarity.

## Design Approach

- Implement side-by-side comparison view
- Highlight attribute-level differences
- Calculate similarity scores using embeddings
- Support comparison across variations, models, or datasets
- Export comparison report for documentation

## Implementation Tasks

- [ ] Create `persona compare <id1> <id2>` CLI command
- [ ] Implement diff algorithm for persona attributes
- [ ] Build side-by-side Rich table output
- [ ] Calculate embedding-based similarity scores
- [ ] Highlight differences with colour coding
- [ ] Support multi-persona comparison (> 2)
- [ ] Export comparison as Markdown/HTML
- [ ] Add comparison to experiment workflow
- [ ] Write unit tests

## Success Criteria

- [ ] Differences clearly visible in terminal output
- [ ] Similarity score correlates with human judgement
- [ ] Comparison works across different models/settings
- [ ] Export suitable for stakeholder presentations
- [ ] Supports at least 4 personas in single comparison
- [ ] Test coverage ≥ 80%

## Dependencies

- F-004: Persona generation
- F-006: Experiment management
- Embedding model for similarity

---

## Related Documentation

- [UC-004: Compare Persona Variations](../../../../use-cases/briefs/UC-004-compare-variations.md)
- [F-004: Persona Generation](F-004-persona-generation.md)
- [F-006: Experiment Management](F-006-experiment-management.md)

