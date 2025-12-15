"""
Abstract storage interface for audit records (F-123).

Base class for audit trail storage backends.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Optional

from persona.core.audit.models import AuditRecord


class AuditStore(ABC):
    """Abstract base class for audit record storage."""

    def __init__(self, store_path: Path):
        """Initialise audit store.

        Args:
            store_path: Path to storage location.
        """
        self.store_path = store_path
        self.store_path.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def save(self, record: AuditRecord) -> None:
        """Save an audit record.

        Args:
            record: Audit record to save.
        """
        pass

    @abstractmethod
    def get(self, audit_id: str) -> Optional[AuditRecord]:
        """Retrieve an audit record by ID.

        Args:
            audit_id: Audit record identifier.

        Returns:
            AuditRecord if found, None otherwise.
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def delete(self, audit_id: str) -> bool:
        """Delete an audit record.

        Args:
            audit_id: Audit record identifier.

        Returns:
            True if deleted, False if not found.
        """
        pass

    @abstractmethod
    def prune(self, before_date: datetime) -> int:
        """Delete audit records older than specified date.

        Args:
            before_date: Delete records before this date.

        Returns:
            Number of records deleted.
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """Count total audit records.

        Returns:
            Number of records in storage.
        """
        pass
