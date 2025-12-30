# F-138: Batch Generation Progress Tracking

## Overview

| Attribute | Value |
|-----------|-------|
| **Feature ID** | F-138 |
| **Title** | Batch Generation Progress Tracking |
| **Priority** | P1 (High) |
| **Category** | UX |
| **Milestone** | [v1.12.0](../../milestones/v1.12.0.md) |
| **Status** | 📋 Planned |
| **Dependencies** | F-088 (Async Generation), F-078 (Cost Tracking) |

---

## Problem Statement

When generating multiple personas with `persona generate -n 10`, users currently see:
- A single progress bar for the entire batch
- No visibility into individual persona progress
- No ETA based on actual generation times
- No ability to pause/resume long-running batches
- No cost projection updates as generation progresses

For large batch operations (50+ personas), this lack of visibility creates uncertainty and prevents users from making informed decisions about continuing or stopping generation.

---

## Design Approach

### Core Concept

Provide granular, real-time progress information for batch generation operations with pause/resume capability and dynamic cost projection.

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 Batch Progress System                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │   Batch      │───▶│   Progress   │───▶│   Display    │  │
│  │  Orchestrator│    │   Tracker    │    │   Renderer   │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                   │                   │           │
│         ▼                   ▼                   ▼           │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  Generation  │    │    State     │    │   Console    │  │
│  │   Workers    │    │   Manager    │    │   or TUI     │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│                             │                               │
│                             ▼                               │
│                      ┌──────────────┐                       │
│                      │  Checkpoint  │                       │
│                      │    File      │                       │
│                      └──────────────┘                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Progress States

| State | Description | Symbol |
|-------|-------------|--------|
| `pending` | Queued for generation | ⏳ |
| `generating` | Currently being generated | 🔄 |
| `validating` | Undergoing quality validation | 🔍 |
| `completed` | Successfully generated | ✅ |
| `failed` | Generation failed | ❌ |
| `retrying` | Failed, attempting retry | 🔁 |
| `paused` | User paused generation | ⏸️ |

---

## Key Capabilities

### 1. Per-Persona Progress Display

Show individual status for each persona in the batch.

```bash
# Enable detailed progress
persona generate --from data/ -n 10 --progress detailed
```

**Console Output:**
```
Batch Generation Progress
═════════════════════════════════════════════════════════════

Overall: [████████░░░░░░░░░░░░] 40% (4/10) │ ETA: 2m 15s

Per-Persona Status:
┌────┬──────────────────┬──────────┬─────────┬──────────────┐
│ #  │ ID               │ Status   │ Time    │ Quality      │
├────┼──────────────────┼──────────┼─────────┼──────────────┤
│ 1  │ persona-a1b2c3   │ ✅ Done  │ 12.3s   │ 0.89         │
│ 2  │ persona-d4e5f6   │ ✅ Done  │ 11.8s   │ 0.92         │
│ 3  │ persona-g7h8i9   │ ✅ Done  │ 13.1s   │ 0.87         │
│ 4  │ persona-j0k1l2   │ ✅ Done  │ 12.5s   │ 0.91         │
│ 5  │ persona-m3n4o5   │ 🔄 Gen   │ 8.2s... │ --           │
│ 6  │ persona-p6q7r8   │ ⏳ Queue │ --      │ --           │
│ 7  │ persona-s9t0u1   │ ⏳ Queue │ --      │ --           │
│ 8  │ persona-v2w3x4   │ ⏳ Queue │ --      │ --           │
│ 9  │ persona-y5z6a7   │ ⏳ Queue │ --      │ --           │
│ 10 │ persona-b8c9d0   │ ⏳ Queue │ --      │ --           │
└────┴──────────────────┴──────────┴─────────┴──────────────┘

Cost: $0.48 spent │ $0.72 projected total
Press [P] to pause, [Q] to quit
```

### 2. ETA Estimation

Calculate remaining time based on actual generation performance.

```python
class ETAEstimator:
    def __init__(self, window_size: int = 5):
        self.times: list[float] = []
        self.window_size = window_size

    def record(self, duration: float) -> None:
        self.times.append(duration)
        if len(self.times) > self.window_size:
            self.times.pop(0)

    def estimate_remaining(self, remaining_count: int) -> float:
        if not self.times:
            return 0.0
        avg_time = sum(self.times) / len(self.times)
        return avg_time * remaining_count
```

**ETA Display:**
- Updates after each persona completion
- Shows range for high variance (e.g., "2-4 minutes")
- Accounts for parallel generation

### 3. Pause/Resume Capability

Allow users to pause long-running batches and resume later.

```bash
# Start batch generation (interruptible)
persona generate --from data/ -n 50 --checkpoint batch-50.json

# Press Ctrl+C or 'P' to pause
# Saves state to checkpoint file

# Resume from checkpoint
persona generate --resume batch-50.json
```

