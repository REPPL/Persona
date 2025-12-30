# F-136: Performance Baseline Dashboard

## Overview

| Attribute | Value |
|-----------|-------|
| **Feature ID** | F-136 |
| **Title** | Performance Baseline Dashboard |
| **Priority** | P0 (Critical) |
| **Category** | Observability |
| **Milestone** | [v1.12.0](../../milestones/v1.12.0.md) |
| **Status** | 📋 Planned |
| **Dependencies** | F-129 (Provider Connection Pooling), F-133 (Metric Registry) |

---

## Problem Statement

Persona currently lacks systematic performance tracking, making it difficult to:
- Detect performance regressions between versions
- Compare provider performance objectively
- Establish meaningful SLAs for generation operations
- Identify bottlenecks in the generation pipeline

Without baselines, performance changes go unnoticed until they become critical issues affecting user experience.

---

## Design Approach

### Core Concept

Establish version-controlled performance baselines that enable automated regression detection and historical trend analysis.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Performance Baseline System                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Capture    │───▶│    Store     │───▶│   Compare    │  │
│  │   Engine     │    │   (YAML)     │    │   Engine     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │           │
│         ▼                   ▼                   ▼           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Metrics    │    │  Baselines   │    │   Reports    │  │
│  │  - Latency   │    │  - v1.11.0   │    │  - Markdown  │  │
│  │  - Throughput│    │  - v1.12.0   │    │  - JSON      │  │
│  │  - Memory    │    │  - custom    │    │  - CI/CD     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Metrics Captured

| Metric | Description | Unit |
|--------|-------------|------|
| `generation_latency_p50` | Median generation time | ms |
| `generation_latency_p95` | 95th percentile latency | ms |
| `generation_latency_p99` | 99th percentile latency | ms |
| `throughput_personas_per_minute` | Generation throughput | count/min |
| `memory_peak_mb` | Peak memory during generation | MB |
| `memory_average_mb` | Average memory usage | MB |
| `api_calls_per_persona` | API efficiency metric | count |
| `token_usage_per_persona` | Token efficiency | tokens |

### Baseline Format

```yaml
# baselines/v1.12.0.yaml
version: "1.12.0"
captured_at: "2025-01-15T10:30:00Z"
environment:
  python_version: "3.12.0"
  platform: "darwin-arm64"
  persona_version: "1.12.0"

workloads:
  standard:
    description: "Single persona generation from 1KB input"
    iterations: 100
    metrics:
      generation_latency_p50: 1250
      generation_latency_p95: 1890
      generation_latency_p99: 2340
      throughput_personas_per_minute: 48
      memory_peak_mb: 512

  batch:
    description: "10 personas from 5KB input"
    iterations: 20
    metrics:
      generation_latency_p50: 8500
      generation_latency_p95: 12400
      total_memory_mb: 1024
```

---

## Key Capabilities

### 1. Baseline Capture

Capture current performance metrics and save as versioned baseline.

```bash
# Capture baseline for current version
persona benchmark capture --output baselines/v1.12.0.yaml

# Capture with specific workload
persona benchmark capture --workload batch --output baselines/v1.12.0-batch.yaml

# Capture with custom iterations
persona benchmark capture --iterations 50 --output baselines/custom.yaml
```

### 2. Baseline Comparison

Compare current performance against stored baselines.

```bash
# Compare against specific baseline
persona benchmark compare --baseline baselines/v1.11.0.yaml

# Compare with threshold override
persona benchmark compare --baseline v1.11.0 --threshold 15

# Compare multiple baselines
persona benchmark compare --baseline v1.10.0 --baseline v1.11.0
```

**Output:**
```
Performance Comparison: v1.12.0 vs v1.11.0

Workload: standard
┌────────────────────────────┬──────────┬──────────┬─────────┬────────┐
│ Metric                     │ Baseline │ Current  │ Change  │ Status │
├────────────────────────────┼──────────┼──────────┼─────────┼────────┤
│ generation_latency_p50     │ 1250ms   │ 1180ms   │ -5.6%   │ ✅     │
│ generation_latency_p95     │ 1890ms   │ 2100ms   │ +11.1%  │ ⚠️     │
│ throughput_personas_per_min│ 48       │ 51       │ +6.3%   │ ✅     │
│ memory_peak_mb             │ 512      │ 498      │ -2.7%   │ ✅     │
└────────────────────────────┴──────────┴──────────┴─────────┴────────┘

⚠️ Warning: generation_latency_p95 exceeds 10% threshold
```

### 3. Regression Detection

Automatic detection of performance regressions.

