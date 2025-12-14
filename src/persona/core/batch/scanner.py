"""
Folder processing (F-059).

Provides recursive folder scanning with glob pattern support
for discovering data files.
"""

import fnmatch
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Iterator


class FileOrder(Enum):
    """File ordering options."""
    
    ALPHABETICAL = "alphabetical"
    MODIFIED_ASC = "modified_asc"
    MODIFIED_DESC = "modified_desc"
    SIZE_ASC = "size_asc"
    SIZE_DESC = "size_desc"


@dataclass
class FileInfo:
    """Information about a discovered file."""
    
    path: Path
    size_bytes: int
    modified: datetime
    format: str
    relative_path: str = ""
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "path": str(self.path),
            "relative_path": self.relative_path,
            "size_bytes": self.size_bytes,
            "modified": self.modified.isoformat(),
            "format": self.format,
        }


@dataclass
class ScanResult:
    """Result of a folder scan."""
    
    files: list[FileInfo] = field(default_factory=list)
    total_files: int = 0
    total_size_bytes: int = 0
    excluded_count: int = 0
    scan_path: Path | None = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "files": [f.to_dict() for f in self.files],
            "total_files": self.total_files,
            "total_size_bytes": self.total_size_bytes,
            "excluded_count": self.excluded_count,
            "scan_path": str(self.scan_path) if self.scan_path else None,
        }


