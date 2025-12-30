# F-144: Plugin Testing Utilities

## Overview

| Attribute | Value |
|-----------|-------|
| **Feature ID** | F-144 |
| **Title** | Plugin Testing Utilities |
| **Priority** | P1 (High) |
| **Category** | Developer Experience |
| **Milestone** | [v1.13.0](../../milestones/v1.13.0.md) |
| **Status** | 📋 Planned |
| **Dependencies** | F-107 (Plugin System), F-141 (Plugin Development CLI) |

---

## Problem Statement

Plugin developers need:
- Test fixtures with sample personas and data
- Mock providers for testing without API calls
- Assertion helpers for validating plugin output
- Integration test harness for end-to-end testing

Without these, plugin testing is difficult and inconsistent.

---

## Design Approach

Provide a comprehensive `persona.testing` module with fixtures, mocks, and helpers.

---

## Key Capabilities

### 1. Test Fixtures

Pre-built fixtures for common testing scenarios.

```python
# conftest.py in plugin project
from persona.testing import fixtures

@pytest.fixture
def sample_persona():
    return fixtures.sample_persona()

@pytest.fixture
def sample_personas():
    return fixtures.sample_personas(count=5)

@pytest.fixture
def sample_input_data():
    return fixtures.sample_input_data()

@pytest.fixture
def minimal_persona():
    return fixtures.minimal_persona()

@pytest.fixture
def complex_persona():
    return fixtures.complex_persona()
```

**Available Fixtures:**
```python
# persona/testing/fixtures.py

def sample_persona() -> dict:
    """A typical persona with all standard fields."""
    return {
        "name": "Alex Johnson",
        "demographics": {
            "age": 34,
            "location": "London, UK",
            "occupation": "Product Manager"
        },
        "behaviours": [
            "Early adopter of technology",
            "Prefers mobile over desktop"
        ],
        "goals": [
            "Streamline team workflows",
            "Reduce meeting overhead"
        ],
        "frustrations": [
            "Too many tools to manage",
            "Lack of integration"
        ],
        "quote": "I need tools that work together seamlessly."
    }

def sample_personas(count: int = 5) -> list[dict]:
    """Multiple diverse personas for batch testing."""

def sample_input_data() -> str:
    """Sample interview transcript for persona generation."""

def minimal_persona() -> dict:
    """Persona with only required fields."""

def complex_persona() -> dict:
    """Persona with all optional fields populated."""
```

### 2. Mock Providers

Mock LLM providers for testing without API calls.

```python
from persona.testing import MockProvider

@pytest.fixture
def mock_provider():
    provider = MockProvider()
    provider.set_response({
        "name": "Test User",
        "demographics": {"age": 30}
    })
    return provider

def test_generation(mock_provider):
    result = await generate(data, provider=mock_provider)
    assert result.name == "Test User"
    assert mock_provider.call_count == 1
```

**MockProvider Features:**
```python
class MockProvider:
    def __init__(self):
        self.calls: list[MockCall] = []
        self.responses: list[Any] = []

    def set_response(self, response: Any) -> None:
        """Set the response for the next call."""
        self.responses = [response]

    def set_responses(self, responses: list[Any]) -> None:
        """Set multiple responses for sequential calls."""
        self.responses = responses

    def set_error(self, error: Exception) -> None:
        """Make next call raise an error."""
        self.error = error

    async def generate(self, prompt: str, **kwargs) -> Any:
        self.calls.append(MockCall(prompt=prompt, kwargs=kwargs))
        if hasattr(self, 'error'):
            raise self.error
        return self.responses.pop(0) if self.responses else {}

    @property
    def call_count(self) -> int:
        return len(self.calls)

    @property
    def last_call(self) -> MockCall | None:
        return self.calls[-1] if self.calls else None

    def assert_called_with(self, prompt_contains: str) -> None:
        """Assert last call contained expected prompt."""
        assert self.last_call is not None
        assert prompt_contains in self.last_call.prompt
```

### 3. Assertion Helpers

Custom assertions for plugin validation.

```python
from persona.testing import assertions

def test_formatter_output(formatter, sample_persona):
    output = formatter.format(sample_persona)

    # String assertions
    assertions.assert_non_empty_string(output)
    assertions.assert_contains(output, "Alex Johnson")

    # Persona assertions
    parsed = formatter.parse(output)
    assertions.assert_valid_persona(parsed)
    assertions.assert_persona_has_fields(parsed, ["name", "demographics"])

    # Format-specific assertions
    assertions.assert_valid_json(output)
    assertions.assert_valid_yaml(output)
```

