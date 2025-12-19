# R-018: Documentation Audit and Project Automation

## Overview

| Attribute | Value |
|-----------|-------|
| **Date** | 2025-12-19 |
| **Category** | Documentation & DevOps |
| **Scope** | User-facing documentation, CLI discoverability, project automation |

## Executive Summary

This research document presents findings from a comprehensive audit of Persona's user-facing documentation and an analysis of automation opportunities. The audit evaluates documentation accessibility for three user personas: non-expert users, expert users, and administrators.

**Key Findings:**

1. Documentation structure follows Diátaxis framework effectively
2. Tutorials are comprehensive but have minor inconsistencies
3. CLI has excellent depth but discoverability challenges for hidden commands
4. Project automation is partially implemented; significant opportunities exist
5. No Makefile or unified task runner exists

---

## Part 1: Documentation Audit

### 1.1 Documentation Structure Assessment

**Current Structure:**

```
docs/
├── README.md                 # Hub with Diátaxis navigation
├── tutorials/                # 7 learning-oriented guides
├── guides/                   # 12 task-oriented how-tos
├── reference/                # 7 technical specifications
├── explanation/              # Conceptual content (sparse)
├── use-cases/                # User intent definitions
├── assets/                   # Images and prompts
└── development/              # Developer documentation
```

**Assessment:** ✅ **Good**

