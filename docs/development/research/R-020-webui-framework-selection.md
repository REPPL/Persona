# R-020: WebUI Framework Selection

Research into web framework options for implementing a browser-based interface for Persona.

## Executive Summary

This document evaluates modern web frameworks for building Persona's browser-based interface, considering the existing Python backend, CLI-first architecture, and the goal of extending rather than replacing the TUI.

**Key Finding:** A Python-native approach using FastAPI (already implemented) with a modern frontend framework offers the best path forward. The existing REST API (v1.1.0) provides the backend foundation.

**Recommendation:** Adopt **htmx + Alpine.js** for the initial WebUI (v2.0.0), with an optional migration path to **React + TypeScript** for complex interactive features in future versions.

---

## Context

### Current Architecture

Persona v1.11.0 provides multiple interfaces:

| Interface | Framework | Status | Use Case |
|-----------|-----------|--------|----------|
| CLI | Typer + Rich | ✅ Complete | Primary interface, all features |
| Interactive CLI | questionary | ✅ Complete | Guided workflows |
| TUI Dashboard | Textual | ✅ Complete | Real-time monitoring |
| REST API | FastAPI | ✅ Complete | Programmatic access |
| **WebUI** | TBD | ⏸️ Deferred | Browser-based access |

### Requirements for WebUI

1. **Leverage existing REST API** - No backend duplication
2. **Real-time updates** - Generation progress, quality scores
3. **Familiar UX patterns** - Similar to TUI but more accessible
4. **Enterprise deployment** - SSO, permissions, audit logging
5. **Responsive design** - Desktop and tablet support
6. **Offline capability** - Local-first when using Ollama

---

## Framework Categories

### Category 1: Python-Centric (Server-Side Rendering)

| Framework | Approach | Learning Curve | Best For |
|-----------|----------|----------------|----------|
| **htmx + Alpine.js** | HTML-over-the-wire | Low | Simple interactivity, rapid development |
| **Django + HTMX** | Full-stack Python | Low | Complete web applications |
| **FastAPI + Jinja2** | API + templates | Low | API-first with HTML views |
| **Streamlit** | Python-only | Very Low | Data dashboards, prototypes |
| **Gradio** | Python-only | Very Low | ML model demos |
| **Panel/Holoviz** | Python-only | Low | Data science apps |
| **NiceGUI** | Python-only | Low | Desktop-style UIs |

### Category 2: JavaScript/TypeScript Frontends

| Framework | Approach | Learning Curve | Best For |
|-----------|----------|----------------|----------|
| **React + TypeScript** | Component-based SPA | Medium | Complex interactive UIs |
| **Vue.js** | Progressive framework | Medium | Gradual adoption |
| **Svelte/SvelteKit** | Compiled components | Medium | Performance-critical UIs |
| **Next.js** | React + SSR | Medium-High | Full-featured web apps |
| **Solid.js** | Fine-grained reactivity | Medium | High-performance UIs |

### Category 3: Desktop-Web Hybrid

| Framework | Approach | Learning Curve | Best For |
|-----------|----------|----------------|----------|
| **Tauri** | Rust + Web | Medium | Desktop app distribution |
| **Electron** | Chromium + Node.js | Medium | Cross-platform desktop |
| **Neutralino.js** | Lightweight web view | Low | Simple desktop apps |

---

## Alternatives Analysis

### Option 1: htmx + Alpine.js (Recommended for v2.0.0)

**Approach:** Enhance server-rendered HTML with minimal JavaScript

**Pros:**
- Minimal JavaScript, leverages existing Python/FastAPI backend
- Progressive enhancement over existing API
- Rapid prototyping and iteration
- Small bundle size (~14KB combined)
- No build step required
- Accessible by default (semantic HTML)
- Seamless integration with FastAPI/Jinja2

**Cons:**
- Limited for highly interactive features
- Less common in enterprise (perception issue)
- May require React migration for complex features later

**Architecture:**
```
FastAPI (existing) → Jinja2 Templates → HTML → htmx/Alpine.js
         ↓                    ↓              ↓
    REST API            HTML responses   Client interactivity
```

**Fit for Persona:**
- Persona's core workflow (configure → generate → review) is form-based
- Real-time updates achievable via htmx polling or WebSockets
- Matches CLI-first philosophy (simple, focused)
- Team features can use Alpine.js for client-side state

