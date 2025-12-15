"""
Audit logger for persona generation (F-123).

Main interface for recording audit trails during generation.
"""

import hashlib
import json
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from persona.core.audit.json_store import JsonStore
from persona.core.audit.models import (
    AuditConfig,
    AuditRecord,
    GenerationRecord,
    InputRecord,
    OutputRecord,
    SessionInfo,
)
from persona.core.audit.signing import sign_record
from persona.core.audit.sqlite_store import SqliteStore
from persona.core.audit.store import AuditStore


class AuditLogger:
    """Logger for persona generation audit trails."""

    def __init__(self, config: Optional[AuditConfig] = None):
        """Initialise audit logger.

        Args:
            config: Audit configuration (uses defaults if None).
        """
        self.config = config or AuditConfig()
        self._store: Optional[AuditStore] = None
        self._session_info = SessionInfo.capture_current()

    @property
    def store(self) -> AuditStore:
        """Get storage backend (lazy initialisation).

        Returns:
            Configured audit store.
        """
        if self._store is None:
            store_path = self.config.get_store_path()

            if self.config.store_type == "sqlite":
                self._store = SqliteStore(store_path)
            elif self.config.store_type == "json":
                self._store = JsonStore(store_path)
            else:
                raise ValueError(f"Unknown store type: {self.config.store_type}")

        return self._store

    @staticmethod
    def hash_data(data: Any) -> str:
        """Generate SHA-256 hash of data.

        Args:
            data: Data to hash (str, bytes, or JSON-serialisable).

        Returns:
            Hexadecimal hash string.
        """
        if isinstance(data, bytes):
            content = data
        elif isinstance(data, str):
            content = data.encode("utf-8")
        else:
            # JSON-serialise for consistent hashing
            content = json.dumps(data, sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            )

        return hashlib.sha256(content).hexdigest()

    def log_generation(
        self,
        # Input data
        data: Any,
        data_path: Optional[Path] = None,
        record_count: int = 0,
        data_format: Optional[str] = None,
        # Generation parameters
        provider: str = "",
        model: str = "",
        parameters: Optional[dict[str, Any]] = None,
        prompt: str = "",
        workflow: Optional[str] = None,
        template: Optional[str] = None,
        # Output data
        personas: Any = None,
        output_path: Optional[Path] = None,
        persona_count: int = 0,
        generation_time_ms: int = 0,
        tokens_used: Optional[dict[str, int]] = None,
    ) -> AuditRecord:
        """Log a persona generation session.

        Args:
            data: Input data (for hashing).
            data_path: Path to input data file.
            record_count: Number of input records.
            data_format: Data format (csv, json, etc).
            provider: AI provider name.
            model: Model identifier.
            parameters: Generation parameters.
            prompt: Prompt template (for hashing).
            workflow: Workflow name.
            template: Template name.
            personas: Generated personas (for hashing).
            output_path: Path to output directory.
            persona_count: Number of personas generated.
            generation_time_ms: Generation time in milliseconds.
            tokens_used: Token usage statistics.

        Returns:
            Created audit record.
        """
        if not self.config.enabled:
            # Return minimal record when disabled
            return AuditRecord(
                audit_id="disabled",
                tool_version="unknown",
                session=self._session_info,
                input=InputRecord(
                    data_hash="", data_path=None, record_count=0, format=None
                ),
                generation=GenerationRecord(
                    provider="", model="", parameters={}, prompt_hash=""
                ),
                output=OutputRecord(
                    personas_hash="",
                    output_path=None,
                    persona_count=0,
                    generation_time_ms=0,
                ),
            )

        # Generate audit ID
        audit_id = str(uuid.uuid4())

        # Get tool version
        try:
            from persona import __version__

            tool_version = __version__
        except ImportError:
            tool_version = "unknown"

        # Hash input data
        data_hash = self.hash_data(data) if data is not None else ""

        # Hash prompt
        prompt_hash = self.hash_data(prompt) if prompt else ""

        # Hash personas
        personas_hash = self.hash_data(personas) if personas is not None else ""

        # Create audit record
        record = AuditRecord(
            audit_id=audit_id,
            timestamp=datetime.utcnow(),
            tool_version=tool_version,
            session=self._session_info,
            input=InputRecord(
                data_hash=data_hash,
                data_path=str(data_path) if data_path else None,
                record_count=record_count,
                format=data_format,
            ),
            generation=GenerationRecord(
                provider=provider,
                model=model,
                parameters=parameters or {},
                prompt_hash=prompt_hash,
                workflow=workflow,
                template=template,
            ),
            output=OutputRecord(
                personas_hash=personas_hash,
                output_path=str(output_path) if output_path else None,
                persona_count=persona_count,
                generation_time_ms=generation_time_ms,
                tokens_used=tokens_used,
            ),
        )

        # Sign record if enabled
        if self.config.sign_records and self.config.signing_key:
            record.signature = sign_record(record, self.config.signing_key)

        # Save to store
        self.store.save(record)

        return record

    def get_record(self, audit_id: str) -> Optional[AuditRecord]:
        """Retrieve audit record by ID.

        Args:
            audit_id: Audit record identifier.

        Returns:
            AuditRecord if found, None otherwise.
        """
        return self.store.get(audit_id)

    def list_records(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list[AuditRecord]:
        """List audit records with optional filtering.

        Args:
            start_date: Filter records after this date.
            end_date: Filter records before this date.
            provider: Filter by provider.
            model: Filter by model.
            limit: Maximum number of records to return.

        Returns:
            List of matching audit records.
        """
        return self.store.list(
            start_date=start_date,
            end_date=end_date,
            provider=provider,
            model=model,
            limit=limit,
        )

    def prune_old_records(self, retention_days: Optional[int] = None) -> int:
        """Delete audit records older than retention period.

        Args:
            retention_days: Retention period (uses config default if None).

        Returns:
            Number of records deleted.
        """
        from datetime import timedelta

        days = retention_days or self.config.retention_days
        cutoff_date = datetime.utcnow().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        cutoff_date = cutoff_date - timedelta(days=days)

        return self.store.prune(cutoff_date)
