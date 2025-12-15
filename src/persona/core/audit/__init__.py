"""
Generation audit trail for EU AI Act compliance (F-123).

Provides comprehensive audit logging for persona generation with:
- SHA-256 hashing of inputs, prompts, and outputs
- 180-day retention (EU AI Act compliant)
- SQLite (default) and JSON storage backends
- Optional HMAC-SHA256 signing for record integrity
- Query and export capabilities
"""

from persona.core.audit.logger import AuditLogger
from persona.core.audit.models import (
    AuditConfig,
    AuditRecord,
    GenerationRecord,
    InputRecord,
    OutputRecord,
    SessionInfo,
)
from persona.core.audit.store import AuditStore
from persona.core.audit.trail import AuditTrail

__all__ = [
    "AuditLogger",
    "AuditTrail",
    "AuditStore",
    "AuditConfig",
    "AuditRecord",
    "SessionInfo",
    "InputRecord",
    "GenerationRecord",
    "OutputRecord",
]
