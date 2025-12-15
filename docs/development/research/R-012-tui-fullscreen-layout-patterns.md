# R-012: Full-Screen TUI Layout Patterns

Research into state-of-the-art practices for designing full-screen terminal user interfaces with responsive layouts that adapt to varying terminal dimensions.

## Executive Summary

Full-screen TUI applications face unique challenges compared to web or mobile UIs: terminal dimensions vary wildly (from 80×24 legacy terminals to 400+ column modern displays), character cells are the atomic unit (not pixels), and Unicode/emoji support varies across terminal emulators. This research evaluates current best practices (December 2025) for building complex, adaptive TUI layouts.

**Key Finding:** The optimal approach combines **minimum size validation** with **graceful adaptive layouts**. Enforce a sensible minimum (typically 80×24) to guarantee usability, then use fractional units and responsive containers to maximise the experience on larger terminals.

**Recommendation:** For Persona's planned v1.2.0+ TUI dashboard, implement a hybrid strategy:
1. Validate minimum terminal size (80×24) with clear user feedback
2. Use fractional (`fr`) units for proportional space allocation
3. Employ docked widgets for fixed headers/footers/sidebars
4. Handle resize events to recalculate complex layouts programmatically
5. Design mobile-first (small terminal first, enhance for larger)

---

## Current State of the Art (December 2025)

### The Terminal Layout Problem

Unlike web browsers with CSS media queries and pixel-precise rendering, TUI applications must contend with:

| Challenge | Web | Terminal |
|-----------|-----|----------|
| **Atomic unit** | Pixel | Character cell |
| **Width variability** | 320px–4K+ | 40–400+ columns |
| **Height variability** | Scrollable | Fixed viewport |
| **Font metrics** | Known | Variable (terminal-dependent) |
| **Unicode support** | Consistent | Inconsistent across emulators |
| **Media queries** | Native CSS | Must implement programmatically |

### Textual: The Modern Standard

