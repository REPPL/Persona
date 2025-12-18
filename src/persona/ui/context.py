"""
CLI context management.

Provides a thread-safe context for CLI state, replacing global variables
with a more maintainable and testable pattern.
"""

import threading
from dataclasses import dataclass


@dataclass
class CLIContext:
    """
    Context for CLI state.

    Encapsulates all global CLI state in a single object for:
    - Thread safety
    - Testability (easy to create isolated contexts)
    - Clear state management
    """

    no_color: bool = False
    quiet: bool = False
    verbosity: int = 1  # 0=quiet, 1=normal, 2=verbose, 3=debug
    interactive: bool = False

    def reset(self) -> None:
        """Reset context to default values."""
        self.no_color = False
        self.quiet = False
        self.verbosity = 1
        self.interactive = False

    def set_quiet(self, value: bool) -> None:
        """Set quiet mode, also updating verbosity."""
        self.quiet = value
        if value:
            self.verbosity = 0

    def set_verbose(self, level: int) -> None:
        """Set verbosity level (capped at 3)."""
        if level:
            self.verbosity = min(level + 1, 3)

    @property
    def is_verbose(self) -> bool:
        """Check if verbose mode is enabled."""
        return self.verbosity >= 2

    @property
    def is_debug(self) -> bool:
        """Check if debug mode is enabled."""
        return self.verbosity >= 3


class _CLIContextManager:
    """
    Thread-safe manager for CLI context.

    Provides a singleton-like pattern with thread-local storage
    for safe concurrent access.
    """

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._default = CLIContext()
        self._local = threading.local()

    @property
    def current(self) -> CLIContext:
        """Get current context (thread-local if set, else default)."""
        return getattr(self._local, "context", self._default)

    def get(self) -> CLIContext:
        """Get current context."""
        return self.current

    def set(self, context: CLIContext) -> None:
        """Set thread-local context."""
        self._local.context = context

    def reset(self) -> None:
        """Reset to default context."""
        with self._lock:
            self._default.reset()
            if hasattr(self._local, "context"):
                del self._local.context

    def create_isolated(self) -> CLIContext:
        """Create an isolated context for testing."""
        return CLIContext()

    # Property accessors for backwards compatibility
    @property
    def no_color(self) -> bool:
        """Get no_color from current context."""
        return self.current.no_color

    @no_color.setter
    def no_color(self, value: bool) -> None:
        """Set no_color on current context."""
        self.current.no_color = value

    @property
    def quiet(self) -> bool:
        """Get quiet from current context."""
        return self.current.quiet

    @quiet.setter
    def quiet(self, value: bool) -> None:
        """Set quiet on current context (also updates verbosity)."""
        self.current.set_quiet(value)

    @property
    def verbosity(self) -> int:
        """Get verbosity from current context."""
        return self.current.verbosity

    @verbosity.setter
    def verbosity(self, value: int) -> None:
        """Set verbosity on current context."""
        self.current.verbosity = value

    @property
    def interactive(self) -> bool:
        """Get interactive from current context."""
        return self.current.interactive

    @interactive.setter
    def interactive(self, value: bool) -> None:
        """Set interactive on current context."""
        self.current.interactive = value


# Global context manager instance
_context_manager = _CLIContextManager()


def get_cli_context() -> CLIContext:
    """
    Get the current CLI context.

    Returns:
        Current CLI context instance.
    """
    return _context_manager.current


def set_cli_context(context: CLIContext) -> None:
    """
    Set the current CLI context (thread-local).

    Args:
        context: Context to set.
    """
    _context_manager.set(context)


def reset_cli_context() -> None:
    """Reset CLI context to defaults."""
    _context_manager.reset()


def create_isolated_context() -> CLIContext:
    """
    Create an isolated context for testing.

    Returns:
        New isolated CLIContext instance.
    """
    return _context_manager.create_isolated()


# Backwards-compatible accessors
def get_no_color() -> bool:
    """Get no_color setting."""
    return _context_manager.no_color


def set_no_color(value: bool) -> None:
    """Set no_color setting."""
    _context_manager.no_color = value


def get_quiet() -> bool:
    """Get quiet setting."""
    return _context_manager.quiet


def set_quiet(value: bool) -> None:
    """Set quiet setting."""
    _context_manager.quiet = value


def get_verbosity() -> int:
    """Get verbosity level."""
    return _context_manager.verbosity


def set_verbosity(value: int) -> None:
    """Set verbosity level."""
    _context_manager.verbosity = value


def get_interactive() -> bool:
    """Get interactive setting."""
    return _context_manager.interactive


def set_interactive(value: bool) -> None:
    """Set interactive setting."""
    _context_manager.interactive = value
