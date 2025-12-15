# F-098: TUI Dashboard Application

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001, UC-005 |
| **Milestone** | v1.2.0 |
| **Priority** | P1 |
| **Category** | TUI |

## Problem Statement

Users running long persona generation jobs need a way to monitor progress, browse results, and manage experiments without switching between multiple terminal commands. A full-screen TUI provides an integrated experience.

## Design Approach

- Textual-based full-screen application
- Launched via `persona dashboard` command
- Integrates with existing core functionality
- Optional dependency (`pip install persona[tui]`)

### Application Structure

```python
# src/persona/tui/app.py

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.binding import Binding

class PersonaApp(App):
    """Full-screen TUI dashboard for Persona."""

    CSS_PATH = "styles/app.tcss"

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("?", "help", "Help"),
        Binding("d", "dashboard", "Dashboard"),
        Binding("e", "experiments", "Experiments"),
        Binding("g", "generate", "Generate"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield DashboardScreen()
        yield Footer()

    def on_mount(self) -> None:
        """Validate terminal size on mount."""
        self.call_after_refresh(self._check_terminal_size)
```

### CLI Integration

```bash
# Launch dashboard
persona dashboard

# Launch with specific experiment
persona dashboard --experiment exp-001

# Launch in monitoring mode
persona dashboard --monitor
```

### Screen System

```
PersonaApp
├── DashboardScreen     # Main overview
├── ExperimentsScreen   # Experiment list/management
├── GenerationScreen    # Active generation monitoring
├── PersonaScreen       # Individual persona viewer
└── HelpScreen          # Keyboard shortcuts overlay
```

## Implementation Tasks

- [ ] Create Textual App subclass
- [ ] Implement screen navigation system
- [ ] Add terminal size validation
- [ ] Create base layout with header/footer
- [ ] Add keyboard bindings
- [ ] Create `persona dashboard` command
- [ ] Add optional dependency configuration
- [ ] Implement help overlay screen
- [ ] Write unit tests
- [ ] Write snapshot tests

## Success Criteria

- [ ] Dashboard launches successfully
- [ ] Terminal size validation works
- [ ] Screen navigation functional
- [ ] Keyboard shortcuts work
- [ ] Help overlay displays
- [ ] Optional dependency installs correctly
- [ ] Test coverage ≥ 80%

## Dependencies

- Textual ≥ 0.87.0
- F-094: Streaming Output (for real-time updates)
- Core persona functionality

---

## Related Documentation

- [Milestone v1.2.0](../../milestones/v1.2.0.md)
- [R-012: Full-Screen TUI Layout Patterns](../../research/R-012-tui-fullscreen-layout-patterns.md)
- [F-099: Real-Time Generation Monitor](F-099-realtime-generation-monitor.md)

