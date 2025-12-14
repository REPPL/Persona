"""Structured logging with context propagation (F-074).

Provides structured logging with consistent field naming,
context binding, and multiple output formats.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Callable
import json
import sys


class OutputFormat(Enum):
    """Log output formats."""
    JSON = "json"
    CONSOLE = "console"
    BOTH = "both"


@dataclass
class LogContext:
    """Context information for log entries.

    Attributes:
        experiment_id: Current experiment ID.
        run_id: Current run ID.
        step: Current workflow step.
        model: Current model being used.
        extra: Additional context fields.
    """
    experiment_id: str | None = None
    run_id: str | None = None
    step: str | None = None
    model: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        result = {}
        if self.experiment_id:
            result["experiment_id"] = self.experiment_id
        if self.run_id:
            result["run_id"] = self.run_id
        if self.step:
            result["step"] = self.step
        if self.model:
            result["model"] = self.model
        result.update(self.extra)
        return result

    def merge(self, other: "LogContext") -> "LogContext":
        """Merge with another context (other takes precedence)."""
        return LogContext(
            experiment_id=other.experiment_id or self.experiment_id,
            run_id=other.run_id or self.run_id,
            step=other.step or self.step,
            model=other.model or self.model,
            extra={**self.extra, **other.extra},
        )


@dataclass
class StructuredLogEntry:
    """A structured log entry.

    Attributes:
        timestamp: ISO 8601 timestamp.
        level: Log level.
        event: Event name/description.
        context: Associated context.
        data: Event-specific data.
    """
    timestamp: str
    level: str
    event: str
    context: LogContext
    data: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON output."""
        result = {
            "timestamp": self.timestamp,
            "level": self.level,
            "event": self.event,
            **self.context.to_dict(),
            **self.data,
        }
        return result

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())

    def to_console(self) -> str:
        """Convert to human-readable console format."""
        # Format: timestamp [level] event key=value key=value
        parts = [
            self.timestamp[:19].replace("T", " "),
            f"[{self.level:<5}]",
            self.event,
        ]

        # Add context and data as key=value pairs
        all_fields = {**self.context.to_dict(), **self.data}
        for key, value in all_fields.items():
            if isinstance(value, str) and " " in value:
                parts.append(f'{key}="{value}"')
            else:
                parts.append(f"{key}={value}")

        return " ".join(parts)


class StructuredLogger:
    """Structured logger with context binding.

    Provides structured logging with consistent fields,
    context propagation, and multiple output formats.

    Example:
        >>> logger = StructuredLogger()
        >>> logger = logger.bind(experiment_id="exp-abc123")
        >>> logger.info("data_loaded", file_count=5)
        >>> logger.info("generation_started", model="claude")
    """

    def __init__(
        self,
        name: str = "persona",
        output_format: OutputFormat = OutputFormat.CONSOLE,
        context: LogContext | None = None,
        output_handler: Callable[[str], None] | None = None,
    ):
        """Initialise the logger.

        Args:
            name: Logger name.
            output_format: Output format (json, console, both).
            context: Initial context.
            output_handler: Custom output handler (default: stderr).
        """
        self.name = name
        self.output_format = output_format
        self.context = context or LogContext()
        self.output_handler = output_handler or self._default_output
        self._entries: list[StructuredLogEntry] = []

    def _default_output(self, message: str) -> None:
        """Default output to stderr."""
        print(message, file=sys.stderr)

    def _create_entry(
        self,
        level: str,
        event: str,
        **kwargs: Any,
    ) -> StructuredLogEntry:
        """Create a structured log entry."""
        return StructuredLogEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            level=level,
            event=event,
            context=self.context,
            data=kwargs,
        )

    def _output(self, entry: StructuredLogEntry) -> None:
        """Output a log entry."""
        self._entries.append(entry)

        if self.output_format == OutputFormat.JSON:
            self.output_handler(entry.to_json())
        elif self.output_format == OutputFormat.CONSOLE:
            self.output_handler(entry.to_console())
        else:  # BOTH
            self.output_handler(entry.to_json())
            self.output_handler(entry.to_console())

    def bind(self, **kwargs: Any) -> "StructuredLogger":
        """Create a bound logger with additional context.

        Args:
            **kwargs: Context fields to bind.

        Returns:
            New logger with merged context.
        """
        new_context = LogContext(
            experiment_id=kwargs.pop("experiment_id", None),
            run_id=kwargs.pop("run_id", None),
            step=kwargs.pop("step", None),
            model=kwargs.pop("model", None),
            extra=kwargs,
        )

        return StructuredLogger(
            name=self.name,
            output_format=self.output_format,
            context=self.context.merge(new_context),
            output_handler=self.output_handler,
        )

    def debug(self, event: str, **kwargs: Any) -> StructuredLogEntry:
        """Log a debug event."""
        entry = self._create_entry("debug", event, **kwargs)
        self._output(entry)
        return entry

    def info(self, event: str, **kwargs: Any) -> StructuredLogEntry:
        """Log an info event."""
        entry = self._create_entry("info", event, **kwargs)
        self._output(entry)
        return entry

    def warn(self, event: str, **kwargs: Any) -> StructuredLogEntry:
        """Log a warning event."""
        entry = self._create_entry("warn", event, **kwargs)
        self._output(entry)
        return entry

    def warning(self, event: str, **kwargs: Any) -> StructuredLogEntry:
        """Log a warning event (alias for warn)."""
        return self.warn(event, **kwargs)

    def error(self, event: str, **kwargs: Any) -> StructuredLogEntry:
        """Log an error event."""
        entry = self._create_entry("error", event, **kwargs)
        self._output(entry)
        return entry

    def get_entries(self, level: str | None = None) -> list[StructuredLogEntry]:
        """Get logged entries with optional filtering.

        Args:
            level: Filter by log level.

        Returns:
            List of matching entries.
        """
        if level:
            return [e for e in self._entries if e.level == level]
        return list(self._entries)


# Global logger instance
_global_logger: StructuredLogger | None = None


def configure_logging(
    output_format: OutputFormat = OutputFormat.CONSOLE,
    context: LogContext | None = None,
) -> StructuredLogger:
    """Configure the global logger.

    Args:
        output_format: Output format.
        context: Initial context.

    Returns:
        Configured global logger.
    """
    global _global_logger
    _global_logger = StructuredLogger(
        output_format=output_format,
        context=context,
    )
    return _global_logger


def get_logger(name: str | None = None) -> StructuredLogger:
    """Get the global logger or create a new one.

    Args:
        name: Optional logger name.

    Returns:
        StructuredLogger instance.
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = StructuredLogger(name=name or "persona")
    return _global_logger