[Textual](https://textual.textualize.io/) (26k+ GitHub stars, December 2025) represents the state of the art in Python TUI development. Created by the Rich library team, it brings web-inspired layout concepts to the terminal.

**Core Layout Types:**

| Layout | Description | Best For |
|--------|-------------|----------|
| **Vertical** | Stack children top-to-bottom | Lists, forms, content flow |
| **Horizontal** | Arrange children left-to-right | Toolbars, button rows |
| **Grid** | 2D positioning with rows/columns | Dashboards, complex UIs |
| **Docking** | Pin to container edges | Headers, footers, sidebars |

**Sizing Units:**

| Unit | Meaning | Use Case |
|------|---------|----------|
| `10` | Fixed (10 cells) | Known-size elements |
| `50%` | Percentage of available | Proportional sizing |
| `1fr` | Fractional unit | Flexible space division |
| `auto` | Content-based | Dynamic sizing |
| `vw`/`vh` | Viewport width/height % | Screen-relative |
| `w`/`h` | Container width/height % | Container-relative |

### Key Insight: Fractions Over Floats

Will McGugan (Textual creator) discovered that **floating-point arithmetic causes cumulative rounding errors** in layout calculations:

> "Fractions don't suffer from this kind of rounding error in the way that floats do. A really easy solution to this was to replace floats with fractions."

**Impact:** When dividing screen space (e.g., 1/3 + 2/3), floating-point errors can leave single-character gaps. Using Python's `fractions.Fraction` eliminates this issue entirely.

---

## The Fundamental Question: Minimum Size vs Dynamic Adaptation

### Approach 1: Minimum Size Constraint

**Strategy:** Define a minimum terminal size (e.g., 80×24). If the terminal is smaller, display a warning message and refuse to render the full UI.

**Advantages:**
- ✅ Guarantees usable experience
- ✅ Simplifies layout logic (known minimum bounds)
- ✅ Prevents broken/unusable UI states
- ✅ Clear user feedback when requirements not met

**Disadvantages:**
- ❌ Completely unusable on small terminals
- ❌ Poor experience during resize transitions
- ❌ May frustrate users with non-standard setups

**Common Pattern:**

```python
def check_terminal_size(min_width: int = 80, min_height: int = 24) -> bool:
    """Validate terminal meets minimum size requirements."""
    size = os.get_terminal_size()
    if size.columns < min_width or size.lines < min_height:
        console.print(
            f"[red]Terminal too small![/red]\n"
            f"Required: {min_width}×{min_height}\n"
            f"Current:  {size.columns}×{size.lines}\n"
            f"Please resize your terminal window."
        )
        return False
    return True
```

**Real-World Examples:**
- **bpytop**: Displays "Terminal too small" warning, blocks UI until resized
- **htop**: Has minimum size but degrades gracefully
- **vim/neovim**: Works at any size but warns for very small windows

### Approach 2: Fully Dynamic Adaptation

**Strategy:** Adapt UI to any terminal size, collapsing or hiding elements as space decreases.

**Advantages:**
- ✅ Works on any terminal size
- ✅ Maximises usability across environments
- ✅ Graceful degradation similar to responsive web

**Disadvantages:**
- ❌ Significantly more complex to implement
- ❌ Risk of unusable states (too much collapsed)
- ❌ Testing burden increases dramatically
- ❌ User may not understand why features are missing

**Implementation Complexity:**

```python
# Naive approach - quickly becomes unmaintainable
def render_dashboard(width: int, height: int) -> None:
    if width >= 120:
        # Full layout: sidebar + main + details
        render_three_column()
    elif width >= 80:
        # Medium layout: sidebar + main
        render_two_column()
    elif width >= 60:
        # Compact: main only with tabs
        render_single_column_tabbed()
    else:
        # Minimal: just the essentials
        render_minimal()
```

### Recommended: Hybrid Approach

**Strategy:** Enforce a reasonable minimum for core functionality, then enhance progressively for larger terminals.

**Implementation:**

1. **Hard minimum (80×24)**: Below this, show error message
2. **Baseline UI (80×24)**: Full functionality, compact layout
3. **Enhanced UI (120×40+)**: Additional panels, expanded views
4. **Large screen UI (160×50+)**: All optional elements visible

**Benefits:**
- Guaranteed baseline experience
- Progressive enhancement for larger terminals
- Clear user expectations
- Manageable testing matrix

---

## Layout Patterns for Full-Screen TUIs

### Pattern 1: Docked Edges + Flexible Centre

The most common full-screen pattern. Fixed elements (header, footer, sidebar) dock to edges, with the main content area filling remaining space.

```
┌─────────────────────────────────────────────┐
│ HEADER (docked top, fixed height)           │
├──────────────┬──────────────────────────────┤
│              │                              │
│   SIDEBAR    │        MAIN CONTENT          │
│   (docked    │        (1fr × 1fr)           │
│    left,     │                              │
│    fixed     │        [scrollable]          │
│    width)    │                              │
│              │                              │
├──────────────┴──────────────────────────────┤
│ FOOTER (docked bottom, fixed height)        │
└─────────────────────────────────────────────┘
```

**Textual CSS Implementation:**

```css
Screen {
    layout: grid;
    grid-size: 2;
    grid-columns: 24 1fr;
    grid-rows: 3 1fr 1;
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
    width: 24;
    dock: left;
}

#main {
    width: 1fr;
    height: 1fr;
}
```

### Pattern 2: Grid Dashboard

For monitoring/dashboard applications showing multiple panels of equal importance.

```
┌─────────────────────────────────────────────┐
│ HEADER                                      │
├─────────────────┬───────────────────────────┤
│    PANEL 1      │       PANEL 2             │
│    (1fr)        │       (2fr)               │
├─────────────────┼───────────────────────────┤
│    PANEL 3      │       PANEL 4             │
│    (1fr)        │       (2fr)               │
└─────────────────┴───────────────────────────┘
```

**Textual CSS:**

```css
Screen {
    layout: grid;
    grid-size: 2 3;
    grid-rows: 3 1fr 1fr;
    grid-columns: 1fr 2fr;
    grid-gutter: 1;
}

#header {
    column-span: 2;
}
```

### Pattern 3: Master-Detail

Common for list-based applications (email clients, file managers).

```
┌─────────────────────────────────────────────┐
│ HEADER                                      │
├────────────────────┬────────────────────────┤
│                    │                        │
│   MASTER LIST      │   DETAIL VIEW          │
│   (fixed width     │   (1fr)                │
│    or 1fr)         │                        │
│                    │   [shows selected      │
│   [scrollable]     │    item details]       │
│                    │                        │
└────────────────────┴────────────────────────┘
```

### Pattern 4: Tabbed Interface (Small Screen Fallback)

When horizontal space is constrained, collapse panels into tabs.

```
┌─────────────────────────────────────────────┐
│ HEADER                                      │
├─────────────────────────────────────────────┤
│ [Tab 1] [Tab 2] [Tab 3]                     │
├─────────────────────────────────────────────┤
│                                             │
│   CONTENT (shows active tab)                │
│                                             │
│   [scrollable]                              │
│                                             │
└─────────────────────────────────────────────┘
```

---

## Handling Terminal Resize Events

### The Timing Problem

Resize events fire **before** layout recalculation completes. Code accessing widget dimensions during `on_resize` gets stale values.

**Solution:** Use `call_after_refresh` to defer dimension-dependent logic:

```python
from textual.app import App
from textual.events import Resize

class ResponsiveApp(App):
    def on_resize(self, event: Resize) -> None:
        """Handle terminal resize."""
        # Schedule layout adjustment after Textual recalculates
        self.call_after_refresh(self._adjust_layout)

    def _adjust_layout(self) -> None:
        """Adjust layout based on new terminal size."""
        width, height = self.size

        # Hide sidebar on narrow terminals
        sidebar = self.query_one("#sidebar")
        sidebar.display = width >= 100

        # Collapse details panel on short terminals
        details = self.query_one("#details")
        details.display = height >= 30
```

### Resize Event Properties

The `Resize` event provides:

| Property | Type | Description |
|----------|------|-------------|
| `size` | `Size` | New widget dimensions |
| `virtual_size` | `Size` | Scrollable content size |
| `container_size` | `Size | None` | Parent container size |
| `pixel_size` | `Size | None` | Terminal pixels (if available) |

### Debouncing Resize Handling

Rapid resizing can trigger many events. For expensive operations, debounce:

```python
from textual.app import App
import asyncio

class DebouncedResizeApp(App):
    _resize_task: asyncio.Task | None = None

    def on_resize(self, event) -> None:
        # Cancel pending resize handling
        if self._resize_task:
            self._resize_task.cancel()

        # Schedule new handling with delay
        self._resize_task = asyncio.create_task(
            self._debounced_resize()
        )

    async def _debounced_resize(self) -> None:
        await asyncio.sleep(0.1)  # 100ms debounce
        self.call_after_refresh(self._adjust_layout)
```

---

## Performance Considerations

### Textual's Optimisation Strategies

Based on Will McGugan's research, Textual employs several key optimisations:

**1. Segment-Based Rendering**
Rather than treating the terminal as a character grid, Textual uses "segments" (styled text runs) as the atomic rendering unit. This handles variable-width characters (CJK, emoji) correctly.

**2. Spatial Indexing**
A grid-based spatial map divides the viewport into tiles (100×20 characters), enabling O(1) visibility lookups regardless of widget count.

**3. Partial Updates**
The compositor supports incremental rendering—only affected screen regions redraw when widgets change.

**4. LRU Caching**
"@lru_cache is _fast_." Frequently-called layout functions benefit from caching with `maxsize` of 1000-4000.

**5. Batched Writes**
All screen updates are batched into a single `stdout.write()` call to prevent visual tearing.

### Performance Best Practices

1. **Avoid layout recalculation in hot paths**
   - Cache computed dimensions
   - Only recalculate on resize events

2. **Use `call_after_refresh` for dimension queries**
   - Dimensions are stale during resize handling
   - Defer to after layout recalculation

3. **Prefer `fr` units over percentages**
   - Fractional units handle division cleanly
   - Avoids floating-point rounding errors

4. **Minimise widget count**
   - Each widget adds overhead
   - Combine related content where sensible

---

## Unicode and Emoji Considerations

### The Width Problem

Not all characters occupy one cell:

| Character Type | Width | Example |
|----------------|-------|---------|
| ASCII | 1 cell | `A`, `1`, `@` |
| CJK ideographs | 2 cells | `漢`, `字` |
| Emoji | 1-2 cells | `😀` (varies!) |
| Zero-width | 0 cells | Combining marks |

### Emoji Unpredictability

Will McGugan's finding:

> "Terminal emoji support remains fundamentally unpredictable. Multi-codepoint emojis render inconsistently across terminals. No reliable method to detect terminal Unicode versions."

**Recommendation:** Restrict to Unicode 9.0 emoji for stability, or avoid emoji in layout-critical areas.

### Safe Approach

```python
# Use wcwidth for accurate width calculation
import wcwidth

def safe_width(text: str) -> int:
    """Calculate display width accounting for wide characters."""
    return sum(max(0, wcwidth.wcwidth(c)) for c in text)
```

---

## Implementation Recommendations for Persona

### Target: v1.2.0+ TUI Dashboard

Based on this research, Persona's TUI dashboard should implement:

### 1. Minimum Size Validation

```python
# src/persona/ui/tui/validators.py

from dataclasses import dataclass
import os

@dataclass
class TerminalConstraints:
    """Minimum terminal size requirements."""
    min_width: int = 80
    min_height: int = 24
    recommended_width: int = 120
    recommended_height: int = 40

def validate_terminal_size() -> tuple[bool, str | None]:
    """
    Check if terminal meets minimum requirements.

    Returns:
        Tuple of (is_valid, error_message)
    """
    constraints = TerminalConstraints()
    size = os.get_terminal_size()

    if size.columns < constraints.min_width:
        return False, (
            f"Terminal width {size.columns} is below minimum "
            f"{constraints.min_width}. Please resize."
        )

    if size.lines < constraints.min_height:
        return False, (
            f"Terminal height {size.lines} is below minimum "
            f"{constraints.min_height}. Please resize."
        )

    return True, None
```

### 2. Responsive Dashboard Layout

```css
/* src/persona/ui/tui/dashboard.tcss */

Screen {
    layout: grid;
    grid-size: 2 3;
    grid-rows: 3 1fr 1;
    grid-columns: 28 1fr;
}

#header {
    dock: top;
    height: 3;
    background: $primary;
}

#footer {
    dock: bottom;
    height: 1;
    background: $surface;
}

#sidebar {
    width: 28;
    min-width: 20;
}

#main {
    width: 1fr;
    height: 1fr;
}

/* Narrow terminal: hide sidebar */
Screen.-narrow #sidebar {
    display: none;
}

Screen.-narrow {
    grid-columns: 1fr;
}
```

### 3. Resize Handler with Breakpoints

```python
# src/persona/ui/tui/dashboard.py

from textual.app import App
from textual.events import Resize

class PersonaDashboard(App):
    """Full-screen TUI dashboard for persona monitoring."""

    BREAKPOINTS = {
        'narrow': 80,    # Minimum supported
        'medium': 120,   # Standard desktop
        'wide': 160,     # Large terminals
    }

    def on_resize(self, event: Resize) -> None:
        """Handle terminal resize with breakpoint classes."""
        self.call_after_refresh(self._apply_breakpoints)

    def _apply_breakpoints(self) -> None:
        """Apply CSS classes based on terminal width."""
        width = self.size.width

        # Remove existing breakpoint classes
        self.remove_class('-narrow', '-medium', '-wide')

        # Apply appropriate class
        if width < self.BREAKPOINTS['medium']:
            self.add_class('-narrow')
        elif width < self.BREAKPOINTS['wide']:
            self.add_class('-medium')
        else:
            self.add_class('-wide')
```

### 4. Architecture Integration

```
persona/
├── core/                 # Unchanged - business logic
├── cli/                  # Existing CLI (Typer + Rich + questionary)
└── tui/                  # NEW - Full-screen TUI (v1.2.0+)
    ├── __init__.py
    ├── app.py           # Textual App subclass
    ├── dashboard.py     # Main dashboard screen
    ├── validators.py    # Terminal validation
    ├── widgets/         # Custom widgets
    │   ├── persona_card.py
    │   ├── progress_panel.py
    │   └── cost_tracker.py
    └── styles/          # TCSS stylesheets
        ├── dashboard.tcss
        └── theme.tcss
```

---

## Comparison: Web vs TUI Responsive Design

| Aspect | Web (CSS) | TUI (Textual) |
|--------|-----------|---------------|
| **Media queries** | Native `@media` | Programmatic (Python) |
| **Breakpoints** | `min-width: 768px` | `if width >= 80` |
| **Flexbox** | Native | `layout: horizontal/vertical` |
| **Grid** | Native CSS Grid | Similar syntax |
| **Units** | `px`, `em`, `%`, `fr`, `vw` | cells, `%`, `fr`, `vw`, `vh` |
| **Overflow** | `overflow: scroll` | Automatic scrollbars |
| **Testing** | Browser DevTools | Textual snapshot testing |

---

## Testing Responsive TUI Layouts

### Textual's Snapshot Testing

Textual provides built-in snapshot testing for layout verification:

```python
# tests/tui/test_dashboard.py

from textual.testing import SnapshotTest
from persona.tui.dashboard import PersonaDashboard

class TestDashboardLayouts(SnapshotTest):
    async def test_narrow_layout(self):
        """Verify layout at minimum width."""
        async with PersonaDashboard(size=(80, 24)) as app:
            assert await self.snap(app)

    async def test_wide_layout(self):
        """Verify layout at wide width."""
        async with PersonaDashboard(size=(160, 50)) as app:
            assert await self.snap(app)
```

### Testing Size Constraints

```python
# tests/tui/test_validators.py

import pytest
from unittest.mock import patch
from persona.tui.validators import validate_terminal_size

def test_valid_terminal_size():
    """Terminal meeting requirements passes."""
    with patch('os.get_terminal_size') as mock:
        mock.return_value = os.terminal_size((120, 40))
        is_valid, error = validate_terminal_size()
        assert is_valid
        assert error is None

def test_narrow_terminal_rejected():
    """Terminal below minimum width rejected."""
    with patch('os.get_terminal_size') as mock:
        mock.return_value = os.terminal_size((60, 40))
        is_valid, error = validate_terminal_size()
        assert not is_valid
        assert "width" in error.lower()
```

---

## Sources

### Primary References

- Textual Documentation: Layout Guide. https://textual.textualize.io/guide/layout/
- Textual Documentation: Design a Layout. https://textual.textualize.io/how-to/design-a-layout/
- Textual Documentation: Resize Event. https://textual.textualize.io/events/resize/
- Textual Blog: Algorithms for High Performance Terminal Apps. https://textual.textualize.io/blog/2024/12/12/algorithms-for-high-performance-terminal-apps/
- Textualize Blog: 7 Things I've Learned Building a Modern TUI Framework. https://www.textualize.io/blog/7-things-ive-learned-building-a-modern-tui-framework/

### Supporting References

- Real Python: Python Textual Tutorial. https://realpython.com/python-textual/
- DEV Community: Introduction to Textual. https://dev.to/devasservice/introduction-to-textual-building-modern-text-user-interfaces-in-python-6c2
- Textual GitHub Discussion: Running code on terminal resize. https://github.com/Textualize/textual/discussions/3527
- CSS-Tricks: CSS Grid vs Flexbox for Full Page Layout. https://mastery.games/post/grid-beats-flexbox-full-page-layout/
- Terminal Trove: TUI Terminal Tools. https://terminaltrove.com/categories/tui/
- Awesome TUIs: Curated List. https://github.com/rothgar/awesome-tuis

### Web Responsive Design (for comparison)

- BrowserStack: Responsive Design Breakpoints 2025. https://www.browserstack.com/guide/responsive-design-breakpoints
- UXPin: Responsive Design Best Practices 2025. https://www.uxpin.com/studio/blog/best-practices-examples-of-excellent-responsive-design/

---

## Related Documentation

- [R-011: Interactive CLI Libraries](./R-011-interactive-cli-libraries.md) - Companion research on interactive prompts
- [ADR-0022: Interactive CLI Library Selection](../decisions/adrs/ADR-0022-interactive-cli-library.md) - Decision to use questionary
- [ADR-0005: Typer + Rich CLI Framework](../decisions/adrs/ADR-0005-cli-framework.md) - CLI stack foundation
- [F-094: Streaming Output Display](../roadmap/features/completed/F-094-streaming-output.md) - Related feature

---

**Status**: Complete
