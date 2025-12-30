# R-022: Performance Benchmarking Methodology

Research into establishing performance baselines, regression testing, and quality metrics tracking for Persona.

## Executive Summary

This document evaluates approaches for systematic performance measurement, establishing baselines, and preventing performance regressions.

**Key Finding:** Persona lacks systematic performance tracking. Current quality metrics (F-106) measure output quality but not operational performance (latency, throughput, resource usage).

**Recommendation:** Implement a **three-tier benchmarking system**: micro-benchmarks for critical paths, integration benchmarks for end-to-end workflows, and production observability for real-world performance.

---

## Context

### Current State

| Aspect | Status | Gap |
|--------|--------|-----|
| Quality metrics | ✅ F-106 implemented | Measures output, not performance |
| Cost tracking | ✅ F-078 implemented | Tracks spend, not efficiency |
| Token counting | ✅ F-063 implemented | Counts, doesn't benchmark |
| Latency tracking | ❌ Not implemented | No response time baselines |
| Throughput testing | ❌ Not implemented | No concurrent load testing |
| Memory profiling | ❌ Not implemented | No resource usage baselines |

### Why Performance Benchmarking Matters

1. **Regression detection** - Catch slowdowns before release
2. **Optimisation validation** - Prove improvements work
3. **Capacity planning** - Size infrastructure correctly
4. **SLA compliance** - Meet enterprise requirements
5. **Cost optimisation** - Identify inefficiencies

---

## Benchmarking Dimensions

### Dimension 1: Latency

| Metric | Description | Target |
|--------|-------------|--------|
| **Time to First Token (TTFT)** | Start of generation → first output | <2s (cloud), <5s (local) |
| **End-to-End Latency** | Request → complete response | <30s per persona |
| **P50/P95/P99 Latency** | Distribution percentiles | P99 < 2x P50 |
| **API Response Time** | REST API endpoint latency | <100ms (non-generation) |
| **CLI Startup Time** | Command invocation → ready | <500ms |

### Dimension 2: Throughput

| Metric | Description | Target |
|--------|-------------|--------|
| **Personas per Minute** | Generation rate | >10 (cloud), >2 (local) |
| **Concurrent Requests** | Simultaneous generations | >5 (cloud) |
| **Batch Efficiency** | Overhead per additional persona | <10% |
| **API Requests per Second** | Non-generation endpoints | >100 RPS |

### Dimension 3: Resource Usage

| Metric | Description | Target |
|--------|-------------|--------|
| **Peak Memory** | Maximum RAM during generation | <2GB (standard) |
| **Steady-State Memory** | Idle memory after warmup | <500MB |
| **CPU Utilisation** | During generation | <80% single core |
| **Disk I/O** | Read/write during operation | <100MB/s |
| **Network Bandwidth** | API communication | <10MB per persona |

### Dimension 4: Quality (Efficiency)

| Metric | Description | Target |
|--------|-------------|--------|
| **Tokens per Persona** | Input + output tokens | <10K average |
| **Cost per Persona** | USD per generated persona | <$0.50 (frontier) |
| **Retry Rate** | Failed requests / total | <5% |
| **Parse Success Rate** | Valid JSON output | >98% |

---

## Benchmarking Tiers

### Tier 1: Micro-Benchmarks

**Purpose:** Test individual functions and critical paths

**Tools:**
- `pytest-benchmark` for Python functions
- `hyperfine` for CLI command timing
- Custom timing decorators

**What to Benchmark:**
- JSON parsing (`core/generation/parser.py`)
- Token counting (`core/cost/token_counter.py`)
- Prompt rendering (`core/prompts/renderer.py`)
- Response validation (`core/validation/validator.py`)
- Data loading (`core/data/loader.py`)

**Example:**

```python
import pytest

@pytest.fixture
def sample_response():
    return load_fixture("large_response.json")

def test_json_parsing_performance(benchmark, sample_response):
    result = benchmark(parse_persona_response, sample_response)
    assert result is not None

# benchmark assertions
def test_json_parsing_regression(benchmark, sample_response):
    result = benchmark.pedantic(
        parse_persona_response,
        args=(sample_response,),
        rounds=100,
        iterations=10
    )
    # Assert against baseline
    assert benchmark.stats.mean < 0.01  # 10ms
```

### Tier 2: Integration Benchmarks

**Purpose:** Test end-to-end workflows with mocked external services

**Tools:**
- `locust` for load testing
- `pytest` with fixtures for workflow tests
- Mock providers for deterministic testing

**What to Benchmark:**
- Single persona generation (all providers)
- Batch generation (5, 10, 20 personas)
- Validation workflow
- Export to all formats
- Experiment lifecycle

**Example Locust Test:**

