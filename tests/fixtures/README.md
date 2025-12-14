# Test Fixtures

This directory contains reusable fixtures and helper functions for Persona tests.

## Modules

### llm_mocks.py

Factory functions for creating mock LLM API responses.

**Functions:**
- `create_openai_response()` - Create OpenAI chat completion response
- `create_anthropic_response()` - Create Anthropic messages response
- `create_gemini_response()` - Create Google Gemini response
- `create_persona_generation_response()` - Create formatted persona output
- `create_error_response()` - Create provider-specific error responses

**Usage:**
```python
from tests.fixtures.llm_mocks import create_openai_response

# Create a mock response
response = create_openai_response(
    content="Generated persona content here",
    model="gpt-4",
    prompt_tokens=100,
    completion_tokens=200,
)
```

### data_samples.py

Functions to generate synthetic test data.

**Functions:**
- `generate_interview_csv()` - Generate interview data in CSV format
- `generate_survey_json()` - Generate survey responses in JSON format
- `generate_feedback_markdown()` - Generate user feedback in Markdown
- `write_synthetic_data_files()` - Write all synthetic data to directory

**Usage:**
```python
from tests.fixtures.data_samples import generate_interview_csv

# Generate CSV data
csv_content = generate_interview_csv(num_interviews=5)

# Write to file or use directly in tests
```

### cli_helpers.py

Utilities for testing CLI commands.

**Functions:**
- `run_cli_command()` - Execute CLI command and return result
- `assert_cli_success()` - Assert command succeeded
- `assert_cli_failure()` - Assert command failed with expected code
- `assert_output_contains()` - Assert output contains strings
- `assert_file_created()` - Assert file was created
- `assert_json_file_valid()` - Assert JSON file is valid
- `assert_experiment_structure()` - Assert experiment directory structure
- `assert_output_structure()` - Assert output directory structure

**Usage:**
```python
from tests.fixtures.cli_helpers import run_cli_command, assert_cli_success

# Test a CLI command
result = run_cli_command(app, ["check"])
assert_cli_success(result)
assert "Persona" in result.output
```

## Shared Fixtures (conftest.py)

The main `conftest.py` provides pytest fixtures used across all tests:

### Path Fixtures
- `test_data_dir` - Path to test data directory
- `synthetic_data_dir` - Path to synthetic data
- `mock_responses_dir` - Path to mock API responses

### Environment Fixtures
- `env_no_api_keys` - Remove all API keys from environment
- `env_mock_api_keys` - Set mock API keys for testing

### Mock API Fixtures
- `mock_openai_success` - Mock successful OpenAI response
- `mock_openai_error` - Mock OpenAI error response
- `mock_anthropic_success` - Mock successful Anthropic response
- `mock_anthropic_error` - Mock Anthropic error response
- `mock_gemini_success` - Mock successful Gemini response
- `mock_all_providers_success` - Mock all providers

### Test Data Fixtures
- `sample_interview_csv` - Path to small interview CSV
- `sample_survey_json` - Path to survey JSON
- `sample_feedback_md` - Path to feedback Markdown
- `sample_mixed_format_dir` - Path to mixed format directory

### Temporary Directory Fixtures
- `temp_experiment_dir` - Temporary experiment directory
- `temp_output_dir` - Temporary output directory

### Other Fixtures
- `cli_runner` - Typer CLI test runner
- `valid_persona_schema` - Valid persona JSON schema

## Test Data Structure

```
tests/data/
├── synthetic/
│   ├── interviews_small.csv      # 3 interviews
│   ├── interviews_medium.csv     # 10 interviews
│   ├── survey_responses.json     # Survey data
│   ├── user_feedback.md          # Feedback in Markdown
│   └── mixed_format/             # Multiple formats
├── expected_outputs/
│   ├── persona_schema_valid.json # Valid persona example
│   └── metadata_schema.json      # Valid metadata example
└── mock_responses/
    ├── openai/
    │   ├── chat_completion_success.json
    │   └── error_response.json
    ├── anthropic/
    │   ├── messages_success.json
    │   └── error_response.json
    └── gemini/
        ├── generate_content_success.json
        └── error_response.json
```

## Adding New Fixtures

When adding new test fixtures:

1. **Factory functions** go in the appropriate module (`llm_mocks.py`, `data_samples.py`, etc.)
2. **Pytest fixtures** go in `conftest.py`
3. **Static test data** goes in `tests/data/`

Document new fixtures in this README.

---

## Related Documentation

- [Testing Guide](../../docs/development/testing/)
- [Manual Testing](../manual/README.md)
