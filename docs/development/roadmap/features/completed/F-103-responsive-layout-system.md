# F-103: Responsive Layout System

**Status**: Completed
**Category**: TUI
**Milestone**: v1.2.0

## Summary

Implements a responsive layout system that adapts to terminal size, providing optimal layouts for different widths with smooth transitions.

## Implementation

- **Config**: `TUIConfig` in `/src/persona/tui/config.py`
- **Validators**: Terminal size validation in `/src/persona/tui/validators.py`
- **Styles**: Breakpoint classes in TCSS files

## Breakpoints

| Width | Layout | Features |
|-------|--------|----------|
| < 80 | Error | "Terminal too small" message |
| 80-119 | Compact | Tabbed/stacked interface, no sidebar |
| 120-159 | Standard | Sidebar + main content |
| 160+ | Wide | Sidebar + main + details panel |

## Features

- **Minimum Requirements**: 80×24 terminal
- **Automatic Detection**: Terminal size checked on mount
- **Resize Handling**: Live adaptation to terminal resize events
- **CSS Classes**: Breakpoint classes applied to containers
- **Graceful Degradation**: Error screen for too-small terminals

## Technical Implementation

```python
config = TUIConfig()

# Check requirements
meets, error = config.meets_requirements(width, height)

# Get breakpoint
breakpoint = config.get_breakpoint(width)  # "compact", "standard", "wide", "error"
```

## TCSS Responsive Styles

```tcss
/* Compact layout (80-119) */
#dashboard-container.compact {
    layout: vertical;
}

#dashboard-container.compact .sidebar {
    width: 100%;
    height: 30%;
}

/* Standard layout (120-159) */
#dashboard-container.standard .sidebar {
    width: 25;
}

/* Wide layout (160+) */
#dashboard-container.wide .details-panel {
    display: block;
    width: 25;
}
```

## Adaptive Behaviour

- **Compact**: Stacked layout, hide details panel
- **Standard**: Sidebar + main, hide details panel
- **Wide**: Full three-column layout with all panels

## Related Documentation

- [F-098: TUI Dashboard Application](F-098-tui-dashboard-app.md)
- [v1.2.0 Milestone](../../milestones/v1.2.0.md)

---

**Completed**: 2025-12-15
