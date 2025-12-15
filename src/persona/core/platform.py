"""
Platform utilities for cross-platform support (F-079, F-080, F-081).

Provides platform detection, path management, and cross-platform utilities.
"""

import os
import sys
from pathlib import Path
from typing import Optional


# Platform detection
PLATFORM = sys.platform  # 'win32', 'darwin', 'linux'
IS_WINDOWS = PLATFORM == "win32"
IS_MACOS = PLATFORM == "darwin"
IS_LINUX = PLATFORM.startswith("linux")
IS_POSIX = not IS_WINDOWS


def get_platform_name() -> str:
    """Get a human-readable platform name.

    Returns:
        'windows', 'macos', or 'linux'.
    """
    if IS_WINDOWS:
        return "windows"
    elif IS_MACOS:
        return "macos"
    else:
        return "linux"


def get_config_dir() -> Path:
    """Get platform-appropriate configuration directory.

    Returns:
        Windows: %APPDATA%/persona
        macOS/Linux: ~/.persona
    """
    if IS_WINDOWS:
        # Use APPDATA on Windows (e.g., C:/Users/<user>/AppData/Roaming/persona)
        appdata = os.environ.get("APPDATA")
        if appdata:
            return Path(appdata) / "persona"
        # Fallback to home directory if APPDATA not set
        return Path.home() / ".persona"
    else:
        # Use ~/.persona on Unix-like systems
        return Path.home() / ".persona"


def get_data_dir() -> Path:
    """Get platform-appropriate data directory.

    Returns:
        Windows: %LOCALAPPDATA%/persona
        macOS: ~/Library/Application Support/persona
        Linux: ~/.local/share/persona
    """
    if IS_WINDOWS:
        localappdata = os.environ.get("LOCALAPPDATA")
        if localappdata:
            return Path(localappdata) / "persona"
        return Path.home() / ".persona" / "data"
    elif IS_MACOS:
        return Path.home() / "Library" / "Application Support" / "persona"
    else:
        # XDG Base Directory Specification for Linux
        xdg_data = os.environ.get("XDG_DATA_HOME")
        if xdg_data:
            return Path(xdg_data) / "persona"
        return Path.home() / ".local" / "share" / "persona"


def get_cache_dir() -> Path:
    """Get platform-appropriate cache directory.

    Returns:
        Windows: %LOCALAPPDATA%/persona/cache
        macOS: ~/Library/Caches/persona
        Linux: ~/.cache/persona
    """
    if IS_WINDOWS:
        localappdata = os.environ.get("LOCALAPPDATA")
        if localappdata:
            return Path(localappdata) / "persona" / "cache"
        return Path.home() / ".persona" / "cache"
    elif IS_MACOS:
        return Path.home() / "Library" / "Caches" / "persona"
    else:
        # XDG Base Directory Specification for Linux
        xdg_cache = os.environ.get("XDG_CACHE_HOME")
        if xdg_cache:
            return Path(xdg_cache) / "persona"
        return Path.home() / ".cache" / "persona"


def get_log_dir() -> Path:
    """Get platform-appropriate log directory.

    Returns:
        Windows: %LOCALAPPDATA%/persona/logs
        macOS: ~/Library/Logs/persona
        Linux: ~/.local/state/persona/log
    """
    if IS_WINDOWS:
        localappdata = os.environ.get("LOCALAPPDATA")
        if localappdata:
            return Path(localappdata) / "persona" / "logs"
        return Path.home() / ".persona" / "logs"
    elif IS_MACOS:
        return Path.home() / "Library" / "Logs" / "persona"
    else:
        # XDG Base Directory Specification for Linux
        xdg_state = os.environ.get("XDG_STATE_HOME")
        if xdg_state:
            return Path(xdg_state) / "persona" / "log"
        return Path.home() / ".local" / "state" / "persona" / "log"


def get_temp_dir() -> Path:
    """Get platform-appropriate temporary directory.

    Returns:
        Platform-specific temp directory with persona subdirectory.
    """
    import tempfile
    return Path(tempfile.gettempdir()) / "persona"