```python
from locust import HttpUser, task, between

class PersonaAPIUser(HttpUser):
    wait_time = between(1, 3)

    @task(10)
    def generate_single(self):
        self.client.post("/api/generate", json={
            "data": "Sample interview data...",
            "count": 1,
            "provider": "anthropic"
        })

    @task(3)
    def list_experiments(self):
        self.client.get("/api/experiments")

    @task(1)
    def health_check(self):
        self.client.get("/api/health")
```

### Tier 3: Production Observability

**Purpose:** Monitor real-world performance

**Tools:**
- OpenTelemetry for distributed tracing
- Prometheus for metrics collection
- Grafana for visualisation
- Custom logging with structured output

**What to Monitor:**
- Request latency histograms
- Error rates by provider
- Token usage patterns
- Cost per user/project
- Resource utilisation trends

---

## Baseline Establishment

### Step 1: Define Reference Hardware

**Primary Test Environment:**
- Mac Studio M4 Max, 128GB RAM
- macOS 14.x
- Python 3.12
- Ollama with llama3:70b (local tests)
- Fast internet connection (cloud tests)

**Minimum Supported Environment:**
- MacBook M1 Pro, 16GB RAM
- 8GB available RAM for Persona
- Python 3.12
- Broadband internet

### Step 2: Define Reference Workloads

| Workload | Description | Personas | Provider |
|----------|-------------|----------|----------|
| **quick** | Single fast persona | 1 | Anthropic Haiku |
| **standard** | Typical usage | 3 | Anthropic Sonnet |
| **batch** | Batch generation | 10 | Anthropic Sonnet |
| **local** | Local model | 3 | Ollama llama3:70b |
| **hybrid** | Mixed pipeline | 5 | Ollama + Anthropic |
| **large** | Complex data | 3 | Anthropic Sonnet |

### Step 3: Capture Initial Baselines

Run each workload 10 times, record:
- Mean, median, P95, P99 latency
- Memory peak and steady-state
- Token counts (input/output)
- Cost

Store in version-controlled baseline file:

```yaml
# benchmarks/baselines/v1.12.0.yaml
version: "1.12.0"
captured: "2025-01-15"
environment:
  os: "macOS 14.2"
  python: "3.12.1"
  hardware: "Mac Studio M4 Max 128GB"

workloads:
  standard:
    latency_p50_ms: 8500
    latency_p95_ms: 12000
    latency_p99_ms: 15000
    memory_peak_mb: 850
    tokens_input: 3200
    tokens_output: 2100
    cost_usd: 0.18
```

---

## Regression Detection

### Automated Checks

**Pre-Commit:**
- Micro-benchmark critical paths
- Fail if >10% regression from baseline

**CI Pipeline:**
- Run integration benchmarks on PR
- Compare against version baseline
- Warn at 10%, fail at 25% regression

**Release Gate:**
- Full benchmark suite
- Manual review of any regressions
- Update baseline after approval

### Regression Thresholds

| Metric | Warning | Failure |
|--------|---------|---------|
| Latency (P50) | +10% | +25% |
| Latency (P99) | +15% | +35% |
| Memory Peak | +20% | +50% |
| Token Usage | +5% | +15% |
| Error Rate | +1% | +5% |

### Regression Response

```
Regression Detected
        ↓
┌───────────────────────┐
│ Is it intentional?    │
│ (new feature, safety) │
└───────────────────────┘
        ↓
    ┌───┴───┐
   Yes     No
    ↓       ↓
Document   Investigate
in ADR     root cause
    ↓       ↓
Update    Fix before
baseline  merge
```

---

## Implementation Architecture

### Benchmark Module Structure

```
src/persona/
├── benchmarks/           # Benchmark infrastructure
│   ├── __init__.py
│   ├── baselines/        # Version-controlled baselines
│   │   ├── v1.11.0.yaml
│   │   └── v1.12.0.yaml
│   ├── workloads/        # Benchmark workload definitions
│   │   ├── quick.py
│   │   ├── standard.py
│   │   └── batch.py
│   ├── runners/          # Benchmark execution
│   │   ├── micro.py
│   │   └── integration.py
│   ├── reporters/        # Result formatting
│   │   ├── console.py
│   │   ├── json.py
│   │   └── markdown.py
│   └── cli.py            # CLI commands
│
tests/
├── benchmarks/           # pytest-benchmark tests
│   ├── test_parsing.py
│   ├── test_prompts.py
│   └── test_validation.py
```

### CLI Commands

```bash
# Run micro-benchmarks
persona benchmark micro

# Run integration benchmarks
persona benchmark integration --workload standard

# Compare against baseline
persona benchmark compare --baseline v1.11.0

# Generate new baseline
persona benchmark capture --output baselines/v1.12.0.yaml

# Generate report
persona benchmark report --format markdown
```

### Observability Integration

```python
# Instrumentation decorator
from persona.observability import observe

@observe(name="generate_persona", track_tokens=True)
async def generate(self, data: str, count: int) -> list[Persona]:
    ...

# Automatic metrics collection:
# - persona_generation_duration_seconds (histogram)
# - persona_generation_tokens_total (counter)
# - persona_generation_errors_total (counter)
```

