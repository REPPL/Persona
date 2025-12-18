"""
Tests for data preview functionality (F-022).
"""

from pathlib import Path

from persona.core.preview import (
    DataPreviewer,
    FilePreview,
    IssueSeverity,
    PreviewIssue,
    PreviewResult,
)


class TestIssueSeverity:
    """Tests for IssueSeverity enum."""

    def test_error_severity(self):
        """Test error severity value."""
        assert IssueSeverity.ERROR.value == "error"

    def test_warning_severity(self):
        """Test warning severity value."""
        assert IssueSeverity.WARNING.value == "warning"

    def test_info_severity(self):
        """Test info severity value."""
        assert IssueSeverity.INFO.value == "info"


class TestPreviewIssue:
    """Tests for PreviewIssue dataclass."""

    def test_basic_issue(self):
        """Test creating a basic issue."""
        issue = PreviewIssue(
            severity=IssueSeverity.ERROR,
            message="Test error",
        )

        assert issue.severity == IssueSeverity.ERROR
        assert issue.message == "Test error"
        assert issue.file_path is None

    def test_issue_with_file(self):
        """Test creating an issue with file path."""
        issue = PreviewIssue(
            severity=IssueSeverity.WARNING,
            message="Test warning",
            file_path=Path("test.csv"),
        )

        assert issue.file_path == Path("test.csv")

    def test_issue_with_details(self):
        """Test creating an issue with details."""
        issue = PreviewIssue(
            severity=IssueSeverity.INFO,
            message="Test info",
            details={"key": "value"},
        )

        assert issue.details == {"key": "value"}


class TestFilePreview:
    """Tests for FilePreview dataclass."""

    def test_default_values(self):
        """Test default preview values."""
        preview = FilePreview(
            file_path=Path("test.csv"),
            format="csv",
        )

        assert preview.size_bytes == 0
        assert preview.token_count == 0
        assert preview.loadable is True
        assert len(preview.issues) == 0

    def test_to_dict(self):
        """Test conversion to dictionary."""
        preview = FilePreview(
            file_path=Path("test.csv"),
            format="csv",
            size_bytes=1000,
            token_count=250,
            line_count=50,
            sample_content="Sample text",
        )

        data = preview.to_dict()

        assert data["file"] == "test.csv"
        assert data["format"] == "csv"
        assert data["size_bytes"] == 1000
        assert data["token_count"] == 250
        assert data["loadable"] is True

    def test_to_dict_with_issues(self):
        """Test to_dict includes issues."""
        preview = FilePreview(
            file_path=Path("test.csv"),
            format="csv",
            issues=[
                PreviewIssue(
                    severity=IssueSeverity.WARNING,
                    message="Large file",
                ),
            ],
        )

        data = preview.to_dict()

        assert len(data["issues"]) == 1
        assert data["issues"][0]["severity"] == "warning"


class TestPreviewResult:
    """Tests for PreviewResult dataclass."""

    def test_empty_result(self):
        """Test empty preview result."""
        result = PreviewResult()

        assert result.total_files == 0
        assert result.total_tokens == 0
        assert result.has_errors is False
        assert result.has_warnings is False

    def test_has_errors(self):
        """Test has_errors property."""
        result = PreviewResult(
            issues=[
                PreviewIssue(
                    severity=IssueSeverity.ERROR,
                    message="Error",
                ),
            ],
        )

        assert result.has_errors is True
        assert result.has_warnings is False

    def test_has_warnings(self):
        """Test has_warnings property."""
        result = PreviewResult(
            issues=[
                PreviewIssue(
                    severity=IssueSeverity.WARNING,
                    message="Warning",
                ),
            ],
        )

        assert result.has_errors is False
        assert result.has_warnings is True

    def test_has_errors_from_file(self):
        """Test has_errors detects file-level errors."""
        result = PreviewResult(
            files=[
                FilePreview(
                    file_path=Path("test.csv"),
                    format="csv",
                    issues=[
                        PreviewIssue(
                            severity=IssueSeverity.ERROR,
                            message="File error",
                        ),
                    ],
                ),
            ],
        )

        assert result.has_errors is True

    def test_loadable_files(self):
        """Test loadable_files property."""
        result = PreviewResult(
            files=[
                FilePreview(
                    file_path=Path("good.csv"),
                    format="csv",
                    loadable=True,
                ),
                FilePreview(
                    file_path=Path("bad.csv"),
                    format="csv",
                    loadable=False,
                ),
            ],
        )

        assert len(result.loadable_files) == 1
        assert result.loadable_files[0].file_path == Path("good.csv")

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = PreviewResult(
            total_files=2,
            total_tokens=1000,
            estimated_cost_usd=0.0025,
            model="claude-sonnet-4-20250514",
            persona_count=3,
        )

        data = result.to_dict()

        assert data["total_files"] == 2
        assert data["total_tokens"] == 1000
        assert data["estimated_cost_usd"] == 0.0025
        assert data["model"] == "claude-sonnet-4-20250514"


