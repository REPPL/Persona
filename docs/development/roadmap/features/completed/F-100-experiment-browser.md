# F-100: Experiment Browser

**Status**: Completed
**Category**: TUI
**Milestone**: v1.2.0

## Summary

Provides a full-screen interface for browsing, filtering, and managing experiments with search functionality and quick actions.

## Implementation

- **Screen**: `ExperimentBrowserScreen` in `/src/persona/tui/screens/experiments.py`
- **Widget**: `ExperimentList` in `/src/persona/tui/widgets/experiment_list.py`

## Features

- List view of all experiments
- Status indicators (completed, in-progress, empty)
- Search/filter functionality
- Create new experiment button
- Select experiment for details
- Keyboard navigation (↑/↓, Enter, /)

## Components

- `ExperimentList`: Sidebar widget displaying experiments
- `ExperimentListItem`: Individual experiment list item
- `ExperimentBrowserScreen`: Full-screen experiment browser

## Related Documentation

- [F-098: TUI Dashboard Application](F-098-tui-dashboard-app.md)
- [F-101: Persona Viewer](F-101-persona-viewer.md)

---

**Completed**: 2025-12-15
