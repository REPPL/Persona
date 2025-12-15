"""
Audit trail query and export interface (F-123).

High-level interface for querying and exporting audit records.
"""

import csv
import json
from datetime import datetime
from io import StringIO
from pathlib import Path
from typing import Literal, Optional

from persona.core.audit.logger import AuditLogger
from persona.core.audit.models import AuditConfig, AuditRecord
from persona.core.audit.signing import verify_signature


class AuditTrail:
    """High-level interface for audit trail operations."""

    def __init__(self, config: Optional[AuditConfig] = None):
        """Initialise audit trail interface.

        Args:
            config: Audit configuration (uses defaults if None).
        """
        self.config = config or AuditConfig()
        self.logger = AuditLogger(config)

    def query(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list[AuditRecord]:
        """Query audit records with filtering.

        Args:
            start_date: Filter records after this date.
            end_date: Filter records before this date.
            provider: Filter by provider.
            model: Filter by model.
            limit: Maximum number of records to return.

        Returns:
            List of matching audit records.
        """
        return self.logger.list_records(
            start_date=start_date,
            end_date=end_date,
            provider=provider,
            model=model,
            limit=limit,
        )

    def get(self, audit_id: str) -> Optional[AuditRecord]:
        """Get a specific audit record.

        Args:
            audit_id: Audit record identifier.

        Returns:
            AuditRecord if found, None otherwise.
        """
        return self.logger.get_record(audit_id)

    def verify(self, audit_id: str) -> tuple[bool, Optional[str]]:
        """Verify signature of an audit record.

        Args:
            audit_id: Audit record identifier.

        Returns:
            Tuple of (is_valid, error_message).
        """
        record = self.logger.get_record(audit_id)

        if not record:
            return False, "Record not found"

        if not record.signature:
            return False, "Record is not signed"

        if not self.config.signing_key:
            return False, "No signing key configured"

        is_valid = verify_signature(record, self.config.signing_key)
        return is_valid, None if is_valid else "Signature verification failed"

    def export(
        self,
        format: Literal["json", "csv", "jsonl"] = "json",
        output_path: Optional[Path] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        """Export audit records to file or string.

        Args:
            format: Export format (json, csv, jsonl).
            output_path: Output file path (returns string if None).
            start_date: Filter records after this date.
            end_date: Filter records before this date.
            provider: Filter by provider.
            model: Filter by model.

        Returns:
            Exported data as string (if output_path is None).
        """
        records = self.query(
            start_date=start_date,
            end_date=end_date,
            provider=provider,
            model=model,
        )

        if format == "json":
            output = self._export_json(records)
        elif format == "csv":
            output = self._export_csv(records)
        elif format == "jsonl":
            output = self._export_jsonl(records)
        else:
            raise ValueError(f"Unknown format: {format}")

        if output_path:
            output_path.write_text(output)
            return ""
        return output

    def _export_json(self, records: list[AuditRecord]) -> str:
        """Export records as JSON array.

        Args:
            records: Records to export.

        Returns:
            JSON string.
        """
        data = [json.loads(record.model_dump_json()) for record in records]
        return json.dumps(data, indent=2)

    def _export_jsonl(self, records: list[AuditRecord]) -> str:
        """Export records as JSON Lines.

        Args:
            records: Records to export.

        Returns:
            JSON Lines string.
        """
        lines = [record.model_dump_json() for record in records]
        return "\n".join(lines)

    def _export_csv(self, records: list[AuditRecord]) -> str:
        """Export records as CSV.

        Args:
            records: Records to export.

        Returns:
            CSV string.
        """
        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            "audit_id",
            "timestamp",
            "tool_version",
            "user",
            "platform",
            "provider",
            "model",
            "data_hash",
            "prompt_hash",
            "personas_hash",
            "persona_count",
            "generation_time_ms",
            "has_signature",
        ])

        # Write rows
        for record in records:
            writer.writerow([
                record.audit_id,
                record.timestamp.isoformat(),
                record.tool_version,
                record.session.user,
                record.session.platform,
                record.generation.provider,
                record.generation.model,
                record.input.data_hash[:16] + "...",  # Truncate hash
                record.generation.prompt_hash[:16] + "...",
                record.output.personas_hash[:16] + "...",
                record.output.persona_count,
                record.output.generation_time_ms,
                "yes" if record.signature else "no",
            ])

        return output.getvalue()

    def prune(self, retention_days: Optional[int] = None) -> int:
        """Delete old audit records.

        Args:
            retention_days: Retention period (uses config default if None).

        Returns:
            Number of records deleted.
        """
        return self.logger.prune_old_records(retention_days)

    def count(self) -> int:
        """Count total audit records.

        Returns:
            Number of records in storage.
        """
        return self.logger.store.count()
