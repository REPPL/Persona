# F-139: Benchmark CLI Commands

## Overview

| Attribute | Value |
|-----------|-------|
| **Feature ID** | F-139 |
| **Title** | Benchmark CLI Commands |
| **Priority** | P1 (High) |
| **Category** | DevOps |
| **Milestone** | [v1.12.0](../../milestones/v1.12.0.md) |
| **Status** | 📋 Planned |
| **Dependencies** | F-136 (Performance Baseline Dashboard) |

---

## Problem Statement

Developers and operations teams need to:
- Run standardised performance benchmarks before releases
- Generate reports for stakeholders and CI/CD pipelines
- Compare performance across different configurations
- Automate regression testing in continuous integration

Currently, there is no unified CLI interface for benchmark operations, forcing manual testing and ad-hoc performance measurement.

---

## Design Approach

### Core Concept

Provide a comprehensive CLI interface for running, reporting, and analysing performance benchmarks with full CI/CD integration support.

### Command Hierarchy

```
persona benchmark
├── run         # Execute benchmark suite
├── capture     # Save baseline snapshot
├── compare     # Compare against baseline
├── report      # Generate benchmark report
├── list        # List available benchmarks/baselines
└── clean       # Remove old baselines/reports
```

### Workload Types

| Workload | Description | Duration | Use Case |
|----------|-------------|----------|----------|
| `quick` | Minimal validation | ~30s | Pre-commit hooks |
| `standard` | Standard benchmark | ~5min | PR validation |
| `full` | Comprehensive suite | ~20min | Release validation |
| `batch` | Batch generation focus | ~10min | Batch performance |
| `provider` | Provider comparison | ~15min | Provider selection |

---

## Key Capabilities

### 1. Benchmark Execution

Run performance benchmarks with configurable workloads.

```bash
# Run standard benchmark
persona benchmark run

# Run specific workload
persona benchmark run --workload quick
persona benchmark run --workload full

# Run with specific provider
persona benchmark run --provider anthropic

# Run with custom iterations
persona benchmark run --iterations 50

# Run specific benchmark only
persona benchmark run --only generation_latency
persona benchmark run --only memory_usage
```

**Output:**
```
Running Benchmark Suite: standard
═════════════════════════════════════════════════════════════

Workload: standard (100 iterations)
Provider: anthropic (claude-sonnet-4-20250514)

Running benchmarks...
  ✅ generation_latency     [████████████████████] 100%
  ✅ throughput             [████████████████████] 100%
  ✅ memory_usage           [████████████████████] 100%
  ✅ api_efficiency         [████████████████████] 100%

Results Summary
───────────────
┌────────────────────────┬─────────┬─────────┬─────────┐
│ Metric                 │ P50     │ P95     │ P99     │
├────────────────────────┼─────────┼─────────┼─────────┤
│ generation_latency     │ 1.23s   │ 1.87s   │ 2.34s   │
│ throughput (per min)   │ 48.7    │ 51.2    │ 52.1    │
│ memory_peak (MB)       │ 512     │ 589     │ 623     │
│ api_calls (per persona)│ 2.1     │ 2.3     │ 2.5     │
└────────────────────────┴─────────┴─────────┴─────────┘

Total time: 4m 32s
```

### 2. Baseline Capture

Save current performance as a named baseline.

```bash
# Capture with auto-generated name (uses version)
persona benchmark capture

# Capture with explicit name
persona benchmark capture --name v1.12.0-rc1

# Capture to specific file
persona benchmark capture --output baselines/v1.12.0.yaml

# Capture specific workload only
persona benchmark capture --workload batch --name v1.12.0-batch
```

**Baseline File:**
```yaml
# baselines/v1.12.0.yaml
name: v1.12.0
version: 1.12.0
captured_at: 2025-01-15T10:30:00Z
environment:
  python_version: "3.12.0"
  platform: darwin-arm64
  cpu: "Apple M2"
  memory_gb: 16
  persona_version: "1.12.0"

workloads:
  standard:
    iterations: 100
    metrics:
      generation_latency_p50: 1230
      generation_latency_p95: 1870
      generation_latency_p99: 2340
      throughput_per_minute: 48.7
      memory_peak_mb: 512
      api_calls_per_persona: 2.1
```

