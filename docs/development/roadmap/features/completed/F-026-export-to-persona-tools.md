# F-026: Export to Persona Tools

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-007 |
| **Milestone** | v0.5.0 |
| **Priority** | P2 |
| **Category** | Export |

## Problem Statement

Design teams use various persona tools (Figma, Miro, UXPressia, Adobe XD) for visualisation and stakeholder communication. Integration with these tools increases adoption by fitting into existing workflows.

## Design Approach

- Export to popular design tool formats
- Include persona images (generated or placeholder)
- Support template customisation per tool
- Enable bulk export for persona sets

## Implementation Tasks

- [ ] Research format requirements for each tool
- [ ] Implement Figma persona template export
- [ ] Implement Miro JSON export
- [ ] Implement UXPressia format export
- [ ] Implement Adobe XD export
- [ ] Add `persona export <id> --format <tool>` command
- [ ] Support bulk export (`persona export --all`)
- [ ] Add export preview
- [ ] Write integration tests

## Success Criteria

- [ ] Exports import correctly into target tools
- [ ] Visual formatting matches tool conventions
- [ ] All persona attributes preserved
- [ ] Bulk export handles large persona sets
- [ ] Preview accurate to final export
- [ ] Test coverage ≥ 80%

## Dependencies

- F-004: Persona generation
- F-005: Output formatting

---

## Related Documentation

- [UC-007: Customise Persona Format](../../../../use-cases/briefs/UC-007-custom-format.md)
- [G-03: Design Integration](../../../../guides/design-integration.md)
- [F-005: Output Formatting](F-005-output-formatting.md)
