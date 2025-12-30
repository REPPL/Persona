# R-030: Analytics & Usage Tracking

## Executive Summary

This research analyses approaches for privacy-respecting analytics and usage tracking in CLI applications. Analytics enable understanding user patterns, feature adoption, and pain points. Recommended approach: opt-in local analytics with optional anonymised cloud aggregation, following industry best practices for privacy.

---

## Research Context

| Attribute | Value |
|-----------|-------|
| **ID** | R-030 |
| **Category** | Product Insights |
| **Status** | Complete |
| **Priority** | P3 |
| **Informs** | Future analytics features |

---

## Problem Statement

Without analytics, Persona development is blind to:
- Which features are actually used
- Where users encounter errors
- Common usage patterns
- Performance in real-world conditions
- Feature adoption rates

However, analytics must balance insights with privacy, especially for a tool handling potentially sensitive research data.

---

## State of the Art Analysis

### Privacy Models

| Model | Description | Privacy | Insights |
|-------|-------------|---------|----------|
| **No tracking** | No analytics at all | ✅ Maximum | ❌ None |
| **Local only** | Store on user machine | ✅ High | ⚠️ Limited |
| **Opt-in cloud** | User consents to upload | ⚠️ Medium | ✅ Good |
| **Opt-out cloud** | Default on, can disable | ❌ Lower | ✅ Best |
| **Always on** | No user control | ❌ None | ✅ Best |

### Industry Standards

**Homebrew (CLI Analytics):**
- Opt-out model with prominent notice
- Collects: OS, architecture, command, duration
- Excludes: arguments, paths, user data
- Anonymises: hashes machine ID

**VS Code:**
- Separate telemetry levels (off, crash, error, all)
- Detailed privacy documentation
- Machine ID hashed

**npm:**
- Opt-in analytics
- Collects: command, duration, error codes
- Explicit consent prompt

### Data Categories

| Category | Examples | Privacy Risk | Value |
|----------|----------|--------------|-------|
| **Commands** | `generate`, `export` | Low | High |
| **Timing** | Generation latency | Low | High |
| **Errors** | Exception types | Low | High |
| **Environment** | OS, Python version | Low | Medium |
| **Usage patterns** | Feature frequency | Low | High |
| **Content** | Prompts, personas | ❌ High | Low |
| **Paths** | File paths | Medium | Low |
| **User identity** | Username, email | ❌ High | None |

---

## Recommended Approach

### Tiered Analytics

```yaml
analytics:
  level: local  # off, local, anonymised, full

  local:
    enabled: true
    storage: ~/.persona/analytics.db
    retention_days: 90

  cloud:
    enabled: false  # Requires explicit opt-in
    endpoint: https://analytics.persona.dev
    anonymise: true
```

### Data Collection Specification

**Always Collected (local):**
```json
{
  "event": "command_executed",
  "command": "generate",
  "duration_ms": 1234,
  "success": true,
  "timestamp": "2025-01-15T10:30:00Z",
  "version": "1.14.0"
}
```

**Opt-in Cloud (anonymised):**
```json
{
  "machine_id": "sha256:abc123...",  // Hashed, not reversible
  "os": "darwin",
  "python_version": "3.12",
  "event": "command_executed",
  "command": "generate",
  "provider": "anthropic",
  "duration_ms": 1234,
  "success": true
}
```

**Never Collected:**
- File paths
- Prompt content
- Persona data
- API keys
- User identity

### Implementation

```python
from enum import Enum
from dataclasses import dataclass
import hashlib
import sqlite3

class AnalyticsLevel(Enum):
    OFF = "off"
    LOCAL = "local"
    ANONYMISED = "anonymised"
    FULL = "full"

@dataclass
class AnalyticsEvent:
    event_type: str
    command: str | None = None
    duration_ms: int | None = None
    success: bool | None = None
    error_type: str | None = None  # Exception class name only
    provider: str | None = None

class AnalyticsCollector:
    def __init__(self, config: AnalyticsConfig):
        self.config = config
        self.level = config.level

    def track(self, event: AnalyticsEvent) -> None:
        if self.level == AnalyticsLevel.OFF:
            return

        # Always store locally
        self._store_local(event)

        # Optionally send to cloud
        if self.level in (AnalyticsLevel.ANONYMISED, AnalyticsLevel.FULL):
            self._send_cloud(event)

    def _anonymise(self, event: AnalyticsEvent) -> dict:
        """Remove or hash identifying information."""
        return {
            "machine_id": self._hash_machine_id(),
            "os": platform.system(),
            "version": __version__,
            **asdict(event)
        }

    def _hash_machine_id(self) -> str:
        """Create non-reversible machine identifier."""
        raw = f"{platform.node()}:{getpass.getuser()}:{uuid.getnode()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
```

### User Communication

**First Run Notice:**
```
Persona collects anonymous usage analytics to improve the tool.
No personal data, file paths, or content is collected.

Analytics level: local (stored on your machine only)

To change: persona config set analytics.level off
To learn more: https://persona.dev/privacy
```

**Analytics Commands:**
```bash
# View current settings
persona analytics status

# Change level
persona analytics set-level off|local|anonymised

# View local data
persona analytics show

# Export analytics
persona analytics export --output analytics.json

# Clear analytics
persona analytics clear
```

---

## Evaluation

| Approach | Privacy | Insights | Adoption | Complexity |
|----------|---------|----------|----------|------------|
| No tracking | ✅ | ❌ | ✅ | ✅ |
| Local only (recommended start) | ✅ | ⚠️ | ✅ | ⚠️ |
| Opt-in cloud | ⚠️ | ✅ | ⚠️ | ⚠️ |
| Opt-out cloud | ⚠️ | ✅ | ⚠️ | ⚠️ |

---

## Recommendation

**Phase 1:** Local-only analytics
- Store usage data on user's machine
- Provide commands to view/export
- No cloud transmission

**Phase 2:** Optional cloud analytics
- Add opt-in cloud aggregation
- Require explicit consent
- Full anonymisation

**Phase 3:** Analytics dashboard
- Aggregate insights for development
- Public usage statistics (anonymised)

---

## References

1. [Homebrew Analytics](https://docs.brew.sh/Analytics)
2. [VS Code Telemetry](https://code.visualstudio.com/docs/getstarted/telemetry)
3. [GDPR Compliance for Analytics](https://gdpr.eu/)
4. [Plausible Analytics](https://plausible.io/) - Privacy-focused example

---

## Related Documentation

- [ADR-0016: AI Transparency Commitment](../decisions/adrs/ADR-0016-ai-transparency.md)
- [F-140: Cost Analytics Dashboard](../roadmap/features/planned/F-140-cost-analytics-dashboard.md)

---

**Status**: Complete
