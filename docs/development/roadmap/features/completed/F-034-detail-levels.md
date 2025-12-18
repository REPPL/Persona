# F-034: Detail Levels

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001, UC-005 |
| **Milestone** | v0.3.0 |
| **Priority** | P1 |
| **Category** | Variation |

## Problem Statement

Beyond structural complexity, users need control over the narrative detail in persona descriptions. Some contexts require brief, scannable personas whilst others need rich narrative descriptions for empathy-building.

## Design Approach

- Two detail levels: minimal, detailed
- Orthogonal to complexity levels (can combine)
- Affects prose length and descriptive depth
- Configurable via CLI and experiment config

### Detail Definitions

| Level | Description Length | Quote Style | Narrative |
|-------|-------------------|-------------|-----------|
| Minimal | 1-2 sentences per section | Keywords only | Bullet points |
| Detailed | 3-5 sentences per section | Full quotes | Flowing prose |

## Implementation Tasks

- [ ] Define detail level enum (minimal, detailed)
- [ ] Create detail-specific prompt templates
- [ ] Implement output formatting per detail level
- [ ] Add `--detail` CLI flag
- [ ] Add detail to experiment config
- [ ] Combine with complexity levels
- [ ] Update token estimation for detail levels
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Both levels produce valid personas
- [ ] Minimal personas are 40% shorter in output
- [ ] Detailed personas include narrative flow
- [ ] Combines correctly with complexity levels
- [ ] Test coverage ≥ 80%

## Dependencies

- F-004: Persona generation pipeline
- F-033: Complexity levels

---

## Related Documentation

- [Milestone v0.3.0](../../milestones/v0.3.0.md)
- [F-033: Complexity Levels](F-033-complexity-levels.md)
- [F-035: Variation Combinations](F-035-variation-combinations.md)
