# F-040: Optional Output Sections

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001, UC-006 |
| **Milestone** | v0.4.0 |
| **Priority** | P2 |
| **Category** | Output |

## Problem Statement

Different stakeholders need different information. Developers may not need empathy maps, whilst designers may not need technical metrics. Users need granular control over which sections appear in output.

## Design Approach

- Configurable output sections
- Include/exclude via CLI and config
- Section presets for common use cases
- Maintain data integrity (full data always stored)

### Available Sections

| Section | Default | Use Case |
|---------|---------|----------|
| Demographics | Always | All |
| Goals | Always | All |
| Pain Points | Always | All |
| Behaviours | On | Design |
| Motivations | On | Research |
| Quotes | On | Empathy |
| Evidence | Off | Research |
| Reasoning | Off | Audit |
| Metadata | Off | Technical |

## Implementation Tasks

- [ ] Define section enum and defaults
- [ ] Create section configuration schema
- [ ] Implement section filtering in formatters
- [ ] Add `--include` and `--exclude` CLI options
- [ ] Create section presets (design, research, minimal)
- [ ] Update all formatters to respect settings
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] All sections individually controllable
- [ ] Presets work correctly
- [ ] Full data always preserved in JSON
- [ ] CLI options intuitive
- [ ] Test coverage ≥ 80%

## Dependencies

- F-005: Output formatting

---

## Related Documentation

- [Milestone v0.4.0](../../milestones/v0.4.0.md)
- [F-005: Output Formatting](F-005-output-formatting.md)
