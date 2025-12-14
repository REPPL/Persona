# Testing Guide

Comprehensive guide to testing Persona, covering automated tests, manual testing, and contributing new tests.

## Contents

| Document | Description |
|----------|-------------|
| [Synthetic Data](synthetic_data.md) | Test data design and generation methodology |
| [Manual Testing](../../../tests/manual/README.md) | Manual test procedures and scripts |
| [Test Fixtures](../../../tests/fixtures/README.md) | Fixture reference and usage |

## Testing Philosophy

Persona follows a testing pyramid approach with three layers:

1. **Unit Tests** (base): Fast, isolated tests for individual components
2. **Integration Tests** (middle): Tests verifying component interactions
3. **Manual Tests** (top): Human verification of user-facing functionality

All features require ≥80% test coverage before release.

## Quick Start

```bash
# Activate virtual environment
source .venv/bin/activate

# Install all dependencies
pip install -e ".[all]"

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src/persona tests/

# Run specific test categories
pytest tests/unit/           # Unit tests only
pytest tests/integration/    # Integration tests only
pytest -m real_api           # Real API tests only (requires keys)
```

## Test Organisation

```
tests/
├── conftest.py              # Shared fixtures
├── fixtures/
│   ├── llm_mocks.py         # Mock LLM responses
│   ├── data_samples.py      # Test data generators
│   └── cli_helpers.py       # CLI test utilities
├── data/
│   ├── synthetic/           # Synthetic input data
│   ├── expected_outputs/    # Expected result schemas
│   └── mock_responses/      # Mock API responses
├── unit/
│   ├── core/                # Tests for persona.core
│   └── ui/                  # Tests for persona.ui
├── integration/             # Cross-component tests
└── manual/                  # Manual test scripts
```

## Running Tests

### All Tests (Default)

```bash
pytest tests/
```

This runs all unit and integration tests with mock APIs. Fast and free.

### With Coverage Report

```bash
pytest --cov=src/persona --cov-report=html tests/
open htmlcov/index.html  # View coverage report
```

### Specific Test Files

```bash
pytest tests/unit/core/test_data_loaders.py
pytest tests/integration/test_generation_flow.py
```

### Specific Test Functions

```bash
pytest tests/unit/core/test_data_loaders.py::test_csv_loading
```

### By Marker

```bash
pytest -m "not real_api"     # Exclude real API tests (default)
pytest -m real_api           # Only real API tests
pytest -m "slow"             # Only slow tests
```

## Mock vs Real API Tests

### Mock Tests (Default)

All standard tests use mocked API responses:
- No API keys required
- Fast and deterministic
- Free (no API costs)
- Run automatically in CI

### Real API Tests

Tests marked with `@pytest.mark.real_api` call actual APIs:
- Require valid API keys
- Incur API costs (designed to be minimal)
- Skipped by default
- Run explicitly: `pytest -m real_api`

**Setting up API keys:**
```bash
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export GOOGLE_API_KEY="your-key"
```

Real API tests are designed to:
- Use minimal tokens (short prompts, low max_tokens)
- Test one provider at a time
- Document expected costs in docstrings

## Writing Tests

### Unit Test Example

```python
# tests/unit/core/test_data_loaders.py

import pytest
from persona.core.data_loaders import CSVLoader

class TestCSVLoader:
    """Tests for CSV data loader."""

    def test_loads_valid_csv(self, sample_interview_csv):
        """Test loading a valid CSV file."""
        loader = CSVLoader()
        data = loader.load(sample_interview_csv)

        assert len(data) == 3
        assert "transcript" in data[0]

    def test_handles_missing_file(self):
        """Test error handling for missing files."""
        loader = CSVLoader()

        with pytest.raises(FileNotFoundError):
            loader.load("nonexistent.csv")

    def test_handles_empty_csv(self, tmp_path):
        """Test handling of empty CSV files."""
        empty_csv = tmp_path / "empty.csv"
        empty_csv.write_text("")

        loader = CSVLoader()
        with pytest.raises(ValueError, match="Empty file"):
            loader.load(str(empty_csv))
```

### Integration Test Example

