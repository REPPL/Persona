# R-019: Project Automation Implementation

## Executive Summary

This research note analyses best practices for Python project automation in 2025, comparing task runners, Docker strategies, and CI/CD patterns. The analysis informs implementation of comprehensive automation infrastructure for Persona.

**Recommendation:** Implement Makefile as unified task runner with POSIX-compatible scripts, multi-stage Docker builds, and GitHub Actions for CI/CD.

---

## Current State of the Art (2025)

### Task Runners

The Python ecosystem offers several task runner options:

| Tool | Type | Pros | Cons |
|------|------|------|------|
| **Make** | Native | Universal, battle-tested, zero deps | Tab syntax, macOS/Linux focus |
| **just** | Rust CLI | Modern syntax, no tab issues | Requires install |
| **invoke** | Python | Pure Python, familiar | Adds dependency |
| **nox** | Python | Session-based, matrix support | Complex for simple tasks |
| **tox** | Python | Multi-env testing | Heavyweight |

**Industry Trend:** Make remains dominant for its ubiquity. Modern projects often combine Make with Python tools for complex scenarios.

### Shell Script Portability

**POSIX Compatibility Challenges:**

| Pattern | macOS | Linux | Solution |
|---------|-------|-------|----------|
| `sed -i` | Requires backup suffix | Works directly | Use `sed -i.bak` + `rm *.bak` |
| `readlink -f` | Not available | Works | Use `cd && pwd` pattern |
| `echo -e` | May not interpret escapes | Works | Use `printf` instead |
| Array syntax | Limited | Full | Use POSIX-compatible alternatives |

### Docker Best Practices

**Multi-Stage Builds (2025 Standard):**

```dockerfile
# Stage 1: Builder with all build tools
FROM python:3.12-slim AS builder
WORKDIR /app
COPY pyproject.toml .
RUN pip wheel -w /wheels -e ".[api]"

# Stage 2: Runtime with minimal footprint
FROM python:3.12-slim
COPY --from=builder /wheels /wheels
RUN pip install --no-cache-dir /wheels/*.whl
```

**Key Practices:**
- Use specific Python version tags (not `latest`)
- Non-root user for security
- Health checks for orchestration
- `.dockerignore` to reduce context size

### GitHub Actions Patterns

**Release Automation:**
- Trigger on tag push (`v*`)
- Generate changelog from conventional commits
- Create GitHub Release with assets

**Documentation Deployment:**
- Trigger on docs changes
- Build with `--strict` mode
- Deploy to GitHub Pages

---

## Alternatives Analysis

### Makefile vs Just vs Invoke

| Criterion | Make | Just | Invoke |
|-----------|------|------|--------|
| **Installation** | Pre-installed | Requires install | pip install |
| **Learning Curve** | Moderate | Low | Low |
| **Platform Support** | macOS/Linux/WSL | All platforms | All platforms |
| **Ecosystem Adoption** | Universal | Growing | Moderate |
| **Complexity Handling** | Good | Excellent | Excellent |
| **IDE Support** | Variable | Good | Good |

**Decision:** Make for Persona due to:
1. Zero installation requirement
2. Industry standard recognition
3. Existing `ci.yml` uses similar patterns
4. Sufficient for project complexity

### Docker Strategy

| Option | Build Time | Image Size | Maintainability |
|--------|------------|------------|-----------------|
| Single Dockerfile | Fast | Large | Simple |
| Multi-Stage | Moderate | Small | Moderate |
| Separate Dev/Prod | Fast | Optimal | Complex |

**Decision:** Multi-stage production + separate dev Dockerfile:
- Production: Small, secure, API-focused
- Development: Full tooling, volume mounts, hot reload

---

## Recommendation

### Implementation Architecture

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
    ├── ci.yml            # Existing CI
    ├── release.yml       # Release automation
    └── docs.yml          # Documentation deployment
```

### Makefile Targets

| Target | Purpose | Command |
|--------|---------|---------|
| `help` | Show available commands | (auto-generated) |
| `install` | Production dependencies | `pip install -e .` |
| `dev` | All dev dependencies | `pip install -e ".[all]"` |
| `test` | Run tests with coverage | `pytest --cov` |
| `lint` | Run ruff linter | `ruff check` |
| `format` | Format code | `ruff format` |
| `type-check` | Run mypy | `mypy src/` |
| `check` | lint + type + test | Combined |
| `security` | bandit + safety | Combined |
| `pii-scan` | Run PII scan | `./scripts/pii_scan.sh` |
| `docs` | Serve documentation | `mkdocs serve` |
| `docs-build` | Build documentation | `mkdocs build` |
| `clean` | Remove build artefacts | rm commands |

### Setup Script Workflow

```bash
./scripts/setup.sh
```

1. Verify Python 3.12+
2. Create virtual environment
3. Install all dependencies
4. Install pre-commit hooks
5. Copy `.env.example` to `.env`
6. Run `persona check`
7. Print activation instructions

### Release Script Workflow

```bash
./scripts/release.sh [major|minor|patch]
```

1. Verify clean git state
2. Verify on main branch
3. Verify up-to-date with remote
4. Run tests
5. Run PII scan
6. Calculate new version
7. Update `pyproject.toml`
8. Create commit + annotated tag
9. Print push instructions

### Docker Configuration

**Production (Dockerfile):**
- Base: `python:3.12-slim`
- Multi-stage build
- Install `persona[api]` only
- Non-root user
- Health check endpoint
- Expose port 8000

**Development (Dockerfile.dev):**
- Base: `python:3.12-slim`
- Install `persona[all]`
- Enable hot reload
- Volume mounts for code

### GitHub Workflows

**release.yml:**
- Trigger: Tag push `v*`
- Steps: Checkout, install, test, changelog, release

**docs.yml:**
- Trigger: Push to main (docs/** changed)
- Steps: Build MkDocs, deploy to Pages

---

## Impact on Existing Decisions

| Area | Impact |
|------|--------|
| CI workflow | Extended with release automation |
| Documentation | Added deployment pipeline |
| Development | Standardised onboarding process |
| Deployment | Docker-first strategy documented |

---

## Implementation Considerations

### POSIX Compatibility

All scripts must work on macOS and Linux:

```bash
# sed -i pattern (macOS-compatible)
sed -i.bak 's/old/new/' file
rm file.bak

# Python version detection
PYTHON=$(command -v python3.12 || command -v python3 || command -v python)

# Colour output (POSIX-safe)
printf '\033[0;32m%s\033[0m\n' "Success"
```

### Docker BuildKit

Modern Docker features require BuildKit:

```bash
# Enable BuildKit (default in Docker 23+)
export DOCKER_BUILDKIT=1
docker build .
```

### GitHub Pages Setup

First-time deployment requires:
1. Repository Settings → Pages
2. Source: GitHub Actions
3. Branch protection for `gh-pages` (optional)

---

## Sources

1. GNU Make Manual: https://www.gnu.org/software/make/manual/
2. Just documentation: https://just.systems/man/en/
3. Docker Python best practices: https://docs.docker.com/language/python/
4. GitHub Actions documentation: https://docs.github.com/en/actions
5. Python Packaging User Guide: https://packaging.python.org/
6. Conventional Commits: https://www.conventionalcommits.org/

---

## Related Documentation

- [F-127: Project Automation Feature Spec](../roadmap/features/planned/F-127-project-automation.md)
- [R-018: Documentation Audit & Automation](./R-018-documentation-audit-and-automation.md)
- [CI Workflow](.github/workflows/ci.yml)
