# F-028: Synthetic Data Generation

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-008 |
| **Milestone** | v0.1.0 |
| **Priority** | P2 |
| **Category** | Demo |

## Problem Statement

Testing Persona without real research data is difficult. New users need a way to evaluate the tool before committing their own data. A demo mode with synthetic data enables quick evaluation and is useful for tutorials and testing.

## Design Approach

- Generate realistic synthetic interview data
- Run full generation pipeline with sample data
- Explain each step as it progresses
- Show example output with cost breakdown
- Provide cleanup option for demo data

## Implementation Tasks

- [ ] Create `persona demo` CLI command
- [ ] Build synthetic interview data generator
- [ ] Implement step-by-step progress display
- [ ] Show explanations for each pipeline stage
- [ ] Display cost breakdown after completion
- [ ] Create sample data templates (various domains)
- [ ] Add `--clean` flag to remove demo data
- [ ] Support `--domain` flag for domain-specific demos
- [ ] Write integration tests

## Success Criteria

- [ ] Demo completes successfully with API key
- [ ] Synthetic data realistic enough for evaluation
- [ ] Step explanations educational for new users
- [ ] Cost displayed clearly
- [ ] Cleanup removes all demo artifacts
- [ ] Multiple domains available
- [ ] Test coverage ≥ 80%

## Dependencies

- F-001: Data loading
- F-004: Persona generation
- F-008: CLI interface

---

## Related Documentation

- [UC-008: Demo Without Real Data](../../../../use-cases/briefs/UC-008-demo-mode.md)
- [T-01: Getting Started](../../../../tutorials/01-getting-started.md)
- [F-008: CLI Interface](F-008-cli-interface.md)
