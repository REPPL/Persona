# R-023: Caching Strategies for LLM Responses

Research into caching mechanisms for reducing API costs, improving latency, and enabling offline workflows in Persona.

## Executive Summary

This document evaluates caching strategies for LLM responses and related data to reduce costs and improve performance.

**Key Finding:** Persona has URL content caching (F-126) but no general response caching. Given the non-deterministic nature of LLM outputs, semantic caching based on input similarity is more valuable than exact-match caching.

**Recommendation:** Implement a **multi-layer caching architecture** with exact-match caching for deterministic operations and semantic similarity caching for LLM responses, using Redis or SQLite depending on deployment context.

---

## Context

### Current Caching in Persona

| Feature | Caching Status | Location |
|---------|----------------|----------|
| URL content | ✅ Implemented (F-126) | `~/.cache/persona/url/` |
| LLM responses | ❌ Not implemented | - |
| Token counts | ❌ Not implemented | - |
| Cost estimates | ❌ Not implemented | - |
| Templates | ✅ In-memory | Runtime |
| Model registry | ✅ In-memory | Runtime |

### Why Cache LLM Responses?

| Benefit | Impact |
|---------|--------|
| **Cost reduction** | Avoid repeat API calls for similar inputs |
| **Latency improvement** | Instant response for cached queries |
| **Offline support** | Use cached personas when offline |
| **Reproducibility** | Deterministic outputs for testing |
| **Rate limit management** | Reduce provider throttling |

### Challenges with LLM Caching

| Challenge | Explanation |
|-----------|-------------|
| **Non-determinism** | Same prompt may produce different outputs |
| **Large payloads** | Responses can be 10KB+ each |
| **Semantic similarity** | "Generate 3 personas" ≈ "Create three personas" |
| **Context sensitivity** | Same prompt + different data = different output |
| **Staleness** | Cached personas may not reflect model improvements |

---

## Caching Layers

### Layer 1: Input Data Cache

**Purpose:** Cache processed input data to avoid re-parsing

**Scope:**
- Parsed CSV/JSON/YAML data
- Tokenised text
- Extracted entities

**Strategy:** Content-hash based (SHA-256 of raw input)

**TTL:** 24 hours (configurable)

**Implementation:**
```python
class InputCache:
    def get(self, content_hash: str) -> ProcessedData | None: ...
    def set(self, content_hash: str, data: ProcessedData) -> None: ...
```

### Layer 2: Prompt Cache

**Purpose:** Cache rendered prompts for exact-match scenarios

**Scope:**
- Rendered Jinja2 templates
- System prompts
- Few-shot examples

**Strategy:** Hash of (template_name + variables + model)

**TTL:** 1 hour (prompts rarely change)

**Implementation:**
```python
class PromptCache:
    def get(self, template: str, variables: dict, model: str) -> str | None: ...
    def set(self, template: str, variables: dict, model: str, prompt: str) -> None: ...
```

### Layer 3: Response Cache (Semantic)

**Purpose:** Cache LLM responses with semantic similarity matching

**Scope:**
- Full LLM responses
- Parsed personas
- Quality scores

**Strategy:** Embedding-based similarity with configurable threshold

**TTL:** 7 days (configurable)

**Implementation:**
```python
class ResponseCache:
    def __init__(self, similarity_threshold: float = 0.95):
        self.embedding_model = load_embedding_model()
        self.similarity_threshold = similarity_threshold

    def get(self, prompt: str, model: str) -> CachedResponse | None:
        prompt_embedding = self.embed(prompt)
        candidates = self.find_similar(prompt_embedding, model)
        for candidate in candidates:
            if cosine_similarity(prompt_embedding, candidate.embedding) >= self.similarity_threshold:
                return candidate.response
        return None

    def set(self, prompt: str, model: str, response: LLMResponse) -> None:
        embedding = self.embed(prompt)
        self.store(prompt, embedding, model, response)
```

### Layer 4: Result Cache

**Purpose:** Cache final generated personas

**Scope:**
- Complete persona objects
- Export formats
- Quality assessments

**Strategy:** Hash of (input_data + config + model + timestamp_bucket)

**TTL:** 30 days (or until manually invalidated)

---

## Storage Backends

### Option 1: Filesystem (Default)

**Approach:** JSON files in cache directory

**Pros:**
- No dependencies
- Works offline
- Simple implementation
- Easy to inspect/debug

**Cons:**
- No built-in expiration
- Manual cleanup needed
- Not suitable for team sharing

**Use Case:** Single-user CLI, local development

