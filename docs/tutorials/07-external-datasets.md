# External Datasets

Learn how to load data from remote URLs for persona generation.

## Overview

Persona supports loading source data directly from URLs, enabling you to:

- Use publicly available datasets
- Reference shared research data
- Work with remote repositories (e.g., GitHub)

This tutorial covers URL data ingestion, terms acceptance, caching, and attribution tracking.

## Prerequisites

- Completed [Getting Started](01-getting-started.md) tutorial
- Completed [Working with Data Formats](03-data-formats.md) tutorial
- Internet connection for fetching remote data

## Loading Data from URLs

### Basic URL Loading

Use the `--from` flag with a URL instead of a local file path:

```bash
persona generate --from https://example.com/data/interviews.csv
```

Persona automatically:
1. Detects URL vs local file paths
2. Fetches the content with appropriate headers
3. Caches the response locally
4. Tracks attribution metadata

### Supported URL Types

| URL Type | Example | Notes |
|----------|---------|-------|
| Direct URLs | `https://example.com/data.csv` | Any publicly accessible URL |
| GitHub raw | `https://raw.githubusercontent.com/...` | Raw file content |
| GitHub blob | `https://github.com/user/repo/blob/main/data.csv` | Automatically converted to raw URL |
| Gists | `https://gist.github.com/...` | Public gists only |

### GitHub URL Conversion

Persona automatically converts GitHub blob URLs to raw URLs:

```bash
# This:
persona generate --from https://github.com/user/repo/blob/main/data.csv

# Becomes:
# https://raw.githubusercontent.com/user/repo/main/data.csv
```

## Terms Acceptance

When using external data, you must explicitly accept responsibility for:
- Copyright compliance
- Licence terms
- Data usage policies

### Accepting Terms

Use the `--accept-terms` flag:

```bash
persona generate \
  --from https://example.com/data/interviews.csv \
  --accept-terms
```

Without this flag, Persona will prompt you to confirm:

```
⚠️  External Data Source Detected

URL: https://example.com/data/interviews.csv

By proceeding, you confirm that:
1. You have permission to use this data
2. Your usage complies with any applicable licence
3. You accept responsibility for data usage

Accept terms? [y/N]:
```

### Why Terms Acceptance?

External data may have:
- Copyright restrictions
- Licence requirements (CC-BY, MIT, etc.)
- Usage limitations
- Privacy considerations

The `--accept-terms` flag creates an audit trail showing you acknowledged these responsibilities.

## Caching

Persona caches fetched URLs to:
- Reduce network traffic
- Speed up repeated runs
- Enable offline work with previously fetched data

### Cache Location

Cached data is stored in:
- **macOS/Linux**: `~/.cache/persona/url_cache/`
- **Windows**: `%LOCALAPPDATA%\persona\url_cache\`

### Cache Behaviour

| Scenario | Behaviour |
|----------|-----------|
| First fetch | Downloads and caches content |
| Subsequent fetch | Uses cache if valid |
| ETag/Last-Modified changed | Re-downloads content |
| `--no-cache` flag | Bypasses cache |

### Bypassing the Cache

Force a fresh download:

```bash
persona generate \
  --from https://example.com/data/interviews.csv \
  --accept-terms \
  --no-cache
```

### Clearing the Cache

Remove all cached URLs:

```bash
persona cache clear
```

Or remove a specific URL:

```bash
persona cache remove https://example.com/data/interviews.csv
```

## Attribution Tracking

Persona tracks attribution metadata for external sources, creating an audit trail for research reproducibility.

### What's Tracked

For each URL source:
- Original URL provided
- Resolved URL (after any conversions)
- Fetch timestamp
- Content hash (SHA256)
- Content type and size
- ETag/Last-Modified headers

### Viewing Attribution

Attribution is included in experiment output:

```json
{
  "experiment": {
    "name": "interview-study",
    "sources": [
      {
        "source_type": "remote_url",
        "original_url": "https://github.com/user/repo/blob/main/data.csv",
        "resolved_url": "https://raw.githubusercontent.com/user/repo/main/data.csv",
        "fetched_at": "2025-01-15T10:30:00Z",
        "sha256": "abc123...",
        "terms_accepted": true
      }
    ]
  }
}
```

### Research Reproducibility

The SHA256 hash enables verification that:
- You're working with the same data as a previous run
- Data hasn't been modified since the original study

## Error Handling

### Common Errors

**URL Validation Error**
```
❌ Invalid URL: example.com/data.csv
   URLs must include the protocol (https://)
```

Fix: Include the protocol:
```bash
persona generate --from https://example.com/data.csv
```

**Terms Not Accepted**
```
❌ Terms not accepted for external source
   Use --accept-terms to confirm data usage
```

Fix: Add the `--accept-terms` flag.

**HTTP Errors**
```
❌ Failed to fetch URL: 404 Not Found
   https://example.com/missing.csv
```

Fix: Verify the URL is correct and accessible.

## SDK Usage

Load URL data programmatically:

```python
from persona.sdk import PersonaGenerator
from persona.sdk.models import PersonaConfig

config = PersonaConfig(
    source="https://example.com/data/interviews.csv",
    accept_terms=True,
    use_cache=True
)

generator = PersonaGenerator()
result = generator.generate(config)

# Access source attribution
for source in result.sources:
    print(f"Source: {source.original_url}")
    print(f"Fetched: {source.fetched_at}")
    print(f"Hash: {source.sha256}")
```

## Best Practices

### Do's

- ✅ Always verify data licences before use
- ✅ Use `--accept-terms` explicitly in scripts
- ✅ Keep cached data for reproducibility
- ✅ Document source URLs in your research notes
- ✅ Verify SHA256 hashes when reproducing studies

### Don'ts

- ❌ Use copyrighted data without permission
- ❌ Assume all public URLs are freely usable
- ❌ Clear cache before completing a study
- ❌ Ignore attribution metadata

## Next Steps

- Explore [Building a Library](05-building-library.md) for organising research
- Learn about [Validating Quality](06-validating-quality.md) for ensuring data accuracy
- See the [CLI Reference](../guides/cli/reference.md) for all URL-related flags

---

## Related Documentation

- [Data Formats Tutorial](03-data-formats.md) - Local file formats
- [F-126: URL Data Ingestion](../development/roadmap/features/completed/F-126-url-data-ingestion.md) - Feature specification
- [CLI Reference](../guides/cli/reference.md) - Command-line options

