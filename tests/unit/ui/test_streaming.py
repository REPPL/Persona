"""
Tests for streaming output display (F-094).
"""

import sys
from unittest.mock import MagicMock, patch

import pytest

from persona.ui.streaming import (
    StreamingOutput,
    SimpleProgress,
    GenerationProgress,
    PersonaProgress,
    get_progress_handler,
)


class TestPersonaProgress:
    """Tests for PersonaProgress dataclass."""

    def test_default_values(self):
        """Test default persona progress values."""
        progress = PersonaProgress(index=1)

        assert progress.index == 1
        assert progress.name is None
        assert progress.title is None
        assert progress.status == "pending"
        assert progress.start_time is None
        assert progress.end_time is None

    def test_custom_values(self):
        """Test persona progress with custom values."""
        progress = PersonaProgress(
            index=2,
            name="Alex Chen",
            title="Product Manager",
            status="complete",
        )

        assert progress.index == 2
        assert progress.name == "Alex Chen"
        assert progress.title == "Product Manager"
        assert progress.status == "complete"


class TestGenerationProgress:
    """Tests for GenerationProgress dataclass."""

    def test_init_creates_persona_list(self):
        """Test that init creates persona progress list."""
        progress = GenerationProgress(total=3)

        assert progress.total == 3
        assert progress.current == 0
        assert len(progress.personas) == 3
        assert all(p.status == "pending" for p in progress.personas)

    def test_init_with_existing_personas(self):
        """Test init with existing personas list."""
        personas = [PersonaProgress(index=1, status="complete")]
        progress = GenerationProgress(total=1, personas=personas)

        assert len(progress.personas) == 1
        assert progress.personas[0].status == "complete"


class TestStreamingOutput:
    """Tests for StreamingOutput class."""

    @pytest.fixture
    def mock_console(self):
        """Create mock console."""
        return MagicMock()

    @pytest.fixture
    def streaming(self, mock_console):
        """Create streaming output instance."""
        return StreamingOutput(console=mock_console, show_progress=True)

    def test_init(self, streaming, mock_console):
        """Test streaming output initialization."""
        assert streaming.console == mock_console
        assert streaming.show_progress is True

    def test_init_no_progress(self, mock_console):
        """Test streaming output with progress disabled."""
        streaming = StreamingOutput(console=mock_console, show_progress=False)
        assert streaming.show_progress is False

    @patch("persona.ui.streaming.sys.stdout")
    def test_start_returns_callback(self, mock_stdout, streaming):
        """Test start returns progress callback."""
        mock_stdout.isatty.return_value = False  # Non-TTY for simpler test

        callback = streaming.start(total=3, provider="anthropic", model="claude")

        assert callable(callback)
        assert streaming._state is not None
        assert streaming._state.total == 3
        assert streaming._state.provider == "anthropic"
        assert streaming._state.model == "claude"

    @patch("persona.ui.streaming.sys.stdout")
    def test_finish_updates_state(self, mock_stdout, streaming):
        """Test finish updates state."""
        mock_stdout.isatty.return_value = False

        streaming.start(total=2)

        mock_persona = MagicMock()
        mock_persona.name = "Test Persona"
        mock_persona.title = "Tester"

        streaming.finish(
            personas=[mock_persona, mock_persona],
            input_tokens=100,
            output_tokens=50,
        )

        assert streaming._state.status == "complete"
        assert streaming._state.input_tokens == 100
        assert streaming._state.output_tokens == 50

    @patch("persona.ui.streaming.sys.stdout")
    def test_error_updates_state(self, mock_stdout, streaming):
        """Test error updates state."""
        mock_stdout.isatty.return_value = False

        streaming.start(total=3)
        streaming.error("Test error")

        assert streaming._state.status == "error"

    @patch("persona.ui.streaming.sys.stdout")
    def test_progress_callback_updates_status(self, mock_stdout, streaming):
        """Test progress callback updates status."""
        mock_stdout.isatty.return_value = False

        callback = streaming.start(total=3)

        callback("Loading input data...")
        assert streaming._state.status == "loading"

        callback("Generating with anthropic...")
        assert streaming._state.status == "generating"
        assert streaming._state.personas[0].status == "generating"

        callback("Parsing response...")
        assert streaming._state.status == "parsing"

        callback("Generation complete!")
        assert streaming._state.status == "complete"