**Implementation:**
```
~/.cache/persona/
├── inputs/
│   └── {content_hash}.json
├── prompts/
│   └── {prompt_hash}.json
├── responses/
│   ├── index.sqlite      # Embedding index
│   └── {response_id}.json
└── results/
    └── {result_hash}.json
```

### Option 2: SQLite

**Approach:** Local SQLite database with optional embedding index

**Pros:**
- Transactional
- Built-in expiration via cleanup queries
- Efficient querying
- Single file, portable

**Cons:**
- Single-process write lock
- Not suitable for distributed caching

**Use Case:** Single-user with efficient storage, portable cache

**Schema:**
```sql
CREATE TABLE cache_entries (
    id TEXT PRIMARY KEY,
    cache_type TEXT NOT NULL,  -- 'input', 'prompt', 'response', 'result'
    key_hash TEXT NOT NULL,
    data BLOB NOT NULL,
    embedding BLOB,            -- For semantic cache
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP,
    hit_count INTEGER DEFAULT 0,
    UNIQUE(cache_type, key_hash)
);

CREATE INDEX idx_cache_type_key ON cache_entries(cache_type, key_hash);
CREATE INDEX idx_expires ON cache_entries(expires_at);
```

### Option 3: Redis

**Approach:** In-memory cache with persistence

**Pros:**
- Fast (in-memory)
- Built-in TTL
- Distributed caching
- Pub/sub for invalidation

**Cons:**
- External dependency
- Memory cost
- Requires Redis server

**Use Case:** Team deployments, high-throughput scenarios

**Implementation:**
```python
class RedisCache:
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.client = redis.from_url(redis_url)

    def get(self, key: str) -> bytes | None:
        return self.client.get(f"persona:{key}")

    def set(self, key: str, value: bytes, ttl: int = 3600) -> None:
        self.client.setex(f"persona:{key}", ttl, value)
```

### Option 4: Cloud Object Storage

**Approach:** S3/GCS for large cached objects

**Pros:**
- Unlimited storage
- Cross-region
- Cost-effective for large objects

**Cons:**
- Network latency
- Not suitable for small objects
- Requires cloud setup

**Use Case:** Large response caching, team sharing

---

## Semantic Similarity Caching

### Embedding Model Selection

| Model | Dimensions | Quality | Speed | Size |
|-------|------------|---------|-------|------|
| **all-MiniLM-L6-v2** | 384 | Good | Fast | 80MB |
| **bge-small-en-v1.5** | 384 | Good | Fast | 133MB |
| **nomic-embed-text** | 768 | Better | Medium | 274MB |
| **text-embedding-3-small** | 1536 | Best | API call | - |

**Recommendation:** Use `all-MiniLM-L6-v2` for local caching (balance of quality and size).

### Similarity Threshold Tuning

| Threshold | Behaviour | Use Case |
|-----------|-----------|----------|
| 0.99+ | Exact-match only | Testing, reproducibility |
| 0.95-0.98 | Minor variations | Typo tolerance |
| 0.90-0.94 | Similar intent | General caching |
| 0.85-0.89 | Broad matching | Aggressive caching |
| <0.85 | Too permissive | Not recommended |

**Default:** 0.95 (conservative, low false positive rate)

### Cache Hit Strategy

```
Request arrives
      ↓
┌─────────────────────────┐
│ Compute prompt hash     │
└─────────────────────────┘
      ↓
┌─────────────────────────┐
│ Check exact-match cache │
└─────────────────────────┘
      ↓ (miss)
┌─────────────────────────┐
│ Compute prompt embedding│
└─────────────────────────┘
      ↓
┌─────────────────────────┐
│ Search semantic cache   │
│ (ANN with threshold)    │
└─────────────────────────┘
      ↓ (miss)
┌─────────────────────────┐
│ Call LLM provider       │
└─────────────────────────┘
      ↓
┌─────────────────────────┐
│ Store in both caches    │
└─────────────────────────┘
```

---

## Cache Invalidation

### Automatic Invalidation

| Trigger | Action |
|---------|--------|
| TTL expiration | Remove entry |
| Model version change | Invalidate model-specific entries |
| Template change | Invalidate prompt cache |
| Config change | Invalidate affected entries |

### Manual Invalidation

```bash
# Clear all caches
persona cache clear

# Clear specific layer
persona cache clear --layer responses

# Clear by age
persona cache clear --older-than 7d

# Clear by model
persona cache clear --model claude-sonnet-4-20250514

# Show cache stats
persona cache stats
```

### Invalidation Patterns

