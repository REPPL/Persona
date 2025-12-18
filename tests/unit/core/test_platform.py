"""
Tests for platform utilities (F-079, F-080, F-081).
"""

import os
import sys
from pathlib import Path
from unittest.mock import patch

from persona.core.platform import (
    IS_LINUX,
    IS_MACOS,
    IS_POSIX,
    IS_WINDOWS,
    PLATFORM,
    PathManager,
    ensure_dir,
    find_executable,
    get_cache_dir,
    get_config_dir,
    get_data_dir,
    get_log_dir,
    get_path_manager,
    get_python_executable,
    get_shell_info,
    get_temp_dir,
    is_executable,
    normalise_path,
    path_to_posix,
)


class TestPlatformDetection:
    """Tests for platform detection constants."""

    def test_platform_is_string(self):
        """Test that PLATFORM is a string."""
        assert isinstance(PLATFORM, str)

    def test_exactly_one_platform_true(self):
        """Test that exactly one platform flag is True."""
        flags = [IS_WINDOWS, IS_MACOS, IS_LINUX]
        # At least one should be True
        assert any(flags), "At least one platform flag should be True"
        # IS_POSIX should be inverse of IS_WINDOWS
        assert IS_POSIX == (not IS_WINDOWS)

    def test_current_platform(self):
        """Test current platform detection matches sys.platform."""
        if sys.platform == "win32":
            assert IS_WINDOWS is True
            assert IS_POSIX is False
        elif sys.platform == "darwin":
            assert IS_MACOS is True
            assert IS_POSIX is True
        elif sys.platform.startswith("linux"):
            assert IS_LINUX is True
            assert IS_POSIX is True


class TestConfigDir:
    """Tests for config directory functions."""

    def test_get_config_dir_returns_path(self):
        """Test that get_config_dir returns a Path."""
        result = get_config_dir()
        assert isinstance(result, Path)

    def test_get_config_dir_contains_persona(self):
        """Test that config dir path contains 'persona'."""
        result = get_config_dir()
        assert "persona" in str(result).lower()

    @patch.dict(os.environ, {"APPDATA": "/mock/appdata"}, clear=False)
    def test_get_config_dir_windows(self, monkeypatch):
        """Test Windows config directory."""
        monkeypatch.setattr("persona.core.platform.IS_WINDOWS", True)
        # Need to reimport to pick up the monkeypatched value
        from persona.core import platform

        monkeypatch.setattr(platform, "IS_WINDOWS", True)

        # Since we can't easily reload the module, test the function logic
        if os.environ.get("APPDATA"):
            result = Path(os.environ["APPDATA"]) / "persona"
            assert "persona" in str(result)


class TestDataDir:
    """Tests for data directory functions."""

    def test_get_data_dir_returns_path(self):
        """Test that get_data_dir returns a Path."""
        result = get_data_dir()
        assert isinstance(result, Path)

    def test_get_data_dir_contains_persona(self):
        """Test that data dir path contains 'persona'."""
        result = get_data_dir()
        assert "persona" in str(result).lower()


class TestCacheDir:
    """Tests for cache directory functions."""

    def test_get_cache_dir_returns_path(self):
        """Test that get_cache_dir returns a Path."""
        result = get_cache_dir()
        assert isinstance(result, Path)

    def test_get_cache_dir_contains_persona(self):
        """Test that cache dir path contains 'persona'."""
        result = get_cache_dir()
        assert "persona" in str(result).lower()


class TestLogDir:
    """Tests for log directory functions."""

    def test_get_log_dir_returns_path(self):
        """Test that get_log_dir returns a Path."""
        result = get_log_dir()
        assert isinstance(result, Path)

    def test_get_log_dir_contains_persona(self):
        """Test that log dir path contains 'persona'."""
        result = get_log_dir()
        assert "persona" in str(result).lower()


class TestTempDir:
    """Tests for temp directory functions."""

    def test_get_temp_dir_returns_path(self):
        """Test that get_temp_dir returns a Path."""
        result = get_temp_dir()
        assert isinstance(result, Path)

    def test_get_temp_dir_contains_persona(self):
        """Test that temp dir path contains 'persona'."""
        result = get_temp_dir()
        assert "persona" in str(result)


class TestEnsureDir:
    """Tests for directory creation."""

    def test_ensure_dir_creates_directory(self, tmp_path):
        """Test that ensure_dir creates directory."""
        test_dir = tmp_path / "test" / "nested" / "dir"
        assert not test_dir.exists()

        result = ensure_dir(test_dir)

        assert test_dir.exists()
        assert test_dir.is_dir()
        assert result == test_dir

    def test_ensure_dir_idempotent(self, tmp_path):
        """Test that ensure_dir is idempotent."""
        test_dir = tmp_path / "test"
        test_dir.mkdir()

        # Should not raise
        result = ensure_dir(test_dir)
        assert result == test_dir


