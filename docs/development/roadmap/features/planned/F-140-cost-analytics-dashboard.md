# F-140: Cost Analytics Dashboard

## Overview

| Attribute | Value |
|-----------|-------|
| **Feature ID** | F-140 |
| **Title** | Cost Analytics Dashboard |
| **Priority** | P1 (High) |
| **Category** | Observability |
| **Milestone** | [v1.12.0](../../milestones/v1.12.0.md) |
| **Status** | 📋 Planned |
| **Dependencies** | F-078 (Cost Tracking), F-098 (TUI Dashboard) |

---

## Problem Statement

Persona tracks costs per generation but lacks:
- Historical cost analysis and trends
- Budget planning and forecasting
- Per-provider cost breakdown
- Per-experiment cost attribution
- Proactive budget alerts
- Cost optimisation recommendations

Users managing budgets need visibility into spending patterns to make informed decisions about provider selection, generation frequency, and budget allocation.

---

## Design Approach

### Core Concept

Provide comprehensive cost analytics with historical tracking, forecasting, and actionable optimisation recommendations.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Cost Analytics System                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Generation  │───▶│    Cost      │───▶│  Analytics   │  │
│  │   Events     │    │    Store     │    │   Engine     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                             │                   │           │
│                             ▼                   ▼           │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    Cost Metrics                       │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │  │
│  │  │  Daily   │  │ Provider │  │Experiment│  ...      │  │
│  │  │  Totals  │  │ Breakdown│  │  Costs   │           │  │
│  │  └──────────┘  └──────────┘  └──────────┘           │  │
│  └──────────────────────────────────────────────────────┘  │
│                             │                               │
│         ┌───────────────────┼───────────────────┐          │
│         ▼                   ▼                   ▼          │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Forecasts  │    │    Alerts    │    │Optimisation │  │
│  │              │    │              │    │   Advice    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Storage Schema

```sql
CREATE TABLE cost_records (
    id INTEGER PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    provider TEXT NOT NULL,
    model TEXT NOT NULL,
    experiment_id TEXT,
    operation TEXT NOT NULL,  -- generation, validation, etc.
    input_tokens INTEGER,
    output_tokens INTEGER,
    cost_usd REAL NOT NULL,
    persona_count INTEGER DEFAULT 1
);

CREATE INDEX idx_cost_time ON cost_records(timestamp);
CREATE INDEX idx_cost_provider ON cost_records(provider);
CREATE INDEX idx_cost_experiment ON cost_records(experiment_id);
```

---

## Key Capabilities

### 1. Cost History

View historical cost data with flexible time ranges.

```bash
# View last 30 days
persona cost history

# Specific time range
persona cost history --days 90

# Filter by provider
persona cost history --provider anthropic

# Filter by experiment
persona cost history --experiment user-research-2025
```

**Console Output:**
```
Cost History (Last 30 Days)
═════════════════════════════════════════════════════════════

Daily Cost Trend
$50 │                              ╭─╮
    │                         ╭────╯ │
$40 │              ╭──────────╯      │
    │         ╭────╯                 ╰──╮
$30 │    ╭────╯                         ╰───
    │────╯
$20 │
    └────────────────────────────────────────
     Week 1    Week 2    Week 3    Week 4

Summary
───────
Total Spent:    $987.45
Daily Average:  $32.91
Personas Gen:   2,847
Cost/Persona:   $0.35 avg
```

### 2. Cost Breakdown

Analyse costs by different dimensions.

```bash
# Breakdown by provider
persona cost breakdown --by provider

# Breakdown by experiment
persona cost breakdown --by experiment

# Breakdown by model
persona cost breakdown --by model

# Breakdown by time period
persona cost breakdown --by week
```

**Output:**
```
Cost Breakdown by Provider (Last 30 Days)
═════════════════════════════════════════════════════════════

┌───────────┬───────────┬──────────┬──────────────┬──────────┐
│ Provider  │ Cost      │ Share    │ Personas     │ $/Persona│
├───────────┼───────────┼──────────┼──────────────┼──────────┤
│ anthropic │ $654.32   │ 66.2%    │ 1,456        │ $0.45    │
│ openai    │ $298.76   │ 30.2%    │ 1,247        │ $0.24    │
│ ollama    │ $34.37    │ 3.5%     │ 144          │ $0.24    │
└───────────┴───────────┴──────────┴──────────────┴──────────┘

Total: $987.45 across 2,847 personas
```

