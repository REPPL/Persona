"""
Audit trail data models (F-123).

Pydantic models for audit records and configuration.
"""

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class SessionInfo(BaseModel):
    """Session information for audit record."""

    user: str = Field(..., description="Username from environment")
    platform: str = Field(..., description="Operating system platform")
    python_version: str = Field(..., description="Python version")

    @classmethod
    def capture_current(cls) -> "SessionInfo":
        """Capture current session information.

        Returns:
            SessionInfo with current environment details.
        """
        import getpass
        import platform

        return cls(
            user=getpass.getuser(),
            platform=platform.system(),
            python_version=sys.version.split()[0],
        )


class InputRecord(BaseModel):
    """Input data record for audit."""

    data_hash: str = Field(..., description="SHA-256 hash of input data")
    data_path: Optional[str] = Field(None, description="Path to data file")
    record_count: int = Field(..., description="Number of input records")
    format: Optional[str] = Field(None, description="Data format (csv, json, etc)")


class GenerationRecord(BaseModel):
    """Generation parameters record for audit."""

    provider: str = Field(..., description="AI provider (anthropic, openai, etc)")
    model: str = Field(..., description="Model identifier")
    parameters: dict[str, Any] = Field(
        default_factory=dict, description="Generation parameters"
    )
    prompt_hash: str = Field(..., description="SHA-256 hash of prompt template")
    workflow: Optional[str] = Field(None, description="Workflow used")
    template: Optional[str] = Field(None, description="Template used")


class OutputRecord(BaseModel):
    """Output record for audit."""

    personas_hash: str = Field(..., description="SHA-256 hash of generated personas")
    output_path: Optional[str] = Field(None, description="Path to output directory")
    persona_count: int = Field(..., description="Number of personas generated")
    generation_time_ms: int = Field(..., description="Generation time in milliseconds")
    tokens_used: Optional[dict[str, int]] = Field(
        None, description="Token usage (input, output)"
    )


class AuditRecord(BaseModel):
    """Complete audit record for a generation session."""

    audit_id: str = Field(..., description="Unique audit record identifier")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC), description="UTC timestamp"
    )
    tool_version: str = Field(..., description="Persona version")
    session: SessionInfo = Field(..., description="Session information")
    input: InputRecord = Field(..., description="Input data record")
    generation: GenerationRecord = Field(..., description="Generation parameters")
    output: OutputRecord = Field(..., description="Output record")
    signature: Optional[str] = Field(None, description="HMAC-SHA256 signature")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class AuditConfig(BaseModel):
    """Configuration for audit trail."""

    enabled: bool = Field(default=True, description="Enable audit trail")
    store_type: Literal["sqlite", "json"] = Field(
        default="sqlite", description="Storage backend type"
    )
    store_path: Optional[Path] = Field(
        None, description="Custom storage path (defaults to platform data dir)"
    )
    retention_days: int = Field(
        default=180, description="Retention period in days (EU AI Act: 180)"
    )
    sign_records: bool = Field(default=False, description="Enable HMAC-SHA256 signing")
    signing_key: Optional[str] = Field(None, description="HMAC signing key")

    def get_store_path(self) -> Path:
        """Get the storage path, using default if not specified.

        Returns:
            Path to storage directory.
        """
        if self.store_path:
            return self.store_path

        # Use platform data directory
        from persona.core.platform import get_data_dir

        return get_data_dir() / "audit"

    class Config:
        arbitrary_types_allowed = True
