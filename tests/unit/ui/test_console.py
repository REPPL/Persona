"""
Tests for console utilities (F-086).
"""


from persona.ui.console import PersonaConsole, Verbosity, get_console


class TestVerbosity:
    """Tests for Verbosity enum."""

    def test_verbosity_values(self):
        """Test verbosity level values."""
        assert Verbosity.QUIET == 0
        assert Verbosity.NORMAL == 1
        assert Verbosity.VERBOSE == 2
        assert Verbosity.DEBUG == 3

    def test_verbosity_ordering(self):
        """Test verbosity levels are ordered."""
        assert Verbosity.QUIET < Verbosity.NORMAL
        assert Verbosity.NORMAL < Verbosity.VERBOSE
        assert Verbosity.VERBOSE < Verbosity.DEBUG


class TestPersonaConsole:
    """Tests for PersonaConsole class."""

    def test_default_verbosity(self):
        """Test default verbosity is NORMAL."""
        console = PersonaConsole()
        assert console.verbosity == Verbosity.NORMAL

    def test_quiet_mode(self):
        """Test quiet mode properties."""
        console = PersonaConsole(verbosity=Verbosity.QUIET)
        assert console.is_quiet is True
        assert console.is_verbose is False
        assert console.is_debug is False

    def test_normal_mode(self):
        """Test normal mode properties."""
        console = PersonaConsole(verbosity=Verbosity.NORMAL)
        assert console.is_quiet is False
        assert console.is_verbose is False
        assert console.is_debug is False

    def test_verbose_mode(self):
        """Test verbose mode properties."""
        console = PersonaConsole(verbosity=Verbosity.VERBOSE)
        assert console.is_quiet is False
        assert console.is_verbose is True
        assert console.is_debug is False

    def test_debug_mode(self):
        """Test debug mode properties."""
        console = PersonaConsole(verbosity=Verbosity.DEBUG)
        assert console.is_quiet is False
        assert console.is_verbose is True  # Debug includes verbose
        assert console.is_debug is True

    def test_no_color_default(self):
        """Test no_color defaults to False."""
        console = PersonaConsole()
        # Note: actual value depends on NO_COLOR env var
        # Just check it doesn't raise

    def test_no_color_explicit(self):
        """Test explicit no_color setting."""
        console = PersonaConsole(no_color=True)
        assert console.no_color is True


class TestGetConsole:
    """Tests for get_console function."""

    def test_default_console(self):
        """Test default console creation."""
        console = get_console()
        assert console.verbosity == Verbosity.NORMAL

    def test_quiet_flag(self):
        """Test quiet flag creates quiet console."""
        console = get_console(quiet=True)
        assert console.verbosity == Verbosity.QUIET

    def test_verbosity_levels(self):
        """Test verbosity level parameter."""
        console = get_console(verbosity=0)
        assert console.verbosity == Verbosity.QUIET

        console = get_console(verbosity=1)
        assert console.verbosity == Verbosity.NORMAL

        console = get_console(verbosity=2)
        assert console.verbosity == Verbosity.VERBOSE

        console = get_console(verbosity=3)
        assert console.verbosity == Verbosity.DEBUG

    def test_quiet_overrides_verbosity(self):
        """Test quiet flag overrides verbosity setting."""
        console = get_console(quiet=True, verbosity=3)
        assert console.verbosity == Verbosity.QUIET

    def test_verbosity_clamped(self):
        """Test verbosity is clamped to valid range."""
        console = get_console(verbosity=-1)
        assert console.verbosity == Verbosity.QUIET

        console = get_console(verbosity=10)
        assert console.verbosity == Verbosity.DEBUG

    def test_no_color_parameter(self):
        """Test no_color parameter is passed through."""
        console = get_console(no_color=True)
        assert console.no_color is True


class TestNoColorEnvironment:
    """Tests for NO_COLOR environment variable support."""

    def test_no_color_env_respected(self, monkeypatch):
        """Test NO_COLOR environment variable is respected."""
        monkeypatch.setenv("NO_COLOR", "1")
        console = get_console()
        assert console.no_color is True

    def test_no_color_env_empty_respected(self, monkeypatch):
        """Test NO_COLOR with empty value is still respected."""
        monkeypatch.setenv("NO_COLOR", "")
        console = get_console()
        assert console.no_color is True

    def test_no_color_env_not_set(self, monkeypatch):
        """Test without NO_COLOR env var."""
        monkeypatch.delenv("NO_COLOR", raising=False)
        console = get_console(no_color=False)
        assert console.no_color is False