def ensure_dir(path: Path) -> Path:
    """Ensure a directory exists, creating it if necessary.

    Args:
        path: Directory path to ensure.

    Returns:
        The path (for chaining).
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_shell_info() -> dict[str, str]:
    """Get information about the current shell environment.

    Returns:
        Dictionary with shell name, path, and capabilities.
    """
    shell = os.environ.get("SHELL", "")
    comspec = os.environ.get("COMSPEC", "")

    if IS_WINDOWS:
        if "powershell" in comspec.lower():
            shell_name = "powershell"
        else:
            shell_name = "cmd"
        shell_path = comspec
    else:
        shell_path = shell
        if "zsh" in shell:
            shell_name = "zsh"
        elif "bash" in shell:
            shell_name = "bash"
        elif "fish" in shell:
            shell_name = "fish"
        else:
            shell_name = "sh"

    return {
        "name": shell_name,
        "path": shell_path,
        "platform": PLATFORM,
    }


def normalise_path(path: str | Path) -> Path:
    """Normalise a path for the current platform.

    Handles:
    - Expanding ~ to home directory
    - Converting separators
    - Resolving .. and .

    Args:
        path: Path string or Path object.

    Returns:
        Normalised Path object.
    """
    p = Path(path).expanduser()
    # Don't resolve symlinks, just normalise
    return Path(os.path.normpath(p))


def path_to_posix(path: Path) -> str:
    """Convert path to POSIX-style string (for config files).

    Args:
        path: Path to convert.

    Returns:
        POSIX-style path string with forward slashes.
    """
    return path.as_posix()


def is_executable(path: Path) -> bool:
    """Check if a file is executable.

    Args:
        path: Path to check.

    Returns:
        True if the file exists and is executable.
    """
    if not path.exists():
        return False

    if IS_WINDOWS:
        # On Windows, check file extension
        return path.suffix.lower() in {".exe", ".cmd", ".bat", ".ps1", ".com"}
    else:
        # On Unix, check execute permission
        return os.access(path, os.X_OK)


def find_executable(name: str) -> Optional[Path]:
    """Find an executable in the system PATH.

    Args:
        name: Name of executable to find.

    Returns:
        Path to executable or None if not found.
    """
    import shutil
    result = shutil.which(name)
    return Path(result) if result else None


def get_python_executable() -> Path:
    """Get the current Python executable path.

    Returns:
        Path to the Python interpreter.
    """
    return Path(sys.executable)


class PathManager:
    """Manager for platform-independent paths (F-081).

    Provides a centralised way to access all Persona directories.
    """

    def __init__(self):
        """Initialise path manager."""
        self._config_dir: Optional[Path] = None
        self._data_dir: Optional[Path] = None
        self._cache_dir: Optional[Path] = None
        self._log_dir: Optional[Path] = None

    @property
    def config_dir(self) -> Path:
        """Get configuration directory."""
        if self._config_dir is None:
            self._config_dir = get_config_dir()
        return self._config_dir

    @property
    def data_dir(self) -> Path:
        """Get data directory."""
        if self._data_dir is None:
            self._data_dir = get_data_dir()
        return self._data_dir

    @property
    def cache_dir(self) -> Path:
        """Get cache directory."""
        if self._cache_dir is None:
            self._cache_dir = get_cache_dir()
        return self._cache_dir

    @property
    def log_dir(self) -> Path:
        """Get log directory."""
        if self._log_dir is None:
            self._log_dir = get_log_dir()
        return self._log_dir

    @property
    def temp_dir(self) -> Path:
        """Get temporary directory."""
        return get_temp_dir()

    @property
    def global_config_file(self) -> Path:
        """Get global configuration file path."""
        return self.config_dir / "config.yaml"

    def ensure_all(self) -> None:
        """Ensure all directories exist."""
        ensure_dir(self.config_dir)
        ensure_dir(self.data_dir)
        ensure_dir(self.cache_dir)
        ensure_dir(self.log_dir)

    def get_config_dir(self) -> Path:
        """Get configuration directory.

        Returns:
            Path to configuration directory.
        """
        return self.config_dir

    def get_data_dir(self) -> Path:
        """Get data directory.

        Returns:
            Path to data directory.
        """
        return self.data_dir

    def get_cache_dir(self) -> Path:
        """Get cache directory.

        Returns:
            Path to cache directory.
        """
        return self.cache_dir

    def get_log_dir(self) -> Path:
        """Get log directory.

        Returns:
            Path to log directory.
        """
        return self.log_dir

    def get_temp_dir(self) -> Path:
        """Get temporary directory.

        Returns:
            Path to temporary directory.
        """
        return self.temp_dir

    def normalize_path(self, path: str | Path) -> Path:
        """Normalise a path for the current platform.

        Handles:
        - Expanding ~ to home directory
        - Converting separators
        - Resolving .. and .

        Args:
            path: Path string or Path object.

        Returns:
            Normalised Path object.
        """
        return normalise_path(path)

    def get_platform_info(self) -> dict:
        """Get platform information.

        Returns:
            Dictionary with platform details.
        """
        import platform as plat

        return {
            "system": plat.system(),
            "release": plat.release(),
            "version": plat.version(),
            "machine": plat.machine(),
            "python_version": plat.python_version(),
            "is_windows": IS_WINDOWS,
            "is_macos": IS_MACOS,
            "is_linux": IS_LINUX,
            "config_dir": str(self.config_dir),
            "data_dir": str(self.data_dir),
            "cache_dir": str(self.cache_dir),
            "log_dir": str(self.log_dir),
        }


# Module-level singleton
_path_manager: Optional[PathManager] = None


def get_path_manager() -> PathManager:
    """Get the global path manager instance.

    Returns:
        PathManager singleton.
    """
    global _path_manager
    if _path_manager is None:
        _path_manager = PathManager()
    return _path_manager
