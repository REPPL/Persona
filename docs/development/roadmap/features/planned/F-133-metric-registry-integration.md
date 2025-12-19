# F-133: Quality Metric Registry Integration

**Milestone:** v1.11.0 - Code Quality & Architecture

**Category:** Architecture

**Priority:** Medium

---

## Problem Statement

QualityScorer hard-codes metric instantiation in `__init__`:

```python
self._completeness = CompletenessMetric(self.config)
self._consistency = ConsistencyMetric(self.config)
# ... etc
```

This creates issues:
- Adding new metrics requires modifying QualityScorer
- Cannot dynamically load metrics via plugin system
- Hard-coded dependencies prevent testing alternative implementations
- MetricRegistry exists but isn't used

---

## Solution

Use registry pattern for metrics:

```python
class QualityScorer:
    def __init__(
        self,
        config: QualityConfig,
        registry: MetricRegistry | None = None,
    ) -> None:
        self.config = config
        self.registry = registry or MetricRegistry.default()
        self._metrics = self.registry.get_all_metrics(config)
```

---

## Implementation Tasks

- [ ] Update MetricRegistry with `get_all_metrics()` method
- [ ] Modify QualityScorer to accept registry parameter
- [ ] Remove hard-coded metric instantiation
- [ ] Add metric discovery via registry
- [ ] Enable custom metric registration
- [ ] Update tests for new pattern

---

## Success Criteria

- [ ] QualityScorer uses registry for metric discovery
- [ ] New metrics can be added without modifying QualityScorer
- [ ] Custom metrics can be registered via plugins
- [ ] No regression in existing functionality

---

## Dependencies

- F-107 (Plugin System) - leverages existing plugin infrastructure

---

## Related Documentation

- [v1.11.0 Milestone](../../milestones/v1.11.0.md)
- [F-106 Quality Metrics](../completed/F-106-quality-metrics.md)

---

**Status**: Planned
