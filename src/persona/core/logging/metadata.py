"""Metadata recording for reproducibility (F-076).

Records comprehensive metadata about generation runs
for reproducibility, auditing, and analysis.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import hashlib
import json
import platform
import sys


@dataclass
class GenerationConfig:
    """Generation configuration metadata.

    Attributes:
        model: Model identifier.
        provider: LLM provider.
        persona_count: Number of personas.
        complexity: Complexity level.
        detail_level: Detail level.
        temperature: Temperature setting.
        max_tokens: Max tokens setting.
        extra: Additional configuration.
    """
    model: str = ""
    provider: str = ""
    persona_count: int = 0
    complexity: str = "moderate"
    detail_level: str = "standard"
    temperature: float = 0.7
    max_tokens: int = 4096
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "model": self.model,
            "provider": self.provider,
            "persona_count": self.persona_count,
            "complexity": self.complexity,
            "detail_level": self.detail_level,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            **self.extra,
        }


@dataclass
class DataSourceInfo:
    """Information about data sources.

    Attributes:
        files: List of source file paths.
        total_files: Number of files.
        total_tokens: Estimated total tokens.
        total_bytes: Total file size in bytes.
        checksums: File checksums.
    """
    files: list[str] = field(default_factory=list)
    total_files: int = 0
    total_tokens: int = 0
    total_bytes: int = 0
    checksums: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "files": self.files,
            "total_files": self.total_files,
            "total_tokens": self.total_tokens,
            "total_bytes": self.total_bytes,
            "checksums": self.checksums,
        }


@dataclass
class EnvironmentInfo:
    """Execution environment information.

    Attributes:
        persona_version: Persona package version.
        python_version: Python version.
        platform: Operating system.
        platform_version: OS version.
        timezone: System timezone.
        hostname: Machine hostname (optional).
    """
    persona_version: str = ""
    python_version: str = ""
    platform: str = ""
    platform_version: str = ""
    timezone: str = "UTC"
    hostname: str = ""

    @classmethod
    def capture(cls) -> "EnvironmentInfo":
        """Capture current environment info."""
        try:
            from persona import __version__
            version = __version__
        except ImportError:
            version = "unknown"

        return cls(
            persona_version=version,
            python_version=f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            platform=sys.platform,
            platform_version=platform.release(),
            timezone=datetime.now().astimezone().tzname() or "UTC",
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {
            "persona_version": self.persona_version,
            "python_version": self.python_version,
            "platform": self.platform,
            "platform_version": self.platform_version,
            "timezone": self.timezone,
        }
        if self.hostname:
            result["hostname"] = self.hostname
        return result


@dataclass
class CostInfo:
    """Cost information for a generation.

    Attributes:
        input_tokens: Number of input tokens.
        output_tokens: Number of output tokens.
        total_cost_usd: Total cost in USD.
        cost_per_persona: Average cost per persona.
    """
    input_tokens: int = 0
    output_tokens: int = 0
    total_cost_usd: float = 0.0
    cost_per_persona: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_cost_usd": self.total_cost_usd,
            "cost_per_persona": self.cost_per_persona,
        }


@dataclass
class GenerationMetadata:
    """Complete generation metadata.

    Attributes:
        metadata_version: Metadata schema version.
        experiment_id: Experiment identifier.
        run_id: Run identifier.
        timestamp_start: Start time.
        timestamp_end: End time.
        duration_seconds: Total duration.
        configuration: Generation configuration.
        data_sources: Source data information.
        environment: Execution environment.
        costs: Cost information.
        checksums: Output checksums.
        errors: Any errors encountered.
        warnings: Any warnings generated.
    """
    metadata_version: str = "1.0"
    experiment_id: str = ""
    run_id: str = ""
    timestamp_start: str = ""
    timestamp_end: str = ""
    duration_seconds: float = 0.0
    configuration: GenerationConfig = field(default_factory=GenerationConfig)
    data_sources: DataSourceInfo = field(default_factory=DataSourceInfo)
    environment: EnvironmentInfo = field(default_factory=EnvironmentInfo)
    costs: CostInfo = field(default_factory=CostInfo)
    checksums: dict[str, str] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "metadata_version": self.metadata_version,
            "generation": {
                "experiment_id": self.experiment_id,
                "run_id": self.run_id,
                "timestamp_start": self.timestamp_start,
                "timestamp_end": self.timestamp_end,
                "duration_seconds": self.duration_seconds,
            },
            "configuration": self.configuration.to_dict(),
            "data_sources": self.data_sources.to_dict(),
            "environment": self.environment.to_dict(),
            "costs": self.costs.to_dict(),
            "checksums": self.checksums,
            "errors": self.errors,
            "warnings": self.warnings,
        }

    def to_json(self, indent: int = 2) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "GenerationMetadata":
        """Create from dictionary."""
        gen = data.get("generation", {})
        return cls(
            metadata_version=data.get("metadata_version", "1.0"),
            experiment_id=gen.get("experiment_id", ""),
            run_id=gen.get("run_id", ""),
            timestamp_start=gen.get("timestamp_start", ""),
            timestamp_end=gen.get("timestamp_end", ""),
            duration_seconds=gen.get("duration_seconds", 0.0),
            configuration=GenerationConfig(**data.get("configuration", {})),
            data_sources=DataSourceInfo(**data.get("data_sources", {})),
            environment=EnvironmentInfo(**data.get("environment", {})),
            costs=CostInfo(**data.get("costs", {})),
            checksums=data.get("checksums", {}),
            errors=data.get("errors", []),
            warnings=data.get("warnings", []),
        )


class MetadataRecorder:
    """Recorder for generation metadata.

    Captures comprehensive metadata about a generation run
    for reproducibility and auditing.

    Example:
        >>> recorder = MetadataRecorder(
        ...     experiment_id="exp-abc123",
        ...     run_id="run-def456"
        ... )
        >>> recorder.start()
        >>> recorder.set_config(model="claude", persona_count=3)
        >>> recorder.add_data_source("interview.md", tokens=5000)
        >>> metadata = recorder.finish()
    """

    def __init__(
        self,
        experiment_id: str = "",
        run_id: str = "",
    ):
        """Initialise the recorder.

        Args:
            experiment_id: Experiment identifier.
            run_id: Run identifier.
        """
        self._metadata = GenerationMetadata(
            experiment_id=experiment_id,
            run_id=run_id,
            environment=EnvironmentInfo.capture(),
        )
        self._started = False

    def start(self) -> None:
        """Mark the start of generation."""
        self._metadata.timestamp_start = datetime.now(timezone.utc).isoformat()
        self._started = True

    def set_config(
        self,
        model: str = "",
        provider: str = "",
        persona_count: int = 0,
        complexity: str = "moderate",
        detail_level: str = "standard",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        **extra: Any,
    ) -> None:
        """Set generation configuration.

        Args:
            model: Model identifier.
            provider: LLM provider.
            persona_count: Number of personas.
            complexity: Complexity level.
            detail_level: Detail level.
            temperature: Temperature setting.
            max_tokens: Max tokens.
            **extra: Additional configuration.
        """
        self._metadata.configuration = GenerationConfig(
            model=model,
            provider=provider,
            persona_count=persona_count,
            complexity=complexity,
            detail_level=detail_level,
            temperature=temperature,
            max_tokens=max_tokens,
            extra=extra,
        )

    def add_data_source(
        self,
        path: str,
        tokens: int = 0,
        size_bytes: int = 0,
        checksum: str = "",
    ) -> None:
        """Add a data source file.

        Args:
            path: File path.
            tokens: Estimated tokens.
            size_bytes: File size.
            checksum: File checksum.
        """
        self._metadata.data_sources.files.append(path)
        self._metadata.data_sources.total_files += 1
        self._metadata.data_sources.total_tokens += tokens
        self._metadata.data_sources.total_bytes += size_bytes
        if checksum:
            self._metadata.data_sources.checksums[path] = checksum

    def set_costs(
        self,
        input_tokens: int = 0,
        output_tokens: int = 0,
        total_cost_usd: float = 0.0,
    ) -> None:
        """Set cost information.

        Args:
            input_tokens: Input token count.
            output_tokens: Output token count.
            total_cost_usd: Total cost.
        """
        persona_count = self._metadata.configuration.persona_count or 1
        self._metadata.costs = CostInfo(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_cost_usd=total_cost_usd,
            cost_per_persona=total_cost_usd / persona_count,
        )

    def add_checksum(self, name: str, checksum: str) -> None:
        """Add an output checksum.

        Args:
            name: Checksum name/label.
            checksum: Checksum value.
        """
        self._metadata.checksums[name] = checksum

    def add_error(self, error: str) -> None:
        """Record an error.

        Args:
            error: Error message.
        """
        self._metadata.errors.append(error)

    def add_warning(self, warning: str) -> None:
        """Record a warning.

        Args:
            warning: Warning message.
        """
        self._metadata.warnings.append(warning)

    def finish(self) -> GenerationMetadata:
        """Mark the end of generation and return metadata.

        Returns:
            Complete GenerationMetadata.
        """
        self._metadata.timestamp_end = datetime.now(timezone.utc).isoformat()

        # Calculate duration
        if self._metadata.timestamp_start:
            start = datetime.fromisoformat(
                self._metadata.timestamp_start.replace("Z", "+00:00")
            )
            end = datetime.fromisoformat(
                self._metadata.timestamp_end.replace("Z", "+00:00")
            )
            self._metadata.duration_seconds = (end - start).total_seconds()

        return self._metadata

    def get_metadata(self) -> GenerationMetadata:
        """Get current metadata (without finishing)."""
        return self._metadata

    def save(self, path: Path) -> None:
        """Save metadata to file.

        Args:
            path: Output file path.
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self._metadata.to_json())


def record_metadata(
    experiment_id: str,
    run_id: str,
    config: dict[str, Any],
    data_files: list[str],
    costs: dict[str, Any] | None = None,
) -> GenerationMetadata:
    """Convenience function to record metadata.

    Args:
        experiment_id: Experiment identifier.
        run_id: Run identifier.
        config: Generation configuration.
        data_files: List of data file paths.
        costs: Optional cost information.

    Returns:
        GenerationMetadata object.
    """
    recorder = MetadataRecorder(experiment_id, run_id)
    recorder.start()
    recorder.set_config(**config)

    for path in data_files:
        recorder.add_data_source(path)

    if costs:
        recorder.set_costs(**costs)

    return recorder.finish()


def calculate_checksum(content: str | bytes) -> str:
    """Calculate SHA-256 checksum.

    Args:
        content: Content to hash.

    Returns:
        Hex-encoded checksum.
    """
    if isinstance(content, str):
        content = content.encode("utf-8")
    return f"sha256:{hashlib.sha256(content).hexdigest()}"
