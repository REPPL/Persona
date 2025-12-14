"""Tests for experiment logger (F-073)."""

import json
import tempfile
from pathlib import Path
from datetime import datetime, timezone

import pytest

from persona.core.logging.experiment_logger import (
    ExperimentLogger,
    LogEvent,
    LogLevel,
    EventType,
    log_event,
    read_log_file,
)


class TestLogLevel:
    """Tests for LogLevel enum."""

    def test_log_levels_exist(self) -> None:
        """All log levels are defined."""
        assert LogLevel.DEBUG.value == "debug"
        assert LogLevel.INFO.value == "info"
        assert LogLevel.WARN.value == "warn"
        assert LogLevel.ERROR.value == "error"


class TestEventType:
    """Tests for EventType enum."""

    def test_experiment_events(self) -> None:
        """Experiment lifecycle events are defined."""
        assert EventType.EXPERIMENT_STARTED.value == "experiment_started"
        assert EventType.EXPERIMENT_COMPLETED.value == "experiment_completed"
        assert EventType.EXPERIMENT_FAILED.value == "experiment_failed"

    def test_generation_events(self) -> None:
        """Generation events are defined."""
        assert EventType.GENERATION_STARTED.value == "generation_started"
        assert EventType.GENERATION_COMPLETED.value == "generation_completed"
        assert EventType.GENERATION_FAILED.value == "generation_failed"

    def test_data_events(self) -> None:
        """Data loading events are defined."""
        assert EventType.DATA_LOADED.value == "data_loaded"
        assert EventType.DATA_VALIDATED.value == "data_validated"

    def test_llm_events(self) -> None:
        """LLM call events are defined."""
        assert EventType.LLM_CALL_STARTED.value == "llm_call_started"
        assert EventType.LLM_CALL_COMPLETED.value == "llm_call_completed"
        assert EventType.LLM_CALL_FAILED.value == "llm_call_failed"

    def test_persona_events(self) -> None:
        """Persona events are defined."""
        assert EventType.PERSONA_CREATED.value == "persona_created"
        assert EventType.PERSONA_VALIDATED.value == "persona_validated"

    def test_other_events(self) -> None:
        """Other event types are defined."""
        assert EventType.CONFIG_LOADED.value == "config_loaded"
        assert EventType.OUTPUT_WRITTEN.value == "output_written"
        assert EventType.PROVIDER_INITIALISED.value == "provider_initialised"
        assert EventType.CUSTOM.value == "custom"


class TestLogEvent:
    """Tests for LogEvent dataclass."""

    def test_create_log_event(self) -> None:
        """Can create a log event with all fields."""
        event = LogEvent(
            timestamp="2025-01-01T00:00:00+00:00",
            level=LogLevel.INFO,
            event=EventType.EXPERIMENT_STARTED,
            experiment_id="exp-123",
            run_id="run-456",
            message="Test message",
            payload={"key": "value"},
        )

        assert event.timestamp == "2025-01-01T00:00:00+00:00"
        assert event.level == LogLevel.INFO
        assert event.event == EventType.EXPERIMENT_STARTED
        assert event.experiment_id == "exp-123"
        assert event.run_id == "run-456"
        assert event.message == "Test message"
        assert event.payload == {"key": "value"}

    def test_log_event_defaults(self) -> None:
        """Log event has sensible defaults."""
        event = LogEvent(
            timestamp="2025-01-01T00:00:00+00:00",
            level=LogLevel.INFO,
            event=EventType.CUSTOM,
        )

        assert event.experiment_id is None
        assert event.run_id is None
        assert event.message == ""
        assert event.payload == {}

    def test_to_dict(self) -> None:
        """Log event can be converted to dict."""
        event = LogEvent(
            timestamp="2025-01-01T00:00:00+00:00",
            level=LogLevel.INFO,
            event=EventType.DATA_LOADED,
            experiment_id="exp-123",
            message="Loaded data",
            payload={"files": 3},
        )

        result = event.to_dict()

        assert result["timestamp"] == "2025-01-01T00:00:00+00:00"
        assert result["level"] == "info"
        assert result["event"] == "data_loaded"
        assert result["experiment_id"] == "exp-123"
        assert result["message"] == "Loaded data"
        assert result["payload"]["files"] == 3

    def test_to_json(self) -> None:
        """Log event can be serialized to JSON."""
        event = LogEvent(
            timestamp="2025-01-01T00:00:00+00:00",
            level=LogLevel.ERROR,
            event=EventType.EXPERIMENT_FAILED,
            message="Something failed",
        )

        json_str = event.to_json()
        parsed = json.loads(json_str)

        assert parsed["level"] == "error"
        assert parsed["event"] == "experiment_failed"
        assert parsed["message"] == "Something failed"

    def test_from_dict(self) -> None:
        """Can create LogEvent from dict."""
        data = {
            "timestamp": "2025-01-01T00:00:00+00:00",
            "level": "info",
            "event": "data_loaded",
            "experiment_id": "exp-123",
            "payload": {"count": 5},
        }

        event = LogEvent.from_dict(data)

        assert event.level == LogLevel.INFO
        assert event.event == EventType.DATA_LOADED
        assert event.experiment_id == "exp-123"


