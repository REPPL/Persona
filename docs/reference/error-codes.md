# Error Codes Reference

Complete reference of error codes and exceptions in Persona.

## Error Code Format

Error codes follow the format: `PERSONA-XXX-YYY`

- `XXX`: Category (see table below)
- `YYY`: Specific error within category

| Category | Code Range | Description |
|----------|------------|-------------|
| Configuration | 100-199 | Setup and configuration errors |
| Data | 200-299 | Data loading and format errors |
| Provider | 300-399 | LLM provider and API errors |
| Validation | 400-499 | Persona validation errors |
| Budget | 500-599 | Cost and budget errors |
| Internal | 900-999 | Internal errors |

## Configuration Errors (100-199)

### PERSONA-100-001: MissingAPIKeyError

**Message:** `API key not found for provider: {provider}`

**Cause:** Required API key environment variable is not set.

**Solution:**
```bash
# Set the appropriate environment variable
export ANTHROPIC_API_KEY=your-key      # For Anthropic
export OPENAI_API_KEY=your-key         # For OpenAI
export GOOGLE_API_KEY=your-key         # For Google/Gemini
```

### PERSONA-100-002: InvalidConfigError

**Message:** `Invalid configuration: {details}`

**Cause:** Configuration file has invalid syntax or values.

**Solution:**
- Check YAML/JSON syntax in config files
- Verify all required fields are present
- Use `persona check` to validate configuration

### PERSONA-100-003: ProviderNotFoundError

**Message:** `Provider not found: {provider}`

**Cause:** Specified provider is not supported or not installed.

**Solution:**
```bash
# List available providers
persona models --list-providers

# Use a supported provider
persona generate ./data/ --provider anthropic
```

### PERSONA-100-004: ModelNotConfiguredError

**Message:** `Model not configured: {model}`

**Cause:** Specified model is not available for the provider.

**Solution:**
```bash
# List available models
persona models --provider anthropic

# Use a supported model
persona generate ./data/ --model claude-sonnet-4-5-20250929
```

## Data Errors (200-299)

### PERSONA-200-001: DataLoadError

**Message:** `Failed to load data from: {path}`

**Cause:** File or directory could not be read.

**Solution:**
- Verify path exists and is accessible
- Check file permissions
- Ensure path is a file or directory (not a device/socket)

### PERSONA-200-002: DataFormatError

**Message:** `Unsupported or invalid data format: {format}`

**Cause:** Data file format is not recognised or is malformed.

**Supported formats:**
- CSV (`.csv`)
- JSON (`.json`)
- Markdown (`.md`)
- Plain text (`.txt`)

**Solution:**
```bash
# Preview data to check format
persona preview ./data/

# Convert to supported format if needed
```

### PERSONA-200-003: EmptyDataError

**Message:** `No data found in: {path}`

**Cause:** Data source contains no usable content.

**Solution:**
- Verify files contain actual content
- Check that CSV files have data rows (not just headers)
- Ensure markdown files have text content

### PERSONA-200-004: EncodingError

**Message:** `Failed to decode file: {path}`

**Cause:** File uses unsupported text encoding.

**Solution:**
- Convert file to UTF-8 encoding
- Specify encoding explicitly if supported

## Provider Errors (300-399)

### PERSONA-300-001: APIError

**Message:** `API request failed: {details}`

**Cause:** LLM provider API returned an error.

**Solution:**
- Check provider status page
- Verify API key is valid
- Try again after a few minutes

### PERSONA-300-002: RateLimitError

**Message:** `Rate limit exceeded. Retry after: {seconds}s`

**Cause:** Too many requests to the provider API.

**Solution:**
- Wait for the specified retry time
- Use `--delay` flag to slow down requests
- Upgrade API tier for higher limits

### PERSONA-300-003: AuthenticationError

**Message:** `Authentication failed for provider: {provider}`

**Cause:** API key is invalid, expired, or has insufficient permissions.

**Solution:**
- Verify API key is correct
- Check key hasn't expired
- Ensure key has required permissions

### PERSONA-300-004: ModelNotFoundError

**Message:** `Model not found: {model}`

**Cause:** Specified model doesn't exist or isn't available.

**Solution:**
```bash
# List available models for provider
persona models --provider anthropic
```

### PERSONA-300-005: ContextLengthError

**Message:** `Input exceeds model context length: {tokens} > {max_tokens}`

**Cause:** Input data is too large for the model.

**Solution:**
- Use a model with larger context window
- Reduce input data size
- Enable automatic chunking

### PERSONA-300-006: TimeoutError

**Message:** `Request timed out after {seconds}s`

**Cause:** Provider took too long to respond.

**Solution:**
- Increase timeout with `--timeout` flag
- Reduce request complexity
- Try again later

## Validation Errors (400-499)

### PERSONA-400-001: InvalidPersonaError

**Message:** `Generated persona is invalid: {details}`

**Cause:** LLM output doesn't match expected persona schema.

**Solution:**
- Try a different model or temperature
- Check prompt templates
- Use `--include-reasoning` to debug

### PERSONA-400-002: SchemaValidationError

**Message:** `Schema validation failed: {field}`

**Cause:** Persona data doesn't match required schema.

**Solution:**
- Review generated output format
- Check schema requirements
- Adjust generation parameters

### PERSONA-400-003: MissingFieldError

**Message:** `Required field missing: {field}`

**Cause:** Generated persona is missing a required field.

**Solution:**
- Use higher detail level (`--detail-level detailed`)
- Try more capable model
- Check input data quality

## Budget Errors (500-599)

### PERSONA-500-001: CostLimitExceededError

**Message:** `Estimated cost ${estimated} exceeds limit ${limit}`

**Cause:** Generation would exceed configured cost limit.

**Solution:**
```bash
# Increase limit
persona generate ./data/ --max-cost 10.00

# Or reduce scope
persona generate ./data/ --count 3  # Fewer personas
```

### PERSONA-500-002: TokenLimitExceededError

**Message:** `Token count {count} exceeds limit {limit}`

**Cause:** Input or output tokens exceed configured limits.

**Solution:**
- Reduce input data size
- Lower persona count
- Increase token limits in config

## Internal Errors (900-999)

### PERSONA-900-001: InternalError

**Message:** `Internal error: {details}`

**Cause:** Unexpected error in Persona internals.

**Solution:**
- Report issue at: https://github.com/anthropics/persona/issues
- Include full error traceback
- Provide reproduction steps

### PERSONA-900-002: ConfigCorruptedError

**Message:** `Configuration file corrupted: {path}`

**Cause:** Configuration file is unreadable or corrupted.

**Solution:**
```bash
# Reset configuration
persona config reset

# Or manually remove config file
rm ~/.persona/config.yaml
```

## Exit Codes

CLI commands return these exit codes:

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Configuration error |
| 3 | Data error |
| 4 | Provider error |
| 5 | Validation error |
| 6 | Budget exceeded |
| 130 | User interrupt (Ctrl+C) |

## Debugging

Enable debug output for more information:

```bash
# CLI
persona generate ./data/ -vv

# SDK
import logging
logging.getLogger("persona").setLevel(logging.DEBUG)
```

---

## Related Documentation

- [Error Handling Guide](../guides/error-handling.md)
- [Troubleshooting Guide](../guides/troubleshooting.md)
- [SDK Patterns](../guides/sdk-patterns.md)