| Pattern | When to Use |
|---------|-------------|
| **Time-based (TTL)** | Default, suitable for most cases |
| **Version-based** | When model updates invalidate cached responses |
| **Event-based** | When configuration changes |
| **Size-based (LRU)** | When cache size limits reached |

---

## Configuration

### Default Configuration

```yaml
# persona.yaml
cache:
  enabled: true
  backend: sqlite  # filesystem, sqlite, redis
  directory: ~/.cache/persona

  layers:
    input:
      enabled: true
      ttl: 86400  # 24 hours
    prompt:
      enabled: true
      ttl: 3600   # 1 hour
    response:
      enabled: true
      ttl: 604800  # 7 days
      semantic:
        enabled: true
        threshold: 0.95
        model: all-MiniLM-L6-v2
    result:
      enabled: true
      ttl: 2592000  # 30 days

  limits:
    max_size_mb: 1024
    max_entries: 10000
    cleanup_interval: 3600

  redis:
    url: redis://localhost:6379
    prefix: persona
```

### Environment Overrides

```bash
export PERSONA_CACHE_ENABLED=true
export PERSONA_CACHE_BACKEND=redis
export PERSONA_CACHE_REDIS_URL=redis://cache.example.com:6379
```

---

## Cost-Benefit Analysis

### Scenario: Research Project (100 personas over 30 days)

**Without Caching:**
- 100 unique generations × $0.20 = $20.00
- Average latency: 10 seconds
- Total time: ~17 minutes

**With Caching (30% cache hit rate):**
- 70 unique + 30 cached = $14.00
- Cached latency: <100ms
- Total time: ~12 minutes

**Savings:** $6.00 (30%) + 5 minutes

### Scenario: Development/Testing (500 runs over 30 days)

**Without Caching:**
- 500 generations × $0.10 (Haiku) = $50.00

**With Caching (60% cache hit rate due to repeated tests):**
- 200 unique + 300 cached = $20.00

**Savings:** $30.00 (60%)

### Break-Even Analysis

Cache overhead:
- Storage: ~10KB per cached response
- Embedding computation: ~10ms per entry
- Index maintenance: ~1% CPU

Break-even: 2+ cache hits per entry covers overhead

---

## Implementation Plan

### Phase 1: Filesystem Cache (v1.12.0)

- Input data caching
- Prompt caching
- Basic response caching (exact match)
- CLI commands: `cache stats`, `cache clear`

### Phase 2: SQLite + Semantic (v1.13.0)

- Migrate to SQLite backend
- Add semantic similarity layer
- Embedding index with ANN search
- Cache analytics

### Phase 3: Distributed (v2.0.0)

- Redis backend option
- Cross-user cache sharing (within org)
- Cache invalidation pub/sub
- S3 backend for large objects

---

## Proposed Features

This research informs the following features:

1. **F-138: Response Caching Layer** (P0, v1.13.0)
2. **F-139: Persona Diff Tool** (uses cache for comparisons) (P1, v1.14.0)

---

## Research Sources

### LLM Caching

- [GPTCache: Semantic Caching for LLMs](https://github.com/zilliztech/GPTCache)
- [LangChain Caching](https://python.langchain.com/docs/modules/model_io/models/llms/how_to/llm_caching)
- [Semantic Caching for LLM Applications](https://www.pinecone.io/learn/semantic-cache/)
- [Caching Strategies for Generative AI](https://aws.amazon.com/blogs/database/build-generative-ai-applications-with-amazon-elasticache/)

### Embedding Models

- [Sentence Transformers](https://www.sbert.net/)
- [MTEB Leaderboard](https://huggingface.co/spaces/mteb/leaderboard)
- [Choosing Embedding Models](https://www.pinecone.io/learn/retrieval-embedding/)

### Caching Infrastructure

- [Redis Caching Patterns](https://redis.io/docs/manual/patterns/)
- [SQLite as a Cache](https://www.sqlite.org/fasterthanfs.html)
- [Caching Best Practices](https://aws.amazon.com/caching/best-practices/)

### Vector Search

- [Approximate Nearest Neighbours](https://www.pinecone.io/learn/what-is-similarity-search/)
- [FAISS for Similarity Search](https://github.com/facebookresearch/faiss)
- [Annoy Library](https://github.com/spotify/annoy)

---

## Related Documentation

- [F-126: URL Data Ingestion](../roadmap/features/completed/F-126-url-data-ingestion.md)
- [F-078: Cost Tracking](../roadmap/features/completed/F-078-cost-tracking.md)
- [R-022: Performance Benchmarking](./R-022-performance-benchmarking.md)
- [ADR-0031: Caching Architecture](../decisions/adrs/ADR-0031-caching-architecture.md) (Planned)
