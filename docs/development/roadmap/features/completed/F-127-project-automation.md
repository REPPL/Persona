# F-127: Project Automation Infrastructure

## Problem Statement

Persona lacks standardised automation infrastructure for common development tasks. New contributors must manually piece together commands from documentation, and release processes are error-prone. This creates friction for:

1. **New contributors** - Unclear setup process
2. **Regular development** - No unified task runner
3. **Release management** - Manual, error-prone process
4. **Deployment** - No Docker configuration

## Design Approach

Implement comprehensive automation covering:

1. **Makefile** - Unified task runner with auto-generated help
2. **Developer Setup** - One-command onboarding script
3. **Release Automation** - Version bumping with safety checks
4. **Docker Support** - Production and development containers
5. **CI/CD Workflows** - Release and documentation automation

### Architecture

```
Project Root
├── Makefile              # Unified task runner
├── .python-version       # pyenv/asdf support
├── .dockerignore         # Docker build exclusions
├── CONTRIBUTING.md       # Developer guidelines
├── scripts/
│   ├── setup.sh          # Developer onboarding
│   └── release.sh        # Release automation
├── Dockerfile            # Production API
├── Dockerfile.dev        # Development environment
├── docker-compose.yml    # Production orchestration
├── docker-compose.dev.yml # Development orchestration
└── .github/workflows/
    ├── release.yml       # Release automation
    └── docs.yml          # Documentation deployment
```

---

## Implementation Tasks

### P1: Makefile (~150 lines)

- [ ] Create Makefile with auto-generated help
- [ ] Add `install` target for production deps
- [ ] Add `dev` target for all dependencies
- [ ] Add `test` target with coverage
- [ ] Add `lint` target for ruff
- [ ] Add `format` target for code formatting
- [ ] Add `type-check` target for mypy
- [ ] Add `check` target combining lint/type/test
- [ ] Add `security` target for bandit/safety
- [ ] Add `pii-scan` target
- [ ] Add `docs` and `docs-build` targets
- [ ] Add `clean` target

### P2: Developer Setup (~320 lines)

- [ ] Create `.python-version` with 3.12
- [ ] Create `scripts/setup.sh` with:
  - Python version check
  - Virtual environment creation
  - Dependency installation
  - Pre-commit hook setup
  - `.env` file creation
  - Installation verification
- [ ] Create `CONTRIBUTING.md` with:
  - Getting started guide
  - Development workflow
  - Code standards
  - Pull request process
  - Release process

### P3: Release Automation (~180 lines)

- [ ] Create `scripts/release.sh` with:
  - Clean git state verification
  - Main branch check
  - Up-to-date verification
  - Test execution
  - PII scan
  - Version calculation
  - `pyproject.toml` update
  - Commit and tag creation
  - Push instructions

### P4: Docker Support (~205 lines)

- [ ] Create `.dockerignore` (~35 lines)
- [ ] Create `Dockerfile` with:
  - Multi-stage build
  - `persona[api]` installation
  - Non-root user
  - Health check
  - Port 8000 exposure
- [ ] Create `Dockerfile.dev` with:
  - Full `persona[all]` installation
  - Hot reload support
- [ ] Create `docker-compose.yml` with:
  - API service
  - Optional Ollama service
  - Volume configuration
- [ ] Create `docker-compose.dev.yml` with:
  - Development service
  - Volume mounts
  - Hot reload configuration

### P5: GitHub Workflows (~145 lines)

- [ ] Create `.github/workflows/release.yml` with:
  - Tag push trigger
  - Checkout with full history
  - Install and test
  - Changelog generation
  - GitHub Release creation
- [ ] Create `.github/workflows/docs.yml` with:
  - Main push trigger (docs changes)
  - MkDocs build with --strict
  - GitHub Pages deployment

### Documentation

- [ ] Update `docs/development/research/README.md` index
- [ ] Update `docs/development/roadmap/features/planned/README.md` index

---

## Success Criteria

| Component | Verification |
|-----------|--------------|
| Makefile | `make help` shows all targets |
| Makefile | Each target executes successfully |
| setup.sh | Fresh clone + run = working environment |
| release.sh | Safety checks block invalid releases |
| release.sh | Version calculation works correctly |
| Dockerfile | `docker build` succeeds |
| Dockerfile | Container health check passes |
| docker-compose | `docker compose up` starts API |
| docker-compose.dev | Volume mounts enable hot reload |
| release.yml | Tag push creates GitHub Release |
| docs.yml | Docs changes trigger build |

---

## Dependencies

| Dependency | Type | Notes |
|------------|------|-------|
| pyproject.toml | Existing | Version source, dependency groups |
| ci.yml | Existing | Pattern reference for workflows |
| scripts/pii_scan.sh | Existing | Called by release script |
| mkdocs.yml | Required | Must exist for docs workflow |

---

## Testing Approach

### Manual Verification

1. **Makefile**: Run each target, verify output
2. **setup.sh**: Test in clean environment
3. **release.sh**: Test with `--dry-run` flag
4. **Docker**: Build and run containers
5. **Workflows**: Push test tags/docs changes

### Automated Verification

CI workflow validates:
- Makefile targets work
- Docker builds succeed
- Documentation builds pass

---

## Related Documentation

- [R-019: Project Automation Implementation](../../research/R-019-project-automation-implementation.md)
- [R-018: Documentation Audit & Automation](../../research/R-018-documentation-audit-and-automation.md)
- [Deployment Guide](../../../guides/deployment.md)
- [REST API Reference](../../../guides/rest-api.md)
