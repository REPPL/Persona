# ADR-0024: TUI Dashboard Architecture

## Status

Accepted

## Context

Persona v1.2.0 needed a full-screen terminal interface for:
- Real-time generation monitoring
- Experiment browsing and management
- Persona viewing and comparison
- Cost tracking during generation
- Quality metrics visualisation

The TUI needed to:
- Work in any terminal emulator
- Support keyboard navigation
- Update in real-time
- Remain responsive during background operations
- Integrate with the existing CLI

## Decision

Implement the TUI using **Textual**, a modern Python TUI framework:

### Architecture

```
persona dashboard
       ↓
┌─────────────────────────────────────────────────────────────┐
│ TUI Application (Textual)                                   │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Header (title, status, keybindings)                     │ │
│ └─────────────────────────────────────────────────────────┘ │
│ ┌─────────────────────┬───────────────────────────────────┐ │
│ │ Sidebar             │ Main Content Area                 │ │
│ │ (navigation)        │ (screen-specific)                 │ │
│ │                     │                                   │ │
│ │ • Dashboard         │ ┌───────────────────────────────┐ │ │
│ │ • Experiments       │ │ Active Screen Content         │ │ │
│ │ • Personas          │ │                               │ │ │
│ │ • Generation        │ │                               │ │ │
│ │ • Settings          │ └───────────────────────────────┘ │ │
│ │                     │                                   │ │
│ └─────────────────────┴───────────────────────────────────┘ │
│ ┌─────────────────────────────────────────────────────────┐ │
│ │ Footer (status bar, help)                               │ │
│ └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Screen Components

| Screen | Purpose | Key Widgets |
|--------|---------|-------------|
| **Dashboard** | Overview, recent activity | Stats cards, recent list |
| **Experiments** | Browse/manage experiments | DataTable, tree view |
| **Generation** | Real-time generation monitor | Progress bar, log stream |
| **Personas** | View/compare personas | Markdown viewer, diff view |
| **Settings** | Configuration editor | Form inputs, toggles |

### Widget Composition

```python
class DashboardScreen(Screen):
    """Main dashboard with overview stats."""

    def compose(self) -> ComposeResult:
        yield Header()
        with Horizontal():
            yield Sidebar()
            with Vertical(id="main"):
                yield StatsRow()
                yield RecentExperiments()
                yield CostSummary()
        yield Footer()
```

### Async Operations

All long-running operations run in background workers:

```python
@work(exclusive=True)
async def run_generation(self, config: GenerationConfig) -> None:
    """Run generation in background worker."""
    async for progress in self.generator.stream(config):
        self.post_message(GenerationProgress(progress))
    self.post_message(GenerationComplete())
```

## Consequences

**Positive:**
- Rich, interactive terminal experience
- Cross-platform (Windows, macOS, Linux)
- Keyboard-driven (accessible)
- Real-time updates via reactive system
- CSS-like styling for customisation
- Built-in widgets (DataTable, Tree, etc.)

**Negative:**
- Learning curve for Textual concepts
- Large dependency (textual + rich)
- Terminal capabilities vary
- Testing TUI apps is non-trivial

## Alternatives Considered

### Rich Console Only

**Description:** Use Rich for formatted output without full TUI.
**Pros:** Already a dependency, simpler, no new concepts.
**Cons:** No interactivity, no real-time updates, no screens.
**Why Not Chosen:** Insufficient for monitoring use case.

### Blessed/Curses

**Description:** Use low-level terminal libraries.
**Pros:** Maximum control, smaller dependencies.
**Cons:** Very low-level, lots of boilerplate, cross-platform issues.
**Why Not Chosen:** Development time too high.

### Urwid

**Description:** Established Python TUI library.
**Pros:** Mature, well-documented.
**Cons:** Older design, callback-based, less intuitive.
**Why Not Chosen:** Textual is more modern and easier to use.

### Click + Rich

**Description:** Extend CLI with rich output and limited interactivity.
**Pros:** Minimal new code, works with existing CLI.
**Cons:** Not a full TUI, limited interaction model.
**Why Not Chosen:** Doesn't meet real-time monitoring needs.

## Research Reference

See [R-012: TUI Full-Screen Layout Patterns](../../research/R-012-tui-fullscreen-layout-patterns.md) for layout design research.

## Implementation Details

### Responsive Layout

The TUI adapts to terminal size:

```python
def on_resize(self, event: Resize) -> None:
    """Handle terminal resize."""
    if event.size.width < 80:
        self.sidebar.display = False
    else:
        self.sidebar.display = True
```

### Theme Support

```css
/* Default theme */
DashboardScreen {
    background: $surface;
}

.stats-card {
    border: solid $primary;
    padding: 1 2;
}

/* Dark theme variant */
DashboardScreen.-dark-mode {
    background: $surface-darken-2;
}
```

### Integration with CLI

```bash
# Launch full TUI
persona dashboard

# Launch specific screen
persona dashboard --screen experiments

# Launch in read-only mode
persona dashboard --readonly
```

---

## Related Documentation

- [F-098: TUI Dashboard App](../../roadmap/features/completed/F-098-tui-dashboard-app.md)
- [F-099: Real-time Generation Monitor](../../roadmap/features/completed/F-099-realtime-generation-monitor.md)
- [F-100: Experiment Browser](../../roadmap/features/completed/F-100-experiment-browser.md)
- [F-101: Persona Viewer](../../roadmap/features/completed/F-101-persona-viewer.md)
- [F-102: Cost Tracker Widget](../../roadmap/features/completed/F-102-cost-tracker-widget.md)
- [F-103: Responsive Layout System](../../roadmap/features/completed/F-103-responsive-layout-system.md)
- [Textual Documentation](https://textual.textualize.io/)