```python
# tests/integration/test_generation_flow.py

import pytest
from tests.fixtures.cli_helpers import run_cli_command, assert_cli_success

class TestGenerationFlow:
    """End-to-end tests for persona generation."""

    def test_full_generation_mock(
        self,
        cli_runner,
        mock_openai_success,
        sample_interview_csv,
        temp_output_dir,
    ):
        """Test complete generation flow with mocked API."""
        result = run_cli_command(
            app,
            ["generate", "--from", sample_interview_csv, "--mock"]
        )

        assert_cli_success(result)
        assert "Generated 1 persona" in result.output

    @pytest.mark.real_api
    def test_full_generation_openai(
        self,
        cli_runner,
        sample_interview_csv,
    ):
        """Test generation with real OpenAI API.

        Cost: ~$0.01 (uses small input, low max_tokens)
        """
        result = run_cli_command(
            app,
            ["generate", "--from", sample_interview_csv, "--provider", "openai"]
        )

        assert_cli_success(result)
```

### Using Fixtures

```python
def test_with_mock_api(mock_openai_success, sample_interview_csv):
    """Test using mock API and sample data fixtures."""
    # mock_openai_success automatically mocks OpenAI API
    # sample_interview_csv provides path to test CSV
    pass

def test_with_temp_dirs(temp_experiment_dir, temp_output_dir):
    """Test using temporary directories."""
    # Directories are created fresh for each test
    # Automatically cleaned up after test
    pass

def test_environment(env_mock_api_keys):
    """Test with mock API keys in environment."""
    import os
    assert os.environ["OPENAI_API_KEY"].startswith("sk-test")
```

## Test Data

See [Synthetic Data](synthetic_data.md) for detailed documentation on test data design.

### Quick Reference

| File | Format | Records | Use Case |
|------|--------|---------|----------|
| `interviews_small.csv` | CSV | 3 | Quick tests |
| `interviews_medium.csv` | CSV | 10 | Realistic tests |
| `survey_responses.json` | JSON | 5 | JSON loading |
| `user_feedback.md` | Markdown | 3 | Markdown loading |
| `mixed_format/` | Mixed | Various | Multi-format tests |

### Creating Custom Test Data

```python
from tests.fixtures.data_samples import (
    generate_interview_csv,
    generate_survey_json,
)

# Generate custom CSV
csv_data = generate_interview_csv(num_interviews=5)

# Generate custom JSON
json_data = generate_survey_json(num_responses=10)
```

## Manual Testing

Manual tests verify user-facing functionality that automated tests cannot fully cover.

**Location:** `tests/manual/`

### Per-Version Test Scripts

Each version has a manual test script:
- `v0.1.0_test_script.md`
- `v0.2.0_test_script.md`
- etc.

### Running Manual Tests

1. Checkout the version to test
2. Install in fresh environment
3. Follow test script step-by-step
4. Record results
5. Share output with Claude for review

See [Manual Testing Guide](../../../tests/manual/README.md) for details.

## CI/CD Integration

Tests run automatically on:
- Pull requests
- Pushes to main branch
- Release tags

### CI Pipeline

```yaml
# Runs on every PR/push
- pytest tests/ --cov=src/persona
- Check coverage ≥ 80%
- Lint with ruff
- Type check with mypy
```

### Release Pipeline

```yaml
# Runs on release tags
- Full test suite
- Real API tests (with secrets)
- Build and publish
```

## Troubleshooting

### Common Issues

**Tests can't find modules:**
```bash
pip install -e ".[all]"  # Install in editable mode
```

**Mock responses not loading:**
```bash
# Check file exists
ls tests/data/mock_responses/openai/
```

**Real API tests failing:**
```bash
# Verify API key is set
echo $OPENAI_API_KEY
```

### Debugging Tests

```bash
# Verbose output
pytest -v tests/unit/

# Show print statements
pytest -s tests/unit/

# Stop on first failure
pytest -x tests/

# Debug with pdb
pytest --pdb tests/unit/test_specific.py
```

---

## Related Documentation

- [Synthetic Data](synthetic_data.md) - Test data design methodology
- [Manual Testing Guide](../../../tests/manual/README.md)
- [Test Fixtures Reference](../../../tests/fixtures/README.md)
- [ADR-0017: Testing Alongside](../decisions/adrs/ADR-0017-testing-alongside.md)