The structure follows the [Diátaxis framework](https://diataxis.fr/) with clear separation of concerns:
- Tutorials for learning
- Guides for task completion
- Reference for lookup
- Explanation for understanding

**Gap Identified:** The `explanation/` directory is sparse (only `privacy-considerations.md`). Consider adding:
- How generation works (referenced in tutorials but doesn't exist)
- Architecture overview for curious users
- LLM selection rationale

---

### 1.2 Non-Expert User Experience

**Target Persona:** First-time user, basic CLI knowledge, wants to generate personas quickly.

**Path Tested:** README → Getting Started Tutorial → First generation

#### Strengths

| Aspect | Rating | Notes |
|--------|--------|-------|
| Installation instructions | ✅ Excellent | Clear, copy-pasteable commands |
| Prerequisites | ✅ Excellent | Clear Python version, API key links |
| Step-by-step flow | ✅ Excellent | 7 numbered steps with checkpoints |
| Sample data included | ✅ Excellent | Demo project with ready-to-use data |
| Troubleshooting | ✅ Good | Common issues addressed |
| Output explanation | ✅ Good | Tutorial 02 explains structure |

#### Issues Identified

| Issue | Severity | Location | Recommendation |
|-------|----------|----------|----------------|
| Quick Start in docs/README.md uses deprecated command | Medium | `docs/README.md` line 13-14 | Change `persona create experiment` to `persona experiment create` |
| Tutorial references non-existent doc | Low | `02-understanding-output.md` line 253 | `how-generation-works.md` doesn't exist |
| Model names outdated | Low | Various | Update to 2025 model names where shown |

#### Recommended Improvements

1. **Add "First 5 Minutes" Quick Start Card**
   - One-page visual guide showing: Install → Configure → Generate
   - QR code linking to demo project

2. **Create Interactive Mode Tutorial**
   - The `-i` flag enables guided prompts
   - Currently undocumented in tutorials

3. **Add Video Walkthrough Link**
   - Even a simple terminal recording would help

---

### 1.3 Expert User Experience

**Target Persona:** UX researcher, comfortable with CLI, wants advanced features.

**Path Tested:** Guides → CLI Reference → Advanced commands

#### Strengths

| Aspect | Rating | Notes |
|--------|--------|-------|
| CLI Reference completeness | ✅ Excellent | 1255 lines, all commands documented |
| Options tables | ✅ Excellent | Consistent format with types/defaults |
| Examples | ✅ Excellent | Real-world usage patterns |
| Guide coverage | ✅ Good | 12 guides covering common tasks |
| Error handling guide | ✅ Excellent | Comprehensive error codes |

#### Issues Identified

| Issue | Severity | Location | Recommendation |
|-------|----------|----------|----------------|
| Hidden commands poorly discoverable | Medium | CLI Reference line 1192+ | Add "Advanced Features" tutorial |
| Variant/Lineage complex for first-time use | Medium | No tutorial | Add "Research Workflow" tutorial |
| SDK quickstart assumes Python expertise | Low | `tutorials/sdk-quickstart.md` | Add more context for researchers |

#### Recommended Improvements

1. **Create "Power User Cheatsheet"**
   - One-page reference for hidden commands
   - Keyboard shortcuts and aliases

2. **Add Workflow Recipes**
   - "Research Study Workflow" (experiment → variants → compare)
   - "Batch Processing Workflow" (hybrid mode, cost control)

3. **Improve Command Discovery**
   - Add `persona commands --all` to show hidden commands
   - Or `persona advanced` command group

---

### 1.4 Administrator Experience

**Target Persona:** DevOps/IT, setting up for team, managing costs and security.

**Path Tested:** API Key Setup → CI/CD Integration → Security

#### Strengths

| Aspect | Rating | Notes |
|--------|--------|-------|
| API key setup | ✅ Excellent | Multiple providers, .env workflow |
| Security practices | ✅ Excellent | Never commit keys, rotate guidance |
| Budget controls | ✅ Good | PERSONA_BUDGET_* env vars |
| CI/CD guide | ✅ Good | GitHub Actions example |
| Privacy setup | ✅ Excellent | PII detection, anonymisation |

#### Issues Identified

| Issue | Severity | Location | Recommendation |
|-------|----------|----------|----------------|
| No Docker deployment guide | Medium | Missing | Add containerisation guide |
| No multi-user setup guide | Medium | Missing | Add team installation guide |
| No audit log documentation | Low | CLI Reference | Document `audit` commands |

#### Recommended Improvements

1. **Add Deployment Guide**
   - Docker/container deployment
   - Environment variable management
   - Secrets management (Vault, AWS Secrets Manager)

2. **Add Team Administration Guide**
   - Shared configuration
   - Cost allocation per user/project
   - Audit trail for compliance

3. **Document REST API**
   - The `serve` command starts an API server
   - No REST API documentation exists

---

### 1.5 CLI Discoverability Assessment

**Current State:**

```
Visible in --help:
  check, cost, models, init, generate, preview, export, validate, project, config, help

Hidden (require direct access):
  experiment, variant, lineage, compare, cluster, refine, score, evaluate,
  academic, faithfulness, fidelity, diversity, bias, verify, privacy,
  synthesise, audit, serve, dashboard, vendor, model, template, workflow,
  plugin, script
```

**Issue:** 27 commands hidden vs 11 visible. Expert features are difficult to discover.

**Recommendation Matrix:**

| Category | Commands | Recommendation |
|----------|----------|----------------|
| Should be visible | `experiment`, `compare`, `cluster` | Core research workflow |
| Fine as hidden | `lineage`, `audit`, `vendor` | Advanced/internal |
| Needs promotion | `privacy`, `synthesise` | Security/research value |

---

## Part 2: Project Automation Research

### 2.1 Current Automation State

**Existing Automation:**

| Tool | Purpose | Status |
|------|---------|--------|
| GitHub Actions CI | Tests, lint, type check, security | ✅ Implemented |
| Pre-commit hooks | Format, lint, secrets, links | ✅ Implemented |
| PII scan script | Prevent personal data commits | ✅ Implemented |
| pyproject.toml scripts | Package entry point only | ⚠️ Limited |

**Missing Automation:**

| Task | Current Method | Impact |
|------|----------------|--------|
| Run all tests | `pytest tests/` | Manual |
| Build documentation | `mkdocs build` | Manual |
| Release workflow | Manual git tag | Error-prone |
| Development setup | Multiple commands | Friction |
| Demo data generation | Manual | Inconsistent |

### 2.2 Automation Opportunities

#### Priority 1: Makefile or Task Runner

**Recommendation:** Create a `Makefile` for common development tasks.

**Proposed Tasks:**

```makefile
# Development
.PHONY: install dev test lint format type-check

install:          # Install production dependencies
dev:              # Install with all dev dependencies
test:             # Run test suite with coverage
lint:             # Run ruff linter
format:           # Format code with ruff
type-check:       # Run mypy type checking
check:            # Run lint + type-check + test

# Documentation
.PHONY: docs docs-serve docs-build

docs:             # Build and serve documentation
docs-serve:       # Live-reload documentation server
docs-build:       # Build documentation for deployment

# Security
.PHONY: security pii-scan audit

security:         # Run bandit + safety
pii-scan:         # Run PII scan script
audit:            # Full security audit

# Release
.PHONY: release bump-version tag changelog

release:          # Full release workflow
bump-version:     # Increment version in pyproject.toml
tag:              # Create and push git tag
changelog:        # Generate changelog from commits

# Demo & Examples
.PHONY: demo demo-data demo-generate

demo:             # Run full demo workflow
demo-data:        # Generate/refresh demo data
demo-generate:    # Generate personas from demo data

# Cleanup
.PHONY: clean clean-cache clean-build clean-all

clean:            # Remove common artifacts
clean-cache:      # Remove Python caches
clean-build:      # Remove build artifacts
clean-all:        # Full cleanup
```

#### Priority 2: Development Setup Script

**Recommendation:** Create `scripts/setup.sh` for one-command setup.

```bash
#!/bin/bash
# scripts/setup.sh - Development environment setup

# 1. Check Python version
# 2. Create virtual environment
# 3. Install dependencies
# 4. Install pre-commit hooks
# 5. Copy .env.example to .env
# 6. Run initial checks
# 7. Print next steps
```

#### Priority 3: Release Automation

**Recommendation:** Create `scripts/release.sh` for consistent releases.

**Workflow:**
1. Verify branch is main
2. Run full test suite
3. Verify documentation is up to date
4. Check for uncommitted changes
5. Update version in pyproject.toml
6. Generate changelog entry
7. Create git tag
8. Push to remote
9. Create GitHub release

#### Priority 4: Documentation Generation

**Recommendation:** Automate CLI reference generation.

```bash
# scripts/generate-cli-docs.sh
# Parse CLI help output and update docs/reference/cli-reference.md
# Detect drift between implementation and documentation
```

### 2.3 Alternative Task Runners

| Tool | Pros | Cons | Recommendation |
|------|------|------|----------------|
| **Makefile** | Universal, no dependencies, fast | Windows compatibility | ✅ Primary choice |
| **just** | Better syntax, cross-platform | Extra dependency | Consider for cross-platform |
| **invoke** | Python-native, complex tasks | Another dep, less common | Not recommended |
| **nox** | Good for test matrices | Overkill for simple tasks | Not recommended |
| **hatch** | Modern Python, built-in | Lock-in to hatch | Not recommended |

### 2.4 Proposed File Structure

```
Persona/
├── Makefile                    # Primary task automation
├── scripts/
│   ├── setup.sh                # Development setup
│   ├── release.sh              # Release workflow
│   ├── pii_scan.sh             # (existing) PII scanning
│   ├── generate-cli-docs.sh    # CLI docs generation
│   ├── sync-docs.sh            # Documentation sync check
│   └── demo.sh                 # Demo workflow
├── .github/
│   └── workflows/
│       ├── ci.yml              # (existing) CI pipeline
│       ├── release.yml         # NEW: Release automation
│       └── docs.yml            # NEW: Documentation deployment
```

---

## Part 3: Recommendations Summary

### Documentation Improvements

| Priority | Issue | Action | Effort |
|----------|-------|--------|--------|
| P1 | Quick Start uses deprecated command | Fix `docs/README.md` | 5 min |
| P1 | Hidden commands hard to discover | Add "Advanced Features" guide | 2 hrs |
| P2 | No deployment/Docker guide | Create administrator guide | 4 hrs |
| P2 | REST API undocumented | Document `/serve` API | 3 hrs |
| P2 | Missing "How Generation Works" | Create explanation doc | 2 hrs |
| P3 | Tutorial references broken link | Fix or create target | 1 hr |
| P3 | Model names outdated | Update throughout | 1 hr |

### Automation Improvements

| Priority | Task | Action | Effort |
|----------|------|--------|--------|
| P1 | No unified task runner | Create Makefile | 2 hrs |
| P1 | Manual release process | Create release script | 3 hrs |
| P2 | Development setup friction | Create setup.sh | 1 hr |
| P2 | CLI docs can drift | Create generation script | 2 hrs |
| P3 | No documentation CI | Add docs.yml workflow | 1 hr |

### Quick Wins (< 30 minutes each)

1. Fix `docs/README.md` Quick Start command
2. Add `persona commands --all` alias
3. Create `make test` alias for `pytest`
4. Add `.nvmrc` or `.python-version` for tooling
5. Create `CONTRIBUTING.md` with development setup

---

## Related Documentation

- [R-005: CLI Design Patterns](R-005-cli-design-patterns.md)
- [CLI Reference](../../reference/cli-reference.md)
- [Getting Started Tutorial](../../tutorials/01-getting-started.md)
- [CI Workflow](../../../.github/workflows/ci.yml)

---

**Status**: Complete