### Option 2: React + TypeScript + Tailwind CSS

**Approach:** Modern SPA with component architecture

**Pros:**
- Industry standard, large ecosystem
- Excellent TypeScript support
- Rich component libraries (shadcn/ui, Radix)
- Good for complex interactive dashboards
- Strong testing ecosystem (Jest, React Testing Library)
- Easy to hire developers

**Cons:**
- Requires separate build process
- Larger bundle sizes (100KB+)
- More complexity than needed for initial WebUI
- API design must consider client needs

**Architecture:**
```
FastAPI (existing) → REST/GraphQL API → React SPA
         ↓                   ↓              ↓
    Backend logic       JSON responses   Rich client UI
```

**Fit for Persona:**
- Better for future complex features (drag-and-drop persona builder, visual workflow editor)
- May be overkill for initial release
- Consider for v2.1.0+ if htmx reaches limits

### Option 3: Streamlit / Gradio

**Approach:** Pure Python UI frameworks

**Pros:**
- No frontend code required
- Rapid prototyping
- Built-in components for data apps
- Good for internal tools and demos

**Cons:**
- Limited customisation
- Not production-ready for public-facing apps
- Difficult to integrate with existing REST API
- Session management challenges
- Performance issues at scale

**Fit for Persona:**
- Useful for internal research dashboards
- Not suitable for production WebUI
- Consider for `persona dashboard --dev` developer mode

### Option 4: Vue.js or Svelte

**Approach:** Alternative modern JavaScript frameworks

**Pros:**
- Vue: Gentle learning curve, good documentation
- Svelte: Excellent performance, simple syntax
- Both have active communities

**Cons:**
- Smaller ecosystems than React
- Fewer enterprise-ready component libraries
- Less common in enterprise settings

**Fit for Persona:**
- Viable alternatives if React feels too heavy
- Svelte particularly good for performance-sensitive features
- Consider if team has existing Vue/Svelte experience

### Option 5: Desktop Hybrid (Tauri/Electron)

**Approach:** Package web app as desktop application

**Pros:**
- Native desktop experience
- Offline-first possible
- File system access
- Can bundle Ollama

**Cons:**
- Distribution complexity
- Platform-specific issues
- Users already have CLI/TUI

**Fit for Persona:**
- Not recommended for v2.0.0
- Consider for v3.0.0 if desktop distribution becomes priority
- Tauri preferred over Electron (Rust backend, smaller bundles)

---

## Recommendation

### v2.0.0: htmx + Alpine.js + Tailwind CSS

**Rationale:**
1. **Minimal new complexity** - Leverages existing FastAPI backend
2. **Rapid development** - No separate frontend build, familiar Python templates
3. **Progressive enhancement** - Can add React later where needed
4. **CLI-aligned philosophy** - Simple, focused, gets out of the way
5. **Enterprise-ready** - SSO via FastAPI integrations, audit via existing system

**Implementation Approach:**
```
src/persona/web/
├── __init__.py
├── app.py              # FastAPI app with template routes
├── templates/
│   ├── base.html       # Layout with htmx/Alpine.js
│   ├── dashboard.html  # Main dashboard
│   ├── generate.html   # Generation workflow
│   ├── experiments.html # Experiment browser
│   └── components/     # Reusable partials
├── static/
│   ├── css/tailwind.css
│   └── js/app.js       # Alpine.js components
└── routes/
    ├── pages.py        # HTML page routes
    └── partials.py     # htmx partial routes
```

### Future: React Migration Path

If WebUI needs exceed htmx capabilities (complex drag-and-drop, real-time collaboration, offline-first):

1. **v2.1.0**: Introduce React for specific complex features
2. **v2.2.0**: Migrate remaining features to React
3. **v3.0.0**: Full React SPA with optional Tauri desktop app

---

## Technology Stack for v2.0.0

| Layer | Technology | Justification |
|-------|------------|---------------|
| **Backend** | FastAPI (existing) | Already implemented in v1.1.0 |
| **Templates** | Jinja2 | Python-native, familiar syntax |
| **Interactivity** | htmx | HTML-over-the-wire, minimal JS |
| **Client State** | Alpine.js | Lightweight reactivity |
| **Styling** | Tailwind CSS | Utility-first, rapid development |
| **Icons** | Heroicons | Tailwind-compatible SVG icons |
| **Charts** | Chart.js or Vega-Lite | Quality metrics visualisation |
| **WebSockets** | FastAPI WebSockets | Real-time generation progress |

