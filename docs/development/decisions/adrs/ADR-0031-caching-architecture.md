# ADR-0031: Caching Architecture

## Status

Planned

## Context

Persona currently has URL caching for remote data ingestion (F-126) but lacks a comprehensive caching strategy. Effective caching could:
- Reduce API costs by avoiding redundant LLM calls
- Improve response times for similar requests
- Enable offline operation for cached content
- Support semantic similarity matching for "close enough" queries

Key questions:
- What should be cached? (prompts, responses, embeddings)
- How to identify cache hits? (exact match vs semantic similarity)
- Where to store cache? (memory, disk, external)
- How to manage cache invalidation?

## Decision

Implement a **multi-layer caching architecture** with pluggable backends and semantic matching support.

### Cache Layers

```
┌─────────────────────────────────────────────────────────────┐
│                     Cache Architecture                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Layer 1: Input Cache                                        │
│  └─ Cache parsed input data (documents, URLs)               │
│                                                              │
│  Layer 2: Prompt Cache                                       │
│  └─ Cache rendered prompts (template + data)                │
│                                                              │
│  Layer 3: Response Cache                                     │
│  └─ Cache LLM responses (semantic or exact match)           │
│                                                              │
│  Layer 4: Result Cache                                       │
│  └─ Cache final personas (post-processing)                  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Cache Key Strategy

```python
from hashlib import sha256
import json

class CacheKey:
    @staticmethod
    def for_input(path: str, content_hash: str) -> str:
        """Key for input data cache."""
        return f"input:{sha256(f'{path}:{content_hash}'.encode()).hexdigest()}"

    @staticmethod
    def for_prompt(template: str, data_hash: str, provider: str) -> str:
        """Key for prompt cache."""
        return f"prompt:{sha256(f'{template}:{data_hash}:{provider}'.encode()).hexdigest()}"

    @staticmethod
    def for_response(prompt_hash: str, model: str, params_hash: str) -> str:
        """Key for response cache."""
        return f"response:{sha256(f'{prompt_hash}:{model}:{params_hash}'.encode()).hexdigest()}"
```

### Semantic Cache Matching

```python
class SemanticCache:
    """Cache with semantic similarity matching."""

    def __init__(
        self,
        backend: CacheBackend,
        encoder: SentenceEncoder,
        similarity_threshold: float = 0.95
    ):
        self.backend = backend
        self.encoder = encoder
        self.threshold = similarity_threshold
        self.index = self._build_index()

    async def get(self, key: str, query_text: str) -> CacheResult | None:
        # Try exact match first
        exact = await self.backend.get(key)
        if exact:
            return CacheResult(value=exact, match_type="exact")

        # Try semantic match
        query_embedding = self.encoder.encode(query_text)
        similar = self.index.search(query_embedding, threshold=self.threshold)

        if similar:
            cached = await self.backend.get(similar.key)
            return CacheResult(
                value=cached,
                match_type="semantic",
                similarity=similar.score
            )

        return None

    async def set(
        self,
        key: str,
        value: Any,
        query_text: str,
        ttl: int | None = None
    ) -> None:
        embedding = self.encoder.encode(query_text)
        await self.backend.set(key, value, ttl)
        self.index.add(key, embedding)
```

### Cache Backends

```python
from abc import ABC, abstractmethod

class CacheBackend(ABC):
    @abstractmethod
    async def get(self, key: str) -> Any | None: ...

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int | None = None) -> None: ...

    @abstractmethod
    async def delete(self, key: str) -> bool: ...

    @abstractmethod
    async def clear(self) -> None: ...

class MemoryBackend(CacheBackend):
    """In-memory cache with LRU eviction."""

    def __init__(self, max_size: int = 1000):
        self.cache = OrderedDict()
        self.max_size = max_size

class FileSystemBackend(CacheBackend):
    """Disk-based cache with directory structure."""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir

class SQLiteBackend(CacheBackend):
    """SQLite-based cache with TTL support."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
```

### Cache Configuration

```yaml
cache:
  enabled: true

  layers:
    input:
      enabled: true
      backend: filesystem
      ttl: 86400  # 24 hours
    prompt:
      enabled: true
      backend: memory
      max_size: 1000
    response:
      enabled: true
      backend: sqlite
      ttl: 604800  # 7 days
      semantic:
        enabled: true
        threshold: 0.95
        model: all-MiniLM-L6-v2
    result:
      enabled: true
      backend: filesystem
      ttl: null  # No expiry

  backends:
    memory:
      max_size: 1000
    filesystem:
      directory: ~/.persona/cache
    sqlite:
      path: ~/.persona/cache.db

  invalidation:
    on_config_change: true
    on_version_upgrade: true
```

### Cache Manager

```python
class CacheManager:
    """Unified cache management."""

    def __init__(self, config: CacheConfig):
        self.layers = self._init_layers(config)

    async def get_or_generate(
        self,
        layer: str,
        key: str,
        generator: Callable[[], Awaitable[T]],
        **cache_kwargs
    ) -> T:
        """Get from cache or generate and cache."""
        cache = self.layers.get(layer)
        if cache:
            cached = await cache.get(key, **cache_kwargs)
            if cached:
                logger.debug(f"Cache hit: {layer}:{key}")
                return cached.value

        result = await generator()

        if cache:
            await cache.set(key, result, **cache_kwargs)
            logger.debug(f"Cache set: {layer}:{key}")

        return result

    async def invalidate(self, layer: str | None = None) -> None:
        """Invalidate cache layer(s)."""
        if layer:
            await self.layers[layer].clear()
        else:
            for cache in self.layers.values():
                await cache.clear()
```

## Consequences

**Positive:**
- Significant cost reduction for repeated queries
- Faster response times for cache hits
- Semantic matching catches similar queries
- Flexible backend selection
- Offline capability for cached content

**Negative:**
- Storage overhead for cache data
- Complexity in cache invalidation
- Semantic cache requires embedding model
- Potential for stale results

## Alternatives Considered

### No Caching

**Description:** Always generate fresh results.

**Pros:** Simple, always current.

**Cons:** Higher costs, slower, no offline.

**Why Not Chosen:** Cost savings too significant.

### Redis/Memcached

**Description:** External caching service.

**Pros:** Proven, distributed, fast.

**Cons:** External dependency, operational burden.

**Why Not Chosen:** Overkill for single-user CLI tool.

### LLM Provider Cache Only

**Description:** Rely on provider's caching.

**Pros:** No implementation needed.

**Cons:** Not all providers cache, no semantic matching.

**Why Not Chosen:** Need more control.

## Research Reference

See [R-023: Caching Strategies for LLM Responses](../../research/R-023-caching-strategies.md) for detailed analysis.

---

## Related Documentation

- [R-023: Caching Strategies for LLM Responses](../../research/R-023-caching-strategies.md)
- [F-126: URL Data Ingestion](../../roadmap/features/completed/F-126-url-data-ingestion.md)

---

**Status**: Planned
