# F-022: Data Preview

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001 |
| **Milestone** | v0.1.0 |
| **Priority** | P1 |
| **Category** | Data |

## Problem Statement

Users want to see what data will be processed before incurring LLM costs. Currently they must trust the system blindly without visibility into what's being sent to the AI model.

## Design Approach

- Show detected file format and structure
- Display token count and estimated cost
- Preview sample content (first N lines/items)
- Highlight potential issues (encoding, format errors)
- Allow dry-run without API calls

## Implementation Tasks

- [ ] Create `persona preview <source>` CLI command
- [ ] Implement format detection display
- [ ] Show token count breakdown by file
- [ ] Calculate and display estimated cost
- [ ] Preview first N items of content
- [ ] Add warning for potential issues
- [ ] Support folder preview (multiple files)
- [ ] Add `--dry-run` flag to generate command
- [ ] Write unit tests

## Success Criteria

- [ ] Format correctly detected for all supported types
- [ ] Token count matches actual usage within 5%
- [ ] Cost estimate accurate to pricing
- [ ] Sample content representative of full data
- [ ] Clear warnings for problematic files
- [ ] Test coverage ≥ 80%

## Dependencies

- F-001: Data loading
- F-007: Cost estimation

---

## Related Documentation

- [UC-001: Generate Personas](../../../../use-cases/briefs/UC-001-generate-personas.md)
- [F-001: Data Loading](F-001-data-loading.md)
- [F-007: Cost Estimation](F-007-cost-estimation.md)