### 3. Cost Forecasting

Predict future costs based on historical patterns.

```bash
# Forecast next 7 days
persona cost forecast

# Forecast with specific horizon
persona cost forecast --days 30

# Forecast with budget context
persona cost forecast --budget 500
```

**Output:**
```
Cost Forecast (Next 7 Days)
═════════════════════════════════════════════════════════════

Based on last 30 days of activity:

┌─────────────┬──────────┬──────────┬──────────┐
│ Period      │ Low Est. │ Expected │ High Est.│
├─────────────┼──────────┼──────────┼──────────┤
│ Tomorrow    │ $28.50   │ $32.91   │ $38.20   │
│ Next 3 days │ $85.50   │ $98.73   │ $114.60  │
│ Next 7 days │ $199.50  │ $230.37  │ $267.40  │
└─────────────┴──────────┴──────────┴──────────┘

Budget Impact
─────────────
Monthly Budget: $500.00
Spent This Month: $423.12
Forecast Remaining: $230.37
Status: ⚠️ May exceed budget by ~$153

Recommendation: Consider using hybrid mode to reduce costs
```

### 4. Budget Alerts

Configure proactive budget notifications.

```bash
# Set monthly budget
persona cost budget set --monthly 500

# Set daily limit
persona cost budget set --daily 50

# Set per-experiment budget
persona cost budget set --experiment user-research --limit 200

# Enable alerts
persona cost alerts enable

# View budget status
persona cost budget status
```

**Configuration:**
```yaml
cost:
  budgets:
    monthly: 500.00
    daily: 50.00
    experiments:
      user-research-2025: 200.00
  alerts:
    enabled: true
    thresholds:
      - percent: 50
        action: log
      - percent: 80
        action: warn
      - percent: 100
        action: stop  # or warn
    notification: console  # console, webhook (future)
```

**Alert Example:**
```
⚠️ Budget Alert: Monthly spend has reached 80% ($400.00 of $500.00)
   Projected to exceed budget in 6 days at current rate.
   Run 'persona cost forecast' for details.
```

### 5. Cost Optimisation Recommendations

Get actionable advice to reduce costs.

```bash
# View recommendations
persona cost optimise

# Get detailed analysis
persona cost optimise --verbose
```

**Output:**
```
Cost Optimisation Recommendations
═════════════════════════════════════════════════════════════

Based on your usage patterns:

1. Switch to Hybrid Mode for Batch Operations
   ─────────────────────────────────────────
   Current: 100% frontier for batches of 10+
   Recommended: Enable hybrid mode
   Potential Savings: $127.45/month (19%)

   Run: persona config set hybrid.enabled true

2. Use Smaller Model for Low-Complexity Personas
   ─────────────────────────────────────────────
   Current: claude-sonnet-4-20250514 for all generations
   Recommended: claude-haiku for simple personas
   Potential Savings: $89.32/month (13%)

   Complexity threshold: coherence_target < 0.8

3. Enable Response Caching
   ───────────────────────
   Detected: 23% similar prompt patterns
   Recommended: Enable semantic caching
   Potential Savings: $45.67/month (7%)

   Run: persona config set cache.semantic.enabled true

Total Potential Savings: $262.44/month (39%)
```

### 6. TUI Dashboard Integration

Display cost analytics in the TUI dashboard.

```bash
# Launch TUI with cost panel
persona tui --panel cost
```

**TUI Display:**
```
┌─ Cost Analytics ─────────────────────────────────────────────┐
│                                                               │
│  Today: $32.45    This Week: $187.23    This Month: $423.12  │
│                                                               │
│  ┌─ Daily Trend (7d) ────────────────────────────────────┐   │
│  │ $50│        ╭─╮                                       │   │
│  │    │   ╭────╯ ╰──╮                                    │   │
│  │ $30│───╯         ╰────                                │   │
│  │    └──────────────────                                │   │
│  │      M   T   W   T   F   S   S                        │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                               │
│  Budget: $423.12 / $500.00 (84.6%) ████████████████░░░       │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## CLI Commands

```bash
# Cost history
persona cost history [--days N] [--provider NAME] [--experiment NAME]
persona cost history --format csv --output costs.csv

