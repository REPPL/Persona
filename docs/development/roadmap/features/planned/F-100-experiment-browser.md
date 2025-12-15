# F-100: Experiment Browser

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-002, UC-005 |
| **Milestone** | v1.2.0 |
| **Priority** | P2 |
| **Category** | TUI |

## Problem Statement

Users need to browse, search, and manage experiments without repeatedly running CLI commands. A visual experiment browser provides quick access to experiment history, status, and actions.

## Design Approach

- Filterable experiment list
- Status indicators (complete, in progress, failed)
- Quick actions (view, continue, delete)
- Search and sort functionality
- Keyboard-driven navigation

### Browser Layout

```
┌─────────────────────────────────────────────────────────────┐
│ EXPERIMENTS                    [/] Search  [N] New  [R] Refresh
├─────────────────────────────────────────────────────────────┤
│ Filter: [All ▼]  Sort: [Recent ▼]           Showing 12/45  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────────────────────────────────────────────┐   │
│   │ > exp-001-marketing-personas          ✓ Complete    │   │
│   │     Created: 2025-12-14 14:30                       │   │
│   │     Personas: 10 │ Provider: anthropic              │   │
│   ├─────────────────────────────────────────────────────┤   │
│   │   exp-002-developer-archetypes        ⏳ In Progress│   │
│   │     Created: 2025-12-15 09:15                       │   │
│   │     Personas: 3/8 │ Provider: openai                │   │
│   ├─────────────────────────────────────────────────────┤   │
│   │   exp-003-customer-segments           ✗ Failed      │   │
│   │     Created: 2025-12-15 10:00                       │   │
│   │     Error: Rate limit exceeded                      │   │
│   ├─────────────────────────────────────────────────────┤   │
│   │   exp-004-stakeholder-analysis        ○ Draft       │   │
│   │     Created: 2025-12-15 11:30                       │   │
│   │     Personas: 0 │ Not started                       │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ [Enter] View  [G] Generate  [D] Delete  [E] Edit  [↑↓] Nav │
└─────────────────────────────────────────────────────────────┘
```

### Data Model Integration

```python
# src/persona/tui/widgets/experiment_list.py

from textual.widgets import ListView, ListItem
from persona.core.experiment import ExperimentManager

class ExperimentList(ListView):
    """Browseable experiment list with filtering."""

    def __init__(self) -> None:
        super().__init__()
        self.manager = ExperimentManager()

    def on_mount(self) -> None:
        self.load_experiments()

    def load_experiments(self, filter_status: str | None = None) -> None:
        experiments = self.manager.list_experiments()
        if filter_status:
            experiments = [e for e in experiments if e.status == filter_status]

        self.clear()
        for exp in sorted(experiments, key=lambda x: x.created_at, reverse=True):
            self.append(ExperimentListItem(exp))
```

### Status Icons

| Status | Icon | Colour |
|--------|------|--------|
| Complete | ✓ | Green |
| In Progress | ⏳ | Yellow |
| Failed | ✗ | Red |
| Draft | ○ | Grey |

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `↑`/`↓` | Navigate list |
| `Enter` | View experiment |
| `G` | Start generation |
| `D` | Delete (with confirm) |
| `E` | Edit configuration |
| `N` | New experiment |
| `/` | Focus search |
| `R` | Refresh list |
| `Esc` | Clear search/filter |

## Implementation Tasks

- [ ] Create ExperimentList widget
- [ ] Implement ExperimentListItem with status display
- [ ] Add search functionality
- [ ] Add filter dropdown
- [ ] Add sort options
- [ ] Implement delete with confirmation dialog
- [ ] Add refresh mechanism
- [ ] Create new experiment flow
- [ ] Write unit tests
- [ ] Write snapshot tests

## Success Criteria

- [ ] Experiments load and display correctly
- [ ] Status icons accurate
- [ ] Search filters in real-time
- [ ] Filter dropdown works
- [ ] Sort options work
- [ ] Delete confirmation prevents accidents
- [ ] Keyboard navigation complete
- [ ] Test coverage ≥ 80%

## Dependencies

- F-098: TUI Dashboard Application
- Experiment management from core

---

## Related Documentation

- [Milestone v1.2.0](../../milestones/v1.2.0.md)
- [F-098: TUI Dashboard Application](F-098-tui-dashboard-app.md)
- [F-101: Persona Viewer](F-101-persona-viewer.md)

