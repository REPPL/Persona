"""
JSON storage backend for audit records (F-123).

Alternative storage backend using JSON files.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from persona.core.audit.models import AuditRecord
from persona.core.audit.store import AuditStore


class JsonStore(AuditStore):
    """JSON file storage backend for audit records."""

    def __init__(self, store_path: Path):
        """Initialise JSON store.

        Args:
            store_path: Path to storage directory.
        """
        super().__init__(store_path)
        self.records_dir = store_path / "records"
        self.records_dir.mkdir(parents=True, exist_ok=True)

    def _get_record_path(self, audit_id: str) -> Path:
        """Get path for a record file.

        Args:
            audit_id: Audit record identifier.

        Returns:
            Path to record JSON file.
        """
        return self.records_dir / f"{audit_id}.json"

    def save(self, record: AuditRecord) -> None:
        """Save an audit record.

        Args:
            record: Audit record to save.
        """
        record_path = self._get_record_path(record.audit_id)
        record_data = json.loads(record.model_dump_json())

        with open(record_path, "w") as f:
            json.dump(record_data, f, indent=2)

    def get(self, audit_id: str) -> Optional[AuditRecord]:
        """Retrieve an audit record by ID.

        Args:
            audit_id: Audit record identifier.

        Returns:
            AuditRecord if found, None otherwise.
        """
        record_path = self._get_record_path(audit_id)

        if not record_path.exists():
            return None

        with open(record_path) as f:
            data = json.load(f)
            return AuditRecord.model_validate(data)

    def list(
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
        records = []

        for record_path in self.records_dir.glob("*.json"):
            try:
                with open(record_path) as f:
                    data = json.load(f)
                    record = AuditRecord.model_validate(data)

                    # Apply filters
                    if start_date and record.timestamp < start_date:
                        continue
                    if end_date and record.timestamp > end_date:
                        continue
                    if provider and record.generation.provider != provider:
                        continue
                    if model and record.generation.model != model:
                        continue

                    records.append(record)
            except (json.JSONDecodeError, ValueError):
                # Skip invalid records
                continue

        # Sort by timestamp descending
        records.sort(key=lambda r: r.timestamp, reverse=True)

        if limit:
            records = records[:limit]

        return records

    def delete(self, audit_id: str) -> bool:
        """Delete an audit record.

        Args:
            audit_id: Audit record identifier.

        Returns:
            True if deleted, False if not found.
        """
        record_path = self._get_record_path(audit_id)

        if record_path.exists():
            record_path.unlink()
            return True
        return False

    def prune(self, before_date: datetime) -> int:
        """Delete audit records older than specified date.

        Args:
            before_date: Delete records before this date.

        Returns:
            Number of records deleted.
        """
        deleted_count = 0

        for record_path in self.records_dir.glob("*.json"):
            try:
                with open(record_path) as f:
                    data = json.load(f)
                    timestamp_str = data.get("timestamp")
                    if timestamp_str:
                        timestamp = datetime.fromisoformat(timestamp_str)
                        if timestamp < before_date:
                            record_path.unlink()
                            deleted_count += 1
            except (json.JSONDecodeError, ValueError):
                # Skip invalid records
                continue

        return deleted_count

    def count(self) -> int:
        """Count total audit records.

        Returns:
            Number of records in storage.
        """
        return len(list(self.records_dir.glob("*.json")))
