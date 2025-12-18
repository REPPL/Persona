"""Experiment logger with JSON Lines output (F-073).

Logs all experiment events to JSON Lines format for
debugging, analysis, and reproducibility.
"""

import json
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any


class LogLevel(Enum):
    """Log severity levels."""

    DEBUG = "debug"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"


class EventType(Enum):
    """Standard event types for experiments."""

    EXPERIMENT_STARTED = "experiment_started"
    EXPERIMENT_COMPLETED = "experiment_completed"
    EXPERIMENT_FAILED = "experiment_failed"
    DATA_LOADED = "data_loaded"
    DATA_VALIDATED = "data_validated"
    GENERATION_STARTED = "generation_started"
    GENERATION_COMPLETED = "generation_completed"
    GENERATION_FAILED = "generation_failed"
    PERSONA_CREATED = "persona_created"
    PERSONA_VALIDATED = "persona_validated"
    OUTPUT_WRITTEN = "output_written"
    CONFIG_LOADED = "config_loaded"
    PROVIDER_INITIALISED = "provider_initialised"
    LLM_CALL_STARTED = "llm_call_started"
    LLM_CALL_COMPLETED = "llm_call_completed"
    LLM_CALL_FAILED = "llm_call_failed"
    CUSTOM = "custom"


@dataclass
class LogEvent:
    """A single log event.

    Attributes:
        timestamp: ISO 8601 timestamp.
        level: Log severity level.
        event: Event type.
        experiment_id: Associated experiment ID.
        run_id: Associated run ID.
        payload: Additional event data.
        message: Human-readable message.
    """

    timestamp: str
    level: LogLevel
    event: EventType
    experiment_id: str | None = None
    run_id: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for JSON serialisation."""
        return {
            "timestamp": self.timestamp,
            "level": self.level.value,
            "event": self.event.value,
            "experiment_id": self.experiment_id,
            "run_id": self.run_id,
            "payload": self.payload,
            "message": self.message,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LogEvent":
        """Create from dictionary."""
        return cls(
            timestamp=data["timestamp"],
            level=LogLevel(data["level"]),
            event=EventType(data["event"]),
            experiment_id=data.get("experiment_id"),
            run_id=data.get("run_id"),
            payload=data.get("payload", {}),
            message=data.get("message", ""),
        )


class ExperimentLogger:
    """Logger for experiment events in JSON Lines format.

    Logs events to `.jsonl` files with one JSON object per line,
    enabling easy streaming and querying.

    Example:
        >>> logger = ExperimentLogger(
        ...     log_dir=Path("experiments/my-exp/logs"),
        ...     experiment_id="exp-abc123"
        ... )
        >>> logger.info(EventType.EXPERIMENT_STARTED, {"model": "claude"})
        >>> logger.close()
    """

    # Default max file size before rotation (10MB)
    DEFAULT_MAX_SIZE = 10 * 1024 * 1024

    def __init__(
        self,
        log_dir: Path | None = None,
        experiment_id: str | None = None,
        run_id: str | None = None,
        max_file_size: int = DEFAULT_MAX_SIZE,
        enable_debug_log: bool = False,
    ):
        """Initialise the logger.

        Args:
            log_dir: Directory for log files.
            experiment_id: Default experiment ID.
            run_id: Default run ID.
            max_file_size: Max bytes before rotation.
            enable_debug_log: Create separate debug log file.
        """
        self.log_dir = log_dir
        self.experiment_id = experiment_id
        self.run_id = run_id
        self.max_file_size = max_file_size
        self.enable_debug_log = enable_debug_log

        self._main_file: Any = None
        self._debug_file: Any = None
        self._event_count = 0
        self._events: list[LogEvent] = []

        if log_dir:
            self._setup_files()

    def _setup_files(self) -> None:
        """Set up log files."""
        if self.log_dir:
            self.log_dir.mkdir(parents=True, exist_ok=True)
            main_path = self.log_dir / "experiment.jsonl"
            self._main_file = open(main_path, "a", encoding="utf-8")

            if self.enable_debug_log:
                debug_path = self.log_dir / "debug.jsonl"
                self._debug_file = open(debug_path, "a", encoding="utf-8")

    def _create_event(
        self,
        level: LogLevel,
        event: EventType,
        payload: dict[str, Any] | None = None,
        message: str = "",
        experiment_id: str | None = None,
        run_id: str | None = None,
    ) -> LogEvent:
        """Create a log event."""
        return LogEvent(
            timestamp=datetime.now(UTC).isoformat(),
            level=level,
            event=event,
            experiment_id=experiment_id or self.experiment_id,
            run_id=run_id or self.run_id,
            payload=payload or {},
            message=message,
        )

    def _write_event(self, event: LogEvent) -> None:
        """Write event to log files."""
        self._events.append(event)
        self._event_count += 1

        if self._main_file:
            self._main_file.write(event.to_json() + "\n")
            self._main_file.flush()

            # Check for rotation
            if self._main_file.tell() > self.max_file_size:
                self._rotate_file()

        if self._debug_file and event.level == LogLevel.DEBUG:
            self._debug_file.write(event.to_json() + "\n")
            self._debug_file.flush()

    def _rotate_file(self) -> None:
        """Rotate log file when size exceeded."""
        if not self._main_file or not self.log_dir:
            return

        self._main_file.close()

        # Rename old file
        current_path = self.log_dir / "experiment.jsonl"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_path = self.log_dir / f"experiment_{timestamp}.jsonl"
        current_path.rename(archive_path)

        # Open new file
        self._main_file = open(current_path, "a", encoding="utf-8")

    def debug(
        self,
        event: EventType,
        payload: dict[str, Any] | None = None,
        message: str = "",
    ) -> LogEvent:
        """Log a debug event."""
        log_event = self._create_event(LogLevel.DEBUG, event, payload, message)
        self._write_event(log_event)
        return log_event

    def info(
        self,
        event: EventType,
        payload: dict[str, Any] | None = None,
        message: str = "",
    ) -> LogEvent:
        """Log an info event."""
        log_event = self._create_event(LogLevel.INFO, event, payload, message)
        self._write_event(log_event)
        return log_event

    def warn(
        self,
        event: EventType,
        payload: dict[str, Any] | None = None,
        message: str = "",
    ) -> LogEvent:
        """Log a warning event."""
        log_event = self._create_event(LogLevel.WARN, event, payload, message)
        self._write_event(log_event)
        return log_event

    def error(
        self,
        event: EventType,
        payload: dict[str, Any] | None = None,
        message: str = "",
    ) -> LogEvent:
        """Log an error event."""
        log_event = self._create_event(LogLevel.ERROR, event, payload, message)
        self._write_event(log_event)
        return log_event

    def log(
        self,
        level: LogLevel,
        event: EventType,
        payload: dict[str, Any] | None = None,
        message: str = "",
    ) -> LogEvent:
        """Log an event with specified level."""
        log_event = self._create_event(level, event, payload, message)
        self._write_event(log_event)
        return log_event

    def bind(
        self,
        experiment_id: str | None = None,
        run_id: str | None = None,
    ) -> "ExperimentLogger":
        """Create a bound logger with default context.

        Args:
            experiment_id: Default experiment ID for this logger.
            run_id: Default run ID for this logger.

        Returns:
            New logger instance with bound context.
        """
        return ExperimentLogger(
            log_dir=self.log_dir,
            experiment_id=experiment_id or self.experiment_id,
            run_id=run_id or self.run_id,
            max_file_size=self.max_file_size,
            enable_debug_log=self.enable_debug_log,
        )

    def get_events(
        self,
        level: LogLevel | None = None,
        event_type: EventType | None = None,
    ) -> list[LogEvent]:
        """Get logged events with optional filtering.

        Args:
            level: Filter by log level.
            event_type: Filter by event type.

        Returns:
            List of matching events.
        """
        events = self._events

        if level:
            events = [e for e in events if e.level == level]
        if event_type:
            events = [e for e in events if e.event == event_type]

        return events

    @property
    def event_count(self) -> int:
        """Get total number of logged events."""
        return self._event_count

    def close(self) -> None:
        """Close log files."""
        if self._main_file:
            self._main_file.close()
            self._main_file = None
        if self._debug_file:
            self._debug_file.close()
            self._debug_file = None

    def __enter__(self) -> "ExperimentLogger":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()


def log_event(
    event: EventType,
    payload: dict[str, Any] | None = None,
    level: LogLevel = LogLevel.INFO,
    experiment_id: str | None = None,
    run_id: str | None = None,
) -> LogEvent:
    """Convenience function to create a log event.

    Args:
        event: Event type.
        payload: Event data.
        level: Log level.
        experiment_id: Experiment ID.
        run_id: Run ID.

    Returns:
        Created LogEvent.
    """
    return LogEvent(
        timestamp=datetime.now(UTC).isoformat(),
        level=level,
        event=event,
        experiment_id=experiment_id,
        run_id=run_id,
        payload=payload or {},
    )


def read_log_file(path: Path) -> list[LogEvent]:
    """Read events from a JSON Lines log file.

    Args:
        path: Path to .jsonl file.

    Returns:
        List of LogEvent objects.
    """
    events = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                data = json.loads(line)
                events.append(LogEvent.from_dict(data))
    return events
