# Tests

Test suite for Persona.

## Structure

```
tests/
├── conftest.py           # Shared fixtures
├── unit/                 # Unit tests
│   ├── test_data_loaders.py
│   ├── test_llm_providers.py
│   └── ...
└── integration/          # Integration tests
    ├── test_cli.py
    └── test_generation.py
```

## Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=src/persona --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_data_loaders.py
```

## Coverage Target

Minimum 80% coverage required for releases.

*Tests will be added alongside v0.1.0 implementation.*

---

## Related Documentation

- [ADR-0017: Testing Alongside Implementation](../docs/development/decisions/adrs/ADR-0017-testing-alongside.md)
- [Development Hub](../docs/development/README.md)
