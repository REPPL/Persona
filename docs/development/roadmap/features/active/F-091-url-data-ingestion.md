# F-091: URL Data Ingestion

## Overview

| Attribute | Value |
|-----------|-------|
| **Use Case** | UC-001, UC-006 |
| **Milestone** | v1.10.0 |
| **Priority** | P1 |
| **Category** | Data |

## Problem Statement

Users need to load data directly from URLs (GitHub repositories, public datasets, APIs) without manually downloading files. Current data loading only supports local filesystem paths, requiring manual download and management of remote data sources.

Additionally, when using external data, proper attribution and licence compliance is essential but often overlooked by data tools.

## Design Approach

- Extend `DataLoader` to detect and handle URLs
- Support HTTPS URLs with automatic GitHub URL conversion
- Explicit terms acknowledgement via `--accept-terms` flag
- ETag-based caching with configurable TTL
- Attribution metadata embedded in output
- Rate limiting and polite fetching

### URL Support

| URL Type | Example | Handling |
|----------|---------|----------|
| Raw file | `https://example.com/data.csv` | Direct fetch |
| GitHub blob | `github.com/user/repo/blob/main/file.csv` | Convert to raw |
| GitHub raw | `raw.githubusercontent.com/...` | Direct fetch |
| Gist | `gist.github.com/user/id/raw/file` | Convert to raw |

### Data Source Configuration

**In project.yaml:**
```yaml
data_sources:
  # Local file (existing - unchanged)
  - name: interviews
    path: data/interviews.csv
    type: qualitative

  # Remote URL (NEW)
  - name: survey_responses
    url: https://github.com/AdaLovelaceInstitute/wave-2.../data.csv
    type: quantitative
    terms_accepted: true
    attribution:
      title: "Wave 2 UK AI Attitudes Survey"
      creators: ["Ada Lovelace Institute", "Alan Turing Institute"]
      licence: "Custom - Attribution + Notification Required"
```

**In experiment config.yaml:**
```yaml
name: ada-lovelace-demo
provider: anthropic
data_sources:
  - name: survey
    url: https://raw.githubusercontent.com/AdaLovelaceInstitute/.../data.csv
    type: quantitative
    terms_accepted: true
```

### CLI Interface

```bash
# Basic URL ingestion (requires terms acceptance)
persona generate --from https://example.com/data.csv --accept-terms

# Force cache refresh
persona generate --from URL --accept-terms --no-cache

# Mixed local and remote sources
persona generate --from ./local.csv --from https://remote.csv --accept-terms
```

### Output Attribution

When URL sources are used, auto-generate `attribution.md`:

```markdown
# Data Attribution

This persona generation used data from external sources.

## Wave 2 UK AI Attitudes Survey

- **Source:** Ada Lovelace Institute & Alan Turing Institute
- **URL:** https://github.com/AdaLovelaceInstitute/wave-2...
- **Fetched:** 2025-03-15T14:29:45Z
- **Licence:** Custom - Attribution + Notification Required

*Users must credit the original data sources.*
```

## Implementation Tasks

### Phase 1: Core URL Fetching
- [ ] Create `src/persona/core/data/url.py`
  - [ ] `URLSource` dataclass (url, etag, fetched_at, attribution)
  - [ ] `URLFetchResult` dataclass (content, source, from_cache)
  - [ ] `URLFetcher` class with fetch/fetch_async methods
  - [ ] GitHub URL conversion logic
  - [ ] URL validation (HTTPS-only, blocklist)
- [ ] Create `src/persona/core/data/attribution.py`
  - [ ] `Attribution` dataclass

### Phase 2: Caching
- [ ] Create `src/persona/core/data/url_cache.py`
  - [ ] `CacheEntry` dataclass
  - [ ] `URLCache` class with get/put/clear methods
  - [ ] ETag-based conditional requests
  - [ ] TTL expiry handling

### Phase 3: DataLoader Integration
- [ ] Modify `src/persona/core/data/loader.py`
  - [ ] Add `_is_url()` detection method
  - [ ] Add `_load_from_url()` method
  - [ ] Add `accept_terms` parameter to `load_path()`
  - [ ] Integrate `URLFetcher`
- [ ] Modify `src/persona/core/data/formats.py`
  - [ ] Add `load_content(str)` method to `FormatLoader`
- [ ] Update `src/persona/core/data/__init__.py`
  - [ ] Export URL classes

### Phase 4: Model Changes
- [ ] Modify `src/persona/core/project/context.py`
  - [ ] Add `SourceType` enum (LOCAL_FILE, REMOTE_URL)
  - [ ] Add `url`, `source_type`, `attribution`, `terms_accepted` to `DataSource`
- [ ] Modify `src/persona/core/experiments/manager.py`
  - [ ] Support URL data sources in experiments

### Phase 5: CLI Integration
- [ ] Modify `src/persona/ui/commands/generate.py`
  - [ ] Add `--accept-terms` flag
  - [ ] Add `--no-cache` flag
  - [ ] Display attribution in output

### Phase 6: Output Integration
- [ ] Modify `src/persona/core/output/manager.py`
  - [ ] Include URL sources in `metadata.json`
  - [ ] Auto-generate `attribution.md` for URL sources

### Phase 7: Testing
- [ ] Create `tests/unit/core/data/test_url.py`
- [ ] Create `tests/unit/core/data/test_url_cache.py`
- [ ] Add integration tests for URL loading

## Success Criteria

- [ ] `persona generate --from https://... --accept-terms` works
- [ ] GitHub blob URLs auto-convert to raw URLs
- [ ] Cache stores data with ETag for conditional requests
- [ ] Without `--accept-terms`, URL fetch fails with guidance
- [ ] Attribution appears in output `metadata.json`
- [ ] `attribution.md` auto-generated for URL sources
- [ ] All tests pass, coverage maintained ≥80%

## Dependencies

- `httpx` (already in dependencies, 0.25.0+)
- `tiktoken` (for token counting of fetched content)

## Related Documentation

- [R-017: Remote Data Ingestion](../../research/R-017-remote-data-ingestion.md) - Research findings
- [Tutorial: External Datasets](../../../tutorials/07-external-datasets.md) - User guide
- [Data Formats Tutorial](../../../tutorials/03-data-formats.md) - Existing data loading

---

**Status**: In Progress
