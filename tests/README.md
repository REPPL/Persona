# Tests

Test suite for Persona with comprehensive automated and manual testing.

## Structure

```
tests/
├── conftest.py              # Shared pytest fixtures
├── fixtures/                # Test helpers and factories
│   ├── llm_mocks.py         # Mock LLM API responses
│   ├── data_samples.py      # Synthetic data generators
│   └── cli_helpers.py       # CLI testing utilities
├── data/                    # Test data files
│   ├── synthetic/           # Synthetic input data
│   ├── expected_outputs/    # Expected result schemas
│   └── mock_responses/      # Mock API response files
├── unit/                    # Unit tests
│   ├── core/                # Tests for persona.core
│   └── ui/                  # Tests for persona.ui
├── integration/             # Integration tests
└── manual/                  # Manual test scripts (per-version)
```

## Running Tests

```bash
# Activate virtual environment
source .venv/bin/activate

# Run all tests (mocked, fast)
pytest tests/

# Run with coverage report
pytest --cov=src/persona --cov-report=html tests/

# Run specific categories
pytest tests/unit/              # Unit tests only
pytest tests/integration/       # Integration tests only
pytest -m real_api              # Real API tests (requires keys)

# Verbose output
pytest -v tests/
```

## Test Categories

### Automated Tests

| Category | Location | API Calls | Speed |
|----------|----------|-----------|-------|
| Unit | `tests/unit/` | Mocked | Fast |
| Integration | `tests/integration/` | Mocked | Medium |
| Real API | Any (marked) | Real | Slow |

### Manual Tests

Manual test scripts for human verification: `tests/manual/`

Each version has a dedicated test script:
- `v0.1.0_test_script.md`
- `v0.2.0_test_script.md`
- etc.

## Coverage Target

**Minimum 80% coverage required for releases.**

```bash
# Check coverage
pytest --cov=src/persona --cov-report=term-missing tests/

# Generate HTML report
pytest --cov=src/persona --cov-report=html tests/
open htmlcov/index.html
```

## API Testing

### Mock Tests (Default)

All standard tests use mocked API responses. No API keys required.

### Real API Tests

Tests marked with `@pytest.mark.real_api` require actual API keys:

```bash
# Set API keys
export OPENAI_API_KEY="your-key"
export ANTHROPIC_API_KEY="your-key"
export GOOGLE_API_KEY="your-key"

# Run real API tests
pytest -m real_api
```

---

## Related Documentation

- [Testing Guide](../docs/development/testing/) - Comprehensive testing documentation
- [Synthetic Data](../docs/development/testing/synthetic_data.md) - Test data design and bias mitigation
- [Manual Testing](manual/README.md) - Manual test procedures
- [Test Fixtures](fixtures/README.md) - Fixture reference
- [ADR-0017: Testing Alongside](../docs/development/decisions/adrs/ADR-0017-testing-alongside.md)
