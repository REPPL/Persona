# R-025: Batch Processing Optimisation

## Executive Summary

This research analyses strategies for optimising batch persona generation, focusing on parallelisation, memory management, and failure handling. The current batch module is functional but under-optimised for large-scale operations (50+ personas). Recommended approach: implement adaptive concurrency with backpressure, chunked processing for memory efficiency, and checkpoint-based recovery.

---

## Research Context

| Attribute | Value |
|-----------|-------|
| **ID** | R-025 |
| **Category** | Scalability |
| **Status** | Complete |
| **Priority** | P2 |
| **Informs** | F-138 (Batch Progress Tracking), v1.13.0+ features |

---

## Problem Statement

Persona's batch generation currently:
- Uses fixed concurrency limits regardless of provider capabilities
- Loads all input data into memory before processing
- Has limited checkpoint/recovery for long-running batches
- Lacks adaptive rate limiting per provider
- Provides minimal progress visibility

For enterprise use cases generating 100+ personas, these limitations impact reliability and performance.

---

## State of the Art Analysis

### Concurrency Models

#### 1. Fixed Concurrency Pool

**Description:** Static number of concurrent workers.

```python
async def process_batch(items: list, concurrency: int = 5):
    semaphore = asyncio.Semaphore(concurrency)

    async def worker(item):
        async with semaphore:
            return await process(item)

    return await asyncio.gather(*[worker(i) for i in items])
```

| Aspect | Assessment |
|--------|------------|
| Simplicity | ✅ Easy to implement |
| Efficiency | ⚠️ May underutilise or overload |
| Adaptability | ❌ Cannot respond to conditions |

#### 2. Adaptive Concurrency

**Description:** Dynamically adjust concurrency based on success rates and latency.

```python
class AdaptiveConcurrency:
    def __init__(self, min_workers: int = 1, max_workers: int = 20):
        self.current = min_workers
        self.min = min_workers
        self.max = max_workers
        self.success_window: deque[bool] = deque(maxlen=20)
        self.latency_window: deque[float] = deque(maxlen=20)

    def record_result(self, success: bool, latency: float) -> None:
        self.success_window.append(success)
        self.latency_window.append(latency)
        self._adjust()

    def _adjust(self) -> None:
        if len(self.success_window) < 10:
            return

        success_rate = sum(self.success_window) / len(self.success_window)
        avg_latency = sum(self.latency_window) / len(self.latency_window)

        if success_rate > 0.95 and avg_latency < self.target_latency:
            self.current = min(self.current + 1, self.max)
        elif success_rate < 0.8 or avg_latency > self.target_latency * 2:
            self.current = max(self.current - 2, self.min)
```

| Aspect | Assessment |
|--------|------------|
| Simplicity | ⚠️ Moderate complexity |
| Efficiency | ✅ Optimises for conditions |
| Adaptability | ✅ Responds to provider state |

#### 3. Backpressure-Based Flow Control

**Description:** Producer-consumer with queue backpressure.

```python
class BackpressureQueue:
    def __init__(self, max_size: int = 100):
        self.queue = asyncio.Queue(maxsize=max_size)
        self.producers_done = asyncio.Event()

    async def produce(self, items: Iterable):
        for item in items:
            await self.queue.put(item)  # Blocks when full
        self.producers_done.set()

    async def consume(self, worker_fn, n_workers: int):
        async def worker():
            while True:
                try:
                    item = await asyncio.wait_for(
                        self.queue.get(), timeout=1.0
                    )
                    await worker_fn(item)
                except asyncio.TimeoutError:
                    if self.producers_done.is_set() and self.queue.empty():
                        break

        await asyncio.gather(*[worker() for _ in range(n_workers)])
```

| Aspect | Assessment |
|--------|------------|
| Memory | ✅ Bounded memory usage |
| Efficiency | ✅ Natural flow control |
| Complexity | ⚠️ Producer/consumer pattern |

