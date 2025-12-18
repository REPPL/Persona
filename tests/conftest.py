"""
Shared pytest fixtures for Persona tests.

This module provides common fixtures used across unit and integration tests,
including mock LLM providers, test data, and CLI helpers.
"""

import json
from collections.abc import Generator
from pathlib import Path
from typing import Any

import pytest
import responses

# Test data directory
TEST_DATA_DIR = Path(__file__).parent / "data"
SYNTHETIC_DATA_DIR = TEST_DATA_DIR / "synthetic"
MOCK_RESPONSES_DIR = TEST_DATA_DIR / "mock_responses"
EXPECTED_OUTPUTS_DIR = TEST_DATA_DIR / "expected_outputs"


# =============================================================================
# Path Fixtures
# =============================================================================


@pytest.fixture
def test_data_dir() -> Path:
    """Return the test data directory path."""
    return TEST_DATA_DIR


@pytest.fixture
def synthetic_data_dir() -> Path:
    """Return the synthetic test data directory path."""
    return SYNTHETIC_DATA_DIR


@pytest.fixture
def mock_responses_dir() -> Path:
    """Return the mock API responses directory path."""
    return MOCK_RESPONSES_DIR


# =============================================================================
# Environment Fixtures
# =============================================================================


@pytest.fixture
def env_no_api_keys(monkeypatch: pytest.MonkeyPatch) -> None:
    """Remove all API keys from environment."""
    for key in ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY"]:
        monkeypatch.delenv(key, raising=False)


@pytest.fixture
def env_mock_api_keys(monkeypatch: pytest.MonkeyPatch) -> dict[str, str]:
    """Set mock API keys for testing."""
    keys = {
        "OPENAI_API_KEY": "sk-test-mock-openai-key",
        "ANTHROPIC_API_KEY": "sk-ant-test-mock-anthropic-key",
        "GOOGLE_API_KEY": "test-mock-google-key",
    }
    for key, value in keys.items():
        monkeypatch.setenv(key, value)
    return keys


# =============================================================================
# Temporary Directory Fixtures
# =============================================================================


@pytest.fixture
def temp_experiment_dir(tmp_path: Path) -> Path:
    """Create a temporary experiment directory."""
    exp_dir = tmp_path / "experiments" / "test-experiment"
    exp_dir.mkdir(parents=True)
    return exp_dir


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Create a temporary output directory."""
    output_dir = tmp_path / "outputs"
    output_dir.mkdir(parents=True)
    return output_dir


# =============================================================================
# Mock Response Loaders
# =============================================================================


def load_mock_response(provider: str, filename: str) -> dict[str, Any]:
    """Load a mock API response from the test data directory."""
    response_path = MOCK_RESPONSES_DIR / provider / filename
    if not response_path.exists():
        raise FileNotFoundError(f"Mock response not found: {response_path}")
    with open(response_path) as f:
        return json.load(f)


@pytest.fixture
def mock_response_loader():
    """Provide the mock response loader function."""
    return load_mock_response


# =============================================================================
# OpenAI Mock Fixtures
# =============================================================================


@pytest.fixture
def mock_openai_success(env_mock_api_keys: dict[str, str]) -> Generator:
    """Mock successful OpenAI API response."""
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://api.openai.com/v1/chat/completions",
            json=load_mock_response("openai", "chat_completion_success.json"),
            status=200,
        )
        yield rsps


@pytest.fixture
def mock_openai_error(env_mock_api_keys: dict[str, str]) -> Generator:
    """Mock OpenAI API error response."""
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://api.openai.com/v1/chat/completions",
            json=load_mock_response("openai", "error_response.json"),
            status=401,
        )
        yield rsps


# =============================================================================
# Anthropic Mock Fixtures
# =============================================================================


@pytest.fixture
def mock_anthropic_success(env_mock_api_keys: dict[str, str]) -> Generator:
    """Mock successful Anthropic API response."""
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://api.anthropic.com/v1/messages",
            json=load_mock_response("anthropic", "messages_success.json"),
            status=200,
        )
        yield rsps


@pytest.fixture
def mock_anthropic_error(env_mock_api_keys: dict[str, str]) -> Generator:
    """Mock Anthropic API error response."""
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://api.anthropic.com/v1/messages",
            json=load_mock_response("anthropic", "error_response.json"),
            status=401,
        )
        yield rsps


# =============================================================================
# Gemini Mock Fixtures
# =============================================================================


@pytest.fixture
def mock_gemini_success(env_mock_api_keys: dict[str, str]) -> Generator:
    """Mock successful Google Gemini API response."""
    with responses.RequestsMock() as rsps:
        # Gemini uses a different URL pattern with API key
        rsps.add_callback(
            responses.POST,
            responses.matchers.re.compile(
                r"https://generativelanguage\.googleapis\.com/.*"
            ),
            callback=lambda req: (
                200,
                {},
                json.dumps(
                    load_mock_response("gemini", "generate_content_success.json")
                ),
            ),
        )
        yield rsps


# =============================================================================
# Multi-Provider Fixtures
# =============================================================================


@pytest.fixture
def mock_all_providers_success(
    mock_openai_success,
    mock_anthropic_success,
    mock_gemini_success,
) -> None:
    """Mock all providers with successful responses."""
    pass  # Fixtures are combined


# =============================================================================
# Test Data Fixtures
# =============================================================================


@pytest.fixture
def sample_interview_csv() -> str:
    """Return path to sample interview CSV."""
    return str(SYNTHETIC_DATA_DIR / "interviews_small.csv")


@pytest.fixture
def sample_survey_json() -> str:
    """Return path to sample survey JSON."""
    return str(SYNTHETIC_DATA_DIR / "survey_responses.json")


@pytest.fixture
def sample_feedback_md() -> str:
    """Return path to sample feedback markdown."""
    return str(SYNTHETIC_DATA_DIR / "user_feedback.md")


@pytest.fixture
def sample_mixed_format_dir() -> str:
    """Return path to mixed format test data directory."""
    return str(SYNTHETIC_DATA_DIR / "mixed_format")


# =============================================================================
# Schema Fixtures
# =============================================================================


@pytest.fixture
def valid_persona_schema() -> dict[str, Any]:
    """Load valid persona JSON schema."""
    schema_path = EXPECTED_OUTPUTS_DIR / "persona_schema_valid.json"
    if schema_path.exists():
        with open(schema_path) as f:
            return json.load(f)
    # Default minimal schema if file doesn't exist yet
    return {
        "id": "persona-001",
        "name": "Test Persona",
        "demographics": {"age_range": "25-34"},
        "goals": ["Test goal"],
        "pain_points": ["Test pain point"],
    }


# =============================================================================
# CLI Testing Fixtures
# =============================================================================


@pytest.fixture
def cli_runner():
    """Provide Typer CLI test runner."""
    from typer.testing import CliRunner

    return CliRunner()


# =============================================================================
# Markers
# =============================================================================


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "real_api: marks tests requiring real API calls (deselect with '-m \"not real_api\"')",
    )


def pytest_collection_modifyitems(config, items):
    """Skip real_api tests unless explicitly requested."""
    if not config.getoption("-m") or "real_api" not in config.getoption("-m"):
        skip_real_api = pytest.mark.skip(
            reason="Real API tests skipped by default. Use '-m real_api' to run."
        )
        for item in items:
            if "real_api" in item.keywords:
                item.add_marker(skip_real_api)