class TestSimpleProgress:
    """Tests for SimpleProgress class."""

    @pytest.fixture
    def mock_console(self):
        """Create mock console."""
        return MagicMock()

    @pytest.fixture
    def simple(self, mock_console):
        """Create simple progress instance."""
        return SimpleProgress(console=mock_console)

    def test_init(self, simple, mock_console):
        """Test simple progress initialization."""
        assert simple.console == mock_console

    def test_start_returns_callback(self, simple):
        """Test start returns callback."""
        callback = simple.start(total=5)

        assert callable(callback)
        assert simple._total == 5

    def test_progress_callback(self, simple, mock_console):
        """Test progress callback prints message."""
        callback = simple.start(total=3)
        callback("Loading data...")

        mock_console.print.assert_called()

    def test_finish(self, simple, mock_console):
        """Test finish shows completion."""
        simple.start(total=3)
        simple.finish(personas=[1, 2, 3], input_tokens=100, output_tokens=50)

        # Should print completion message
        assert mock_console.print.called


class TestGetProgressHandler:
    """Tests for get_progress_handler function."""

    @patch("persona.ui.streaming.sys.stdout")
    def test_returns_streaming_for_tty(self, mock_stdout):
        """Test returns StreamingOutput for TTY."""
        mock_stdout.isatty.return_value = True

        handler = get_progress_handler(show_progress=True)

        assert isinstance(handler, StreamingOutput)

    @patch("persona.ui.streaming.sys.stdout")
    def test_returns_simple_for_non_tty(self, mock_stdout):
        """Test returns SimpleProgress for non-TTY."""
        mock_stdout.isatty.return_value = False

        handler = get_progress_handler(show_progress=True)

        assert isinstance(handler, SimpleProgress)

    @patch("persona.ui.streaming.sys.stdout")
    def test_returns_simple_when_progress_disabled(self, mock_stdout):
        """Test returns SimpleProgress when progress disabled."""
        mock_stdout.isatty.return_value = True

        handler = get_progress_handler(show_progress=False)

        assert isinstance(handler, SimpleProgress)


class TestStreamingOutputDisplay:
    """Tests for display building methods."""

    @pytest.fixture
    def streaming(self):
        """Create streaming output with mocked console."""
        console = MagicMock()
        return StreamingOutput(console=console, show_progress=True)

    def test_build_persona_tree_empty(self, streaming):
        """Test building persona tree with no state."""
        tree = streaming._build_persona_tree()
        assert tree is not None

    @patch("persona.ui.streaming.sys.stdout")
    def test_build_persona_tree_with_state(self, mock_stdout, streaming):
        """Test building persona tree with state."""
        mock_stdout.isatty.return_value = False
        streaming.start(total=3)

        tree = streaming._build_persona_tree()
        assert tree is not None

    @patch("persona.ui.streaming.sys.stdout")
    def test_build_token_info_empty(self, mock_stdout, streaming):
        """Test building token info with no state."""
        text = streaming._build_token_info()
        assert text is not None

    @patch("persona.ui.streaming.sys.stdout")
    def test_build_token_info_with_state(self, mock_stdout, streaming):
        """Test building token info with state."""
        mock_stdout.isatty.return_value = False
        streaming.start(total=3)

        text = streaming._build_token_info()
        assert text is not None


class TestStreamingOutputIntegration:
    """Integration tests for streaming output."""

    @patch("persona.ui.streaming.sys.stdout")
    def test_full_workflow_non_tty(self, mock_stdout):
        """Test complete workflow in non-TTY mode."""
        mock_stdout.isatty.return_value = False
        console = MagicMock()

        handler = get_progress_handler(console=console, show_progress=True)
        callback = handler.start(total=2, provider="anthropic", model="claude")

        # Simulate progress
        callback("Loading input data...")
        callback("Generating with anthropic...")
        callback("Parsing response...")
        callback("Generation complete!")

        # Simulate personas
        persona1 = MagicMock()
        persona1.name = "Alex"
        persona1.title = "PM"

        persona2 = MagicMock()
        persona2.name = "Jordan"
        persona2.title = "Dev"

        handler.finish(
            personas=[persona1, persona2],
            input_tokens=1000,
            output_tokens=500,
        )

        # Should have called print multiple times
        assert console.print.called
