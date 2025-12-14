"""Tests for structured logging (F-074)."""

import json
from typing import Any

import pytest

from persona.core.logging.structured import (
    StructuredLogger,
    LogContext,
    StructuredLogEntry,
    OutputFormat,
    configure_logging,
    get_logger,
)


class TestOutputFormat:
    """Tests for OutputFormat enum."""

    def test_formats_exist(self) -> None:
        """All output formats are defined."""
        assert OutputFormat.JSON.value == "json"
        assert OutputFormat.CONSOLE.value == "console"
        assert OutputFormat.BOTH.value == "both"


class TestLogContext:
    """Tests for LogContext dataclass."""

    def test_create_context(self) -> None:
        """Can create a log context."""
        ctx = LogContext(
            experiment_id="exp-123",
            run_id="run-456",
            step="generation",
            model="claude-sonnet-4",
        )

        assert ctx.experiment_id == "exp-123"
        assert ctx.run_id == "run-456"
        assert ctx.step == "generation"
        assert ctx.model == "claude-sonnet-4"

    def test_context_defaults(self) -> None:
        """Context has None defaults."""
        ctx = LogContext()

        assert ctx.experiment_id is None
        assert ctx.run_id is None
        assert ctx.step is None
        assert ctx.model is None
        assert ctx.extra == {}

    def test_context_with_extra(self) -> None:
        """Context can hold extra fields."""
        ctx = LogContext(
            experiment_id="exp-123",
            extra={"custom_field": "value", "count": 42},
        )

        assert ctx.extra["custom_field"] == "value"
        assert ctx.extra["count"] == 42

    def test_to_dict(self) -> None:
        """Context can be converted to dict."""
        ctx = LogContext(
            experiment_id="exp-123",
            run_id="run-456",
            extra={"custom": "data"},
        )

        result = ctx.to_dict()

        assert result["experiment_id"] == "exp-123"
        assert result["run_id"] == "run-456"
        assert result["custom"] == "data"

    def test_to_dict_excludes_none(self) -> None:
        """to_dict excludes None values."""
        ctx = LogContext(experiment_id="exp-123")

        result = ctx.to_dict()

        assert "experiment_id" in result
        assert "run_id" not in result
        assert "step" not in result
        assert "model" not in result

    def test_merge_contexts(self) -> None:
        """Can merge two contexts."""
        ctx1 = LogContext(
            experiment_id="exp-123",
            step="loading",
            extra={"a": 1},
        )
        ctx2 = LogContext(
            run_id="run-456",
            step="generation",
            extra={"b": 2},
        )

        merged = ctx1.merge(ctx2)

        # ctx2 takes precedence
        assert merged.experiment_id == "exp-123"  # from ctx1 (ctx2 is None)
        assert merged.run_id == "run-456"  # from ctx2
        assert merged.step == "generation"  # from ctx2 (overrides ctx1)
        assert merged.extra == {"a": 1, "b": 2}  # merged


class TestStructuredLogEntry:
    """Tests for StructuredLogEntry dataclass."""

    def test_create_entry(self) -> None:
        """Can create a log entry."""
        entry = StructuredLogEntry(
            timestamp="2025-01-01T00:00:00+00:00",
            level="info",
            event="data_loaded",
            context=LogContext(experiment_id="exp-123"),
            data={"files": 3},
        )

        assert entry.timestamp == "2025-01-01T00:00:00+00:00"
        assert entry.level == "info"
        assert entry.event == "data_loaded"
        assert entry.data["files"] == 3

    def test_to_dict(self) -> None:
        """Entry can be converted to dict."""
        entry = StructuredLogEntry(
            timestamp="2025-01-01T00:00:00+00:00",
            level="info",
            event="test_event",
            context=LogContext(experiment_id="exp-123"),
            data={"count": 5},
        )

        result = entry.to_dict()

        assert result["timestamp"] == "2025-01-01T00:00:00+00:00"
        assert result["level"] == "info"
        assert result["event"] == "test_event"
        assert result["experiment_id"] == "exp-123"
        assert result["count"] == 5

    def test_to_json(self) -> None:
        """Entry can be serialized to JSON."""
        entry = StructuredLogEntry(
            timestamp="2025-01-01T00:00:00+00:00",
            level="error",
            event="error_occurred",
            context=LogContext(),
            data={"error": "test"},
        )

        json_str = entry.to_json()
        parsed = json.loads(json_str)

        assert parsed["level"] == "error"
        assert parsed["error"] == "test"

    def test_to_console(self) -> None:
        """Entry can be formatted for console output."""
        entry = StructuredLogEntry(
            timestamp="2025-01-01T12:34:56+00:00",
            level="info",
            event="test_event",
            context=LogContext(experiment_id="exp-123"),
            data={"count": 5},
        )

        console = entry.to_console()

        assert "2025-01-01 12:34:56" in console
        assert "[info" in console.lower()
        assert "test_event" in console
        assert "experiment_id=exp-123" in console

    def test_to_console_quotes_spaces(self) -> None:
        """Console format quotes values with spaces."""
        entry = StructuredLogEntry(
            timestamp="2025-01-01T00:00:00+00:00",
            level="info",
            event="test",
            context=LogContext(),
            data={"message": "hello world"},
        )

        console = entry.to_console()

        assert 'message="hello world"' in console


