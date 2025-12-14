# F-060: Multi-File Handling with Separators

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001 |
| **Milestone** | v0.7.0 |
| **Priority** | P1 |
| **Category** | Data |

## Problem Statement

When combining multiple data files for persona generation, the LLM needs clear boundaries between sources. Without proper separators, the model may confuse data from different participants.

## Design Approach

- Insert clear separators between files
- Include source metadata in separators
- Support customisable separator format
- Track which data came from which file
- Preserve file attribution in output

### Separator Format

```markdown
---
SOURCE: participant-003.md
TYPE: Interview Transcript
DATE: 2025-12-10
INDEX: 3 of 15
---

[File content here...]

---
END SOURCE: participant-003.md
---
```

### Configuration

```yaml
# experiment.yaml
data:
  separator:
    style: detailed  # minimal, standard, detailed
    include_metadata: true
    custom_template: null  # Optional Jinja2 template
```

## Implementation Tasks

- [ ] Create FileCombiner class
- [ ] Implement separator templates
- [ ] Add metadata extraction from files
- [ ] Support custom separator templates
- [ ] Track source attribution
- [ ] Add separator style options
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Clear separation between sources
- [ ] Metadata included in separators
- [ ] Custom templates supported
- [ ] Source attribution tracked
- [ ] Test coverage ≥ 80%

## Dependencies

- F-001: Multi-format data loading
- F-059: Folder processing

---

## Related Documentation

- [Milestone v0.7.0](../../milestones/v0.7.0.md)
- [F-001: Data Loading](F-001-data-loading.md)

