# ADR-0035: WebUI Technology Selection

## Status

Planned

## Context

Persona's TUI dashboard (F-098-F-103) provides terminal-based monitoring, but a web-based interface is requested for:
- Non-technical users
- Remote access
- Richer visualisations
- Team dashboards

Need to select web technology that complements existing FastAPI backend.

## Decision

Select **htmx + Alpine.js** for the initial WebUI implementation, with the option to migrate to a more complex framework if needed.

### Technology Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Backend** | FastAPI (existing) | Already in place for REST API |
| **Templating** | Jinja2 (existing) | Used for prompt templates |
| **Interactivity** | htmx | Server-driven, minimal JS |
| **Client state** | Alpine.js | Simple reactivity |
| **Styling** | Tailwind CSS | Utility-first, rapid development |
| **Charts** | Chart.js | Simple, htmx-compatible |

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       WebUI Architecture                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Browser                                                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  htmx (AJAX)  │  Alpine.js (state)  │  Tailwind CSS  │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                  │
│                           ▼ HTTP/WebSocket                   │
│                                                              │
│  Server                                                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                    FastAPI                            │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │   │
│  │  │  REST API   │  │   WebUI     │  │  WebSocket  │  │   │
│  │  │  (existing) │  │  (Jinja2)   │  │  (optional) │  │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │   │
│  └──────────────────────────────────────────────────────┘   │
│                           │                                  │
│                           ▼                                  │
│                  ┌─────────────────┐                        │
│                  │  Persona Core   │                        │
│                  └─────────────────┘                        │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### htmx Patterns

**Server-Driven Updates:**
```html
<!-- Persona list with live search -->
<input type="text"
       name="search"
       hx-get="/api/personas"
       hx-trigger="keyup changed delay:300ms"
       hx-target="#persona-list"
       placeholder="Search personas...">

<div id="persona-list">
  <!-- Server renders HTML fragment -->
</div>
```

**Progress Updates:**
```html
<!-- Generation progress -->
<div hx-get="/api/generation/{{ task_id }}/progress"
     hx-trigger="every 1s"
     hx-swap="outerHTML">
  <progress value="{{ progress }}" max="100"></progress>
  <span>{{ progress }}% complete</span>
</div>
```

**Form Submission:**
```html
<form hx-post="/api/generate"
      hx-target="#result"
      hx-indicator="#loading">
  <textarea name="data">{{ data }}</textarea>
  <button type="submit">Generate</button>
  <span id="loading" class="htmx-indicator">Generating...</span>
</form>

<div id="result"></div>
```

### Alpine.js Patterns

**Client-Side State:**
```html
<div x-data="{ showDetails: false, selectedTab: 'overview' }">
  <button @click="showDetails = !showDetails">
    Toggle Details
  </button>

  <div x-show="showDetails" x-transition>
    <div class="tabs">
      <button @click="selectedTab = 'overview'"
              :class="{ 'active': selectedTab === 'overview' }">
        Overview
      </button>
      <button @click="selectedTab = 'details'"
              :class="{ 'active': selectedTab === 'details' }">
        Details
      </button>
    </div>

    <div x-show="selectedTab === 'overview'">...</div>
    <div x-show="selectedTab === 'details'">...</div>
  </div>
</div>
```

### Page Structure

```
/web/
├── dashboard      # Overview, metrics, recent activity
├── generate       # Generation form and progress
├── personas       # Persona list and detail views
├── experiments    # Experiment management
├── settings       # Configuration
└── admin          # System administration
```

## Consequences

**Positive:**
- Leverages existing FastAPI/Jinja2 infrastructure
- Minimal JavaScript complexity
- Server-side rendering (SEO, performance)
- Progressive enhancement
- Small bundle size (~20KB)

**Negative:**
- Less sophisticated than React/Vue
- Limited offline capability
- Server-dependent interactivity
- May need migration for complex features

## Alternatives Considered

### React/Next.js

**Description:** Full React single-page application.

**Pros:** Rich ecosystem, component reusability, offline support.

**Cons:** Separate codebase, build complexity, bundle size.

**Why Not Chosen:** Overkill for MVP, duplicates backend logic.

### Vue.js

**Description:** Vue with server-side rendering.

**Pros:** Simpler than React, good SSR.

**Cons:** Still requires build step, separate tooling.

**Why Not Chosen:** htmx simpler for server-driven UI.

### Streamlit

**Description:** Python-native web framework.

**Pros:** Pure Python, rapid development.

**Cons:** Limited customisation, not production-grade.

**Why Not Chosen:** Not suitable for production deployment.

### No WebUI (TUI only)

**Description:** Continue with TUI only.

**Pros:** Simple, terminal-native.

**Cons:** Limited audience, no remote access.

**Why Not Chosen:** User demand for web interface.

## Research Reference

See [R-020: WebUI Framework Selection](../../research/R-020-webui-framework-selection.md) for detailed analysis.

---

## Related Documentation

- [R-020: WebUI Framework Selection](../../research/R-020-webui-framework-selection.md)
- [F-098: TUI Dashboard](../../roadmap/features/completed/F-098-tui-dashboard.md)
- [F-105: REST API](../../roadmap/features/completed/F-105-rest-api.md)

---

**Status**: Planned
