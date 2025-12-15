# F-102: Cost Tracker Widget

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-003, UC-006 |
| **Milestone** | v1.2.0 |
| **Priority** | P2 |
| **Category** | TUI |

## Problem Statement

Users need real-time visibility into API costs during generation. A dedicated cost tracker widget provides running totals, per-persona costs, and budget warnings to prevent unexpected expenses.

## Design Approach

- Real-time cost display widget
- Token usage breakdown
- Budget threshold warnings
- Historical cost summary
- Per-provider cost tracking

### Widget Layout (Compact)

```
┌─ Cost Tracker ──────────────────────────┐
│ Current:  $0.23  │ Budget: $5.00       │
│ ████████░░░░░░░░  4.6% used            │
│ Tokens: 7,725 in │ 2,341 out           │
└─────────────────────────────────────────┘
```

### Widget Layout (Expanded)

```
┌─ Cost Tracker ───────────────────────────────────────────┐
│                                                          │
│   Session Total:  $0.23         Budget: $5.00 (4.6%)    │
│   ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│                                                          │
│   ┌─ Breakdown ──────────────────────────────────────┐   │
│   │ Input tokens:   7,725  ($0.02)                   │   │
│   │ Output tokens:  2,341  ($0.21)                   │   │
│   │ Total tokens:  10,066                            │   │
│   └──────────────────────────────────────────────────┘   │
│                                                          │
│   ┌─ By Persona ─────────────────────────────────────┐   │
│   │ Marketing Director      1,234 + 456   $0.04      │   │
│   │ Sales Representative    1,456 + 389   $0.04      │   │
│   │ Customer Success        1,123 + 401   $0.04      │   │
│   │ Technical Writer        1,567 + 512   $0.05      │   │
│   │ UX Designer             1,345 + 423   $0.04      │   │
│   │ Product Manager         1,000 + 160   $0.02 ⏳   │   │
│   └──────────────────────────────────────────────────┘   │
│                                                          │
│   Provider: anthropic (claude-sonnet-4)                  │
│   Rate: $3.00/1M input, $15.00/1M output                 │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Warning States

| State | Trigger | Display |
|-------|---------|---------|
| Normal | < 80% budget | Green progress bar |
| Warning | 80-95% budget | Yellow bar, warning icon |
| Critical | > 95% budget | Red bar, alert message |
| Exceeded | > 100% budget | Red background, stop option |

### Warning Display

```
┌─ Cost Tracker ─────────────────── ⚠️  WARNING ───────────┐
│                                                          │
│   Session Total:  $4.25         Budget: $5.00 (85%)     │
│   ██████████████████████████████████░░░░░░░░░░░░░░░░░░  │
│                                                          │
│   ⚠️  Approaching budget limit!                          │
│   Estimated remaining: 2-3 more personas                 │
│                                                          │
│   [C] Continue  [S] Stop  [I] Increase Budget            │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Integration with Core

```python
# src/persona/tui/widgets/cost_tracker.py

from textual.widgets import Static
from textual.reactive import reactive
from persona.core.cost import CostCalculator

class CostTracker(Static):
    """Real-time cost tracking widget."""

    input_tokens = reactive(0)
    output_tokens = reactive(0)
    budget = reactive(5.0)  # Default $5.00

    def __init__(self, provider: str, model: str) -> None:
        super().__init__()
        self.calculator = CostCalculator(provider, model)

    @property
    def current_cost(self) -> float:
        return self.calculator.calculate(
            input_tokens=self.input_tokens,
            output_tokens=self.output_tokens
        )

    @property
    def budget_percentage(self) -> float:
        return (self.current_cost / self.budget) * 100

    def watch_input_tokens(self, value: int) -> None:
        self._update_display()

    def watch_output_tokens(self, value: int) -> None:
        self._update_display()
        self._check_budget_warning()

    def _check_budget_warning(self) -> None:
        if self.budget_percentage >= 95:
            self.add_class("critical")
            self.post_message(BudgetCritical())
        elif self.budget_percentage >= 80:
            self.add_class("warning")
            self.post_message(BudgetWarning())
```

## Implementation Tasks

- [ ] Create CostTracker widget
- [ ] Implement real-time token counting
- [ ] Add cost calculation integration
- [ ] Create progress bar visualisation
- [ ] Implement budget threshold detection
- [ ] Add warning state styling
- [ ] Create expanded view toggle
- [ ] Add per-persona breakdown
- [ ] Implement budget exceeded dialog
- [ ] Write unit tests
- [ ] Write snapshot tests

## Success Criteria

- [ ] Costs update in real-time
- [ ] Token counts accurate
- [ ] Budget percentage correct
- [ ] Warning thresholds trigger correctly
- [ ] Visual states change appropriately
- [ ] Expanded view shows breakdown
- [ ] Budget exceeded blocks generation
- [ ] Test coverage ≥ 80%

## Dependencies

- F-098: TUI Dashboard Application
- F-078: Cost Tracking (core)
- F-063: Token Count Tracking

---

## Related Documentation

- [Milestone v1.2.0](../../milestones/v1.2.0.md)
- [F-098: TUI Dashboard Application](F-098-tui-dashboard-app.md)
- [F-099: Real-Time Generation Monitor](F-099-realtime-generation-monitor.md)
- [R-004: Token Counting & Cost Estimation](../../research/R-004-token-counting-cost-estimation.md)