**Checkpoint Format:**
```json
{
  "batch_id": "batch-2025-01-15-abc123",
  "created_at": "2025-01-15T10:30:00Z",
  "paused_at": "2025-01-15T10:35:00Z",
  "config": {
    "source_data": "data/",
    "total_count": 50,
    "provider": "anthropic"
  },
  "progress": {
    "completed": 15,
    "failed": 1,
    "pending": 34
  },
  "completed_personas": ["persona-a1b2c3", "persona-d4e5f6", ...],
  "failed_personas": [
    {"id": "persona-x1y2z3", "error": "Rate limit exceeded", "retries": 3}
  ],
  "cost_so_far": 1.23
}
```

### 4. Failure Handling with Retry

Automatically retry failed generations with configurable policy.

```bash
# Configure retry behaviour
persona generate --from data/ -n 10 \
  --retry-count 3 \
  --retry-delay 5
```

**Retry Policy:**
```yaml
batch:
  retry:
    max_attempts: 3
    delay_seconds: 5
    backoff_multiplier: 2  # exponential backoff
    retryable_errors:
      - rate_limit
      - timeout
      - server_error
```

**Console Display for Failures:**
```
⚠️ Persona #7 failed: Rate limit exceeded
   Retry 1/3 in 5s...
   Retry 2/3 in 10s...
   ✅ Succeeded on retry 2
```

### 5. Cost Projection Updates

Show real-time cost tracking and projection.

```
Cost Tracking
─────────────
Spent:     $0.48 (4 personas)
Per unit:  $0.12 avg
Projected: $1.20 total
Budget:    $2.00
Remaining: $0.80 after completion
```

```bash
# Set budget limit
persona generate --from data/ -n 20 --budget 5.00

# Stop if budget exceeded
persona generate --from data/ -n 20 --budget 5.00 --stop-on-budget
```

---

## CLI Commands

```bash
# Basic batch generation with progress
persona generate --from data/ -n 10

# Detailed progress display
persona generate --from data/ -n 10 --progress detailed

# Quiet mode (minimal output)
persona generate --from data/ -n 10 --progress quiet

# With checkpoint for pause/resume
persona generate --from data/ -n 50 --checkpoint my-batch.json

# Resume from checkpoint
persona generate --resume my-batch.json

# With retry configuration
persona generate --from data/ -n 10 --retry-count 3 --retry-delay 5

# With budget limit
persona generate --from data/ -n 20 --budget 5.00

# List active/paused batches
persona batch list

# Cancel a paused batch
persona batch cancel my-batch.json
```

---

## Implementation Tasks

### Phase 1: Progress Tracking Infrastructure
- [ ] Create `BatchProgress` class with per-item tracking
- [ ] Implement progress state machine
- [ ] Add event emitter for status changes
- [ ] Create progress storage/serialisation

### Phase 2: Display Rendering
- [ ] Implement Rich-based progress display
- [ ] Create detailed view with per-persona table
- [ ] Add compact/quiet display modes
- [ ] Implement keyboard interrupt handling

### Phase 3: ETA Estimation
- [ ] Create `ETAEstimator` with rolling average
- [ ] Add variance tracking for range display
- [ ] Implement parallel generation awareness
- [ ] Add historical baseline integration

### Phase 4: Checkpoint/Resume
- [ ] Design checkpoint file format
- [ ] Implement checkpoint writing on pause
- [ ] Create resume logic with state validation
- [ ] Add `--checkpoint` and `--resume` CLI options

### Phase 5: Retry Logic
- [ ] Implement retry policy configuration
- [ ] Add exponential backoff
- [ ] Create retryable error classification
- [ ] Add retry status display

### Phase 6: Cost Projection
- [ ] Integrate with existing cost tracking
- [ ] Implement per-persona cost recording
- [ ] Add projection calculation
- [ ] Create budget limit enforcement

---

## Success Criteria

- [ ] Individual persona progress visible during batch
- [ ] ETA updates based on actual generation times
- [ ] Pause/resume works with checkpoint files
- [ ] Failed generations automatically retry (configurable)
- [ ] Cost projection updates in real-time
- [ ] Budget limits can stop generation
- [ ] Progress modes: detailed, compact, quiet
- [ ] Test coverage >= 85%

---

## Configuration

```yaml
# persona.yaml
batch:
  progress:
    mode: detailed  # detailed, compact, quiet
    refresh_rate: 0.5  # seconds
  checkpoint:
    auto_save: true
    save_interval: 30  # seconds
    directory: .persona/checkpoints
  retry:
    max_attempts: 3
    delay_seconds: 5
    backoff_multiplier: 2
    retryable_errors:
      - rate_limit
      - timeout
      - server_error
  cost:
    track_per_persona: true
    budget_enforcement: warn  # warn, stop
```

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Checkpoint corruption | Low | High | Atomic writes, validation on load |
| ETA inaccuracy | Medium | Low | Range display, "approximately" language |
| Retry storms | Low | Medium | Exponential backoff, circuit breaker |
| Display performance | Low | Low | Throttled updates, efficient rendering |

---

## Related Documentation

- [v1.12.0 Milestone](../../milestones/v1.12.0.md)
- [F-088: Async Generation](../completed/F-088-async-generation.md)
- [F-078: Cost Tracking](../completed/F-078-cost-tracking.md)
- [F-140: Cost Analytics Dashboard](F-140-cost-analytics-dashboard.md)

---

**Status**: Planned
