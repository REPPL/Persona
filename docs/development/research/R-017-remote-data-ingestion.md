# R-017: Remote Data Ingestion

Research into best practices for URL-based data ingestion, attribution compliance, and ethical data sourcing for Persona.

## Executive Summary

This research analyses best practices for fetching data from remote URLs, with specific focus on the Ada Lovelace Institute's "Wave 2 UK AI Attitudes Survey" as a candidate example dataset. The findings inform the design of Persona's URL ingestion feature (F-091).

**Key Findings:**
- Explicit terms acknowledgement (`--accept-terms`) is essential for responsible data use
- Attribution must be embedded in output metadata and auto-generated `attribution.md`
- ETag-based caching with configurable TTL provides efficient re-fetching
- GitHub URLs should auto-convert to `raw.githubusercontent.com` format
- Rate limiting (1 req/sec default) with `Retry-After` header respect is industry standard

**Recommendation:** Implement URL ingestion with built-in compliance tracking, differentiating Persona from tools like pandas that offer no attribution support.

---

## Case Study: Ada Lovelace Institute Dataset

### Dataset Details

| Field | Value |
|-------|-------|
| **Repository** | [AdaLovelaceInstitute/wave-2---how-do-people-feel-about-AI-](https://github.com/AdaLovelaceInstitute/wave-2---how-do-people-feel-about-AI-) |
| **Published** | March 2025 |
| **Fieldwork** | October-November 2023 |
| **Sample** | 3,000+ UK adults (nationally representative) |
| **Partners** | Ada Lovelace Institute + Alan Turing Institute |
| **Funding** | UKRI Public Voices in AI programme |

### Available Files

- Raw datasets: `.dta` (Stata) and `.csv` formats
- Codebook: Excel format
- Technical report with questionnaire (PDF)
- R analysis scripts (`.Rmd`)
- Data tables (Excel)

### Terms of Use

**Licence Type:** Custom permissive (no standard licence file)

**Requirements:**
1. Credit both Ada Lovelace Institute and Alan Turing Institute
2. Notify `hello@adalovelaceinstitute.org` before use
3. Share a copy of research at publication

**Assessment:** Suitable for example use with proper attribution.

---

## Licence Classification Framework

When ingesting remote data, Persona should recognise these licence types:

| Licence | Attribution | Commercial | Derivatives | Notification |
|---------|-------------|------------|-------------|--------------|
| CC0 / Public Domain | Not required | Allowed | Allowed | Not required |
| CC BY | Required | Allowed | Allowed | Not required |
| CC BY-SA | Required | Allowed | Same licence | Not required |
| CC BY-NC | Required | Not allowed | Allowed | Not required |
| Custom (e.g., Ada Lovelace) | Required | Allowed | Allowed | Required |
| All Rights Reserved | Cannot use without permission | | | |

### SPDX Identifier Support

For automated licence detection, support common SPDX identifiers:
- `CC0-1.0` - Public domain dedication
- `CC-BY-4.0` - Attribution 4.0 International
- `CC-BY-SA-4.0` - Attribution-ShareAlike 4.0
- `CC-BY-NC-4.0` - Attribution-NonCommercial 4.0
- `MIT`, `Apache-2.0`, `GPL-3.0` - Code licences (data may differ)

---

## Attribution Metadata Schema

### Required Fields

```yaml
attribution:
  title: "Wave 2 UK AI Attitudes Survey"
  creators:
    - "Ada Lovelace Institute"
    - "Alan Turing Institute"
  source_url: "https://github.com/AdaLovelaceInstitute/wave-2..."
  licence: "Custom - Attribution + Notification Required"
  access_date: "2025-03-15"
```

### Optional Fields

```yaml
attribution:
  # ... required fields ...
  authors:
    - "Roshni Modhvadia"
    - "Tvesha Sippy"
    - "Octavia Field Reid"
    - "Helen Margetts"
  doi: "10.xxxx/xxxxx"
  version: "1.0"
  notify_email: "hello@adalovelaceinstitute.org"
  requirements:
    - "Credit Ada Lovelace Institute and Alan Turing Institute"
    - "Notify before use"
    - "Share research at publication"
```

---

## Industry Comparison

### How Other Tools Handle Remote Data

| Tool | URL Support | Attribution | Terms Check | Caching |
|------|-------------|-------------|-------------|---------|
| pandas | `pd.read_csv(url)` | None | None | None |
| Hugging Face datasets | Full support | Dataset cards | Gated datasets | Local cache |
| DVC | Remote storage | Manual | None | Version-controlled |
| Great Expectations | Limited | None | None | None |
| **Persona (proposed)** | Full support | Embedded | Explicit flag | ETag-based |

**Differentiation Opportunity:** Persona can position itself as the "responsible" choice for data-driven persona generation by building compliance into the workflow.

### FAIR Principles Alignment

| Principle | Implementation |
|-----------|----------------|
| **F**indable | Store source metadata with generated personas |
| **A**ccessible | Cache with clear provenance trail |
| **I**nteroperable | Standard attribution format (YAML/JSON) |
| **R**eusable | Licence/terms clearly documented in output |

---

## Technical Recommendations

### 1. URL Validation

```python
ALLOWED_SCHEMES = {'https'}  # HTTP blocked by default
BLOCKED_HOSTS = {'localhost', '127.0.0.1', '0.0.0.0', '::1'}
ALLOWED_DOMAINS = {
    'github.com',
    'raw.githubusercontent.com',
    'gist.githubusercontent.com',
    'gitlab.com',
    'bitbucket.org',
    # Expand as needed
}
```

**Rationale:** HTTPS-only prevents man-in-the-middle attacks; blocklist prevents SSRF.

### 2. GitHub URL Normalisation

Convert web UI URLs to raw content URLs:

| Input Format | Output Format |
|--------------|---------------|
| `github.com/user/repo/blob/main/file.csv` | `raw.githubusercontent.com/user/repo/main/file.csv` |
| `github.com/user/repo/raw/main/file.csv` | `raw.githubusercontent.com/user/repo/main/file.csv` |
| `gist.github.com/user/id/raw/file.csv` | `gist.githubusercontent.com/user/id/raw/file.csv` |

### 3. Caching Strategy

```
~/.cache/persona/url_data/
└── <sha256_of_url>/
    ├── content.<ext>     # Downloaded data
    ├── metadata.json     # Attribution, fetch time, ETag
    └── .etag             # For conditional requests
```

**Cache Behaviour:**
- ETag/Last-Modified for conditional `GET` requests
- Configurable TTL (default: 24 hours)
- Force refresh with `--no-cache` flag
- Store attribution metadata alongside data

### 4. Rate Limiting

| Domain | Requests/Minute | Concurrent |
|--------|-----------------|------------|
| `github.com` | 30 | 3 |
| `raw.githubusercontent.com` | 60 | 5 |
| Default | 20 | 2 |

Respect `429 Too Many Requests` with exponential backoff and `Retry-After` headers.

### 5. User-Agent Identification

```
User-Agent: Persona/1.x (+https://github.com/REPPL/Persona)
```

Identifies the tool for server logs and allows blocking if necessary.

---

## Ethical Considerations

### Consent & Terms Acknowledgement

**Principle:** Users must actively acknowledge data source terms before fetching.

**Implementation:**
```bash
# Without acknowledgement - fails with guidance
persona generate --from https://github.com/.../data.csv
# Error: Remote data requires terms acceptance. Use --accept-terms.

# With acknowledgement - proceeds
persona generate --from https://github.com/.../data.csv --accept-terms
```

**Rationale:** Explicit consent prevents accidental misuse and documents user acknowledgement.

### Privacy Considerations

Remote data may contain PII despite being "public":
1. **Recommend `--anonymise`** for remote sources by default
2. **Warn** if data appears to contain names, emails, or other PII
3. **Document** that public availability does not equal consent for derivative use

### Data Provenance

Every generated persona from URL sources must include:
- Source URL
- Fetch timestamp
- Attribution requirements
- Licence information

This enables downstream users to verify compliance.

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Terms change after download | Medium | Medium | Store terms snapshot with cached data |
| Data removed from source | Medium | Low | Local cache preserves access |
| PII in "public" data | Medium | High | Recommend/default anonymisation |
| Rate limiting blocks access | Low | Low | Exponential backoff + caching |
| Copyright infringement claims | Low | High | Clear attribution + explicit terms acknowledgement |
| SSRF attacks via URL | Low | High | Strict URL validation, blocklist |

---

## CLI Interface Design

### New Flags

| Flag | Type | Default | Description |
|------|------|---------|-------------|
| `--accept-terms` | bool | False | Acknowledge URL source terms |
| `--no-cache` | bool | False | Bypass cache, fetch fresh |
| `--attribution` | string | Auto | Override auto-detected attribution |

### Example Usage

```bash
# Basic URL ingestion
persona generate --from https://raw.githubusercontent.com/.../data.csv --accept-terms

# Force cache refresh
persona generate --from URL --accept-terms --no-cache

# Multiple sources (mixed local and remote)
persona generate --from ./local.csv --from https://example.com/remote.csv --accept-terms
```

---

## Related Documentation

- [F-091: URL Data Ingestion](../roadmap/features/active/F-091-url-data-ingestion.md) - Feature specification
- [Tutorial: External Datasets](../../tutorials/07-external-datasets.md) - User guide
- [Data Formats Tutorial](../../tutorials/03-data-formats.md) - Existing data loading guide

---

**Status**: Research complete
