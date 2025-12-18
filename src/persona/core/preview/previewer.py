"""
Data preview functionality.

This module provides the DataPreviewer class for previewing data files
before incurring LLM costs during persona generation.
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from persona.core.cost import CostEstimator
from persona.core.data import DataLoader


class IssueSeverity(Enum):
    """Severity levels for preview issues."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class PreviewIssue:
    """
    An issue detected during data preview.

    Attributes:
        severity: Issue severity level.
        message: Human-readable issue description.
        file_path: Path to the affected file (if applicable).
        details: Additional details about the issue.
    """

    severity: IssueSeverity
    message: str
    file_path: Path | None = None
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class FilePreview:
    """
    Preview information for a single file.

    Attributes:
        file_path: Path to the file.
        format: Detected file format.
        size_bytes: File size in bytes.
        token_count: Estimated token count.
        line_count: Number of lines in file.
        sample_content: Preview of file content.
        issues: Any issues detected with this file.
        loadable: Whether the file can be loaded.
    """

    file_path: Path
    format: str
    size_bytes: int = 0
    token_count: int = 0
    line_count: int = 0
    sample_content: str = ""
    issues: list[PreviewIssue] = field(default_factory=list)
    loadable: bool = True

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file": str(self.file_path),
            "format": self.format,
            "size_bytes": self.size_bytes,
            "token_count": self.token_count,
            "line_count": self.line_count,
            "sample_content": self.sample_content,
            "issues": [
                {
                    "severity": issue.severity.value,
                    "message": issue.message,
                }
                for issue in self.issues
            ],
            "loadable": self.loadable,
        }


@dataclass
class PreviewResult:
    """
    Complete preview result for one or more files.

    Attributes:
        files: Preview information for each file.
        total_files: Total number of files.
        total_tokens: Total estimated tokens.
        total_size_bytes: Total size in bytes.
        estimated_cost_usd: Estimated cost in USD.
        issues: Global issues (not file-specific).
        model: Model used for cost estimation.
        persona_count: Number of personas to generate.
    """

    files: list[FilePreview] = field(default_factory=list)
    total_files: int = 0
    total_tokens: int = 0
    total_size_bytes: int = 0
    estimated_cost_usd: float = 0.0
    issues: list[PreviewIssue] = field(default_factory=list)
    model: str = ""
    persona_count: int = 3

    @property
    def has_errors(self) -> bool:
        """Check if any errors were detected."""
        if any(i.severity == IssueSeverity.ERROR for i in self.issues):
            return True
        for file_preview in self.files:
            if any(i.severity == IssueSeverity.ERROR for i in file_preview.issues):
                return True
        return False

    @property
    def has_warnings(self) -> bool:
        """Check if any warnings were detected."""
        if any(i.severity == IssueSeverity.WARNING for i in self.issues):
            return True
        for file_preview in self.files:
            if any(i.severity == IssueSeverity.WARNING for i in file_preview.issues):
                return True
        return False

    @property
    def loadable_files(self) -> list[FilePreview]:
        """Return only loadable files."""
        return [f for f in self.files if f.loadable]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_files": self.total_files,
            "loadable_files": len(self.loadable_files),
            "total_tokens": self.total_tokens,
            "total_size_bytes": self.total_size_bytes,
            "estimated_cost_usd": self.estimated_cost_usd,
            "model": self.model,
            "persona_count": self.persona_count,
            "has_errors": self.has_errors,
            "has_warnings": self.has_warnings,
            "files": [f.to_dict() for f in self.files],
            "issues": [
                {
                    "severity": issue.severity.value,
                    "message": issue.message,
                }
                for issue in self.issues
            ],
        }


