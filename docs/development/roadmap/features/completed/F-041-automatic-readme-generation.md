# F-041: Automatic README Generation

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001, UC-002 |
| **Milestone** | v0.4.0 |
| **Priority** | P2 |
| **Category** | Output |

## Problem Statement

Generated output folders lack context about what they contain and how they were generated. Users returning to old outputs or sharing with colleagues need clear documentation of the generation context.

## Design Approach

- Auto-generate README.md in each output folder
- Include generation parameters and context
- Summarise personas generated
- Link to detailed documentation
- Human-readable and scannable

### README Template

```markdown
# Persona Generation Output

Generated: 2025-12-14 10:30:00
Experiment: user-research-q4

## Summary
- **Personas Generated**: 3
- **Provider**: Anthropic (claude-sonnet-4-5)
- **Source Files**: 5 (interviews.csv, feedback.json, ...)
- **Cost**: $0.45

## Personas
1. **Sarah Chen** - The Mobile Professional
2. **Marcus Johnson** - The Power User
3. **Priya Patel** - The Cautious Adopter

## Files
- `personas/` - Individual persona files
- `metadata.json` - Generation metadata
- `reasoning/` - LLM reasoning traces
```

## Implementation Tasks

- [ ] Create README template (Jinja2)
- [ ] Implement ReadmeGenerator class
- [ ] Extract summary from generation results
- [ ] Add persona overview section
- [ ] Link to documentation
- [ ] Make template customisable
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] README generated for every output
- [ ] Content accurate to generation
- [ ] Readable and scannable
- [ ] Custom templates supported
- [ ] Test coverage ≥ 80%

## Dependencies

- F-013: Timestamped output folders

---

## Related Documentation

- [Milestone v0.4.0](../../milestones/v0.4.0.md)
- [F-013: Timestamped Output](F-013-timestamped-output.md)
