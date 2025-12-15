# F-047: Dynamic Vendor Discovery

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-003, UC-004 |
| **Milestone** | v0.5.0 |
| **Priority** | P2 |
| **Category** | Config |

## Problem Statement

Users with custom vendor configurations or Ollama installations need their available vendors discovered automatically. Manual configuration verification is tedious.

## Design Approach

- Scan configuration directories for vendors
- Probe Ollama for running instances
- Report available and unavailable vendors
- Cache discovery results
- Refresh on demand

## Implementation Tasks

- [ ] Create VendorDiscovery class
- [ ] Scan ~/.persona/vendors/ for YAML
- [ ] Probe built-in vendor endpoints
- [ ] Detect Ollama instances
- [ ] Implement discovery caching
- [ ] Add `persona vendor discover` command
- [ ] Update `persona check` with discovery
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] All configured vendors discovered
- [ ] Ollama auto-detected when running
- [ ] Discovery cached for performance
- [ ] Clear status reporting
- [ ] Test coverage ≥ 80%

## Dependencies

- F-043: Custom vendor configuration

---

## Related Documentation

- [Milestone v0.5.0](../../milestones/v0.5.0.md)
- [F-043: Custom Vendor Configuration](F-043-custom-vendor-configuration.md)

