"""Tests for folder processing (F-059)."""

from pathlib import Path
from tempfile import TemporaryDirectory

from persona.core.batch.scanner import (
    FileOrder,
    FolderScanner,
    ScanResult,
    scan_folder,
)


class TestFolderScanner:
    """Tests for FolderScanner."""

    def test_scan_empty_directory(self):
        """Scans empty directory."""
        with TemporaryDirectory() as tmpdir:
            scanner = FolderScanner()
            result = scanner.scan(tmpdir)

            assert result.total_files == 0
            assert len(result.files) == 0

    def test_scan_single_file(self):
        """Scans single supported file."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text("# Test content")

            scanner = FolderScanner()
            result = scanner.scan(tmpdir)

            assert result.total_files == 1
            assert result.files[0].format == "markdown"

    def test_scan_multiple_files(self):
        """Scans multiple supported files."""
        with TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "a.md").write_text("A content")
            (Path(tmpdir) / "b.csv").write_text("col1,col2\n1,2")
            (Path(tmpdir) / "c.json").write_text('{"key": "value"}')

            scanner = FolderScanner()
            result = scanner.scan(tmpdir)

            assert result.total_files == 3

    def test_scan_ignores_unsupported(self):
        """Ignores unsupported file types."""
        with TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.md").write_text("Supported")
            (Path(tmpdir) / "test.exe").write_text("Unsupported")
            (Path(tmpdir) / "test.dll").write_text("Unsupported")

            scanner = FolderScanner()
            result = scanner.scan(tmpdir)

            assert result.total_files == 1

    def test_scan_recursive(self):
        """Scans subdirectories recursively."""
        with TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "root.md").write_text("Root")
            subdir = Path(tmpdir) / "subdir"
            subdir.mkdir()
            (subdir / "nested.md").write_text("Nested")

            scanner = FolderScanner()
            result = scanner.scan(tmpdir, recursive=True)

            assert result.total_files == 2

    def test_scan_non_recursive(self):
        """Only scans top level when not recursive."""
        with TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "root.md").write_text("Root")
            subdir = Path(tmpdir) / "subdir"
            subdir.mkdir()
            (subdir / "nested.md").write_text("Nested")

            scanner = FolderScanner()
            result = scanner.scan(tmpdir, recursive=False)

            assert result.total_files == 1

    def test_exclude_patterns(self):
        """Excludes files matching patterns."""
        with TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "include.md").write_text("Include")
            (Path(tmpdir) / "exclude.draft.md").write_text("Exclude")

            scanner = FolderScanner(exclude_patterns=["*.draft.md"])
            result = scanner.scan(tmpdir)

            assert result.total_files == 1
            assert result.excluded_count == 1

    def test_custom_extensions(self):
        """Uses custom extensions."""
        with TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.custom").write_text("Custom")
            (Path(tmpdir) / "test.md").write_text("Markdown")

            scanner = FolderScanner(extensions={".custom"})
            result = scanner.scan(tmpdir)

            assert result.total_files == 1

    def test_alphabetical_order(self):
        """Orders files alphabetically."""
        with TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "zebra.md").write_text("Z")
            (Path(tmpdir) / "alpha.md").write_text("A")
            (Path(tmpdir) / "beta.md").write_text("B")

            scanner = FolderScanner(order=FileOrder.ALPHABETICAL)
            result = scanner.scan(tmpdir)

            names = [f.path.name for f in result.files]
            assert names == ["alpha.md", "beta.md", "zebra.md"]

    def test_scan_multiple_folders(self):
        """Scans multiple folders."""
        with TemporaryDirectory() as tmpdir1, TemporaryDirectory() as tmpdir2:
            (Path(tmpdir1) / "a.md").write_text("A")
            (Path(tmpdir2) / "b.md").write_text("B")

            scanner = FolderScanner()
            result = scanner.scan_multiple([tmpdir1, tmpdir2])

            assert result.total_files == 2

    def test_file_info_to_dict(self):
        """FileInfo converts to dict."""
        with TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.md"
            path.write_text("Content")

            scanner = FolderScanner()
            result = scanner.scan(tmpdir)

            data = result.files[0].to_dict()
            assert "path" in data
            assert "format" in data
            assert "size_bytes" in data

    def test_scan_result_to_dict(self):
        """ScanResult converts to dict."""
        result = ScanResult(total_files=0)
        data = result.to_dict()

        assert "files" in data
        assert "total_files" in data

    def test_scan_nonexistent_path(self):
        """Handles nonexistent path gracefully."""
        scanner = FolderScanner()
        result = scanner.scan("/nonexistent/path")

        assert result.total_files == 0


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    def test_scan_folder(self):
        """scan_folder convenience function works."""
        with TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "test.md").write_text("Content")

            result = scan_folder(tmpdir)
            assert result.total_files == 1