### Memory Management Strategies

#### 1. All-in-Memory

Load all items, process all, store all results.

**Pros:** Simple, fast for small batches
**Cons:** Memory grows with batch size

#### 2. Streaming/Chunked Processing

Process in chunks, persist results incrementally.

```python
async def process_chunked(
    items: Iterable,
    chunk_size: int = 10,
    persist_fn: Callable
) -> None:
    chunk = []
    for item in items:
        chunk.append(item)
        if len(chunk) >= chunk_size:
            results = await process_batch(chunk)
            await persist_fn(results)
            chunk = []

    if chunk:  # Final partial chunk
        results = await process_batch(chunk)
        await persist_fn(results)
```

**Pros:** Bounded memory, progressive results
**Cons:** Slightly more complex

#### 3. Memory-Mapped Processing

Use disk-backed structures for very large datasets.

**Pros:** Handles massive batches
**Cons:** Overkill for typical use cases

### Failure Handling Patterns

#### 1. All-or-Nothing

Fail entire batch on any error.

**Pros:** Simple, consistent
**Cons:** Wastes successful work

#### 2. Best-Effort with Retry

Retry failed items, continue with successes.

```python
class BatchProcessor:
    async def process_with_retry(
        self,
        items: list,
        max_retries: int = 3
    ) -> BatchResult:
        results = []
        failed = []

        for item in items:
            for attempt in range(max_retries + 1):
                try:
                    result = await self.process_item(item)
                    results.append(result)
                    break
                except RetryableError as e:
                    if attempt == max_retries:
                        failed.append((item, e))
                    else:
                        await asyncio.sleep(2 ** attempt)  # Exponential backoff
                except NonRetryableError as e:
                    failed.append((item, e))
                    break

        return BatchResult(successful=results, failed=failed)
```

#### 3. Checkpoint-Based Recovery

Persist progress, resume from checkpoint.

```python
class CheckpointedProcessor:
    async def process_resumable(
        self,
        items: list,
        checkpoint_path: Path
    ) -> BatchResult:
        checkpoint = self.load_checkpoint(checkpoint_path)
        pending = [i for i in items if i.id not in checkpoint.completed]

        for item in pending:
            result = await self.process_item(item)
            checkpoint.record(item.id, result)
            checkpoint.save()  # Atomic write

        return checkpoint.to_result()
```

---

## Provider-Specific Considerations

### Rate Limits

| Provider | Requests/min | Tokens/min | Strategy |
|----------|--------------|------------|----------|
| Anthropic | 60 | 100,000 | Token-aware throttling |
| OpenAI | 60-500 | 90,000-150,000 | Tier-based limits |
| Google | 60 | 32,000 | Conservative default |
| Ollama | Unlimited | N/A | Hardware-bound |

### Recommended Per-Provider Settings

```yaml
batch:
  providers:
    anthropic:
      max_concurrent: 5
      requests_per_minute: 50  # Leave headroom
      backoff_multiplier: 2
    openai:
      max_concurrent: 10
      requests_per_minute: 50
      backoff_multiplier: 1.5
    ollama:
      max_concurrent: 2  # Hardware limited
      requests_per_minute: 1000  # Effectively unlimited
```

---

## Evaluation Matrix

| Strategy | Memory | Throughput | Reliability | Complexity |
|----------|--------|------------|-------------|------------|
| Fixed concurrency | ⚠️ | ⚠️ | ⚠️ | ✅ |
| Adaptive concurrency | ⚠️ | ✅ | ✅ | ⚠️ |
| Backpressure | ✅ | ✅ | ✅ | ⚠️ |
| Chunked processing | ✅ | ✅ | ✅ | ⚠️ |
| Checkpoint recovery | ⚠️ | ⚠️ | ✅ | ⚠️ |

---

## Recommendation

### Primary: Hybrid Approach

Combine multiple strategies for robust batch processing:

