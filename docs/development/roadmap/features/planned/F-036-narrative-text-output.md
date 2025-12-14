# F-036: Narrative Text Output

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001, UC-006 |
| **Milestone** | v0.4.0 |
| **Priority** | P1 |
| **Category** | Output |

## Problem Statement

Stakeholders often need persona presentations that flow as narrative prose rather than structured data. Current JSON and Markdown outputs are technical and not suitable for design presentations or empathy-building workshops.

## Design Approach

- Generate flowing narrative descriptions of each persona
- Support first-person and third-person perspectives
- Include "day in the life" scenarios
- Suitable for presentations and design documentation

### Output Format

```markdown
# Meet Sarah Chen

Sarah is a 32-year-old marketing manager living in an urban area...

## A Day in Sarah's Life

Sarah's morning begins with a quick check of her phone...

## What Drives Sarah

At her core, Sarah values efficiency and work-life balance...
```

## Implementation Tasks

- [ ] Create NarrativeFormatter class
- [ ] Implement first-person perspective option
- [ ] Implement third-person perspective option
- [ ] Add "day in the life" narrative generator
- [ ] Create narrative prompt templates
- [ ] Add `--format narrative` CLI option
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Narratives read naturally as prose
- [ ] Both perspectives work correctly
- [ ] Narratives maintain accuracy to source data
- [ ] Output suitable for presentations
- [ ] Test coverage ≥ 80%

## Dependencies

- F-005: Output formatting

---

## Related Documentation

- [Milestone v0.4.0](../../milestones/v0.4.0.md)
- [F-005: Output Formatting](F-005-output-formatting.md)