| Threshold | Level | Action |
|-----------|-------|--------|
| < 10% | Normal | No action |
| 10-25% | Warning | Log warning, continue |
| > 25% | Failure | Exit with error code |

```bash
# CI/CD integration
persona benchmark compare --baseline v1.11.0 --fail-on-regression

# Custom thresholds
persona benchmark compare --baseline v1.11.0 \
  --warn-threshold 5 \
  --fail-threshold 15
```

### 4. Historical Trends

Visualise performance trends across versions.

```bash
# Show trend for specific metric
persona benchmark trends --metric generation_latency_p50

# Export trend data
persona benchmark trends --format json --output trends.json
```

**TUI Display:**
```
Generation Latency P50 Trend
────────────────────────────

2500ms │
       │    ╭─╮
2000ms │    │ │
       │ ╭──╯ ╰──╮
1500ms │─╯       ╰──────────╮
       │                    ╰─────────
1000ms │
       └──────────────────────────────
        v1.8  v1.9  v1.10  v1.11  v1.12
```

### 5. Provider Comparison

Compare performance across different LLM providers.

```bash
# Run benchmark across all configured providers
persona benchmark providers --workload standard

# Compare specific providers
persona benchmark providers --provider anthropic --provider openai
```

---

## CLI Commands

```bash
# Capture baselines
persona benchmark capture [--workload standard|quick|batch] [--output FILE]
persona benchmark capture --iterations N

# Compare baselines
persona benchmark compare --baseline FILE [--threshold N]
persona benchmark compare --baseline v1.11.0 --fail-on-regression

# View trends
persona benchmark trends [--metric METRIC] [--days N]
persona benchmark trends --format json --output FILE

# Provider comparison
persona benchmark providers [--provider NAME]...

# List available baselines
persona benchmark list
```

---

## Implementation Tasks

### Phase 1: Core Infrastructure
- [ ] Create `persona/benchmarks/` module
- [ ] Implement `MetricCollector` class
- [ ] Create baseline YAML schema
- [ ] Implement baseline storage/loading

### Phase 2: Capture Engine
- [ ] Implement workload definitions (standard, quick, batch)
- [ ] Create benchmark runner with statistical analysis
- [ ] Add environment fingerprinting
- [ ] Implement `persona benchmark capture` command

### Phase 3: Comparison Engine
- [ ] Implement baseline comparison logic
- [ ] Create threshold configuration
- [ ] Add regression detection
- [ ] Implement `persona benchmark compare` command

### Phase 4: Reporting
- [ ] Create Rich table formatters
- [ ] Implement TUI trend visualisation
- [ ] Add JSON/Markdown export
- [ ] Create CI/CD exit codes

### Phase 5: Integration
- [ ] Add pytest-benchmark integration
- [ ] Create GitHub Actions workflow
- [ ] Document CI/CD setup
- [ ] Add provider comparison feature

---

## Success Criteria

- [ ] Baselines can be captured with `persona benchmark capture`
- [ ] Baselines are version-controlled YAML files
- [ ] Comparison shows percentage changes and status
- [ ] 10% latency increase triggers warning
- [ ] 25% latency increase triggers failure exit code
- [ ] Trends visualised in TUI
- [ ] JSON export available for CI/CD integration
- [ ] Provider comparison working
- [ ] Test coverage >= 85%
- [ ] Benchmark overhead < 5% of normal operation

---

## Configuration

```yaml
# persona.yaml
benchmarks:
  enabled: true
  baselines_dir: ./baselines
  default_workload: standard
  iterations:
    standard: 100
    quick: 10
    batch: 20
  thresholds:
    warn: 10  # percentage
    fail: 25  # percentage
  metrics:
    - generation_latency_p50
    - generation_latency_p95
    - throughput_personas_per_minute
    - memory_peak_mb
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Benchmark variance | Medium | Medium | Multiple runs, statistical analysis, outlier removal |
| Environment differences | Medium | High | Environment fingerprinting, normalisation |
| Storage growth | Low | Low | Retention policy, compression |
| CI timeout | Low | Medium | Quick workload option, parallel execution |

---

## Research Foundation

- [R-022: Performance Benchmarking Methodology](../../../research/R-022-performance-benchmarking.md)

---

## Related Documentation

- [v1.12.0 Milestone](../../milestones/v1.12.0.md)
- [F-137: Quality Trend Dashboard](F-137-quality-trend-dashboard.md)
- [F-139: Benchmark CLI Commands](F-139-benchmark-cli.md)
- [ADR-0032: Performance Baseline Commitment](../../../decisions/adrs/ADR-0032-performance-baseline-commitment.md)

---

**Status**: Planned
