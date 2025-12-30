# F-137: Quality Trend Dashboard

## Overview

| Attribute | Value |
|-----------|-------|
| **Feature ID** | F-137 |
| **Title** | Quality Trend Dashboard |
| **Priority** | P1 (High) |
| **Category** | Observability |
| **Milestone** | [v1.12.0](../../milestones/v1.12.0.md) |
| **Status** | 📋 Planned |
| **Dependencies** | F-106 (Quality Metrics Scoring), F-133 (Metric Registry) |

---

## Problem Statement

Persona generates quality scores for individual personas but lacks:
- Historical tracking of quality metrics over time
- Visibility into quality trends across experiments
- Early warning for quality degradation
- Per-provider quality comparison
- Ability to set and track quality goals

Users cannot currently answer questions like "Has our persona quality improved over the last month?" or "Which provider consistently produces the highest coherence scores?"

---

## Design Approach

### Core Concept

Track and visualise quality metrics over time to identify patterns, detect degradation, and enable data-driven provider selection.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Quality Trend System                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Generation          Quality           Trend                 │
│  Pipeline    ───▶    Store     ───▶    Engine               │
│                      (SQLite)                                │
│                         │                                    │
│                         ▼                                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   Quality Metrics                     │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │   │
│  │  │Coherence │  │Faithful- │  │Complete- │  ...      │   │
│  │  │  Score   │  │   ness   │  │   ness   │           │   │
│  │  └──────────┘  └──────────┘  └──────────┘           │   │
│  └──────────────────────────────────────────────────────┘   │
│                         │                                    │
│                         ▼                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Trends    │  │   Alerts    │  │   Goals     │         │
│  │  Dashboard  │  │   Engine    │  │  Tracking   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Metrics Tracked

| Metric | Description | Range |
|--------|-------------|-------|
| `coherence` | Internal consistency of persona | 0.0 - 1.0 |
| `faithfulness` | Alignment with source data | 0.0 - 1.0 |
| `completeness` | Required fields populated | 0.0 - 1.0 |
| `distinctiveness` | Uniqueness vs other personas | 0.0 - 1.0 |
| `authenticity` | Realistic human-like qualities | 0.0 - 1.0 |
| `composite` | Weighted average of all metrics | 0.0 - 1.0 |

### Storage Schema

```sql
CREATE TABLE quality_scores (
    id INTEGER PRIMARY KEY,
    persona_id TEXT NOT NULL,
    experiment_id TEXT,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    metric TEXT NOT NULL,
    score REAL NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (persona_id) REFERENCES personas(id)
);

CREATE INDEX idx_quality_time ON quality_scores(recorded_at);
CREATE INDEX idx_quality_provider ON quality_scores(provider);
CREATE INDEX idx_quality_metric ON quality_scores(metric);
```

---

## Key Capabilities

### 1. Time-Series Quality Scores

View quality metrics over configurable time periods.

```bash
# View quality trends for last 30 days
persona quality trends

# Specific time range
persona quality trends --days 90

# Filter by provider
persona quality trends --provider anthropic --days 30
```

**TUI Display:**
```
Quality Trends (Last 30 Days)
─────────────────────────────

Coherence Score
1.0 │         ╭───────────────────╮
    │    ╭────╯                   ╰───╮
0.8 │────╯                            ╰──
    │
0.6 │
    └────────────────────────────────────
     Week 1    Week 2    Week 3    Week 4

Metric Summary
┌─────────────┬─────────┬─────────┬────────┬─────────┐
│ Metric      │ Current │ 7d Avg  │ 30d Avg│ Trend   │
├─────────────┼─────────┼─────────┼────────┼─────────┤
│ Coherence   │ 0.87    │ 0.85    │ 0.83   │ ↑ +2.4% │
│ Faithfulness│ 0.91    │ 0.90    │ 0.89   │ ↑ +1.1% │
│ Completeness│ 0.95    │ 0.94    │ 0.94   │ → +0.0% │
│ Composite   │ 0.89    │ 0.87    │ 0.86   │ ↑ +1.2% │
└─────────────┴─────────┴─────────┴────────┴─────────┘
```

### 2. Per-Provider Quality Tracking

Compare quality metrics across different LLM providers.

```bash
# Provider quality comparison
persona quality providers

# Specific metric comparison
persona quality providers --metric coherence
```

**Output:**
```
Provider Quality Comparison (Last 30 Days)
──────────────────────────────────────────

┌───────────┬───────────┬────────────┬────────────┬───────────┐
│ Provider  │ Coherence │ Faithful.  │ Complete.  │ Composite │
├───────────┼───────────┼────────────┼────────────┼───────────┤
│ anthropic │ 0.91 ★    │ 0.93 ★     │ 0.96       │ 0.92 ★    │
│ openai    │ 0.88      │ 0.90       │ 0.97 ★     │ 0.90      │
│ ollama    │ 0.79      │ 0.82       │ 0.91       │ 0.82      │
└───────────┴───────────┴────────────┴────────────┴───────────┘

★ = Best in category
```

### 3. Experiment-Level Quality History

Track quality for specific experiments over time.