# Cost breakdown
persona cost breakdown --by provider|experiment|model|week|month

# Cost forecasting
persona cost forecast [--days N] [--budget N]

# Budget management
persona cost budget set --monthly|--daily|--experiment N
persona cost budget status
persona cost budget clear

# Alerts
persona cost alerts enable|disable
persona cost alerts list

# Optimisation
persona cost optimise [--verbose]

# Export
persona cost export [--format csv|json] [--output FILE]
```

---

## Implementation Tasks

### Phase 1: Storage Infrastructure
- [ ] Create cost records SQLite schema
- [ ] Implement `CostStore` class
- [ ] Add automatic recording during generation
- [ ] Create migration for existing cost data

### Phase 2: History & Breakdown
- [ ] Implement time-series queries
- [ ] Create aggregation by dimension
- [ ] Add Rich table formatters
- [ ] Implement `persona cost history` command
- [ ] Implement `persona cost breakdown` command

### Phase 3: Forecasting
- [ ] Implement trend analysis algorithm
- [ ] Create confidence interval calculation
- [ ] Add budget impact projection
- [ ] Implement `persona cost forecast` command

### Phase 4: Budget & Alerts
- [ ] Create budget configuration schema
- [ ] Implement threshold monitoring
- [ ] Add alert actions (log, warn, stop)
- [ ] Create `persona cost budget` commands
- [ ] Create `persona cost alerts` commands

### Phase 5: Optimisation Engine
- [ ] Implement usage pattern analysis
- [ ] Create recommendation rules
- [ ] Calculate potential savings
- [ ] Implement `persona cost optimise` command

### Phase 6: TUI Integration
- [ ] Create cost dashboard panel
- [ ] Implement sparkline charts
- [ ] Add budget progress bar
- [ ] Integrate with existing TUI

### Phase 7: Export & Reporting
- [ ] Implement CSV export
- [ ] Implement JSON export
- [ ] Add filtering options
- [ ] Create scheduled export capability

---

## Success Criteria

- [ ] Cost history viewable for configurable time periods
- [ ] Breakdown available by provider, experiment, model, time
- [ ] 7-day forecast with confidence intervals
- [ ] Budget alerts trigger at configured thresholds
- [ ] At least 3 optimisation recommendations generated
- [ ] TUI displays cost analytics panel
- [ ] CSV/JSON export available
- [ ] Test coverage >= 85%

---

## Configuration

```yaml
# persona.yaml
cost:
  tracking:
    enabled: true
    retention_days: 365
  budgets:
    monthly: null  # No limit by default
    daily: null
    experiments: {}
  alerts:
    enabled: false
    thresholds:
      - percent: 80
        action: warn
      - percent: 100
        action: warn
  optimisation:
    analyse_interval: weekly
    recommendations:
      hybrid_mode: true
      model_selection: true
      caching: true
  export:
    auto_export: false
    format: csv
    directory: ./cost-reports
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Forecast inaccuracy | Medium | Low | Confidence intervals, disclaimers |
| Storage growth | Low | Low | Aggregation, retention policy |
| Alert fatigue | Medium | Medium | Configurable thresholds, cooldown |
| Stale recommendations | Low | Low | Recalculate on demand, date stamps |

---

## Research Foundation

- [R-023: Caching Strategies for LLM Responses](../../../research/R-023-caching-strategies.md)

---

## Related Documentation

- [v1.12.0 Milestone](../../milestones/v1.12.0.md)
- [F-078: Cost Tracking](../completed/F-078-cost-tracking.md)
- [F-136: Performance Baseline Dashboard](F-136-performance-baseline-dashboard.md)
- [F-137: Quality Trend Dashboard](F-137-quality-trend-dashboard.md)
- [F-138: Batch Generation Progress Tracking](F-138-batch-progress-tracking.md)

---

**Status**: Planned
