# ADR-0032: Performance Baseline Commitment

## Status

Planned

## Context

Persona needs a formal commitment to performance baselines to:
- Prevent performance regressions between releases
- Provide users with reliable performance expectations
- Enable objective performance comparisons
- Support CI/CD integration for automated testing

Without explicit baselines, performance can degrade gradually without detection.

## Decision

Establish **formal performance baselines** with automated regression detection in CI/CD.

### Baseline Metrics

| Metric | Baseline (v1.12.0) | Warning Threshold | Failure Threshold |
|--------|-------------------|-------------------|-------------------|
| Single persona generation (P50) | 1,500ms | +10% | +25% |
| Single persona generation (P95) | 3,000ms | +10% | +25% |
| Batch generation (10 personas, P50) | 12,000ms | +10% | +25% |
| Memory peak (single) | 512MB | +20% | +50% |
| Memory peak (batch 10) | 1,024MB | +20% | +50% |
| CLI startup time | 500ms | +20% | +50% |

### Baseline Format

```yaml
# baselines/v1.12.0.yaml
version: "1.12.0"
captured_at: "2025-01-15T10:00:00Z"
environment:
  python_version: "3.12"
  platform: "linux-x86_64"

metrics:
  generation:
    single:
      latency_p50_ms: 1500
      latency_p95_ms: 3000
      latency_p99_ms: 4500
    batch_10:
      latency_p50_ms: 12000
      latency_p95_ms: 18000
  memory:
    single_peak_mb: 512
    batch_10_peak_mb: 1024
  startup:
    cli_cold_ms: 500

thresholds:
  warning: 10  # percent
  failure: 25  # percent
```

### CI/CD Integration

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

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: pip install -e ".[all]"

      - name: Run benchmarks
        run: persona benchmark run --workload standard

      - name: Compare against baseline
        run: |
          persona benchmark compare \
            --baseline baselines/v1.11.0.yaml \
            --fail-on-regression

      - name: Upload results
        uses: actions/upload-artifact@v4
        with:
          name: benchmark-results
          path: benchmark-results/
```

### Regression Detection

```python
class RegressionDetector:
    def __init__(self, baseline: Baseline, thresholds: Thresholds):
        self.baseline = baseline
        self.thresholds = thresholds

    def check(self, current: BenchmarkResult) -> RegressionReport:
        regressions = []

        for metric, baseline_value in self.baseline.metrics.items():
            current_value = current.metrics.get(metric)
            if current_value is None:
                continue

            change_percent = (
                (current_value - baseline_value) / baseline_value
            ) * 100

            if change_percent > self.thresholds.failure:
                regressions.append(Regression(
                    metric=metric,
                    baseline=baseline_value,
                    current=current_value,
                    change=change_percent,
                    severity="failure"
                ))
            elif change_percent > self.thresholds.warning:
                regressions.append(Regression(
                    metric=metric,
                    baseline=baseline_value,
                    current=current_value,
                    change=change_percent,
                    severity="warning"
                ))

        return RegressionReport(
            regressions=regressions,
            passed=not any(r.severity == "failure" for r in regressions)
        )
```

### Release Gating

Performance regressions above the failure threshold **block releases**:

1. All PRs run benchmark comparison
2. Failures prevent merge (unless explicitly overridden)
3. Release tags require clean benchmark run
4. Baseline updates require explicit approval

### Baseline Update Process

```bash
# Capture new baseline after intentional change
persona benchmark capture --output baselines/v1.13.0.yaml

# Requires PR with:
# 1. Updated baseline file
# 2. Justification for regression (if any)
# 3. Approval from maintainer
```

## Consequences

**Positive:**
- Performance regressions caught automatically
- Clear expectations for users
- Historical performance tracking
- Prevents gradual degradation

**Negative:**
- Benchmark variance may cause false positives
- Baseline maintenance overhead
- May block valid changes

## Alternatives Considered

### Relative Comparison Only

**Description:** Compare against previous release only.

**Pros:** Simple, always have baseline.

**Cons:** Allows gradual degradation over time.

**Why Not Chosen:** Need absolute reference point.

### No Performance Gates

**Description:** Track but don't block releases.

**Pros:** Flexibility, no false positives.

**Cons:** Regressions can slip through.

**Why Not Chosen:** Need enforcement.

### SLA-Based Approach

**Description:** Define SLAs, not baselines.

**Pros:** User-focused, flexible.

**Cons:** Hard to enforce in CI, no regression detection.

**Why Not Chosen:** Need CI integration.

## Research Reference

See [R-022: Performance Benchmarking Methodology](../../research/R-022-performance-benchmarking.md) for benchmarking approach.

---

## Related Documentation

- [R-022: Performance Benchmarking Methodology](../../research/R-022-performance-benchmarking.md)
- [F-136: Performance Baseline Dashboard](../../roadmap/features/planned/F-136-performance-baseline-dashboard.md)
- [F-139: Benchmark CLI Commands](../../roadmap/features/planned/F-139-benchmark-cli.md)

---

**Status**: Planned
