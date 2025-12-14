"""
Tests for data loading functionality (F-001).
"""

import pytest
from pathlib import Path

from persona.core.data import DataLoader, CSVLoader, JSONLoader, TextLoader


class TestDataLoader:
    """Tests for the DataLoader class."""

    def test_init(self):
        """Test DataLoader initialisation."""
        loader = DataLoader()
        assert loader is not None
        assert len(loader.supported_extensions) > 0

    def test_supported_extensions(self):
        """Test that common extensions are supported."""
        loader = DataLoader()
        extensions = loader.supported_extensions

        assert ".csv" in extensions
        assert ".json" in extensions
        assert ".md" in extensions
        assert ".txt" in extensions
        assert ".yaml" in extensions
        assert ".yml" in extensions

    def test_discover_files_single_file(self, tmp_path: Path):
        """Test file discovery with a single file."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("col1,col2\nval1,val2")

        loader = DataLoader()
        files = loader.discover_files(test_file)

        assert len(files) == 1
        assert files[0] == test_file

    def test_discover_files_directory(self, tmp_path: Path):
        """Test file discovery in a directory."""
        (tmp_path / "file1.csv").write_text("a,b\n1,2")
        (tmp_path / "file2.json").write_text('{"key": "value"}')
        (tmp_path / "file3.unknown").write_text("ignored")

        loader = DataLoader()
        files = loader.discover_files(tmp_path)

        assert len(files) == 2
        assert any(f.name == "file1.csv" for f in files)
        assert any(f.name == "file2.json" for f in files)

    def test_discover_files_recursive(self, tmp_path: Path):
        """Test recursive file discovery."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        (tmp_path / "root.txt").write_text("root content")
        (subdir / "nested.txt").write_text("nested content")

        loader = DataLoader()
        files = loader.discover_files(tmp_path, recursive=True)

        assert len(files) == 2

    def test_discover_files_non_recursive(self, tmp_path: Path):
        """Test non-recursive file discovery."""
        subdir = tmp_path / "subdir"
        subdir.mkdir()

        (tmp_path / "root.txt").write_text("root content")
        (subdir / "nested.txt").write_text("nested content")

        loader = DataLoader()
        files = loader.discover_files(tmp_path, recursive=False)

        assert len(files) == 1
        assert files[0].name == "root.txt"

    def test_discover_files_not_found(self):
        """Test error when path does not exist."""
        loader = DataLoader()

        with pytest.raises(FileNotFoundError):
            loader.discover_files(Path("/nonexistent/path"))

    def test_load_file_csv(self, tmp_path: Path):
        """Test loading a CSV file."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("name,role\nAlice,Developer\nBob,Designer")

        loader = DataLoader()
        content = loader.load_file(test_file)

        assert "Alice" in content
        assert "Developer" in content
        assert "Bob" in content

    def test_load_file_json(self, tmp_path: Path):
        """Test loading a JSON file."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"participant": "P001", "feedback": "Great product"}')

        loader = DataLoader()
        content = loader.load_file(test_file)

        assert "P001" in content
        assert "Great product" in content

    def test_load_file_unsupported(self, tmp_path: Path):
        """Test error for unsupported file format."""
        test_file = tmp_path / "test.xyz"
        test_file.write_text("some content")

        loader = DataLoader()

        with pytest.raises(ValueError) as excinfo:
            loader.load_file(test_file)

        assert "Unsupported file format" in str(excinfo.value)

    def test_load_path_single_file(self, tmp_path: Path):
        """Test loading from a single file path."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Interview transcript content here.")

        loader = DataLoader()
        content, files = loader.load_path(test_file)

        assert "Interview transcript" in content
        assert len(files) == 1

    def test_load_path_directory(self, tmp_path: Path):
        """Test loading from a directory."""
        (tmp_path / "interview1.txt").write_text("First interview content")
        (tmp_path / "interview2.txt").write_text("Second interview content")

        loader = DataLoader()
        content, files = loader.load_path(tmp_path)

        assert "First interview" in content
        assert "Second interview" in content
        assert len(files) == 2

    def test_load_path_empty_directory(self, tmp_path: Path):
        """Test error when no loadable files found."""
        loader = DataLoader()

        with pytest.raises(ValueError) as excinfo:
            loader.load_path(tmp_path)

        assert "No loadable files found" in str(excinfo.value)

    def test_count_tokens(self):
        """Test token counting functionality."""
        loader = DataLoader()
        text = "This is a test sentence for token counting."

        token_count = loader.count_tokens(text)

        assert isinstance(token_count, int)
        assert token_count > 0
        assert token_count < len(text)  # Tokens should be fewer than characters

    def test_validate_content_valid(self):
        """Test content validation with valid content."""
        loader = DataLoader()
        content = "This is valid content with more than 100 characters. " * 5

        assert loader.validate_content(content) is True

    def test_validate_content_empty(self):
        """Test content validation with empty content."""
        loader = DataLoader()

        assert loader.validate_content("") is False
        assert loader.validate_content("   ") is False

    def test_validate_content_too_short(self):
        """Test content validation with too short content."""
        loader = DataLoader()

        assert loader.validate_content("Short", min_length=100) is False


class TestCSVLoader:
    """Tests for the CSV loader."""

    def test_extensions(self):
        """Test supported extensions."""
        loader = CSVLoader()
        assert ".csv" in loader.extensions

    def test_load_basic(self, tmp_path: Path):
        """Test basic CSV loading."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("participant_id,response\nP001,Great\nP002,Good")

        loader = CSVLoader()
        content = loader.load(test_file)

        assert "P001" in content
        assert "Great" in content
        assert "Entry 1" in content
        assert "Entry 2" in content

    def test_load_empty(self, tmp_path: Path):
        """Test loading empty CSV."""
        test_file = tmp_path / "empty.csv"
        test_file.write_text("col1,col2\n")

        loader = CSVLoader()
        content = loader.load(test_file)

        assert content == ""


class TestJSONLoader:
    """Tests for the JSON loader."""

    def test_extensions(self):
        """Test supported extensions."""
        loader = JSONLoader()
        assert ".json" in loader.extensions

    def test_load_object(self, tmp_path: Path):
        """Test loading JSON object."""
        test_file = tmp_path / "test.json"
        test_file.write_text('{"name": "Alice", "role": "Developer"}')

        loader = JSONLoader()
        content = loader.load(test_file)

        assert "Alice" in content
        assert "Developer" in content

    def test_load_array(self, tmp_path: Path):
        """Test loading JSON array."""
        test_file = tmp_path / "test.json"
        test_file.write_text('[{"id": 1}, {"id": 2}]')

        loader = JSONLoader()
        content = loader.load(test_file)

        assert "Item 1" in content
        assert "Item 2" in content


class TestTextLoader:
    """Tests for the text loader."""

    def test_extensions(self):
        """Test supported extensions."""
        loader = TextLoader()
        assert ".txt" in loader.extensions
        assert ".text" in loader.extensions

    def test_load(self, tmp_path: Path):
        """Test loading text file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Plain text content here.")

        loader = TextLoader()
        content = loader.load(test_file)

        assert content == "Plain text content here."