class TestStructuredLogger:
    """Tests for StructuredLogger class."""

    def test_create_logger(self) -> None:
        """Can create a structured logger."""
        logger = StructuredLogger(name="test")

        assert logger.name == "test"

    def test_create_with_context(self) -> None:
        """Can create logger with initial context."""
        ctx = LogContext(experiment_id="exp-123")
        logger = StructuredLogger(context=ctx)

        assert logger.context.experiment_id == "exp-123"

    def test_info_logging(self) -> None:
        """Can log info events."""
        output: list[str] = []
        logger = StructuredLogger(
            output_format=OutputFormat.JSON,
            output_handler=output.append,
        )

        entry = logger.info("data_loaded", files=3)

        assert entry.level == "info"
        assert entry.event == "data_loaded"
        assert len(output) == 1
        assert '"level": "info"' in output[0]

    def test_debug_logging(self) -> None:
        """Can log debug events."""
        output: list[str] = []
        logger = StructuredLogger(
            output_format=OutputFormat.JSON,
            output_handler=output.append,
        )

        entry = logger.debug("trace_info", detail="test")

        assert entry.level == "debug"

    def test_warn_logging(self) -> None:
        """Can log warning events."""
        output: list[str] = []
        logger = StructuredLogger(
            output_format=OutputFormat.JSON,
            output_handler=output.append,
        )

        entry = logger.warn("rate_limit", remaining=5)

        assert entry.level == "warn"

    def test_warning_alias(self) -> None:
        """warning() is alias for warn()."""
        logger = StructuredLogger()

        entry = logger.warning("test_warning")

        assert entry.level == "warn"

    def test_error_logging(self) -> None:
        """Can log error events."""
        output: list[str] = []
        logger = StructuredLogger(
            output_format=OutputFormat.JSON,
            output_handler=output.append,
        )

        entry = logger.error("request_failed", status=500)

        assert entry.level == "error"

    def test_bind_context(self) -> None:
        """Can bind additional context."""
        logger = StructuredLogger()
        bound = logger.bind(experiment_id="exp-123", run_id="run-456")

        entry = bound.info("test_event")

        assert entry.context.experiment_id == "exp-123"
        assert entry.context.run_id == "run-456"

    def test_bind_preserves_existing_context(self) -> None:
        """Binding preserves existing context."""
        ctx = LogContext(experiment_id="exp-123", step="loading")
        logger = StructuredLogger(context=ctx)
        bound = logger.bind(run_id="run-456")

        assert bound.context.experiment_id == "exp-123"
        assert bound.context.step == "loading"
        assert bound.context.run_id == "run-456"

    def test_bind_returns_new_logger(self) -> None:
        """Binding returns a new logger instance."""
        logger = StructuredLogger()
        bound = logger.bind(experiment_id="exp-123")

        assert logger is not bound
        assert logger.context.experiment_id is None
        assert bound.context.experiment_id == "exp-123"

    def test_json_output_format(self) -> None:
        """Logger outputs JSON when configured."""
        output: list[str] = []
        logger = StructuredLogger(
            output_format=OutputFormat.JSON,
            output_handler=output.append,
        )

        logger.info("test_event")

        assert len(output) == 1
        parsed = json.loads(output[0])
        assert parsed["event"] == "test_event"

    def test_console_output_format(self) -> None:
        """Logger outputs console format when configured."""
        output: list[str] = []
        logger = StructuredLogger(
            output_format=OutputFormat.CONSOLE,
            output_handler=output.append,
        )

        logger.info("test_event", count=5)

        assert len(output) == 1
        assert "test_event" in output[0]
        assert "count=5" in output[0]

    def test_both_output_format(self) -> None:
        """Logger outputs both formats when configured."""
        output: list[str] = []
        logger = StructuredLogger(
            output_format=OutputFormat.BOTH,
            output_handler=output.append,
        )

        logger.info("test_event")

        assert len(output) == 2  # JSON and console

    def test_get_entries(self) -> None:
        """Can retrieve logged entries."""
        logger = StructuredLogger()

        logger.info("event1")
        logger.debug("event2")
        logger.error("event3")

        entries = logger.get_entries()
        assert len(entries) == 3

    def test_get_entries_filtered_by_level(self) -> None:
        """Can filter entries by level."""
        logger = StructuredLogger()

        logger.info("event1")
        logger.debug("event2")
        logger.error("event3")

        info_entries = logger.get_entries(level="info")
        assert len(info_entries) == 1
        assert info_entries[0].event == "event1"


class TestGlobalLogger:
    """Tests for global logger functions."""

    def test_configure_logging(self) -> None:
        """Can configure global logger."""
        logger = configure_logging(output_format=OutputFormat.JSON)

        assert logger.output_format == OutputFormat.JSON

    def test_configure_logging_with_context(self) -> None:
        """Can configure global logger with context."""
        ctx = LogContext(experiment_id="exp-global")
        logger = configure_logging(context=ctx)

        assert logger.context.experiment_id == "exp-global"

    def test_get_logger_returns_instance(self) -> None:
        """get_logger returns a logger instance."""
        logger = get_logger()

        assert isinstance(logger, StructuredLogger)

    def test_get_logger_with_name(self) -> None:
        """Can get logger with specific name."""
        # Note: get_logger returns the global logger once configured.
        # The name parameter is only used when creating a new global logger.
        # This test verifies the function returns a StructuredLogger.
        logger = get_logger(name="custom")

        assert isinstance(logger, StructuredLogger)