class FolderScanner:
    """
    Scans folders for data files.
    
    Supports recursive scanning, glob patterns, and exclusion patterns.
    
    Example:
        >>> scanner = FolderScanner()
        >>> result = scanner.scan("./interviews/")
        >>> for file in result.files:
        ...     print(file.path)
    """
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS: set[str] = {
        ".csv", ".json", ".md", ".markdown", ".txt", ".yaml", ".yml",
    }
    
    def __init__(
        self,
        extensions: set[str] | None = None,
        exclude_patterns: list[str] | None = None,
        order: FileOrder = FileOrder.ALPHABETICAL,
    ):
        """
        Initialise the scanner.
        
        Args:
            extensions: Supported file extensions. Defaults to common data formats.
            exclude_patterns: Glob patterns for files to exclude.
            order: How to order discovered files.
        """
        self._extensions = extensions or self.SUPPORTED_EXTENSIONS
        self._exclude_patterns = exclude_patterns or []
        self._order = order
    
    def scan(
        self,
        path: str | Path,
        recursive: bool = True,
        pattern: str | None = None,
    ) -> ScanResult:
        """
        Scan a folder for data files.
        
        Args:
            path: Folder path or glob pattern.
            recursive: Whether to scan subdirectories.
            pattern: Optional glob pattern to filter files.
        
        Returns:
            ScanResult with discovered files.
        """
        path = Path(path)
        result = ScanResult(scan_path=path)
        
        # Handle glob patterns in path
        if "*" in str(path) or "?" in str(path):
            files = self._scan_glob(path)
        elif path.is_file():
            # Single file
            files = [path] if self._is_supported(path) else []
        elif path.is_dir():
            # Directory scan
            files = self._scan_directory(path, recursive, pattern)
        else:
            # Path doesn't exist
            return result
        
        # Process discovered files
        excluded = 0
        for file_path in files:
            if self._is_excluded(file_path):
                excluded += 1
                continue
            
            file_info = self._create_file_info(file_path, path)
            result.files.append(file_info)
        
        # Sort files
        result.files = self._sort_files(result.files)
        
        # Calculate totals
        result.total_files = len(result.files)
        result.total_size_bytes = sum(f.size_bytes for f in result.files)
        result.excluded_count = excluded
        
        return result
    
    def scan_multiple(
        self,
        paths: list[str | Path],
        recursive: bool = True,
    ) -> ScanResult:
        """
        Scan multiple folders.
        
        Args:
            paths: List of folder paths.
            recursive: Whether to scan subdirectories.
        
        Returns:
            Combined ScanResult.
        """
        combined = ScanResult()
        seen_paths: set[Path] = set()
        
        for path in paths:
            result = self.scan(path, recursive)
            for file_info in result.files:
                if file_info.path not in seen_paths:
                    combined.files.append(file_info)
                    seen_paths.add(file_info.path)
            combined.excluded_count += result.excluded_count
        
        combined.files = self._sort_files(combined.files)
        combined.total_files = len(combined.files)
        combined.total_size_bytes = sum(f.size_bytes for f in combined.files)
        
        return combined
    
    def add_exclude_pattern(self, pattern: str) -> None:
        """Add an exclusion pattern."""
        self._exclude_patterns.append(pattern)
    
    def set_order(self, order: FileOrder) -> None:
        """Set file ordering."""
        self._order = order
    
    def _scan_directory(
        self,
        directory: Path,
        recursive: bool,
        pattern: str | None,
    ) -> Iterator[Path]:
        """Scan a directory for files."""
        if recursive:
            glob_pattern = "**/*" if pattern is None else f"**/{pattern}"
            for file_path in directory.glob(glob_pattern):
                if file_path.is_file() and self._is_supported(file_path):
                    yield file_path
        else:
            glob_pattern = "*" if pattern is None else pattern
            for file_path in directory.glob(glob_pattern):
                if file_path.is_file() and self._is_supported(file_path):
                    yield file_path
    
    def _scan_glob(self, pattern: Path) -> Iterator[Path]:
        """Scan using a glob pattern."""
        # Get the base directory (first part without glob chars)
        parts = pattern.parts
        base_parts = []
        for part in parts:
            if "*" in part or "?" in part:
                break
            base_parts.append(part)
        
        if base_parts:
            base_dir = Path(*base_parts)
        else:
            base_dir = Path(".")
        
        # Build the remaining glob pattern
        remaining = str(pattern).replace(str(base_dir), "").lstrip("/\\")
        
        if base_dir.exists():
            for file_path in base_dir.glob(remaining):
                if file_path.is_file() and self._is_supported(file_path):
                    yield file_path
    
    def _is_supported(self, path: Path) -> bool:
        """Check if file extension is supported."""
        return path.suffix.lower() in self._extensions
    
    def _is_excluded(self, path: Path) -> bool:
        """Check if file matches exclusion patterns."""
        path_str = str(path)
        for pattern in self._exclude_patterns:
            if fnmatch.fnmatch(path_str, pattern):
                return True
            if fnmatch.fnmatch(path.name, pattern):
                return True
        return False
    
    def _create_file_info(self, path: Path, base_path: Path) -> FileInfo:
        """Create FileInfo from a path."""
        stat = path.stat()
        
        # Calculate relative path
        try:
            if base_path.is_dir():
                relative = path.relative_to(base_path)
            else:
                relative = path.name
        except ValueError:
            relative = path.name
        
        return FileInfo(
            path=path.resolve(),
            size_bytes=stat.st_size,
            modified=datetime.fromtimestamp(stat.st_mtime),
            format=self._detect_format(path),
            relative_path=str(relative),
        )
    
    def _detect_format(self, path: Path) -> str:
        """Detect file format from extension."""
        ext = path.suffix.lower()
        format_map = {
            ".csv": "csv",
            ".json": "json",
            ".md": "markdown",
            ".markdown": "markdown",
            ".txt": "text",
            ".yaml": "yaml",
            ".yml": "yaml",
        }
        return format_map.get(ext, "unknown")
    
    def _sort_files(self, files: list[FileInfo]) -> list[FileInfo]:
        """Sort files according to configured order."""
        if self._order == FileOrder.ALPHABETICAL:
            return sorted(files, key=lambda f: f.path.name.lower())
        elif self._order == FileOrder.MODIFIED_ASC:
            return sorted(files, key=lambda f: f.modified)
        elif self._order == FileOrder.MODIFIED_DESC:
            return sorted(files, key=lambda f: f.modified, reverse=True)
        elif self._order == FileOrder.SIZE_ASC:
            return sorted(files, key=lambda f: f.size_bytes)
        elif self._order == FileOrder.SIZE_DESC:
            return sorted(files, key=lambda f: f.size_bytes, reverse=True)
        return files


def scan_folder(
    path: str | Path,
    recursive: bool = True,
    exclude: list[str] | None = None,
) -> ScanResult:
    """
    Convenience function to scan a folder.
    
    Args:
        path: Folder path.
        recursive: Whether to scan subdirectories.
        exclude: Patterns to exclude.
    
    Returns:
        ScanResult with discovered files.
    """
    scanner = FolderScanner(exclude_patterns=exclude)
    return scanner.scan(path, recursive)
