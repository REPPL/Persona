# F-061: Flexible Persona Count Specification

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001, UC-002 |
| **Milestone** | v0.7.0 |
| **Priority** | P2 |
| **Category** | Generation |

## Problem Statement

Users often don't know exactly how many personas they need. Rigid count specification ("exactly 3") doesn't reflect real-world usage patterns like "3-5 personas" or "about 4".

## Design Approach

- Support exact counts: `3`
- Support ranges: `3-5`
- Support approximate: `~4`, `about 4`
- Let LLM determine optimal count within range
- Report reasoning for chosen count

### Count Specification Formats

| Input | Interpretation | LLM Instruction |
|-------|----------------|-----------------|
| `3` | Exactly 3 | "Generate exactly 3 personas" |
| `3-5` | Between 3 and 5 | "Generate 3-5 personas based on data richness" |
| `~4` | Approximately 4 | "Generate around 4 personas (3-5 acceptable)" |
| `about 4` | Approximately 4 | Same as `~4` |
| `at least 3` | Minimum 3 | "Generate at least 3 personas" |

### CLI Interface

```bash
# Exact count
persona generate --from data.csv --count 3

# Range
persona generate --from data.csv --count "3-5"

# Approximate
persona generate --from data.csv --count "~4"
persona generate --from data.csv --count "about 4"
```

## Implementation Tasks

- [ ] Create CountSpecification parser
- [ ] Support exact counts
- [ ] Support range specifications
- [ ] Support approximate counts
- [ ] Update prompt templates for flexible counts
- [ ] Add count reasoning to output
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] All count formats parsed correctly
- [ ] LLM receives appropriate instructions
- [ ] Count reasoning included in output
- [ ] Flexible counts improve output quality
- [ ] Test coverage ≥ 80%

## Dependencies

- F-004: Persona generation pipeline

---

## Related Documentation

- [Milestone v0.7.0](../../milestones/v0.7.0.md)
- [F-004: Persona Generation](F-004-persona-generation.md)
