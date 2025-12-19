# Contributing to Persona

Thank you for your interest in contributing to Persona! This guide will help you get started.

## Getting Started

### Prerequisites

- Python 3.12 or higher
- Git
- A code editor (VS Code, PyCharm, etc.)

### Quick Setup

```bash
# Clone the repository
git clone https://github.com/REPPL/Persona.git
cd Persona

# Run the setup script
./scripts/setup.sh

# Activate the virtual environment
source .venv/bin/activate

# Verify your setup
persona check
```

The setup script will:
1. Verify Python version
2. Create a virtual environment
3. Install all dependencies
4. Set up pre-commit hooks
5. Create a `.env` template

### Manual Setup

If you prefer manual setup:

```bash
# Create and activate virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# Install all dependencies
pip install -e ".[all]"

# Install pre-commit hooks
pre-commit install

# Create .env from template
cp .env.example .env
```

---

## Development Workflow

### Branching Strategy

We use a simple branching model:

- `main` - Stable release branch
- `feature/*` - Feature development branches
- `fix/*` - Bug fix branches
- `docs/*` - Documentation updates

### Making Changes

1. **Create a branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**

3. **Run quality checks:**
   ```bash
   make check
   ```

4. **Commit with conventional commits:**
   ```bash
   git commit -m "feat(cli): add export command"
   ```

5. **Push and create PR:**
   ```bash
   git push -u origin feature/your-feature-name
   ```

### Available Make Targets

```bash
make help       # Show all commands
make test       # Run tests
make lint       # Run linter
make format     # Format code
make type-check # Run type checker
make check      # Run all checks
make docs       # Serve documentation
make clean      # Remove build artefacts
```

---

## Code Standards

### Python Style

- **Line length:** 88 characters (Black/Ruff default)
- **Formatting:** Ruff (runs automatically via pre-commit)
- **Type hints:** Required for public APIs
- **Docstrings:** Google style for public functions

### British English

**Important:** All text must use British English spelling:

| American | British |
|----------|---------|
| color | colour |
| organize | organise |
| behavior | behaviour |
| optimize | optimise |
| center | centre |

This applies to:
- Documentation
- Code comments
- Error messages
- Commit messages

### Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation only
- `style` - Formatting, no code change
- `refactor` - Code restructuring
- `test` - Adding tests
- `chore` - Maintenance tasks

**Examples:**
```
feat(cli): add persona export command
fix(generation): handle empty input gracefully
docs(guides): add deployment documentation
refactor(providers): simplify API abstraction
```

---

## Testing

### Running Tests

```bash
# Run all tests (excluding real API tests)
make test

# Run all tests including API tests
make test-all

# Run specific test file
pytest tests/test_cli.py

# Run with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ --cov=src/persona --cov-report=html
```

### Writing Tests

- Place tests in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- Use fixtures for setup
- Mark slow/API tests appropriately

```python
import pytest

@pytest.mark.real_api
def test_generate_with_real_api():
    """Test that requires actual API calls."""
    ...
```

---

## Pull Request Process

### Before Submitting

1. **Run all checks:**
   ```bash
   make check
   ```

2. **Run PII scan:**
   ```bash
   make pii-scan
   ```

3. **Update documentation** if needed

4. **Add tests** for new functionality

### PR Template

When creating a PR, include:

```markdown
## Summary
Brief description of changes

## Changes
- Change 1
- Change 2

## Test Plan
How to verify the changes work

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] British English used
- [ ] No PII included
```

### Review Process

1. All PRs require at least one review
2. CI must pass
3. Documentation must be updated for new features
4. Tests must maintain or improve coverage

---

## Release Process

Releases are managed by maintainers using the release script:

```bash
./scripts/release.sh [major|minor|patch]
```

This will:
1. Verify clean git state
2. Run all tests
3. Run PII scan
4. Update version in `pyproject.toml`
5. Create commit and tag
6. Print push instructions

### Versioning

We follow [Semantic Versioning](https://semver.org/):

- **Major** (1.0.0) - Breaking changes
- **Minor** (0.1.0) - New features, backward compatible
- **Patch** (0.0.1) - Bug fixes, backward compatible

---

## Project Structure

```
Persona/
├── src/persona/           # Main package
│   ├── core/              # Core functionality
│   ├── providers/         # LLM providers
│   ├── services/          # Business logic
│   └── ui/                # CLI and TUI
├── tests/                 # Test suite
├── docs/                  # Documentation
│   ├── tutorials/         # Learning guides
│   ├── guides/            # How-to guides
│   ├── reference/         # Technical reference
│   └── development/       # Developer docs
├── scripts/               # Utility scripts
└── templates/             # Prompt templates
```

---

## Getting Help

- **Issues:** [GitHub Issues](https://github.com/REPPL/Persona/issues)
- **Discussions:** [GitHub Discussions](https://github.com/REPPL/Persona/discussions)
- **Documentation:** [docs/](./docs/)

---

## Licence

By contributing, you agree that your contributions will be licensed under the GNU General Public Licence v3 (GPLv3).