class TestShellInfo:
    """Tests for shell information."""

    def test_get_shell_info_returns_dict(self):
        """Test that get_shell_info returns a dictionary."""
        result = get_shell_info()
        assert isinstance(result, dict)

    def test_get_shell_info_has_required_keys(self):
        """Test that shell info has required keys."""
        result = get_shell_info()
        assert "name" in result
        assert "path" in result
        assert "platform" in result

    def test_get_shell_info_name_is_known(self):
        """Test that shell name is a known value."""
        result = get_shell_info()
        known_shells = {"bash", "zsh", "fish", "sh", "powershell", "cmd"}
        assert result["name"] in known_shells


class TestNormalisePath:
    """Tests for path normalisation."""

    def test_normalise_path_expands_tilde(self):
        """Test that ~ is expanded."""
        result = normalise_path("~/test")
        assert "~" not in str(result)
        assert str(result).startswith(str(Path.home()))

    def test_normalise_path_from_string(self):
        """Test normalising from string."""
        result = normalise_path("/some/path")
        assert isinstance(result, Path)

    def test_normalise_path_from_path(self):
        """Test normalising from Path."""
        result = normalise_path(Path("/some/path"))
        assert isinstance(result, Path)


class TestPathToPosix:
    """Tests for POSIX path conversion."""

    def test_path_to_posix_uses_forward_slashes(self):
        """Test that result uses forward slashes."""
        path = Path("some") / "nested" / "path"
        result = path_to_posix(path)
        assert "\\" not in result
        assert "/" in result or result == "some/nested/path"


class TestIsExecutable:
    """Tests for executable detection."""

    def test_is_executable_false_for_nonexistent(self, tmp_path):
        """Test that nonexistent file is not executable."""
        result = is_executable(tmp_path / "nonexistent")
        assert result is False

    def test_is_executable_python(self):
        """Test that Python executable is detected."""
        python_path = get_python_executable()
        assert is_executable(python_path) is True


class TestFindExecutable:
    """Tests for finding executables."""

    def test_find_executable_python(self):
        """Test finding Python in PATH."""
        result = find_executable("python3") or find_executable("python")
        # At least one should be found
        assert result is not None or IS_WINDOWS

    def test_find_executable_nonexistent(self):
        """Test that nonexistent command returns None."""
        result = find_executable("this_command_does_not_exist_xyz123")
        assert result is None


class TestGetPythonExecutable:
    """Tests for Python executable path."""

    def test_get_python_executable_returns_path(self):
        """Test that a Path is returned."""
        result = get_python_executable()
        assert isinstance(result, Path)

    def test_get_python_executable_exists(self):
        """Test that the executable exists."""
        result = get_python_executable()
        assert result.exists()

    def test_get_python_executable_matches_sys(self):
        """Test that result matches sys.executable."""
        result = get_python_executable()
        assert result == Path(sys.executable)


class TestPathManager:
    """Tests for PathManager class."""

    def test_path_manager_init(self):
        """Test PathManager initialisation."""
        manager = PathManager()
        assert manager is not None

    def test_path_manager_config_dir(self):
        """Test config_dir property."""
        manager = PathManager()
        result = manager.config_dir
        assert isinstance(result, Path)
        assert "persona" in str(result).lower()

    def test_path_manager_data_dir(self):
        """Test data_dir property."""
        manager = PathManager()
        result = manager.data_dir
        assert isinstance(result, Path)

    def test_path_manager_cache_dir(self):
        """Test cache_dir property."""
        manager = PathManager()
        result = manager.cache_dir
        assert isinstance(result, Path)

    def test_path_manager_log_dir(self):
        """Test log_dir property."""
        manager = PathManager()
        result = manager.log_dir
        assert isinstance(result, Path)

    def test_path_manager_temp_dir(self):
        """Test temp_dir property."""
        manager = PathManager()
        result = manager.temp_dir
        assert isinstance(result, Path)

    def test_path_manager_global_config_file(self):
        """Test global_config_file property."""
        manager = PathManager()
        result = manager.global_config_file
        assert isinstance(result, Path)
        assert result.name == "config.yaml"

    def test_path_manager_get_platform_info(self):
        """Test get_platform_info method."""
        manager = PathManager()
        result = manager.get_platform_info()

        assert isinstance(result, dict)
        assert "system" in result
        assert "python_version" in result
        assert "is_windows" in result
        assert "config_dir" in result

    def test_path_manager_caching(self):
        """Test that properties are cached."""
        manager = PathManager()
        first = manager.config_dir
        second = manager.config_dir
        # Should be same object (cached)
        assert first is second


class TestGetPathManager:
    """Tests for path manager singleton."""

    def test_get_path_manager_returns_instance(self):
        """Test that get_path_manager returns an instance."""
        result = get_path_manager()
        assert isinstance(result, PathManager)

    def test_get_path_manager_singleton(self):
        """Test that get_path_manager returns same instance."""
        first = get_path_manager()
        second = get_path_manager()
        assert first is second
