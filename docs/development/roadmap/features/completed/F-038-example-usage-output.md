# F-038: Example Usage Output

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001, UC-006, UC-008 |
| **Milestone** | v0.4.0 |
| **Priority** | P2 |
| **Category** | Output |

## Problem Statement

Design teams need practical examples of how each persona would interact with products. Abstract goals and pain points don't directly translate to actionable design decisions without concrete usage scenarios.

## Design Approach

- Generate example user journeys for each persona
- Include friction points and delight moments
- Create feature usage predictions
- Support multiple product contexts

### Output Format

```markdown
## Example Usage: Sarah Chen

### Morning Check-in (Commute)
Sarah opens the app on her phone during her train commute...
- **Friction Point**: Slow loading on mobile network
- **Delight Moment**: Quick access to yesterday's summary

### Feature Usage Predictions
| Feature | Usage Likelihood | Reason |
|---------|-----------------|--------|
| Dashboard | Daily | Morning routine |
| Reports | Weekly | Team meetings |
| Export | Monthly | Stakeholder updates |
```

## Implementation Tasks

- [ ] Create UsageScenarioGenerator class
- [ ] Implement user journey templates
- [ ] Add friction/delight analysis
- [ ] Create feature usage predictor
- [ ] Add `--include examples` CLI option
- [ ] Support custom product context injection
- [ ] Write unit tests
- [ ] Write integration tests

## Success Criteria

- [ ] Scenarios feel realistic and actionable
- [ ] Friction points derive from pain points
- [ ] Feature predictions are justified
- [ ] Works with custom product contexts
- [ ] Test coverage ≥ 80%

## Dependencies

- F-005: Output formatting
- F-004: Persona generation pipeline

---

## Related Documentation

- [Milestone v0.4.0](../../milestones/v0.4.0.md)
- [F-005: Output Formatting](F-005-output-formatting.md)