class TestExperimentLogger:
    """Tests for ExperimentLogger class."""

    def test_create_logger(self) -> None:
        """Can create an experiment logger."""
        logger = ExperimentLogger(
            experiment_id="exp-abc",
            run_id="run-def",
        )

        assert logger.experiment_id == "exp-abc"
        assert logger.run_id == "run-def"

    def test_create_logger_with_log_dir(self) -> None:
        """Can create logger with log directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            logger = ExperimentLogger(
                experiment_id="exp-123",
                log_dir=log_dir,
            )

            assert logger.log_dir == log_dir
            assert (log_dir / "experiment.jsonl").exists()
            logger.close()

    def test_info_logging(self) -> None:
        """Can log info events."""
        logger = ExperimentLogger(experiment_id="exp-123")

        event = logger.info(
            EventType.EXPERIMENT_STARTED,
            payload={"config": "test"},
            message="Started",
        )

        assert event.level == LogLevel.INFO
        assert event.event == EventType.EXPERIMENT_STARTED
        assert event.experiment_id == "exp-123"
        assert event.message == "Started"

    def test_debug_logging(self) -> None:
        """Can log debug events."""
        logger = ExperimentLogger(experiment_id="exp-123")

        event = logger.debug(
            EventType.CUSTOM,
            message="Debug info",
        )

        assert event.level == LogLevel.DEBUG

    def test_warn_logging(self) -> None:
        """Can log warning events."""
        logger = ExperimentLogger(experiment_id="exp-123")

        event = logger.warn(
            EventType.CUSTOM,
            payload={"percent": 85},
        )

        assert event.level == LogLevel.WARN

    def test_error_logging(self) -> None:
        """Can log error events."""
        logger = ExperimentLogger(experiment_id="exp-123")

        event = logger.error(
            EventType.EXPERIMENT_FAILED,
            message="Something failed",
            payload={"error_code": 500},
        )

        assert event.level == LogLevel.ERROR

    def test_logs_to_file(self) -> None:
        """Logger writes events to JSON Lines file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"
            logger = ExperimentLogger(
                experiment_id="exp-123",
                log_dir=log_dir,
            )

            logger.info(EventType.EXPERIMENT_STARTED, message="Start")
            logger.info(EventType.DATA_LOADED, payload={"files": 2})
            logger.info(EventType.EXPERIMENT_COMPLETED, message="Done")
            logger.close()

            # Verify file was created and contains JSON Lines
            log_file = log_dir / "experiment.jsonl"
            assert log_file.exists()
            lines = log_file.read_text().strip().split("\n")
            assert len(lines) == 3

            # Verify each line is valid JSON
            for line in lines:
                data = json.loads(line)
                assert "timestamp" in data
                assert "level" in data
                assert "event" in data

    def test_get_events(self) -> None:
        """Can retrieve logged events."""
        logger = ExperimentLogger(experiment_id="exp-123")

        logger.info(EventType.EXPERIMENT_STARTED)
        logger.debug(EventType.CUSTOM, message="Debug")
        logger.error(EventType.EXPERIMENT_FAILED)

        events = logger.get_events()
        assert len(events) == 3

    def test_get_events_filtered_by_level(self) -> None:
        """Can filter events by level."""
        logger = ExperimentLogger(experiment_id="exp-123")

        logger.info(EventType.EXPERIMENT_STARTED)
        logger.debug(EventType.CUSTOM)
        logger.error(EventType.EXPERIMENT_FAILED)
        logger.warn(EventType.CUSTOM)

        info_events = logger.get_events(level=LogLevel.INFO)
        assert len(info_events) == 1
        assert info_events[0].level == LogLevel.INFO

        error_events = logger.get_events(level=LogLevel.ERROR)
        assert len(error_events) == 1

    def test_get_events_filtered_by_type(self) -> None:
        """Can filter events by event type."""
        logger = ExperimentLogger(experiment_id="exp-123")

        logger.info(EventType.EXPERIMENT_STARTED)
        logger.info(EventType.DATA_LOADED)
        logger.info(EventType.EXPERIMENT_COMPLETED)

        data_events = logger.get_events(event_type=EventType.DATA_LOADED)
        assert len(data_events) == 1
        assert data_events[0].event == EventType.DATA_LOADED

    def test_bind_run_id(self) -> None:
        """Can bind run_id for subsequent events."""
        logger = ExperimentLogger(experiment_id="exp-123")
        bound_logger = logger.bind(run_id="run-456")

        event = bound_logger.info(EventType.GENERATION_STARTED)

        assert event.run_id == "run-456"
        assert event.experiment_id == "exp-123"

    def test_bind_preserves_experiment_id(self) -> None:
        """Binding preserves original experiment_id."""
        logger = ExperimentLogger(experiment_id="exp-abc", run_id="run-def")
        bound = logger.bind(run_id="run-xyz")

        assert bound.experiment_id == "exp-abc"
        assert bound.run_id == "run-xyz"

    def test_context_manager(self) -> None:
        """Logger works as context manager."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"

            with ExperimentLogger(
                experiment_id="exp-123",
                log_dir=log_dir,
            ) as logger:
                logger.info(EventType.EXPERIMENT_STARTED)

            # File should exist after context exits
            assert (log_dir / "experiment.jsonl").exists()

    def test_event_count(self) -> None:
        """Logger tracks event count."""
        logger = ExperimentLogger(experiment_id="exp-123")

        assert logger.event_count == 0

        logger.info(EventType.EXPERIMENT_STARTED)
        logger.debug(EventType.CUSTOM)
        logger.error(EventType.EXPERIMENT_FAILED)

        assert logger.event_count == 3


class TestLogEventConvenienceFunction:
    """Tests for log_event convenience function."""

    def test_creates_event(self) -> None:
        """log_event creates a LogEvent."""
        event = log_event(
            event=EventType.CUSTOM,
            level=LogLevel.INFO,
            experiment_id="exp-123",
            payload={"test": True},
        )

        assert isinstance(event, LogEvent)
        assert event.level == LogLevel.INFO
        assert event.event == EventType.CUSTOM
        assert event.experiment_id == "exp-123"

    def test_timestamp_is_generated(self) -> None:
        """log_event generates current timestamp."""
        event = log_event(
            event=EventType.CUSTOM,
            level=LogLevel.DEBUG,
        )

        # Verify timestamp is recent (within last minute)
        event_time = datetime.fromisoformat(event.timestamp.replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        diff = (now - event_time).total_seconds()
        assert diff < 60


class TestReadLogFile:
    """Tests for read_log_file function."""

    def test_reads_log_file(self) -> None:
        """Can read events from JSON Lines file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            log_dir = Path(tmpdir) / "logs"

            # Create log file with events
            with ExperimentLogger(
                experiment_id="exp-123",
                log_dir=log_dir,
            ) as logger:
                logger.info(EventType.EXPERIMENT_STARTED)
                logger.info(EventType.DATA_LOADED, payload={"count": 5})
                logger.info(EventType.EXPERIMENT_COMPLETED)

            # Read events back
            events = read_log_file(log_dir / "experiment.jsonl")

            assert len(events) == 3
            assert events[0].event == EventType.EXPERIMENT_STARTED
            assert events[1].payload["count"] == 5
