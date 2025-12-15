# F-101: Persona Viewer

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-002, UC-004 |
| **Milestone** | v1.2.0 |
| **Priority** | P2 |
| **Category** | TUI |

## Problem Statement

Users need to view persona details within the TUI without switching to file viewers or other tools. A dedicated persona viewer provides formatted display of all persona attributes, empathy maps, and metadata.

## Design Approach

- Full persona detail display
- Tabbed sections for different aspects
- Scrollable content for long descriptions
- Export and copy functionality
- Navigation between personas in an experiment

### Viewer Layout

```
┌─────────────────────────────────────────────────────────────┐
│ PERSONA: Sarah Chen - Product Manager                [X]   │
├─────────────────────────────────────────────────────────────┤
│ [Overview] [Empathy Map] [Behaviours] [Metadata] [Raw]     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─ Demographics ──────────────────────────────────────┐   │
│   │ Age:        34                                      │   │
│   │ Location:   San Francisco, CA                       │   │
│   │ Role:       Senior Product Manager                  │   │
│   │ Industry:   Enterprise SaaS                         │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│   ┌─ Background ────────────────────────────────────────┐   │
│   │ Sarah has 8 years of experience in product          │   │
│   │ management, specialising in B2B enterprise          │   │
│   │ software. She previously worked at Salesforce       │   │
│   │ and now leads product strategy at a Series B        │   │
│   │ startup focused on developer tools.                 │   │
│   │                                                     │   │
│   │ She holds an MBA from Stanford and a BS in          │   │
│   │ Computer Science from UC Berkeley.                  │   │
│   │                                             [more ▼] │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
│   ┌─ Goals ─────────────────────────────────────────────┐   │
│   │ • Ship features that drive measurable business      │   │
│   │   outcomes                                          │   │
│   │ • Build a product-led growth engine                 │   │
│   │ • Establish data-driven decision making             │   │
│   └─────────────────────────────────────────────────────┘   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ [←] Previous  [→] Next  [C] Copy  [E] Export  [Esc] Close  │
└─────────────────────────────────────────────────────────────┘
```

### Empathy Map Tab

```
┌─────────────────────────────────────────────────────────────┐
│ [Overview] [Empathy Map] [Behaviours] [Metadata] [Raw]     │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─ THINKS ──────────────────┬─ FEELS ─────────────────┐   │
│   │ "How can I prove ROI      │ Excited about new       │   │
│   │  to stakeholders?"        │ product opportunities   │   │
│   │                           │                         │   │
│   │ "We need better data      │ Frustrated by slow      │   │
│   │  to make decisions"       │ engineering velocity    │   │
│   ├───────────────────────────┼─────────────────────────┤   │
│   │─ SAYS ────────────────────┼─ DOES ──────────────────│   │
│   │ "Let's look at the        │ Runs weekly sprint      │   │
│   │  metrics first"           │ planning sessions       │   │
│   │                           │                         │   │
│   │ "What's the user          │ Interviews 3+ users     │   │
│   │  problem here?"           │ per week                │   │
│   └───────────────────────────┴─────────────────────────┘   │
│                                                             │
│   ┌─ PAINS ───────────────────┬─ GAINS ─────────────────┐   │
│   │ • Competing priorities    │ • Clear product-market  │   │
│   │ • Limited engineering     │   fit validation        │   │
│   │   resources               │ • Strong stakeholder    │   │
│   │ • Unclear requirements    │   alignment             │   │
│   └───────────────────────────┴─────────────────────────┘   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Tab Structure

| Tab | Content |
|-----|---------|
| **Overview** | Demographics, background, goals, challenges |
| **Empathy Map** | Thinks/feels/says/does/pains/gains |
| **Behaviours** | Typical behaviours, decision patterns |
| **Metadata** | Generation info, tokens, model, timestamp |
| **Raw** | JSON/YAML raw output for copy/export |

### Keyboard Navigation

| Key | Action |
|-----|--------|
| `Tab` | Next tab |
| `Shift+Tab` | Previous tab |
| `←`/`→` | Previous/next persona |
| `↑`/`↓` | Scroll content |
| `C` | Copy to clipboard |
| `E` | Export dialog |
| `Esc` | Close viewer |

## Implementation Tasks

- [ ] Create PersonaViewer screen
- [ ] Implement tabbed interface
- [ ] Create Overview tab layout
- [ ] Create EmpathyMap tab with quad layout
- [ ] Create Behaviours tab
- [ ] Create Metadata tab
- [ ] Create Raw tab with syntax highlighting
- [ ] Add persona navigation (prev/next)
- [ ] Implement clipboard copy
- [ ] Implement export dialog
- [ ] Write unit tests
- [ ] Write snapshot tests

## Success Criteria

- [ ] All persona fields display correctly
- [ ] Tab navigation works
- [ ] Empathy map renders in quad layout
- [ ] Scrolling works for long content
- [ ] Copy to clipboard functional
- [ ] Export creates valid files
- [ ] Navigation between personas works
- [ ] Test coverage ≥ 80%

## Dependencies

- F-098: TUI Dashboard Application
- F-100: Experiment Browser
- Persona data model from core

---

## Related Documentation

- [Milestone v1.2.0](../../milestones/v1.2.0.md)
- [F-098: TUI Dashboard Application](F-098-tui-dashboard-app.md)
- [F-100: Experiment Browser](F-100-experiment-browser.md)

