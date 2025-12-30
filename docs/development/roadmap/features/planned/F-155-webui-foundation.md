# F-155: WebUI Foundation

## Overview

| Attribute | Value |
|-----------|-------|
| **Feature ID** | F-155 |
| **Title** | WebUI Foundation |
| **Priority** | P1 (High) |
| **Category** | UX |
| **Milestone** | [v2.0.0](../../milestones/v2.0.0.md) |
| **Status** | Planned |
| **Dependencies** | F-151 (Team Workspace), ADR-0035 (WebUI Technology) |

---

## Problem Statement

While CLI and TUI serve technical users well, broader adoption requires:
- Accessibility for non-technical stakeholders
- Visual persona browsing and comparison
- Collaborative review workflows
- Integration with design tools
- Mobile access for on-the-go review

The WebUI foundation provides browser-based access to Persona capabilities.

---

## Design Approach

Build a lightweight WebUI using htmx + Alpine.js per [ADR-0035](../../../decisions/adrs/ADR-0035-webui-technology-selection.md), focusing on core functionality with progressive enhancement.

---

## Key Capabilities

### 1. Persona Browser

Visual interface for browsing and viewing personas.

```
┌─────────────────────────────────────────────────────────────────┐
│  Persona                                    product-research  ▼ │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │  Sarah   │ │  James   │ │  Maria   │ │  David   │  + New    │
│  │  Chen    │ │  Wilson  │ │  Garcia  │ │  Kim     │           │
│  │          │ │          │ │          │ │          │           │
│  │  32, PM  │ │  45, Eng │ │  28, UX  │ │  38, Mkt │           │
│  │  London  │ │  Bristol │ │  Manches │ │  Edinbur │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
│                                                                 │
│  Showing 4 of 47 personas                          Grid | List │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 2. Generation Wizard

Step-by-step persona generation interface.

```
┌─────────────────────────────────────────────────────────────────┐
│  Generate Personas                                     Step 2/4 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ○ Upload Data  ● Configure  ○ Generate  ○ Review               │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ Provider                                                 │   │
│  │ ┌─────────────────────────────────────────────────────┐ │   │
│  │ │ Anthropic (Claude)                              ▼   │ │   │
│  │ └─────────────────────────────────────────────────────┘ │   │
│  │                                                         │   │
│  │ Number of Personas                                      │   │
│  │ ┌─────────────────────────────────────────────────────┐ │   │
│  │ │ 5                                                   │ │   │
│  │ └─────────────────────────────────────────────────────┘ │   │
│  │                                                         │   │
│  │ Output Format                                           │   │
│  │ ○ YAML  ● JSON  ○ Markdown                              │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│                                      [ Back ]  [ Next Step → ] │
└─────────────────────────────────────────────────────────────────┘
```

### 3. Persona Detail View

Rich persona display with all attributes.

```
┌─────────────────────────────────────────────────────────────────┐
│  Sarah Chen                                    Edit | Export ▼  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  Demographics                                  │
│  │             │  ───────────                                   │
│  │   Avatar    │  Age: 32                                       │
│  │             │  Location: London, UK                          │
│  │             │  Occupation: Product Manager                   │
│  └─────────────┘  Industry: Technology                          │
│                                                                 │
│  Goals                          Frustrations                    │
│  ─────                          ────────────                    │
│  • Save time on daily tasks     • Too many tools to manage      │
│  • Improve team collaboration   • Inconsistent data formats     │
│  • Make data-driven decisions   • Slow feedback loops           │
│                                                                 │
│  Behaviours                     Quote                           │
│  ──────────                     ─────                           │
│  • Reviews metrics weekly       "I need to see the big          │
│  • Prefers visual dashboards     picture without drowning       │
│  • Early adopter of tools        in details."                   │
│                                                                 │
│  ─────────────────────────────────────────────────────────────  │
│  Quality Score: 0.89 ████████████░░ Good                        │
│  Generated: 2025-01-15 • Source: interviews.json                │
└─────────────────────────────────────────────────────────────────┘
```

### 4. Quality Dashboard

Visual quality metrics display.

```
┌─────────────────────────────────────────────────────────────────┐
│  Quality Overview                              Last 30 days  ▼  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Composite Score                    Metric Breakdown            │
│  ───────────────                    ────────────────            │
│       0.87                          Coherence     ████████░ 89% │
│    ┌───────┐                        Faithfulness  ███████░░ 82% │
│    │       │                        Completeness  █████████ 94% │
│    │  87%  │                        Consistency   ████████░ 86% │
│    │       │                                                    │
│    └───────┘                                                    │
│     Good                                                        │
│                                                                 │
│  Trend (30 days)                                                │
│  ──────────────                                                 │
│       ╭──────╮    ╭──────────                                   │
│  0.9 ─│      ╰────╯                                             │
│  0.8 ─│                                                         │
│  0.7 ─┼─────────────────────────────                            │
│       Jan 1    Jan 10    Jan 20    Jan 30                       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 5. Workspace Management

