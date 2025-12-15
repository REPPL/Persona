# F-099: Real-Time Generation Monitor

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001, UC-003 |
| **Milestone** | v1.2.0 |
| **Priority** | P1 |
| **Category** | TUI |

## Problem Statement

During persona generation, users want to see progress in real-time: which personas are being generated, current token usage, estimated costs, and any errors that occur. The current CLI output scrolls away; a dedicated monitor widget keeps key information visible.

## Design Approach

- Dedicated generation monitor screen/widget
- Real-time progress updates via async events
- Token and cost tracking display
- Error highlighting and recovery options
- Streaming output from LLM responses

### Monitor Layout

```
┌─────────────────────────────────────────────────────────────┐
│ GENERATION MONITOR                              [C] Cancel  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   Experiment: exp-001-marketing-personas                    │
│   Provider:   Anthropic (Claude Sonnet 4)                   │
│   Started:    14:32:15                                      │
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ Progress ████████████░░░░░░░░ 60% (6/10 personas)   │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│   Current: Generating "Product Manager - Enterprise"...     │
│                                                             │
│   ┌─ Completed ─────────────────────────────────────────┐   │
│   │ ✓ Marketing Director - B2B          (1,234 tokens)  │   │
│   │ ✓ Sales Representative - SMB        (1,456 tokens)  │   │
│   │ ✓ Customer Success Manager          (1,123 tokens)  │   │
│   │ ✓ Technical Writer - Documentation  (1,567 tokens)  │   │
│   │ ✓ UX Designer - Enterprise          (1,345 tokens)  │   │
│   │ ⏳ Product Manager - Enterprise      (streaming...)  │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Tokens: 7,725 │ Est. Cost: $0.23 │ Elapsed: 00:02:34       │
└─────────────────────────────────────────────────────────────┘
```

### Widget Components

```python
# src/persona/tui/widgets/progress_panel.py

from textual.widgets import Static, ProgressBar
from textual.reactive import reactive

class GenerationProgress(Static):
    """Real-time generation progress display."""

    completed = reactive(0)
    total = reactive(0)
    current_persona = reactive("")
    tokens_used = reactive(0)
    estimated_cost = reactive(0.0)

    def compose(self) -> ComposeResult:
        yield ProgressBar(total=self.total)
        yield Static(id="current-status")
        yield PersonaList(id="completed-list")
        yield CostTracker(id="cost-tracker")
```

### Event System

```python
# Events for generation updates
class GenerationStarted(Message):
    def __init__(self, experiment_id: str, total: int) -> None:
        self.experiment_id = experiment_id
        self.total = total

class PersonaStarted(Message):
    def __init__(self, persona_name: str) -> None:
        self.persona_name = persona_name

class PersonaCompleted(Message):
    def __init__(self, persona_name: str, tokens: int) -> None:
        self.persona_name = persona_name
        self.tokens = tokens

class GenerationCompleted(Message):
    def __init__(self, experiment_id: str, total_cost: float) -> None:
        self.experiment_id = experiment_id
        self.total_cost = total_cost
```

## Implementation Tasks

- [ ] Create GenerationScreen
- [ ] Implement ProgressBar widget customisation
- [ ] Create PersonaList widget for completed items
- [ ] Implement streaming token display
- [ ] Add cancel functionality
- [ ] Integrate with generation event system
- [ ] Add elapsed time tracking
- [ ] Implement error state handling
- [ ] Write unit tests
- [ ] Write snapshot tests

## Success Criteria

- [ ] Progress bar updates in real-time
- [ ] Completed personas display with token counts
- [ ] Current generation status visible
- [ ] Cost tracking accurate
- [ ] Cancel works mid-generation
- [ ] Error states display clearly
- [ ] Test coverage ≥ 80%

## Dependencies

- F-098: TUI Dashboard Application
- F-094: Streaming Output Display
- F-078: Cost Tracking

---

## Related Documentation

- [Milestone v1.2.0](../../milestones/v1.2.0.md)
- [F-098: TUI Dashboard Application](F-098-tui-dashboard-app.md)
- [F-102: Cost Tracker Widget](F-102-cost-tracker-widget.md)