---

## Tooling Recommendations

### Micro-Benchmarking

| Tool | Use Case | Integration |
|------|----------|-------------|
| **pytest-benchmark** | Function-level timing | pytest native |
| **py-spy** | CPU profiling | Sampling profiler |
| **memray** | Memory profiling | Python native |
| **hyperfine** | CLI timing | Shell commands |

### Integration Testing

| Tool | Use Case | Integration |
|------|----------|-------------|
| **locust** | Load testing | Python-native, HTTP |
| **k6** | Modern load testing | JavaScript, CLI |
| **vegeta** | HTTP load testing | Go binary, simple |

### Production Observability

| Tool | Use Case | Integration |
|------|----------|-------------|
| **OpenTelemetry** | Distributed tracing | Industry standard |
| **Prometheus** | Metrics collection | Pull-based |
| **Grafana** | Visualisation | Dashboard |
| **Sentry** | Error tracking | SaaS or self-hosted |

### Recommendation

- **Micro:** pytest-benchmark + memray
- **Integration:** locust (Python-native)
- **Production:** OpenTelemetry + Prometheus + Grafana

---

## Reporting and Visualisation

### Benchmark Report Format

```markdown
# Performance Benchmark Report

**Version:** 1.12.0
**Date:** 2025-01-15
**Environment:** Mac Studio M4 Max, macOS 14.2, Python 3.12.1

## Summary

| Workload | P50 (ms) | P95 (ms) | Memory (MB) | Status |
|----------|----------|----------|-------------|--------|
| quick    | 2,100    | 2,800    | 320         | ✅ Pass |
| standard | 8,500    | 12,000   | 850         | ✅ Pass |
| batch    | 35,000   | 48,000   | 1,200       | ⚠️ Warn |
| local    | 45,000   | 65,000   | 2,100       | ✅ Pass |

## Regression Analysis

### batch Workload
- P95 latency increased 18% (40,000 → 48,000 ms)
- Root cause: New validation step added (F-138)
- Verdict: Acceptable trade-off for quality improvement

## Trend (Last 5 Releases)

| Version | standard P50 | Memory | Tokens |
|---------|--------------|--------|--------|
| v1.8.0  | 9,200        | 780    | 5,100  |
| v1.9.0  | 8,900        | 820    | 5,050  |
| v1.10.0 | 8,700        | 830    | 5,020  |
| v1.11.0 | 8,600        | 840    | 5,000  |
| v1.12.0 | 8,500        | 850    | 4,950  |

**Trend:** Steady improvement in latency and token efficiency.
```

### Dashboard Components

For WebUI (v2.0.0):
- Real-time latency graph
- Historical trend charts
- Cost per persona over time
- Provider comparison
- Error rate timeline

---

## Proposed Features

This research informs the following features:

1. **F-136: Performance Baseline Dashboard** (P0, v1.12.0)
2. **F-137: Quality Trend Dashboard** (P1, v1.12.0)
3. **F-140: Cost Analytics Dashboard** (P1, v1.12.0)

---

## Research Sources

### Performance Testing

- [pytest-benchmark Documentation](https://pytest-benchmark.readthedocs.io/)
- [Locust Load Testing](https://locust.io/)
- [Python Profiling with py-spy](https://github.com/benfred/py-spy)
- [memray Memory Profiler](https://github.com/bloomberg/memray)

### Observability

- [OpenTelemetry Python](https://opentelemetry.io/docs/instrumentation/python/)
- [Prometheus Best Practices](https://prometheus.io/docs/practices/naming/)
- [Grafana Dashboard Design](https://grafana.com/docs/grafana/latest/dashboards/)

### LLM Performance

- [LLM Inference Latency Optimization](https://www.anyscale.com/blog/llm-performance-optimization)
- [Measuring LLM Performance](https://www.pinecone.io/learn/llm-performance/)
- [Token Economics in LLM Applications](https://eugeneyan.com/writing/llm-economics/)

### Industry Practices

- [How Stripe Monitors Performance](https://stripe.com/blog/engineering-metrics)
- [Netflix Performance Engineering](https://netflixtechblog.com/performance-under-the-hood-of-netflixs-streaming-app-e8d2f88c1dd6)
- [Google SRE on Latency](https://sre.google/sre-book/monitoring-distributed-systems/)

---

## Related Documentation

- [F-106: Quality Metrics Scoring](../roadmap/features/completed/F-106-quality-metrics.md)
- [F-078: Cost Tracking](../roadmap/features/completed/F-078-cost-tracking.md)
- [F-129: Provider Connection Pooling](../roadmap/features/completed/F-129-provider-connection-pooling.md)
- [ADR-0032: Performance Baseline Commitment](../decisions/adrs/ADR-0032-performance-baseline-commitment.md) (Planned)