Web-based workspace and team management.

```
┌─────────────────────────────────────────────────────────────────┐
│  Workspaces                                         + New       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  product-research ★                          5 members          │
│  Q1 2025 user research                       47 personas        │
│  Last activity: 2 hours ago                                     │
│                                                  [ Open ]       │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  marketing-team                              3 members          │
│  Marketing persona library                   23 personas        │
│  Last activity: 1 day ago                                       │
│                                                  [ Open ]       │
│  ─────────────────────────────────────────────────────────────  │
│                                                                 │
│  engineering                                 8 members          │
│  Developer personas                          156 personas       │
│  Last activity: 3 hours ago                                     │
│                                                  [ Open ]       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Implementation Tasks

### Phase 1: Foundation

- [ ] Set up FastAPI + Jinja2 templates
- [ ] Implement htmx integration
- [ ] Add Alpine.js for reactivity
- [ ] Create base layout and navigation
- [ ] Implement authentication flow

### Phase 2: Persona Browser

- [ ] Create persona grid/list views
- [ ] Implement persona detail page
- [ ] Add search and filtering
- [ ] Implement pagination
- [ ] Add export functionality

### Phase 3: Generation Wizard

- [ ] Create multi-step wizard
- [ ] Implement file upload handling
- [ ] Add configuration form
- [ ] Create progress display
- [ ] Implement result review

### Phase 4: Quality & Workspace

- [ ] Create quality dashboard
- [ ] Add trend visualisations
- [ ] Implement workspace management
- [ ] Add team member management
- [ ] Create activity feed

---

## Technology Stack

Per [ADR-0035](../../../decisions/adrs/ADR-0035-webui-technology-selection.md):

| Component | Technology | Rationale |
|-----------|------------|-----------|
| Backend | FastAPI | Existing API, async support |
| Templates | Jinja2 | Python ecosystem, familiar |
| Interactivity | htmx | Minimal JS, server-driven |
| Reactivity | Alpine.js | Lightweight, declarative |
| Styling | Tailwind CSS | Utility-first, rapid development |
| Charts | Chart.js | Simple, lightweight |

---

## CLI Commands

```bash
# Start WebUI server
persona web start [--port PORT] [--host HOST]

# Stop WebUI server
persona web stop

# WebUI status
persona web status

# Generate static export
persona web export --output ./dist/
```

---

## Success Criteria

- [ ] Persona browsing works across browsers
- [ ] Generation wizard completes end-to-end
- [ ] Quality dashboard displays correctly
- [ ] Workspace management functional
- [ ] Authentication and authorisation working
- [ ] Responsive on mobile devices
- [ ] Test coverage >= 85%

---

## Configuration

```yaml
# WebUI configuration
webui:
  enabled: true
  host: 0.0.0.0
  port: 8080

  authentication:
    enabled: true
    provider: local  # local | oauth | saml

  features:
    generation: true
    quality_dashboard: true
    team_management: true

  appearance:
    theme: auto  # light | dark | auto
    logo_url: null
    custom_css: null

  security:
    cors_origins: ["http://localhost:3000"]
    session_timeout: 24h
    rate_limiting:
      enabled: true
      requests_per_minute: 60
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Scope creep | High | Medium | Foundation only, defer features |
| Browser compatibility | Medium | Medium | Progressive enhancement |
| Performance issues | Medium | Medium | htmx partial updates |
| Security vulnerabilities | Low | High | Security audit, OWASP |
| Mobile UX issues | Medium | Low | Responsive design, testing |

---

## Related Documentation

- [v2.0.0 Milestone](../../milestones/v2.0.0.md)
- [F-151: Team Workspace Support](F-151-team-workspace-support.md)
- [R-020: WebUI Framework Selection](../../../research/R-020-webui-framework-selection.md)
- [ADR-0035: WebUI Technology Selection](../../../decisions/adrs/ADR-0035-webui-technology-selection.md)
- [F-098: TUI Dashboard](../completed/F-098-tui-dashboard.md)

---

**Status**: Planned
