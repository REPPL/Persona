# F-094: Streaming Output Display

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Cases** | UC-001, UC-002 |
| **Milestone** | v1.0.0 |
| **Priority** | P2 |
| **Category** | CLI |

## Problem Statement

Persona generation can take several minutes when generating multiple personas. Currently, users see:

- No feedback until generation completes
- No indication of progress or remaining time
- No visibility into which persona is being generated
- No intermediate results

Users need real-time feedback during long-running operations.

## Design Approach

- Use Rich's Live display for real-time updates
- Show progress bar with ETA
- Display completed personas as they finish
- Stream LLM responses (if provider supports)
- Show token usage incrementally
- Graceful degradation in non-TTY environments

## Implementation Tasks

- [ ] Create streaming output handler with Rich Live
- [ ] Implement per-persona progress tracking
- [ ] Add ETA calculation based on completed items
- [ ] Show persona names/summaries as they complete
- [ ] Integrate with LLM streaming (if available)
- [ ] Display running token count
- [ ] Handle non-TTY output (line-by-line fallback)
- [ ] Add `--no-progress` flag to disable
- [ ] Write tests for streaming output

## Success Criteria

- [ ] Progress bar shows during generation
- [ ] ETA updates as personas complete
- [ ] Completed personas shown incrementally
- [ ] Works without TTY (simplified output)
- [ ] Token count visible during generation
- [ ] Test coverage ≥ 80%

## Display Layout

### During Generation

```
Generating personas... ━━━━━━━━━━━━━━━━━━━━ 67% │ 2/3 │ ETA: 00:45

Completed:
├─ Persona 1: Alex Chen (Product Manager) ✓
│  └─ Goals: improve team velocity, reduce technical debt
├─ Persona 2: Jordan Smith (Developer) ✓
│  └─ Goals: write clean code, learn new technologies
└─ Persona 3: Generating...

Tokens: 4,521 input │ 2,847 output │ ~$0.023
```

### LLM Streaming (Optional)

```
Generating Persona 3...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Name: Riley Morgan
Role: UX Designer
Background: ▋

[Streaming response...]
```

### Completion

```
✓ Generation complete

┌─────────────────────────────────────────────────────────────────┐
│ Generated 3 personas in 2m 15s                                 │
│ Output: outputs/20241215_143022/                               │
│ Tokens: 6,842 input │ 4,231 output │ Total: $0.034             │
└─────────────────────────────────────────────────────────────────┘
```

## Non-TTY Output

```
[1/3] Generating persona 1...
[1/3] Complete: Alex Chen (Product Manager)
[2/3] Generating persona 2...
[2/3] Complete: Jordan Smith (Developer)
[3/3] Generating persona 3...
[3/3] Complete: Riley Morgan (UX Designer)

Generated 3 personas in 2m 15s
Output: outputs/20241215_143022/
```

## Dependencies

- F-016: Interactive Rich UI (provides Rich integration)
- F-063: Token count tracking (provides token data)
- F-004: Persona generation pipeline (provides generation events)

---

## Related Documentation

- [F-016: Interactive Rich UI](../completed/F-016-interactive-rich-ui.md)
- [F-063: Token Count Tracking](../completed/F-063-token-count-tracking.md)
- [ADR-0005: Typer + Rich CLI Framework](../../../decisions/adrs/ADR-0005-cli-framework.md)
