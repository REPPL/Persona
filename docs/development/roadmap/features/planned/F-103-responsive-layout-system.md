# F-103: Responsive Layout System

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001, UC-005 |
| **Milestone** | v1.2.0 |
| **Priority** | P1 |
| **Category** | TUI |

## Problem Statement

Terminal sizes vary dramatically (80×24 to 400+ columns). The TUI must adapt gracefully, showing appropriate layouts for each size while enforcing minimum requirements. This feature implements the responsive layout strategy from R-012.

## Design Approach

Based on [R-012: Full-Screen TUI Layout Patterns](../../research/R-012-tui-fullscreen-layout-patterns.md):

- Minimum size validation (80×24)
- Breakpoint-based CSS classes
- Fractional units for flexible sizing
- Docked widgets for fixed elements
- Resize event handling with debouncing

### Breakpoint System

| Breakpoint | Width | Height | Layout |
|------------|-------|--------|--------|
| **error** | < 80 | < 24 | Error message only |
| **compact** | 80-119 | ≥ 24 | Tabbed, no sidebar |
| **standard** | 120-159 | ≥ 30 | Sidebar + main |
| **wide** | ≥ 160 | ≥ 40 | Sidebar + main + details |

### Compact Layout (80-119 cols)

```
┌───────────────────────────────────────────────────────────────────────┐
│ PERSONA                                                    [?] [Q]   │
├───────────────────────────────────────────────────────────────────────┤
│ [Dashboard] [Experiments] [Generate] [Settings]                       │
├───────────────────────────────────────────────────────────────────────┤
│                                                                       │
│   Content area fills remaining space                                  │
│   Sidebar collapsed into tab navigation                               │
│                                                                       │
│   ┌─────────────────────────────────────────────────────────────┐     │
│   │ Primary content widget                                      │     │
│   │ (scrollable)                                                │     │
│   └─────────────────────────────────────────────────────────────┘     │
│                                                                       │
├───────────────────────────────────────────────────────────────────────┤
│ Status message here                                      │ 14:32:15  │
└───────────────────────────────────────────────────────────────────────┘
```

### Standard Layout (120-159 cols)

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│ PERSONA DASHBOARD                                                          [?] Help [Q] │
├───────────────────┬─────────────────────────────────────────────────────────────────────┤
│                   │                                                                     │
│   SIDEBAR         │   MAIN CONTENT                                                      │
│   (24 cols)       │   (1fr)                                                             │
│                   │                                                                     │
│   Navigation      │   ┌───────────────────────────────────────────────────────────┐     │
│   and context     │   │ Primary widget                                            │     │
│                   │   │                                                           │     │
│                   │   │                                                           │     │
│                   │   └───────────────────────────────────────────────────────────┘     │
│                   │                                                                     │
├───────────────────┴─────────────────────────────────────────────────────────────────────┤
│ Status: Ready                                             │ Cost: $0.00 │ 14:32:15     │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### Wide Layout (160+ cols)

```
┌────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│ PERSONA DASHBOARD                                                                                       [?] Help [Q]  │
├───────────────────┬────────────────────────────────────────────────────────────┬───────────────────────────────────────┤
│                   │                                                            │                                       │
│   SIDEBAR         │   MAIN CONTENT                                             │   DETAILS PANEL                       │
│   (24 cols)       │   (1fr)                                                    │   (32 cols)                           │
│                   │                                                            │                                       │
│   Navigation      │   ┌──────────────────────────────────────────────────┐     │   Context-sensitive                   │
│                   │   │ Primary widget                                   │     │   information                         │
│                   │   │                                                  │     │                                       │
│                   │   │                                                  │     │   Selected item                       │
│                   │   │                                                  │     │   details, help,                      │
│                   │   └──────────────────────────────────────────────────┘     │   or actions                          │
│                   │                                                            │                                       │
├───────────────────┴────────────────────────────────────────────────────────────┴───────────────────────────────────────┤
│ Status: Ready                                                                          │ Cost: $0.00 │ 14:32:15        │
└────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

### Implementation

**Terminal Validation:**

```python
# src/persona/tui/validators.py

from dataclasses import dataclass
import os

@dataclass
class TerminalConstraints:
    """Terminal size requirements."""
    min_width: int = 80
    min_height: int = 24
    compact_width: int = 120
    standard_width: int = 160

def validate_terminal() -> tuple[bool, str | None]:
    """Validate minimum terminal size."""
    size = os.get_terminal_size()

    if size.columns < 80:
        return False, f"Terminal width {size.columns} below minimum 80"

    if size.lines < 24:
        return False, f"Terminal height {size.lines} below minimum 24"

    return True, None
```

**Breakpoint Manager:**

```python
# src/persona/tui/layout.py

from textual.app import App
from textual.events import Resize

class BreakpointMixin:
    """Mixin for responsive breakpoint handling."""

    BREAKPOINTS = {
        'compact': 80,
        'standard': 120,
        'wide': 160,
    }

    def on_resize(self, event: Resize) -> None:
        self.call_after_refresh(self._apply_breakpoints)

    def _apply_breakpoints(self) -> None:
        width = self.size.width

        # Remove existing classes
        self.remove_class('-compact', '-standard', '-wide')

        # Apply appropriate class
        if width < self.BREAKPOINTS['standard']:
            self.add_class('-compact')
        elif width < self.BREAKPOINTS['wide']:
            self.add_class('-standard')
        else:
            self.add_class('-wide')
```

**Responsive CSS:**

```css
/* src/persona/tui/styles/responsive.tcss */

/* Base layout */
Screen {
    layout: grid;
    grid-size: 1;
}

#header {
    dock: top;
    height: 3;
}

#footer {
    dock: bottom;
    height: 1;
}

#sidebar {
    display: none;
}

#details {
    display: none;
}

/* Standard: show sidebar */
Screen.-standard {
    grid-size: 2;
    grid-columns: 24 1fr;
}

Screen.-standard #sidebar {
    display: block;
}

/* Wide: show sidebar and details */
Screen.-wide {
    grid-size: 3;
    grid-columns: 24 1fr 32;
}

Screen.-wide #sidebar {
    display: block;
}

Screen.-wide #details {
    display: block;
}
```

## Implementation Tasks

- [ ] Create terminal validation module
- [ ] Implement BreakpointMixin
- [ ] Create responsive.tcss stylesheet
- [ ] Add "terminal too small" error screen
- [ ] Implement resize debouncing
- [ ] Create compact layout (tabbed)
- [ ] Create standard layout (sidebar)
- [ ] Create wide layout (three-column)
- [ ] Add smooth transitions between layouts
- [ ] Write unit tests
- [ ] Write snapshot tests for each breakpoint

## Success Criteria

- [ ] Minimum size enforced (80×24)
- [ ] Clear error message when too small
- [ ] Compact layout works at 80-119
- [ ] Standard layout works at 120-159
- [ ] Wide layout works at 160+
- [ ] Resize transitions smoothly
- [ ] No visual glitches during resize
- [ ] Test coverage ≥ 80%

## Dependencies

- F-098: TUI Dashboard Application
- Textual CSS system

---

## Related Documentation

- [Milestone v1.2.0](../../milestones/v1.2.0.md)
- [R-012: Full-Screen TUI Layout Patterns](../../research/R-012-tui-fullscreen-layout-patterns.md)
- [F-098: TUI Dashboard Application](F-098-tui-dashboard-app.md)

