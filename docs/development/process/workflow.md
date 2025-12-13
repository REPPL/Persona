# Implementation Workflow

Phased implementation workflow for Persona development.

## Overview

This workflow emphasises AI transparency and documentation-as-you-go.

## Phased Workflow

```
Phase 0: Setup
├── Create branch: milestone/vX.Y.0
├── Create session file: .work/agents/session.yaml
└── Run readiness assessment (≥80% to proceed)

Phase 1: Foundation
├── Implement base components
├── Tests + doc sync checkpoint
└── Commit with thinking log

Phase 2: Core Features
├── Implement features (respect dependencies)
├── Per-feature: tests + UAT + doc sync
└── Commit with thinking log for each feature

Phase 3: Polish
├── Error handling, edge cases
├── Full test suite (≥80% coverage)
└── Documentation audit

Phase 4: Release
├── Thorough UAT (USER RUNS, USER CONFIRMS)
├── Security audit
├── Commit retrospective
├── Merge to main (USER APPROVES)
└── Tag: vX.Y.0
```

## Version Tagging

- `v0.1.0-planning` - Planning documentation only (exception)
- `v0.1.0`, `v0.2.0`, etc. - Minor version releases only
- **No alpha/beta pre-release tags**

## User Intervention Points

| Point | Type | When | Why |
|-------|------|------|-----|
| Scope confirmation | Decision | Phase 0 | Define what's in/out |
| Architecture questions | Decision | Phase 1 | Major design choices |
| UAT for UI features | Verification | Phase 2-3 | Visual inspection |
| Final UAT | Verification | Phase 4 | Comprehensive acceptance |
| Merge approval | Approval | Phase 4 | Main branch protection |

## Documentation Sync Checkpoint

Before EVERY commit that changes functionality:

1. **Command Audit** - Verify CLI matches docs
2. **Feature Audit** - Verify feature spec matches implementation
3. **Status Audit** - Update milestone status

## Thinking Logs

Each significant commit includes a thinking log in devlogs:

```markdown
# Thinking Log: [Feature Name]

## Context
[What prompted this change]

## Approach Considered
[Options evaluated]

## Decision Made
[What was chosen and why]

## Challenges
[Problems solved]

## Outcome
[Result and follow-up]
```

---

## Related Documentation

- [Methodology](methodology/)
- [AI Contributions](../ai-contributions.md)
- [Retrospectives](retrospectives/)
