"""
Data file listing (F-064).

Tracks data source files used in persona generation for
reproducibility and auditing.
"""

import hashlib
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class SourceMetadata:
    """
    Metadata for a single data source file.
    
    Includes hash for integrity verification.
    """
    
    path: Path
    relative_path: str
    size_bytes: int
    modified: datetime
    format: str
    sha256: str
    tokens: int = 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "path": str(self.path),
            "relative_path": self.relative_path,
            "size_bytes": self.size_bytes,
            "modified": self.modified.isoformat(),
            "format": self.format,
            "sha256": self.sha256,
            "tokens": self.tokens,
        }


@dataclass
class SourceSummary:
    """
    Summary of all data sources.
    
    Aggregates metadata for all source files.
    """
    
    files: list[SourceMetadata] = field(default_factory=list)
    total_files: int = 0
    total_size_bytes: int = 0
    total_tokens: int = 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "files": [f.to_dict() for f in self.files],
            "total_files": self.total_files,
            "total_size_bytes": self.total_size_bytes,
            "total_tokens": self.total_tokens,
        }
    
    def to_markdown_table(self) -> str:
        """
        Generate markdown table of sources.
        
        Returns:
            Markdown formatted table.
        """
        if not self.files:
            return "No data sources recorded."
        
        lines = [
            "| File | Size | Modified | Tokens |",
            "|------|------|----------|--------|",
        ]
        
        for source in self.files:
            size_str = _format_size(source.size_bytes)
            date_str = source.modified.strftime("%Y-%m-%d")
            tokens_str = f"{source.tokens:,}" if source.tokens else "-"
            
            lines.append(
                f"| {source.relative_path} | {size_str} | {date_str} | {tokens_str} |"
            )
        
        # Add totals
        total_size = _format_size(self.total_size_bytes)
        total_tokens = f"{self.total_tokens:,}" if self.total_tokens else "-"
        lines.append("")
        lines.append(f"**Total:** {self.total_files} files, {total_size}, {total_tokens} tokens")
        
        return "\n".join(lines)


class DataSourceTracker:
    """
    Tracks data source files.
    
    Records metadata, calculates hashes, and generates summaries.
    
    Example:
        >>> tracker = DataSourceTracker()
        >>> tracker.add_file(Path("./interviews/p001.md"))
        >>> tracker.add_file(Path("./interviews/p002.md"))
        >>> summary = tracker.get_summary()
    """
    
    def __init__(
        self,
        base_path: Path | None = None,
        token_counter: Any | None = None,
    ):
        """
        Initialise the tracker.
        
        Args:
            base_path: Base path for relative path calculation.
            token_counter: Optional TokenCounter for counting tokens.
        """
        self._base_path = base_path or Path(".")
        self._token_counter = token_counter
        self._sources: list[SourceMetadata] = []
    
    def add_file(
        self,
        path: Path,
        content: str | None = None,
        tokens: int | None = None,
    ) -> SourceMetadata:
        """
        Add a file to tracking.
        
        Args:
            path: File path.
            content: Optional pre-loaded content (for hash calculation).
            tokens: Optional pre-counted token count.
        
        Returns:
            SourceMetadata for the file.
        """
        path = Path(path).resolve()
        
        # Read content if not provided
        if content is None and path.exists():
            content = path.read_text(encoding="utf-8")
        
        # Get file stats
        stat = path.stat() if path.exists() else None
        
        # Calculate hash
        file_hash = self._calculate_hash(content or "")
        
        # Calculate relative path
        try:
            relative = path.relative_to(self._base_path.resolve())
        except ValueError:
            relative = path.name
        
        # Count tokens if counter available
        if tokens is None and self._token_counter and content:
            tokens = self._token_counter.count_tokens(content)
        
        metadata = SourceMetadata(
            path=path,
            relative_path=str(relative),
            size_bytes=stat.st_size if stat else len(content or ""),
            modified=datetime.fromtimestamp(stat.st_mtime) if stat else datetime.now(),
            format=self._detect_format(path),
            sha256=file_hash,
            tokens=tokens or 0,
        )
        
        self._sources.append(metadata)
        return metadata
    
    def add_files(
        self,
        paths: list[Path],
    ) -> list[SourceMetadata]:
        """
        Add multiple files.
        
        Args:
            paths: List of file paths.
        
        Returns:
            List of SourceMetadata.
        """
        return [self.add_file(path) for path in paths]
    
    def get_summary(self) -> SourceSummary:
        """
        Get summary of all tracked sources.
        
        Returns:
            SourceSummary with aggregated data.
        """
        return SourceSummary(
            files=list(self._sources),
            total_files=len(self._sources),
            total_size_bytes=sum(s.size_bytes for s in self._sources),
            total_tokens=sum(s.tokens for s in self._sources),
        )
    
    def get_metadata(self) -> dict:
        """
        Get metadata for output.
        
        Returns:
            Dictionary suitable for JSON serialisation.
        """
        summary = self.get_summary()
        return {
            "data_sources": summary.to_dict(),
        }
    
    def generate_readme_section(self) -> str:
        """
        Generate README section for data sources.
        
        Returns:
            Markdown section content.
        """
        summary = self.get_summary()
        
        lines = [
            "## Data Sources",
            "",
            f"This persona set was generated from {summary.total_files} data files:",
            "",
            summary.to_markdown_table(),
        ]
        
        return "\n".join(lines)
    
    def verify_integrity(self) -> list[tuple[SourceMetadata, bool, str]]:
        """
        Verify integrity of tracked files.
        
        Returns:
            List of (metadata, is_valid, message) tuples.
        """
        results = []
        
        for source in self._sources:
            if not source.path.exists():
                results.append((source, False, "File not found"))
                continue
            
            current_hash = self._calculate_hash(
                source.path.read_text(encoding="utf-8")
            )
            
            if current_hash == source.sha256:
                results.append((source, True, "OK"))
            else:
                results.append((source, False, "Hash mismatch - file modified"))
        
        return results
    
    def clear(self) -> None:
        """Clear all tracked sources."""
        self._sources.clear()
    
    def _calculate_hash(self, content: str) -> str:
        """Calculate SHA256 hash of content."""
        return hashlib.sha256(content.encode("utf-8")).hexdigest()[:16]
    
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


def _format_size(size_bytes: int) -> str:
    """Format size in human-readable form."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def track_sources(
    paths: list[Path],
    base_path: Path | None = None,
) -> SourceSummary:
    """
    Convenience function to track source files.
    
    Args:
        paths: File paths to track.
        base_path: Base path for relative paths.
    
    Returns:
        SourceSummary with file information.
    """
    tracker = DataSourceTracker(base_path=base_path)
    tracker.add_files(paths)
    return tracker.get_summary()
