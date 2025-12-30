# F-142: Response Caching Layer

## Overview

| Attribute | Value |
|-----------|-------|
| **Feature ID** | F-142 |
| **Title** | Response Caching Layer |
| **Priority** | P1 (High) |
| **Category** | Performance |
| **Milestone** | [v1.13.0](../../milestones/v1.13.0.md) |
| **Status** | 📋 Planned |
| **Dependencies** | F-126 (URL Data Ingestion - has URL cache) |

---

## Problem Statement

Every LLM API call costs money and adds latency, even when:
- The same prompt is sent multiple times
- Similar prompts would produce acceptable results
- Cached results would be sufficient for testing/development

Without response caching, users pay for redundant API calls.

---

## Design Approach

Implement multi-layer caching with semantic similarity matching for near-duplicate queries.

### Cache Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Cache Layers                             │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Request                                                     │
│     │                                                        │
│     ▼                                                        │
│  ┌──────────────┐                                           │
│  │ Input Cache  │ ← Parsed documents, URL content           │
│  └──────────────┘                                           │
│     │                                                        │
│     ▼                                                        │
│  ┌──────────────┐                                           │
│  │ Prompt Cache │ ← Rendered prompts (template + data)      │
│  └──────────────┘                                           │
│     │                                                        │
│     ▼                                                        │
│  ┌──────────────┐                                           │
│  │Response Cache│ ← LLM responses (exact + semantic)        │
│  └──────────────┘                                           │
│     │                                                        │
│     ▼                                                        │
│  Result                                                      │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Capabilities

### 1. Multi-Layer Caching

Cache at multiple levels for maximum efficiency.

```python
class CacheManager:
    async def get_or_generate(
        self,
        input_data: str,
        prompt_template: str,
        provider: Provider
    ) -> Persona:
        # Check input cache
        input_key = self.hash_input(input_data)
        parsed = await self.input_cache.get(input_key)
        if not parsed:
            parsed = await parse_input(input_data)
            await self.input_cache.set(input_key, parsed)

        # Check prompt cache
        prompt_key = self.hash_prompt(prompt_template, parsed)
        rendered = await self.prompt_cache.get(prompt_key)
        if not rendered:
            rendered = await render_prompt(prompt_template, parsed)
            await self.prompt_cache.set(prompt_key, rendered)

        # Check response cache
        response_key = self.hash_response(rendered, provider)
        response = await self.response_cache.get(response_key, rendered)
        if not response:
            response = await provider.generate(rendered)
            await self.response_cache.set(response_key, response, rendered)

        return response
```

### 2. Semantic Cache Matching

Match semantically similar prompts to cached responses.

```bash
# Enable semantic caching
persona config set cache.response.semantic.enabled true

# Configure similarity threshold
persona config set cache.response.semantic.threshold 0.95
```

**How It Works:**
```python
class SemanticResponseCache:
    def __init__(self, threshold: float = 0.95):
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = VectorIndex()
        self.threshold = threshold

    async def get(self, key: str, query_text: str) -> CachedResponse | None:
        # Try exact match first
        exact = await self.backend.get(key)
        if exact:
            return CachedResponse(value=exact, match="exact")

        # Try semantic match
        embedding = self.encoder.encode(query_text)
        matches = self.index.search(embedding, threshold=self.threshold)

        if matches:
            cached = await self.backend.get(matches[0].key)
            return CachedResponse(
                value=cached,
                match="semantic",
                similarity=matches[0].score
            )

        return None
```

### 3. Cache Statistics

View cache performance metrics.

```bash
# Show cache statistics
persona cache stats

# Show detailed breakdown
persona cache stats --verbose
```

**Output:**
```
Cache Statistics
════════════════════════════════════════════════════════════

Layer          │ Hits    │ Misses  │ Hit Rate │ Size
───────────────┼─────────┼─────────┼──────────┼──────────
Input          │ 1,245   │ 312     │ 79.9%    │ 45.2 MB
Prompt         │ 2,891   │ 567     │ 83.6%    │ 12.8 MB
Response       │ 4,123   │ 1,234   │ 77.0%    │ 156.3 MB
  └─ Exact     │ 3,456   │    -    │ 64.5%    │     -
  └─ Semantic  │   667   │    -    │ 12.4%    │     -

Total Savings
─────────────
Estimated API calls saved: 4,123
Estimated cost saved: $82.46
Estimated time saved: 2h 17m
```

### 4. Cache Management

Control cache behaviour and cleanup.

```bash
# Clear all caches
persona cache clear

# Clear specific layer
persona cache clear --layer response

# Clear old entries
persona cache clear --older-than 7d

# Warm cache with prompts
persona cache warm ./prompts/
```

### 5. Cache Configuration

Fine-tune caching behaviour.

```yaml
cache:
  enabled: true

  input:
    enabled: true
    backend: filesystem
    ttl: 86400  # 24 hours
    max_size: 100MB

  prompt:
    enabled: true
    backend: memory
    max_entries: 10000

  response:
    enabled: true
    backend: sqlite
    ttl: 604800  # 7 days
    max_size: 500MB
    semantic:
      enabled: true
      threshold: 0.95
      model: all-MiniLM-L6-v2

  storage:
    directory: ~/.persona/cache
```

---

## CLI Commands

```bash
# Cache statistics
persona cache stats [--verbose] [--format json]

# Cache management
persona cache clear [--layer LAYER] [--older-than DURATION]
persona cache warm PATH [--layer response]

# Cache configuration
persona cache config show
persona cache config set KEY VALUE
```

---

## Implementation Tasks

### Phase 1: Core Infrastructure
- [ ] Create cache backend interface
- [ ] Implement filesystem backend
- [ ] Implement SQLite backend
- [ ] Implement memory backend
- [ ] Create cache key generation

### Phase 2: Cache Layers
- [ ] Implement input cache layer
- [ ] Implement prompt cache layer
- [ ] Implement response cache layer
- [ ] Create cache manager

### Phase 3: Semantic Matching
- [ ] Integrate sentence-transformers
- [ ] Implement vector index
- [ ] Add similarity search
- [ ] Create semantic cache wrapper

### Phase 4: CLI Commands
- [ ] Implement `cache stats`
- [ ] Implement `cache clear`
- [ ] Implement `cache warm`
- [ ] Add configuration commands

### Phase 5: Integration
- [ ] Integrate with generation pipeline
- [ ] Add cache headers to responses
- [ ] Create cache bypass option
- [ ] Add metrics collection

---

## Success Criteria

- [ ] Cache reduces API calls by 50%+ for repeated queries
- [ ] Semantic matching catches 90%+ of similar prompts
- [ ] Cache statistics accurately reflect usage
- [ ] Cache clear removes specified entries
- [ ] Configuration allows fine-tuning
- [ ] Test coverage >= 85%
- [ ] Cache overhead < 5% of generation time

---

## Related Documentation

- [v1.13.0 Milestone](../../milestones/v1.13.0.md)
- [F-126: URL Data Ingestion](../completed/F-126-url-data-ingestion.md)
- [R-023: Caching Strategies for LLM Responses](../../../research/R-023-caching-strategies.md)
- [ADR-0031: Caching Architecture](../../../decisions/adrs/ADR-0031-caching-architecture.md)

---

**Status**: Planned
