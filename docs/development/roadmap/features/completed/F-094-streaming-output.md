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
- Show token usage incrementally
- Graceful degradation in non-TTY environments

## Implementation Tasks

- [x] Create streaming output handler with Rich Live
- [x] Implement per-persona progress tracking
- [x] Add ETA calculation based on completed items
- [x] Show persona names/summaries as they complete
- [x] Display running token count
- [x] Handle non-TTY output (line-by-line fallback)
- [x] Add `--no-progress` flag to disable
- [x] Write tests for streaming output

## Success Criteria

- [x] Progress bar shows during generation
- [x] ETA updates as personas complete
- [x] Completed personas shown incrementally
- [x] Works without TTY (simplified output)
- [x] Token count visible during generation
- [x] Test coverage ≥ 80%

## Implementation Details

### StreamingOutput Class

The `StreamingOutput` class in `src/persona/ui/streaming.py` provides:

- **Rich Live display**: Real-time updates using Rich's Live component
- **Progress bar**: Shows completion percentage with ETA
- **Persona tree**: Displays completed personas as they finish
- **Token tracking**: Shows input/output tokens and estimated cost
- **Non-TTY fallback**: Line-by-line output for pipes and redirects

### SimpleProgress Class

Fallback for non-TTY environments:

- Line-by-line progress messages
- Basic completion summary
- Works in CI/CD pipelines and scripts

### CLI Flag

```bash
# With progress (default)
persona generate --from ./data.csv

# Without progress bar
persona generate --from ./data.csv --no-progress
```

### Progress Handler Factory

```python
from persona.ui.streaming import get_progress_handler

# Automatically selects appropriate handler
handler = get_progress_handler(
    console=console,
    show_progress=True,  # Set False for --no-progress
)

callback = handler.start(total=3, provider="anthropic", model="claude")
# ... generation happens ...
handler.finish(personas=result.personas, input_tokens=100, output_tokens=50)
```

## Display Layout

### During Generation (TTY)

```
Generating personas... ━━━━━━━━━━━━━━━━━━━━ 67% │ 2/3 │ ETA: 00:45

Personas
├─ ✓ Alex Chen (Product Manager)
├─ ✓ Jordan Smith (Developer)
└─ ● Generating persona 3...

Elapsed: 1m 30s │ Tokens: 4,521 │ Cost: calculating...
```

### Non-TTY Output

```
Generating 3 personas...
Provider: anthropic
Model: claude-sonnet-4-20250514

[0/3] Loading input data...
[0/3] Generating with anthropic...
[0/3] Parsing response...
[3/3] Generation complete!

✓ Generation complete (2m 15s)
```

## Dependencies

- F-016: Interactive Rich UI (provides Rich integration)
- F-063: Token count tracking (provides token data)
- F-004: Persona generation pipeline (provides generation events)

---

## Related Documentation

- [F-016: Interactive Rich UI](./F-016-interactive-rich-ui.md)
- [F-063: Token Count Tracking](./F-063-token-count-tracking.md)
- [ADR-0005: Typer + Rich CLI Framework](../../../../decisions/adrs/ADR-0005-cli-framework.md)