class TestDataPreviewer:
    """Tests for DataPreviewer class."""

    def test_init_default(self):
        """Test default initialisation."""
        previewer = DataPreviewer()

        assert previewer._model == "claude-sonnet-4-20250514"
        assert previewer._persona_count == 3

    def test_init_with_params(self):
        """Test initialisation with parameters."""
        previewer = DataPreviewer(
            model="gpt-4o",
            persona_count=5,
        )

        assert previewer._model == "gpt-4o"
        assert previewer._persona_count == 5

    def test_preview_file_not_exists(self):
        """Test preview of non-existent path."""
        previewer = DataPreviewer()
        result = previewer.preview(Path("/nonexistent/path"))

        assert result.has_errors is True
        assert any("does not exist" in i.message for i in result.issues)

    def test_preview_single_file(self, tmp_path: Path):
        """Test preview of a single file."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("id,name,feedback\n1,Alice,Great product\n")

        previewer = DataPreviewer()
        result = previewer.preview(test_file)

        assert result.total_files == 1
        assert result.total_tokens > 0
        assert len(result.files) == 1
        assert result.files[0].format == "csv"

    def test_preview_directory(self, tmp_path: Path):
        """Test preview of a directory."""
        (tmp_path / "file1.csv").write_text("id,text\n1,Content A\n")
        (tmp_path / "file2.csv").write_text("id,text\n2,Content B\n")

        previewer = DataPreviewer()
        result = previewer.preview(tmp_path)

        assert result.total_files == 2
        assert len(result.files) == 2

    def test_preview_empty_directory(self, tmp_path: Path):
        """Test preview of empty directory."""
        previewer = DataPreviewer()
        result = previewer.preview(tmp_path)

        assert result.has_errors is True
        assert any("No loadable files" in i.message for i in result.issues)

    def test_preview_includes_cost_estimate(self, tmp_path: Path):
        """Test preview includes cost estimate."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("id,feedback\n1,Some user feedback here\n" * 100)

        previewer = DataPreviewer()
        result = previewer.preview(test_file)

        assert result.estimated_cost_usd >= 0

    def test_preview_sample_content(self, tmp_path: Path):
        """Test preview includes sample content."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Line 1\nLine 2\nLine 3\n")

        previewer = DataPreviewer()
        result = previewer.preview(test_file)

        assert len(result.files) == 1
        assert "Line 1" in result.files[0].sample_content

    def test_preview_large_file_warning(self, tmp_path: Path):
        """Test warning for large files."""
        from unittest.mock import patch

        test_file = tmp_path / "large.txt"
        # Create file just over 1MB threshold
        test_file.write_text("x" * 1_100_000)

        previewer = DataPreviewer()

        # Mock loader to avoid slow token counting
        with patch.object(previewer._loader, "load_file", return_value="content"):
            with patch.object(previewer._loader, "count_tokens", return_value=1000):
                preview = previewer._preview_file(test_file)

        assert any("Large file" in i.message for i in preview.issues)

    def test_preview_small_file_warning(self, tmp_path: Path):
        """Test warning for very small files."""
        test_file = tmp_path / "small.txt"
        test_file.write_text("x")  # 1 byte

        previewer = DataPreviewer()
        result = previewer.preview(test_file)

        file_preview = result.files[0]
        assert any("small" in i.message.lower() for i in file_preview.issues)

    def test_preview_file_method(self, tmp_path: Path):
        """Test preview_file method."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"data": "test"}')

        previewer = DataPreviewer()
        preview = previewer.preview_file(test_file)

        assert preview.file_path == test_file
        assert preview.format == "json"
        assert preview.loadable is True

    def test_get_sample_content(self, tmp_path: Path):
        """Test get_sample_content method."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Line 1\nLine 2\nLine 3\nLine 4\nLine 5\n")

        previewer = DataPreviewer()
        sample = previewer.get_sample_content(test_file, max_lines=2)

        assert "Line 1" in sample
        assert "Line 2" in sample
        assert "..." in sample

    def test_preview_mixed_formats(self, tmp_path: Path):
        """Test preview with multiple file formats."""
        (tmp_path / "data.csv").write_text("id,text\n1,CSV content\n")
        (tmp_path / "data.json").write_text('{"text": "JSON content"}')
        (tmp_path / "data.md").write_text("# Markdown content")

        previewer = DataPreviewer()
        result = previewer.preview(tmp_path)

        formats = {f.format for f in result.files}
        assert "csv" in formats
        assert "json" in formats
        assert "md" in formats

    def test_preview_calculates_line_count(self, tmp_path: Path):
        """Test preview calculates line count."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Line 1\nLine 2\nLine 3\n")

        previewer = DataPreviewer()
        result = previewer.preview(test_file)

        assert result.files[0].line_count == 4  # 3 lines + trailing

    def test_preview_file_size(self, tmp_path: Path):
        """Test preview calculates file size."""
        test_file = tmp_path / "test.txt"
        content = "Hello World"
        test_file.write_text(content)

        previewer = DataPreviewer()
        result = previewer.preview(test_file)

        assert result.files[0].size_bytes == len(content)
        assert result.total_size_bytes == len(content)

    def test_preview_unsupported_file(self, tmp_path: Path):
        """Test preview with unsupported file type."""
        test_file = tmp_path / "data.xyz"
        test_file.write_text("Some content")

        previewer = DataPreviewer()
        result = previewer.preview(test_file)

        # Directory has no loadable files
        assert result.has_errors is True

    def test_preview_high_token_warning(self, tmp_path: Path):
        """Test warning for high token count."""
        from unittest.mock import patch

        test_file = tmp_path / "large.txt"
        test_file.write_text("Some content here")

        previewer = DataPreviewer()

        # Mock token counting to return high count
        with patch.object(previewer._loader, "count_tokens", return_value=150000):
            result = previewer.preview(test_file)

        # Should have high token warning
        assert any("High token" in i.message for i in result.issues)

    def test_preview_partial_load_failure(self, tmp_path: Path):
        """Test preview with some files failing to load."""
        (tmp_path / "good.txt").write_text("Good content")
        # Create a file that will fail (binary content as text)
        bad_file = tmp_path / "bad.txt"
        bad_file.write_bytes(b"\x00\x01\x02\x03")

        previewer = DataPreviewer()
        result = previewer.preview(tmp_path)

        # Should have at least one loadable file
        assert len(result.loadable_files) >= 1

    def test_truncate_long_content(self, tmp_path: Path):
        """Test content truncation for long files."""
        test_file = tmp_path / "long.txt"
        # Create file with many lines
        lines = [f"Line {i}" for i in range(100)]
        test_file.write_text("\n".join(lines))

        previewer = DataPreviewer()
        preview = previewer.preview_file(test_file)

        # Sample should be truncated
        assert len(preview.sample_content) < len("\n".join(lines))
        assert "..." in preview.sample_content