**Available Assertions:**
```python
# persona/testing/assertions.py

def assert_valid_persona(persona: dict) -> None:
    """Assert persona has valid structure."""
    assert "name" in persona
    assert isinstance(persona.get("name"), str)
    # ... more validations

def assert_persona_has_fields(persona: dict, fields: list[str]) -> None:
    """Assert persona contains specified fields."""
    for field in fields:
        assert field in persona, f"Missing field: {field}"

def assert_valid_formatter(formatter: Any) -> None:
    """Assert formatter implements required interface."""
    assert hasattr(formatter, "name")
    assert hasattr(formatter, "file_extension")
    assert callable(getattr(formatter, "format", None))

def assert_valid_loader(loader: Any) -> None:
    """Assert loader implements required interface."""
    assert hasattr(loader, "name")
    assert hasattr(loader, "supported_extensions")
    assert callable(getattr(loader, "load", None))

def assert_non_empty_string(value: Any) -> None:
    """Assert value is a non-empty string."""
    assert isinstance(value, str)
    assert len(value.strip()) > 0

def assert_valid_json(value: str) -> None:
    """Assert string is valid JSON."""
    import json
    json.loads(value)  # Raises on invalid

def assert_valid_yaml(value: str) -> None:
    """Assert string is valid YAML."""
    import yaml
    yaml.safe_load(value)
```

### 4. Integration Test Harness

Test plugins in the full Persona context.

```python
from persona.testing import IntegrationTestCase

class TestMyFormatter(IntegrationTestCase):
    plugin_type = "formatter"
    plugin_name = "my_formatter"

    async def test_format_and_export(self):
        """Test formatter with real generation pipeline."""
        # Generate persona using mock provider
        persona = await self.generate_persona(
            data=self.sample_input_data,
            provider=self.mock_provider
        )

        # Export using our formatter
        output_path = self.temp_dir / "output.myfmt"
        await self.export_persona(persona, output_path, format="my_formatter")

        # Verify
        assert output_path.exists()
        content = output_path.read_text()
        self.assert_valid_persona_format(content)

    async def test_round_trip(self):
        """Test format -> parse -> format produces same result."""
        original = self.sample_persona
        formatted = self.formatter.format(original)
        parsed = self.formatter.parse(formatted)
        reformatted = self.formatter.format(parsed)

        assert formatted == reformatted
```

---

## API

```python
# persona/testing/__init__.py

from persona.testing.fixtures import (
    sample_persona,
    sample_personas,
    sample_input_data,
    minimal_persona,
    complex_persona,
)

from persona.testing.mocks import (
    MockProvider,
    MockCache,
    MockLineageStore,
)

from persona.testing.assertions import (
    assert_valid_persona,
    assert_persona_has_fields,
    assert_valid_formatter,
    assert_valid_loader,
    assert_valid_json,
    assert_valid_yaml,
    assert_non_empty_string,
)

from persona.testing.integration import (
    IntegrationTestCase,
    PluginTestCase,
)

__all__ = [
    # Fixtures
    "sample_persona",
    "sample_personas",
    "sample_input_data",
    "minimal_persona",
    "complex_persona",
    # Mocks
    "MockProvider",
    "MockCache",
    "MockLineageStore",
    # Assertions
    "assert_valid_persona",
    "assert_persona_has_fields",
    "assert_valid_formatter",
    "assert_valid_loader",
    "assert_valid_json",
    "assert_valid_yaml",
    "assert_non_empty_string",
    # Integration
    "IntegrationTestCase",
    "PluginTestCase",
]
```

---

## Implementation Tasks

### Phase 1: Fixtures
- [ ] Create fixture data files
- [ ] Implement fixture functions
- [ ] Add parameterised fixtures
- [ ] Create fixture documentation

### Phase 2: Mocks
- [ ] Implement MockProvider
- [ ] Implement MockCache
- [ ] Implement MockLineageStore
- [ ] Add mock configuration

### Phase 3: Assertions
- [ ] Create persona assertions
- [ ] Create format assertions
- [ ] Create plugin interface assertions
- [ ] Add assertion messages

### Phase 4: Integration Harness
- [ ] Create IntegrationTestCase base
- [ ] Add temporary directory management
- [ ] Integrate with generation pipeline
- [ ] Add cleanup handling

### Phase 5: Documentation
- [ ] Write testing guide
- [ ] Add examples to templates
- [ ] Create API reference
- [ ] Add troubleshooting guide

---

## Success Criteria

- [ ] Fixtures provide realistic test data
- [ ] MockProvider enables testing without API calls
- [ ] Assertions catch common plugin errors
- [ ] Integration harness tests full plugin lifecycle
- [ ] Documentation covers all utilities
- [ ] Test coverage >= 90%

---

## Related Documentation

- [v1.13.0 Milestone](../../milestones/v1.13.0.md)
- [F-107: Plugin System](../completed/F-107-plugin-system.md)
- [F-141: Plugin Development CLI](F-141-plugin-development-cli.md)
- [R-027: Plugin Development Patterns](../../../research/R-027-plugin-development-patterns.md)

---

**Status**: Planned
