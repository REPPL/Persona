"""
SQLite storage backend for audit records (F-123).

Default storage backend using SQLite database.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from persona.core.audit.models import AuditRecord
from persona.core.audit.store import AuditStore


class SqliteStore(AuditStore):
    """SQLite storage backend for audit records."""

    def __init__(self, store_path: Path):
        """Initialise SQLite store.

        Args:
            store_path: Path to storage directory.
        """
        super().__init__(store_path)
        self.db_path = store_path / "audit.db"
        self._init_database()

    def _init_database(self) -> None:
        """Initialise database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_records (
                    audit_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    tool_version TEXT,
                    provider TEXT,
                    model TEXT,
                    data_hash TEXT,
                    prompt_hash TEXT,
                    personas_hash TEXT,
                    record_json TEXT NOT NULL
                )
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_timestamp
                ON audit_records(timestamp)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_provider
                ON audit_records(provider)
            """
            )
            cursor.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_model
                ON audit_records(model)
            """
            )
            conn.commit()

    def save(self, record: AuditRecord) -> None:
        """Save an audit record.

        Args:
            record: Audit record to save.
        """
        record_json = record.model_dump_json()

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO audit_records
                (audit_id, timestamp, tool_version, provider, model,
                 data_hash, prompt_hash, personas_hash, record_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.audit_id,
                    record.timestamp.isoformat(),
                    record.tool_version,
                    record.generation.provider,
                    record.generation.model,
                    record.input.data_hash,
                    record.generation.prompt_hash,
                    record.output.personas_hash,
                    record_json,
                ),
            )
            conn.commit()

    def get(self, audit_id: str) -> Optional[AuditRecord]:
        """Retrieve an audit record by ID.

        Args:
            audit_id: Audit record identifier.

        Returns:
            AuditRecord if found, None otherwise.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT record_json FROM audit_records WHERE audit_id = ?",
                (audit_id,),
            )
            row = cursor.fetchone()

            if row:
                return AuditRecord.model_validate_json(row[0])
            return None

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
        query = "SELECT record_json FROM audit_records WHERE 1=1"
        params: list = []

        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())

        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())

        if provider:
            query += " AND provider = ?"
            params.append(provider)

        if model:
            query += " AND model = ?"
            params.append(model)

        query += " ORDER BY timestamp DESC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [AuditRecord.model_validate_json(row[0]) for row in rows]

    def delete(self, audit_id: str) -> bool:
        """Delete an audit record.

        Args:
            audit_id: Audit record identifier.

        Returns:
            True if deleted, False if not found.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM audit_records WHERE audit_id = ?", (audit_id,))
            conn.commit()
            return cursor.rowcount > 0

    def prune(self, before_date: datetime) -> int:
        """Delete audit records older than specified date.

        Args:
            before_date: Delete records before this date.

        Returns:
            Number of records deleted.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM audit_records WHERE timestamp < ?",
                (before_date.isoformat(),),
            )
            conn.commit()
            return cursor.rowcount

    def count(self) -> int:
        """Count total audit records.

        Returns:
            Number of records in storage.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM audit_records")
            return cursor.fetchone()[0]
