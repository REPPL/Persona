# F-048: Dynamic Model Discovery

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-003, UC-004 |
| **Milestone** | v0.5.0 |
| **Priority** | P2 |
| **Category** | Config |

## Problem Statement

Available models change frequently (new releases, deprecations). Users need to know which models are currently available for their configured vendors.

## Design Approach

- Query vendor APIs for available models
- Merge with custom model configurations
- Report deprecation warnings
- Cache model lists with TTL
- Support offline mode with cached data

## Implementation Tasks

- [ ] Create ModelDiscovery class
- [ ] Implement API queries per vendor
- [ ] Merge custom model configs
- [ ] Detect deprecated models
- [ ] Implement caching with TTL
- [ ] Add `persona model discover` command
- [ ] Add `persona model check <id>` command
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Models discovered from all vendors
- [ ] Custom models included in list
- [ ] Deprecation warnings shown
- [ ] Offline mode works with cache
- [ ] Test coverage ≥ 80%

## Dependencies

- F-044: Custom model configuration
- F-047: Dynamic vendor discovery

---

## Related Documentation

- [Milestone v0.5.0](../../milestones/v0.5.0.md)
- [Model Cards](../../../../reference/model-cards.md)

