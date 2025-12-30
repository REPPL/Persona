# F-150: Quality Gate CI Integration

## Overview

| Attribute | Value |
|-----------|-------|
| **Feature ID** | F-150 |
| **Title** | Quality Gate CI Integration |
| **Priority** | P1 (High) |
| **Category** | DevOps |
| **Milestone** | [v1.14.0](../../milestones/v1.14.0.md) |
| **Status** | 📋 Planned |
| **Dependencies** | F-106 (Quality Metrics Scoring), F-136 (Performance Baseline) |

---

## Problem Statement

Teams need to enforce quality standards automatically:
- Reject personas below quality threshold
- Integrate with CI/CD pipelines
- Block merges with quality regressions
- Track quality trends over time

Currently, quality checks require manual review.

---

## Design Approach

Provide CI-friendly commands with appropriate exit codes and reporting.

---

## Key Capabilities

### 1. Quality Gate Command

Check quality against configurable thresholds.

```bash
# Basic quality gate
persona quality gate ./personas/

# With threshold
persona quality gate --threshold 0.85 ./personas/

# CI mode (exit codes)
persona quality gate --ci ./personas/
```

**Exit Codes:**
| Code | Meaning |
|------|---------|
| 0 | All personas pass |
| 1 | Some personas below threshold |
| 2 | Critical quality failure |
| 3 | Configuration error |

### 2. Configuration File

Define quality requirements in config.

```yaml
# quality-gate.yaml
thresholds:
  coherence: 0.80
  faithfulness: 0.75
  completeness: 0.90
  composite: 0.85

rules:
  - name: "No critical bias"
    condition: "bias_score < 0.3"
    severity: critical

  - name: "Minimum goals"
    condition: "len(goals) >= 2"
    severity: warning

fail_on:
  - critical
  - threshold_violation
```

```bash
persona quality gate --config quality-gate.yaml ./personas/
```

### 3. GitHub Actions Integration

Integrate with GitHub workflows.

```yaml
# .github/workflows/quality.yml
name: Persona Quality Gate

on: [pull_request]

jobs:
  quality-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install Persona
        run: pip install persona

      - name: Run Quality Gate
        run: persona quality gate --ci --config quality-gate.yaml ./personas/

      - name: Upload Quality Report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: quality-report
          path: quality-report.json
```

### 4. PR Comment Integration

Post quality results as PR comments.

```bash
# Generate PR comment
persona quality gate --ci --pr-comment ./personas/ > pr-comment.md
```

**PR Comment:**
```markdown
## 🎯 Persona Quality Report

**Status:** ✅ Passed

| Metric | Score | Threshold | Status |
|--------|-------|-----------|--------|
| Coherence | 0.89 | 0.80 | ✅ |
| Faithfulness | 0.92 | 0.75 | ✅ |
| Completeness | 0.95 | 0.90 | ✅ |
| Composite | 0.91 | 0.85 | ✅ |

**Personas Checked:** 5
**All checks passed!**
```

### 5. Quality Trend Tracking

Track quality over time for trend analysis.

```bash
# Record quality snapshot
persona quality snapshot --tag pr-123

# Compare to baseline
persona quality gate --compare-baseline main ./personas/
```

---

## CLI Commands

```bash
# Quality gate
persona quality gate [PATH] [--threshold N] [--ci]
persona quality gate --config FILE [PATH]

# CI reporting
persona quality gate --ci --output report.json
persona quality gate --ci --pr-comment > comment.md

# Snapshots
persona quality snapshot [--tag TAG]
persona quality compare --baseline TAG

# Configuration
persona quality gate --show-config
persona quality gate --init-config > quality-gate.yaml
```

---

## Success Criteria

- [ ] Quality gate returns appropriate exit codes
- [ ] Configuration file supports custom rules
- [ ] GitHub Actions integration documented
- [ ] PR comment generation works
- [ ] Trend tracking stores snapshots
- [ ] Test coverage >= 85%

---

## Related Documentation

- [v1.14.0 Milestone](../../milestones/v1.14.0.md)
- [F-106: Quality Metrics Scoring](../completed/F-106-quality-metrics.md)
- [F-136: Performance Baseline Dashboard](F-136-performance-baseline-dashboard.md)
- [F-139: Benchmark CLI Commands](F-139-benchmark-cli.md)

---

**Status**: Planned