```bash
# Quality history for experiment
persona quality history --experiment user-research-2025

# Export for analysis
persona quality history --experiment user-research-2025 --format csv
```

### 4. Quality Alerts

Configure alerts for quality drops.

```bash
# Enable quality alerting
persona quality alerts enable

# Set alert threshold
persona quality alerts set --metric coherence --threshold 0.75

# List active alerts
persona quality alerts list
```

**Configuration:**
```yaml
quality:
  alerts:
    enabled: true
    thresholds:
      coherence: 0.75
      faithfulness: 0.70
      composite: 0.75
    notification:
      type: console  # console, webhook, email (future)
```

### 5. Quality Goals

Set and track quality improvement goals.

```bash
# Set quality goal
persona quality goals set --metric coherence --target 0.85

# View goal progress
persona quality goals list

# Clear goal
persona quality goals clear --metric coherence
```

**Output:**
```
Quality Goals Progress
──────────────────────

┌─────────────┬────────┬─────────┬──────────┬─────────────┐
│ Metric      │ Target │ Current │ Progress │ Status      │
├─────────────┼────────┼─────────┼──────────┼─────────────┤
│ Coherence   │ 0.85   │ 0.87    │ 102%     │ ✅ Achieved │
│ Faithfulness│ 0.90   │ 0.88    │ 98%      │ 🔄 In Progress│
│ Composite   │ 0.88   │ 0.84    │ 95%      │ 🔄 In Progress│
└─────────────┴────────┴─────────┴──────────┴─────────────┘
```

---

## CLI Commands

```bash
# View trends
persona quality trends [--days N] [--provider NAME] [--metric NAME]
persona quality trends --format json --output trends.json

# Provider comparison
persona quality providers [--metric NAME] [--days N]

# Experiment history
persona quality history --experiment NAME [--format csv|json]

# Alerts management
persona quality alerts enable|disable
persona quality alerts set --metric NAME --threshold N
persona quality alerts list

# Goals management
persona quality goals set --metric NAME --target N
persona quality goals list
persona quality goals clear --metric NAME

# Quality summary
persona quality summary [--days N]
```

---

## Implementation Tasks

### Phase 1: Storage Infrastructure
- [ ] Create quality metrics SQLite schema
- [ ] Implement `QualityStore` class
- [ ] Add automatic recording during generation
- [ ] Create migration for existing data

### Phase 2: Trend Analysis
- [ ] Implement time-series aggregation
- [ ] Create trend calculation (7d, 30d, 90d)
- [ ] Add statistical analysis (std dev, percentiles)
- [ ] Implement `persona quality trends` command

### Phase 3: Provider Comparison
- [ ] Implement provider grouping queries
- [ ] Create comparison report formatter
- [ ] Add best-in-category highlighting
- [ ] Implement `persona quality providers` command

### Phase 4: Alerts System
- [ ] Create alert configuration schema
- [ ] Implement threshold monitoring
- [ ] Add console notification
- [ ] Create `persona quality alerts` commands

### Phase 5: Goals Tracking
- [ ] Implement goal storage
- [ ] Create progress calculation
- [ ] Add goal status reporting
- [ ] Implement `persona quality goals` commands

### Phase 6: TUI Integration
- [ ] Create quality dashboard panel
- [ ] Implement sparkline charts
- [ ] Add real-time updates
- [ ] Integrate with existing TUI

---

## Success Criteria

- [ ] Quality scores automatically recorded during generation
- [ ] Time-series trends visible for last 30 days by default
- [ ] Per-provider quality comparison available
- [ ] Quality alerts configurable with thresholds
- [ ] Quality goals can be set and tracked
- [ ] CSV/JSON export available
- [ ] TUI displays quality trends
- [ ] Test coverage >= 85%

---

## Configuration

```yaml
# persona.yaml
quality:
  tracking:
    enabled: true
    retention_days: 365
  metrics:
    - coherence
    - faithfulness
    - completeness
    - distinctiveness
    - authenticity
  composite_weights:
    coherence: 0.25
    faithfulness: 0.30
    completeness: 0.20
    distinctiveness: 0.15
    authenticity: 0.10
  alerts:
    enabled: false
    thresholds:
      coherence: 0.75
      composite: 0.75
  goals: {}
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Storage growth | Medium | Low | Aggregation, retention policy |
| Alert fatigue | Medium | Medium | Configurable thresholds, cooldown period |
| Metric noise | Low | Medium | Statistical smoothing, outlier removal |
| Query performance | Low | Low | Indexes, query optimisation |

---

## Research Foundation

- [R-022: Performance Benchmarking Methodology](../../../research/R-022-performance-benchmarking.md)
- [R-024: Cross-Provider Consistency Analysis](../../../research/R-024-cross-provider-consistency.md)

---

## Related Documentation

- [v1.12.0 Milestone](../../milestones/v1.12.0.md)
- [F-106: Quality Metrics Scoring](../completed/F-106-quality-metrics.md)
- [F-136: Performance Baseline Dashboard](F-136-performance-baseline-dashboard.md)
- [F-140: Cost Analytics Dashboard](F-140-cost-analytics-dashboard.md)

---

**Status**: Planned