---

## Key Features for WebUI v2.0.0

### Core Features

| Feature | Priority | Complexity |
|---------|----------|------------|
| Dashboard overview | P0 | Low |
| Experiment browser | P0 | Low |
| Generation workflow | P0 | Medium |
| Persona viewer | P0 | Low |
| Quality metrics display | P1 | Low |
| Cost tracking | P1 | Low |
| User authentication | P0 | Medium |
| Project management | P1 | Medium |

### Real-Time Features

| Feature | Technology | Complexity |
|---------|------------|------------|
| Generation progress | htmx polling or WebSocket | Medium |
| Live logs | WebSocket | Medium |
| Cost updates | htmx polling | Low |
| Notifications | WebSocket | Low |

### Enterprise Features

| Feature | Priority | Dependencies |
|---------|----------|--------------|
| SSO (OAuth2/OIDC) | P0 | ADR-0036 |
| Role-based access | P1 | ADR-0036, F-142 |
| Audit logging | P1 | F-123 (existing) |
| Team workspaces | P2 | F-141 |

---

## Security Considerations

### Authentication Options

| Method | Complexity | Enterprise Ready |
|--------|------------|------------------|
| **OAuth2/OIDC** | Medium | Yes (recommended) |
| **SAML 2.0** | High | Yes |
| **API Keys** | Low | Limited |
| **Session Cookies** | Low | Basic |

**Recommendation:** Implement OAuth2/OIDC using `authlib` or `python-social-auth` for SSO support.

### Security Headers

- Content Security Policy (CSP)
- CORS configuration (already in FastAPI)
- CSRF protection for forms
- Rate limiting (already implemented)

---

## Performance Considerations

### htmx Optimisations

- Use `hx-boost` for SPA-like navigation
- Implement `hx-push-url` for browser history
- Cache static templates
- Use `hx-indicator` for loading states

### API Optimisations

- GraphQL for complex queries (optional)
- Response compression (gzip/brotli)
- CDN for static assets
- Redis caching for expensive queries

---

## Proposed Features

This research informs the following features:

1. **F-151: WebUI Dashboard** (P0, v2.0.0)
2. **F-152: WebUI Authentication** (P0, v2.0.0)
3. **F-153: WebUI Generation Workflow** (P0, v2.0.0)
4. **F-154: WebUI Experiment Browser** (P1, v2.0.0)
5. **F-155: WebUI Real-Time Updates** (P1, v2.0.0)

---

## Research Sources

### htmx and Hypermedia

- [htmx Documentation](https://htmx.org/docs/)
- [Hypermedia Systems Book](https://hypermedia.systems/)
- [htmx + FastAPI Integration](https://htmx.org/examples/)
- [Alpine.js Documentation](https://alpinejs.dev/start-here)

### Python Web Frameworks

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Jinja2 Templates](https://jinja.palletsprojects.com/)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [Streamlit vs Gradio Comparison](https://medium.com/@younes.azhar/streamlit-vs-gradio-ee1d24a5ef4b)

### React and Modern Frontends

- [React Documentation](https://react.dev/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Shadcn/ui Components](https://ui.shadcn.com/)
- [State of JS 2024](https://stateofjs.com/)

### Desktop Hybrid

- [Tauri Documentation](https://tauri.app/)
- [Electron vs Tauri Comparison](https://blog.logrocket.com/tauri-electron-comparison-migration-guide/)

### Enterprise Considerations

- [OAuth2 for Python](https://authlib.org/)
- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/tutorial/security/)

---

## Related Documentation

- [F-089: REST API](../roadmap/features/completed/F-089-rest-api.md)
- [F-098: TUI Dashboard](../roadmap/features/completed/F-098-tui-dashboard-app.md)
- [R-012: TUI Layout Patterns](./R-012-tui-fullscreen-layout-patterns.md)
- [ADR-0035: WebUI Technology Selection](../decisions/adrs/ADR-0035-webui-technology-selection.md) (Planned)
