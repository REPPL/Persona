# F-068: Coverage Analysis

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-002, UC-007 |
| **Milestone** | v0.8.0 |
| **Priority** | P2 |
| **Category** | Analysis |

## Problem Statement

Users need to understand how well their personas represent the source data. Are all themes covered? Are any data sources overrepresented or underrepresented?

## Design Approach

- Analyse source data for key themes
- Track which data supports which personas
- Calculate coverage metrics
- Identify gaps and overlaps
- Generate coverage visualisation

### Coverage Metrics

```python
@dataclass
class CoverageAnalysis:
    theme_coverage: dict[str, float]      # Theme → coverage %
    source_utilisation: dict[str, float]  # Source file → utilisation %
    persona_backing: dict[str, list[str]] # Persona → supporting sources
    gaps: list[str]                       # Uncovered themes
    overlaps: list[tuple[str, str]]       # Heavily overlapping personas
```

### CLI Output

```
📊 Coverage Analysis

Theme Coverage:
  ✓ User onboarding        100% (3 personas)
  ✓ Payment friction        85% (2 personas)
  ✓ Mobile experience       70% (2 personas)
  ⚠ Enterprise needs        30% (1 persona)
  ✗ Accessibility           0% (gap)

Source Utilisation:
  ├─ participant-001.md     High (supports 2 personas)
  ├─ participant-002.md     Medium (supports 1 persona)
  └─ participant-003.md     Low (minimal representation)

Suggestions:
  1. Add more data sources covering accessibility
  2. Consider splitting "User onboarding" into sub-themes
  3. Participant 003 may need dedicated persona
```

## Implementation Tasks

- [ ] Create CoverageAnalyser class
- [ ] Implement theme extraction
- [ ] Track source-to-persona mapping
- [ ] Calculate coverage percentages
- [ ] Identify gaps and overlaps
- [ ] Generate coverage report
- [ ] Add suggestions engine
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Theme coverage calculated accurately
- [ ] Source utilisation tracked
- [ ] Gaps identified correctly
- [ ] Actionable suggestions generated
- [ ] Test coverage ≥ 80%

## Dependencies

- F-004: Persona generation pipeline
- F-064: Data file listing

---

## Related Documentation

- [Milestone v0.8.0](../../milestones/v0.8.0.md)
- [F-064: Data File Listing](F-064-data-file-listing.md)