### 3. Baseline Comparison

Compare current performance against stored baselines.

```bash
# Compare against latest baseline
persona benchmark compare

# Compare against specific baseline
persona benchmark compare --baseline v1.11.0

# Compare with custom thresholds
persona benchmark compare --baseline v1.11.0 \
  --warn-threshold 10 \
  --fail-threshold 25

# CI mode (exit code reflects result)
persona benchmark compare --baseline v1.11.0 --ci
```

**Output:**
```
Performance Comparison: Current vs v1.11.0
═════════════════════════════════════════════════════════════

┌────────────────────────┬──────────┬─────────┬─────────┬────────┐
│ Metric                 │ Baseline │ Current │ Change  │ Status │
├────────────────────────┼──────────┼─────────┼─────────┼────────┤
│ generation_latency_p50 │ 1250ms   │ 1230ms  │ -1.6%   │ ✅     │
│ generation_latency_p95 │ 1890ms   │ 1870ms  │ -1.1%   │ ✅     │
│ throughput_per_minute  │ 47.2     │ 48.7    │ +3.2%   │ ✅     │
│ memory_peak_mb         │ 498      │ 512     │ +2.8%   │ ✅     │
│ api_calls_per_persona  │ 2.0      │ 2.1     │ +5.0%   │ ✅     │
└────────────────────────┴──────────┴─────────┴─────────┴────────┘

Summary: All metrics within acceptable thresholds ✅
```

**Exit Codes for CI:**
| Code | Meaning |
|------|---------|
| 0 | All metrics pass |
| 1 | Warning threshold exceeded |
| 2 | Failure threshold exceeded |
| 3 | Benchmark execution error |

### 4. Report Generation

Generate formatted benchmark reports.

```bash
# Generate Markdown report
persona benchmark report --format markdown --output BENCHMARK.md

# Generate JSON report
persona benchmark report --format json --output benchmark.json

# Generate HTML report
persona benchmark report --format html --output benchmark.html

# Include historical comparison
persona benchmark report --format markdown --compare-history 5
```

**Markdown Report:**
```markdown
# Benchmark Report

**Generated:** 2025-01-15T10:45:00Z
**Version:** 1.12.0
**Environment:** darwin-arm64, Python 3.12.0

## Summary

| Metric | Value | vs Baseline |
|--------|-------|-------------|
| Generation Latency (P50) | 1.23s | -1.6% ✅ |
| Throughput | 48.7/min | +3.2% ✅ |
| Memory Peak | 512 MB | +2.8% ✅ |

## Detailed Results

### Generation Latency
- P50: 1.23s
- P95: 1.87s
- P99: 2.34s
- Standard Deviation: 0.31s

### Throughput
- Personas per minute: 48.7
- Sustained rate: 45.2 (>10min runs)

## Environment Details
...
```

### 5. Benchmark Management

List, organise, and clean benchmark artefacts.

```bash
# List available baselines
persona benchmark list

# List with details
persona benchmark list --verbose

# Clean old baselines (keep last N)
persona benchmark clean --keep 5

# Remove specific baseline
persona benchmark clean --name v1.10.0-alpha
```

**Output:**
```
Available Baselines
───────────────────

┌─────────────────┬─────────────────────┬──────────┬─────────┐
│ Name            │ Captured            │ Version  │ Size    │
├─────────────────┼─────────────────────┼──────────┼─────────┤
│ v1.12.0         │ 2025-01-15 10:30    │ 1.12.0   │ 2.3 KB  │
│ v1.11.0         │ 2025-01-01 14:22    │ 1.11.0   │ 2.1 KB  │
│ v1.10.0         │ 2024-12-15 09:15    │ 1.10.0   │ 2.0 KB  │
│ v1.9.0          │ 2024-12-01 11:45    │ 1.9.0    │ 1.9 KB  │
└─────────────────┴─────────────────────┴──────────┴─────────┘

Total: 4 baselines (8.3 KB)
```

---

## CLI Commands

