# F-101: Persona Viewer

**Status**: Complete
**Category**: TUI
**Milestone**: v1.2.0

## Summary

Provides a detailed, full-screen view of individual personas with all attributes, quality scores, evidence links, and navigation between personas.

## Implementation

- **Screen**: `PersonaViewerScreen` in `/src/persona/tui/screens/persona_view.py`
- **Widgets**: `PersonaCard` and `QualityBadge` in `/src/persona/tui/widgets/`

## Features

- Complete persona attribute display:
  - Demographics (name, age, location, background)
  - Role and responsibilities
  - Goals and motivations
  - Frustrations and pain points
  - Behaviours and preferences

- Quality score badge with colour coding
- Navigation between personas (←/→ arrows)
- Scrollable content for long personas
- Organised section layout

## Widget Components

**PersonaCard**: Compact persona display
- Name, role, demographics
- Goals summary
- Quality badge

**QualityBadge**: Colour-coded quality indicator
- Excellent: ≥85 (green)
- Good: ≥70 (blue)
- Acceptable: ≥50 (yellow)
- Poor: <50 (red)

## Related Documentation

- [F-098: TUI Dashboard Application](F-098-tui-dashboard-app.md)
- [F-100: Experiment Browser](F-100-experiment-browser.md)

---

**Completed**: 2025-12-15
