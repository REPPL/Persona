# F-102: Cost Tracker Widget

**Status**: Complete
**Category**: TUI
**Milestone**: v1.2.0

## Summary

Provides real-time API cost tracking with session/total costs, provider breakdown, and budget warnings.

## Implementation

- **Widget**: `CostTracker` in `/src/persona/tui/widgets/cost_tracker.py`

## Features

- **Session Cost**: Current session accumulation
- **Total Cost**: Historical total across all sessions
- **Provider Breakdown**: Cost per provider (Anthropic, OpenAI, Gemini)
- **Budget Warnings**: Configurable limit with visual alert
- **Session Reset**: Clear session while preserving total

## API

```python
tracker = CostTracker()
tracker.add_cost("anthropic", Decimal("0.42"))
tracker.set_budget_limit(Decimal("10.00"))
tracker.reset_session()

# Getters
session_cost = tracker.get_session_cost()
total_cost = tracker.get_total_cost()
breakdown = tracker.get_breakdown()
```

## Display

```
💰 Cost Tracker
Session: $0.42
Total: $5.67
anthropic: $0.42, openai: $0.15

⚠️ Budget limit $10.00 approaching!
```

## Related Documentation

- [F-098: TUI Dashboard Application](F-098-tui-dashboard-app.md)
- [F-099: Real-Time Generation Monitor](F-099-realtime-generation-monitor.md)

---

**Completed**: 2025-12-15