```bash
# Run benchmarks
persona benchmark run [--workload TYPE] [--provider NAME] [--iterations N]
persona benchmark run --only METRIC [--only METRIC...]

# Capture baseline
persona benchmark capture [--name NAME] [--output FILE] [--workload TYPE]

# Compare baselines
persona benchmark compare [--baseline NAME] [--ci]
persona benchmark compare --warn-threshold N --fail-threshold N

# Generate reports
persona benchmark report --format markdown|json|html [--output FILE]
persona benchmark report --compare-history N

# Manage baselines
persona benchmark list [--verbose]
persona benchmark clean [--keep N] [--name NAME]
```

---

## Implementation Tasks

### Phase 1: Core Infrastructure
- [ ] Create `persona/benchmarks/cli.py` module
- [ ] Implement benchmark runner framework
- [ ] Define workload specifications
- [ ] Create metric collection interface

### Phase 2: Run Command
- [ ] Implement `benchmark run` command
- [ ] Add workload selection logic
- [ ] Create progress display
- [ ] Add filtering by metric

### Phase 3: Capture Command
- [ ] Implement `benchmark capture` command
- [ ] Create baseline file writer
- [ ] Add environment fingerprinting
- [ ] Implement auto-naming

### Phase 4: Compare Command
- [ ] Implement `benchmark compare` command
- [ ] Create comparison logic with thresholds
- [ ] Add CI exit codes
- [ ] Create comparison display

### Phase 5: Report Command
- [ ] Implement `benchmark report` command
- [ ] Create Markdown formatter
- [ ] Create JSON formatter
- [ ] Create HTML formatter
- [ ] Add historical comparison

### Phase 6: Management Commands
- [ ] Implement `benchmark list` command
- [ ] Implement `benchmark clean` command
- [ ] Add baseline validation
- [ ] Create cleanup policies

### Phase 7: CI/CD Integration
- [ ] Create GitHub Actions workflow template
- [ ] Add artifact upload support
- [ ] Create PR comment integration
- [ ] Document CI setup

---

## Success Criteria

- [ ] `persona benchmark run` executes benchmarks with progress display
- [ ] `persona benchmark capture` saves baselines with environment info
- [ ] `persona benchmark compare` shows percentage changes and status
- [ ] `persona benchmark report` generates Markdown, JSON, and HTML
- [ ] `persona benchmark list` shows available baselines
- [ ] CI mode returns appropriate exit codes
- [ ] GitHub Actions workflow template available
- [ ] Test coverage >= 85%
- [ ] Benchmark overhead < 5% of normal operation

---

## Configuration

```yaml
# persona.yaml
benchmarks:
  baselines_dir: ./baselines
  reports_dir: ./benchmark-reports

  workloads:
    quick:
      iterations: 10
      timeout: 60
    standard:
      iterations: 100
      timeout: 600
    full:
      iterations: 500
      timeout: 1800

  thresholds:
    warn: 10
    fail: 25

  ci:
    upload_artifacts: true
    comment_on_pr: true
    fail_on_regression: true
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/benchmark.yml
name: Performance Benchmark

on:
  pull_request:
    branches: [main]
  push:
    tags: ['v*']

jobs:
  benchmark:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -e ".[all]"

      - name: Run benchmarks
        run: persona benchmark run --workload standard

      - name: Compare against baseline
        run: persona benchmark compare --baseline main --ci

      - name: Generate report
        run: persona benchmark report --format markdown --output BENCHMARK.md

      - name: Upload benchmark results
        uses: actions/upload-artifact@v4
        with:
          name: benchmark-results
          path: |
            BENCHMARK.md
            baselines/
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Flaky benchmarks | Medium | High | Multiple runs, statistical analysis |
| CI timeout | Low | Medium | Timeout configuration, quick workload |
| False positives | Medium | Medium | Configurable thresholds, trend analysis |
| Environment variance | Medium | Medium | Environment fingerprinting, normalisation |

---

## Research Foundation

- [R-022: Performance Benchmarking Methodology](../../../research/R-022-performance-benchmarking.md)

---

## Related Documentation

- [v1.12.0 Milestone](../../milestones/v1.12.0.md)
- [F-136: Performance Baseline Dashboard](F-136-performance-baseline-dashboard.md)
- [ADR-0032: Performance Baseline Commitment](../../../decisions/adrs/ADR-0032-performance-baseline-commitment.md)

---

**Status**: Planned