class DataPreviewer:
    """
    Previews data files before persona generation.

    Provides information about file formats, token counts, costs,
    and potential issues without making any LLM API calls.

    Example:
        previewer = DataPreviewer()
        result = previewer.preview(Path("./data"))
        print(f"Total tokens: {result.total_tokens}")
        print(f"Estimated cost: ${result.estimated_cost_usd:.4f}")
    """

    # Maximum characters for sample content
    MAX_SAMPLE_CHARS = 500

    # Maximum lines for sample content
    MAX_SAMPLE_LINES = 10

    # Size thresholds for warnings
    LARGE_FILE_BYTES = 1_000_000  # 1MB
    SMALL_FILE_BYTES = 100  # 100 bytes

    # Token thresholds
    HIGH_TOKEN_WARNING = 100_000  # Warn if over 100K tokens

    def __init__(
        self,
        model: str = "claude-sonnet-4-20250514",
        persona_count: int = 3,
    ) -> None:
        """
        Initialise the data previewer.

        Args:
            model: Model for cost estimation.
            persona_count: Expected number of personas to generate.
        """
        self._model = model
        self._persona_count = persona_count
        self._loader = DataLoader()
        self._cost_estimator = CostEstimator()

    def preview(self, path: Path | str) -> PreviewResult:
        """
        Preview data from a file or directory.

        Args:
            path: Path to file or directory.

        Returns:
            PreviewResult with file information and cost estimate.
        """
        path = Path(path)
        result = PreviewResult(
            model=self._model,
            persona_count=self._persona_count,
        )

        if not path.exists():
            result.issues.append(
                PreviewIssue(
                    severity=IssueSeverity.ERROR,
                    message=f"Path does not exist: {path}",
                )
            )
            return result

        # Discover files
        if path.is_file():
            files = [path]
        else:
            files = self._loader.discover_files(path)

        if not files:
            result.issues.append(
                PreviewIssue(
                    severity=IssueSeverity.ERROR,
                    message=f"No loadable files found in: {path}",
                    details={"supported_formats": self._loader.supported_extensions},
                )
            )
            return result

        # Preview each file
        for file_path in files:
            file_preview = self._preview_file(file_path)
            result.files.append(file_preview)
            result.total_files += 1
            result.total_size_bytes += file_preview.size_bytes
            if file_preview.loadable:
                result.total_tokens += file_preview.token_count

        # Calculate cost estimate
        if result.total_tokens > 0:
            estimate = self._cost_estimator.estimate(
                model=self._model,
                input_tokens=result.total_tokens,
                persona_count=self._persona_count,
            )
            result.estimated_cost_usd = float(estimate.total_cost)

        # Check for global issues
        self._check_global_issues(result)

        return result

    def preview_file(self, path: Path | str) -> FilePreview:
        """
        Preview a single file.

        Args:
            path: Path to the file.

        Returns:
            FilePreview with file information.
        """
        return self._preview_file(Path(path))

    def get_sample_content(
        self,
        path: Path | str,
        max_chars: int | None = None,
        max_lines: int | None = None,
    ) -> str:
        """
        Get sample content from a file.

        Args:
            path: Path to the file.
            max_chars: Maximum characters to return.
            max_lines: Maximum lines to return.

        Returns:
            Sample content from the file.
        """
        max_chars = max_chars or self.MAX_SAMPLE_CHARS
        max_lines = max_lines or self.MAX_SAMPLE_LINES

        path = Path(path)

        try:
            content = self._loader.load_file(path)
            return self._truncate_content(content, max_chars, max_lines)
        except Exception:
            return ""

    def _preview_file(self, path: Path) -> FilePreview:
        """Preview a single file."""
        preview = FilePreview(
            file_path=path,
            format=path.suffix.lower().lstrip(".") or "unknown",
        )

        # Get file size
        try:
            preview.size_bytes = path.stat().st_size
        except OSError as e:
            preview.issues.append(
                PreviewIssue(
                    severity=IssueSeverity.ERROR,
                    message=f"Cannot read file size: {e}",
                    file_path=path,
                )
            )
            preview.loadable = False
            return preview

        # Check file size
        if preview.size_bytes > self.LARGE_FILE_BYTES:
            preview.issues.append(
                PreviewIssue(
                    severity=IssueSeverity.WARNING,
                    message=f"Large file ({preview.size_bytes / 1_000_000:.1f} MB)",
                    file_path=path,
                )
            )
        elif preview.size_bytes < self.SMALL_FILE_BYTES:
            preview.issues.append(
                PreviewIssue(
                    severity=IssueSeverity.WARNING,
                    message="Very small file (may lack sufficient content)",
                    file_path=path,
                )
            )

        # Try to load content
        try:
            content = self._loader.load_file(path)
            preview.line_count = content.count("\n") + 1
            preview.token_count = self._loader.count_tokens(content)
            preview.sample_content = self._truncate_content(
                content,
                self.MAX_SAMPLE_CHARS,
                self.MAX_SAMPLE_LINES,
            )
        except UnicodeDecodeError as e:
            preview.issues.append(
                PreviewIssue(
                    severity=IssueSeverity.ERROR,
                    message=f"Encoding error: {e}",
                    file_path=path,
                )
            )
            preview.loadable = False
        except ValueError as e:
            preview.issues.append(
                PreviewIssue(
                    severity=IssueSeverity.ERROR,
                    message=f"Format error: {e}",
                    file_path=path,
                )
            )
            preview.loadable = False
        except Exception as e:
            preview.issues.append(
                PreviewIssue(
                    severity=IssueSeverity.ERROR,
                    message=f"Load error: {e}",
                    file_path=path,
                )
            )
            preview.loadable = False

        # Check for empty content
        if preview.loadable and preview.token_count == 0:
            preview.issues.append(
                PreviewIssue(
                    severity=IssueSeverity.WARNING,
                    message="File appears to be empty",
                    file_path=path,
                )
            )

        return preview

    def _truncate_content(
        self,
        content: str,
        max_chars: int,
        max_lines: int,
    ) -> str:
        """Truncate content to specified limits."""
        lines = content.split("\n")

        # Limit lines
        if len(lines) > max_lines:
            lines = lines[:max_lines]
            truncated_by_lines = True
        else:
            truncated_by_lines = False

        result = "\n".join(lines)

        # Limit characters
        if len(result) > max_chars:
            result = result[:max_chars]
            truncated_by_chars = True
        else:
            truncated_by_chars = False

        # Add truncation indicator
        if truncated_by_lines or truncated_by_chars:
            result = result.rstrip() + "\n..."

        return result

    def _check_global_issues(self, result: PreviewResult) -> None:
        """Check for global issues across all files."""
        # High token count warning
        if result.total_tokens > self.HIGH_TOKEN_WARNING:
            result.issues.append(
                PreviewIssue(
                    severity=IssueSeverity.WARNING,
                    message=(
                        f"High token count ({result.total_tokens:,}). "
                        "Consider splitting data or using a model with larger context."
                    ),
                )
            )

        # No loadable files
        if not result.loadable_files:
            result.issues.append(
                PreviewIssue(
                    severity=IssueSeverity.ERROR,
                    message="No files could be loaded successfully.",
                )
            )

        # Some files failed
        failed_count = len(result.files) - len(result.loadable_files)
        if 0 < failed_count < len(result.files):
            result.issues.append(
                PreviewIssue(
                    severity=IssueSeverity.WARNING,
                    message=f"{failed_count} file(s) could not be loaded.",
                )
            )