```
┌─────────────────────────────────────────────────────────────┐
│                    Batch Processing Pipeline                 │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Input Stream                                                │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────┐                                           │
│  │   Chunker    │  ← Chunk size: 10-20 items                │
│  └──────────────┘                                           │
│       │                                                      │
│       ▼                                                      │
│  ┌──────────────┐    ┌──────────────┐                       │
│  │  Backpressure│───▶│   Adaptive   │                       │
│  │    Queue     │    │  Concurrency │                       │
│  └──────────────┘    └──────────────┘                       │
│                             │                                │
│                             ▼                                │
│  ┌──────────────┐    ┌──────────────┐                       │
│  │  Checkpoint  │◀───│    Worker    │                       │
│  │   Manager    │    │    Pool      │                       │
│  └──────────────┘    └──────────────┘                       │
│       │                                                      │
│       ▼                                                      │
│  Progressive Results                                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Priorities

1. **Adaptive concurrency** - Respond to provider conditions
2. **Chunked processing** - Bound memory usage
3. **Checkpoint recovery** - Handle interruptions
4. **Provider-aware throttling** - Respect rate limits

### Configuration

```yaml
batch:
  processing:
    mode: adaptive  # fixed, adaptive, backpressure
    chunk_size: 10
    checkpoint:
      enabled: true
      interval: 10  # Save every N items
      directory: .persona/checkpoints
  concurrency:
    min_workers: 1
    max_workers: 20
    target_latency_ms: 5000
    success_threshold: 0.9
  retry:
    max_attempts: 3
    backoff_base: 2.0
    retryable_errors:
      - rate_limit
      - timeout
      - server_error
```

---

## Implementation Sketch

```python
class OptimisedBatchProcessor:
    def __init__(
        self,
        provider: Provider,
        config: BatchConfig
    ):
        self.provider = provider
        self.config = config
        self.concurrency = AdaptiveConcurrency(
            min_workers=config.concurrency.min_workers,
            max_workers=config.concurrency.max_workers
        )
        self.checkpoint = CheckpointManager(config.checkpoint)

    async def process(
        self,
        items: list[InputData]
    ) -> BatchResult:
        # Resume from checkpoint if exists
        pending = self.checkpoint.filter_pending(items)

        # Process in chunks
        for chunk in chunked(pending, self.config.chunk_size):
            results = await self._process_chunk(chunk)
            self.checkpoint.record_batch(results)

        return self.checkpoint.to_result()

    async def _process_chunk(
        self,
        chunk: list[InputData]
    ) -> list[PersonaResult]:
        semaphore = asyncio.Semaphore(self.concurrency.current)

        async def worker(item: InputData) -> PersonaResult:
            async with semaphore:
                start = time.monotonic()
                try:
                    result = await self._generate_with_retry(item)
                    self.concurrency.record_result(
                        success=True,
                        latency=time.monotonic() - start
                    )
                    return result
                except Exception as e:
                    self.concurrency.record_result(
                        success=False,
                        latency=time.monotonic() - start
                    )
                    raise

        return await asyncio.gather(
            *[worker(item) for item in chunk],
            return_exceptions=True
        )
```

---

## References

1. [Python asyncio Patterns](https://docs.python.org/3/library/asyncio-task.html)
2. [Backpressure in Reactive Systems](https://www.reactivemanifesto.org/)
3. [Rate Limiting Strategies](https://cloud.google.com/architecture/rate-limiting-strategies)
4. [Exponential Backoff](https://cloud.google.com/storage/docs/exponential-backoff)

---

## Related Documentation

- [F-138: Batch Generation Progress Tracking](../roadmap/features/planned/F-138-batch-progress-tracking.md)
- [F-088: Async Generation](../roadmap/features/completed/F-088-async-generation.md)
- [ADR-0030: Async Execution Model](../decisions/adrs/ADR-0030-async-execution-model.md)

---

**Status**: Complete
