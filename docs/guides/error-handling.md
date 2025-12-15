# Error Handling Guide

This guide covers how to handle errors when using the Persona SDK and CLI.

## Exception Hierarchy

Persona uses a structured exception hierarchy:

```
PersonaError (base)
├── ConfigurationError
│   ├── MissingAPIKeyError
│   ├── InvalidConfigError
│   └── ProviderNotFoundError
├── DataError
│   ├── DataLoadError
│   ├── DataFormatError
│   └── EmptyDataError
├── ProviderError
│   ├── APIError
│   ├── RateLimitError
│   ├── AuthenticationError
│   └── ModelNotFoundError
├── ValidationError
│   ├── InvalidPersonaError
│   └── SchemaValidationError
└── BudgetError
    └── CostLimitExceededError
```

## Handling SDK Errors

### Basic Error Handling

```python
from persona import Generator
from persona.core.errors import (
    PersonaError,
    ConfigurationError,
    DataError,
    ProviderError,
    ValidationError,
)

generator = Generator(provider="anthropic")

try:
    result = generator.generate("./data/", count=5)
except ConfigurationError as e:
    print(f"Configuration problem: {e}")
    print("Check your API keys and settings")
except DataError as e:
    print(f"Data problem: {e}")
    print("Verify your input data format")
except ProviderError as e:
    print(f"Provider error: {e}")
    print("Check API status or try again later")
except ValidationError as e:
    print(f"Validation error: {e}")
except PersonaError as e:
    print(f"Persona error: {e}")
```

### Specific Error Types

```python
from persona.core.errors import (
    MissingAPIKeyError,
    RateLimitError,
    CostLimitExceededError,
)

try:
    result = generator.generate("./data/", count=5)
except MissingAPIKeyError as e:
    print(f"Missing API key for provider: {e.provider}")
    print(f"Set the {e.env_var} environment variable")
except RateLimitError as e:
    print(f"Rate limited. Retry after: {e.retry_after} seconds")
except CostLimitExceededError as e:
    print(f"Cost ${e.estimated_cost:.4f} exceeds limit ${e.limit:.4f}")
```

## Common Error Scenarios

### Missing API Key

```python
# Error: MissingAPIKeyError
# Cause: ANTHROPIC_API_KEY not set

# Solution 1: Set environment variable
import os
os.environ["ANTHROPIC_API_KEY"] = "your-key"

# Solution 2: Pass key directly
generator = Generator(provider="anthropic", api_key="your-key")
```

### Invalid Data Path

```python
# Error: DataLoadError
# Cause: Path doesn't exist or isn't readable

from pathlib import Path

data_path = Path("./data/")
if not data_path.exists():
    print(f"Data path doesn't exist: {data_path}")
elif not data_path.is_dir() and not data_path.is_file():
    print(f"Invalid path type: {data_path}")
```

### Empty Data

```python
# Error: EmptyDataError
# Cause: No usable content in data files

from persona.core.data.loader import DataLoader

loader = DataLoader()
try:
    data = loader.load(Path("./data/"))
    if not data.content:
        print("Data loaded but content is empty")
except EmptyDataError:
    print("No valid data found in the specified path")
```

### Rate Limiting

```python
import time
from persona.core.errors import RateLimitError

def generate_with_backoff(generator, data_path, count, max_retries=5):
    for attempt in range(max_retries):
        try:
            return generator.generate(data_path, count=count)
        except RateLimitError as e:
            if attempt < max_retries - 1:
                wait = e.retry_after or (2 ** attempt)
                print(f"Rate limited. Waiting {wait}s...")
                time.sleep(wait)
            else:
                raise
```

### Authentication Failure

```python
from persona.core.errors import AuthenticationError

try:
    result = generator.generate("./data/", count=3)
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    print("Possible causes:")
    print("  - Invalid API key")
    print("  - Expired API key")
    print("  - Incorrect key for provider")
```

## CLI Error Handling

The CLI provides helpful error messages with guidance:

```bash
# Missing API key
$ persona generate ./data/
Error: ANTHROPIC_API_KEY environment variable not set.

To fix this:
  1. Get an API key from https://console.anthropic.com/
  2. Set the environment variable:
     export ANTHROPIC_API_KEY=your-key-here

# Invalid data path
$ persona generate ./nonexistent/
Error: Data path not found: ./nonexistent/

# Rate limiting
$ persona generate ./data/ --count 100
Warning: Rate limited by provider. Retrying in 30 seconds...
```

## Error Recovery Strategies

### Graceful Degradation

```python
def generate_personas_safe(data_path, providers=None):
    """Try multiple providers, return first successful result."""
    providers = providers or ["anthropic", "openai", "gemini"]
    last_error = None

    for provider in providers:
        try:
            generator = Generator(provider=provider)
            return generator.generate(data_path, count=3)
        except ConfigurationError:
            continue  # Try next provider
        except ProviderError as e:
            last_error = e
            continue

    if last_error:
        raise last_error
    raise ConfigurationError("No providers configured")
```

### Partial Results

```python
from persona import Generator
from persona.core.errors import ProviderError

def generate_batch_safe(data_paths, count=3):
    """Process multiple paths, collect partial results on failure."""
    generator = Generator(provider="anthropic")
    results = []
    failures = []

    for path in data_paths:
        try:
            result = generator.generate(path, count=count)
            results.extend(result.personas)
        except ProviderError as e:
            failures.append({"path": str(path), "error": str(e)})

    return {
        "personas": results,
        "failures": failures,
        "success_rate": len(results) / (len(results) + len(failures))
    }
```

## Logging Errors

Configure logging to capture errors:

```python
import logging
from persona import Generator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("persona")

try:
    generator = Generator(provider="anthropic")
    result = generator.generate("./data/", count=5)
except Exception as e:
    logger.exception("Generation failed")
    raise
```

---

## Related Documentation

- [SDK Quickstart](../tutorials/sdk-quickstart.md)
- [SDK Patterns](./sdk-patterns.md)
- [Error Codes Reference](../reference/error-codes.md)
- [Troubleshooting](./troubleshooting.md)
