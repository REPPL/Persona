"""
Tests for batch processing functionality (F-020).
"""

from pathlib import Path
from unittest.mock import Mock, patch

from persona.core.batch import BatchConfig, BatchProcessor, BatchResult
from persona.core.batch.processor import FileResult
from persona.core.generation.parser import Persona


class TestBatchConfig:
    """Tests for BatchConfig dataclass."""

    def test_default_values(self):
        """Test default configuration values."""
        config = BatchConfig()

        assert config.provider == "anthropic"
        assert config.personas_per_file == 3
        assert config.continue_on_error is True

    def test_custom_values(self):
        """Test custom configuration."""
        config = BatchConfig(
            provider="openai",
            model="gpt-4o",
            personas_per_file=5,
            continue_on_error=False,
        )

        assert config.provider == "openai"
        assert config.model == "gpt-4o"
        assert config.personas_per_file == 5


class TestFileResult:
    """Tests for FileResult dataclass."""

    def test_success_result(self):
        """Test successful file result."""
        result = FileResult(
            file_path=Path("test.csv"),
            success=True,
            personas=[
                Persona(id="p001", name="Alice"),
                Persona(id="p002", name="Bob"),
            ],
            tokens_used=1500,
        )

        assert result.success
        assert len(result.personas) == 2

    def test_failed_result(self):
        """Test failed file result."""
        result = FileResult(
            file_path=Path("bad.csv"),
            success=False,
            error="File not found",
        )

        assert not result.success
        assert result.error == "File not found"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = FileResult(
            file_path=Path("test.csv"),
            personas=[Persona(id="p001", name="Test")],
            tokens_used=1000,
            processing_time=2.5,
        )

        data = result.to_dict()

        assert data["file"] == "test.csv"
        assert data["success"] is True
        assert data["persona_count"] == 1
        assert data["tokens_used"] == 1000


class TestBatchResult:
    """Tests for BatchResult dataclass."""

    def test_empty_result(self):
        """Test empty batch result."""
        result = BatchResult(config=BatchConfig())

        assert result.success_count == 0
        assert result.failure_count == 0
        assert result.total_personas == 0

    def test_result_with_files(self):
        """Test batch result with processed files."""
        result = BatchResult(
            config=BatchConfig(),
            file_results=[
                FileResult(
                    Path("a.csv"),
                    success=True,
                    personas=[
                        Persona(id="p001", name="Alice"),
                    ],
                ),
                FileResult(
                    Path("b.csv"),
                    success=True,
                    personas=[
                        Persona(id="p002", name="Bob"),
                        Persona(id="p003", name="Carol"),
                    ],
                ),
                FileResult(Path("c.csv"), success=False, error="Error"),
            ],
            total_personas=3,
        )

        assert result.success_count == 2
        assert result.failure_count == 1
        assert len(result.all_personas) == 3

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = BatchResult(
            config=BatchConfig(),
            total_personas=5,
            total_tokens=10000,
        )

        data = result.to_dict()

        assert data["total_personas"] == 5
        assert data["total_tokens"] == 10000
        assert "files" in data


class TestBatchProcessor:
    """Tests for BatchProcessor class."""

    def test_init_default(self):
        """Test default initialisation."""
        processor = BatchProcessor()

        assert processor._config is not None

    def test_init_with_config(self):
        """Test initialisation with config."""
        config = BatchConfig(personas_per_file=5)
        processor = BatchProcessor(config=config)

        assert processor._config.personas_per_file == 5

    def test_progress_callback(self):
        """Test setting progress callback."""
        processor = BatchProcessor()

        called = []

        def callback(file, current, total):
            called.append((file, current, total))

        processor.set_progress_callback(callback)

        assert processor._progress_callback is not None

    def test_estimate_batch(self, tmp_path: Path):
        """Test batch estimation."""
        # Create test files
        (tmp_path / "file1.csv").write_text("id,text\n1,Hello world\n")
        (tmp_path / "file2.csv").write_text("id,text\n2,More content here\n")

        processor = BatchProcessor()
        files = list(tmp_path.glob("*.csv"))

        estimate = processor.estimate_batch(files)

        assert estimate["total_files"] == 2
        assert estimate["total_input_tokens"] > 0
        assert estimate["estimated_total_personas"] == 6  # 2 files * 3 per file

    def test_estimate_batch_with_config(self, tmp_path: Path):
        """Test batch estimation with custom config."""
        (tmp_path / "file.csv").write_text("id,text\n1,Content\n")

        config = BatchConfig(personas_per_file=5)
        processor = BatchProcessor(config=config)

        estimate = processor.estimate_batch([tmp_path / "file.csv"])

        assert estimate["personas_per_file"] == 5
        assert estimate["estimated_total_personas"] == 5

    @patch("persona.core.batch.processor.GenerationPipeline")
    @patch("persona.core.batch.processor.ProviderFactory")
    def test_process_files(self, mock_factory, mock_pipeline, tmp_path: Path):
        """Test processing files."""
        # Create test file
        test_file = tmp_path / "test.csv"
        test_file.write_text("id,feedback\n1,Great product\n")

        # Mock provider
        mock_provider = Mock()
        mock_provider.is_configured.return_value = True
        mock_factory.create.return_value = mock_provider

        # Mock pipeline
        mock_result = Mock()
        mock_result.personas = [Persona(id="p001", name="Test User")]
        mock_result.input_tokens = 100
        mock_result.output_tokens = 200
        mock_pipeline.return_value.generate.return_value = mock_result

        processor = BatchProcessor()
        result = processor.process_files([test_file])

        assert result.success_count == 1
        assert result.total_personas == 1

    @patch("persona.core.batch.processor.GenerationPipeline")
    @patch("persona.core.batch.processor.ProviderFactory")
    def test_process_with_error(self, mock_factory, mock_pipeline, tmp_path: Path):
        """Test processing with error."""
        test_file = tmp_path / "test.csv"
        test_file.write_text("id,data\n1,test\n")

        mock_provider = Mock()
        mock_factory.create.return_value = mock_provider
        mock_pipeline.return_value.generate.side_effect = Exception("API error")

        config = BatchConfig(continue_on_error=True)
        processor = BatchProcessor(config=config)
        result = processor.process_files([test_file])

        assert result.failure_count == 1
        assert result.file_results[0].error == "API error"

    @patch("persona.core.batch.processor.GenerationPipeline")
    @patch("persona.core.batch.processor.ProviderFactory")
    def test_process_stop_on_error(self, mock_factory, mock_pipeline, tmp_path: Path):
        """Test processing stops on error when configured."""
        file1 = tmp_path / "file1.csv"
        file1.write_text("id,data\n1,test\n")
        file2 = tmp_path / "file2.csv"
        file2.write_text("id,data\n2,test\n")

        mock_provider = Mock()
        mock_factory.create.return_value = mock_provider
        mock_pipeline.return_value.generate.side_effect = Exception("Error")

        config = BatchConfig(continue_on_error=False)
        processor = BatchProcessor(config=config)
        result = processor.process_files([file1, file2])

        # Should stop after first error
        assert len(result.file_results) == 1

    def test_process_directory(self, tmp_path: Path):
        """Test processing a directory."""
        # Create test files
        (tmp_path / "a.csv").write_text("id,text\n1,Content A\n")
        (tmp_path / "b.json").write_text('{"entries": [{"text": "Content B"}]}')
        (tmp_path / "c.txt").write_text("Plain text content")

        processor = BatchProcessor()

        with patch.object(processor, "process_files") as mock_process:
            mock_process.return_value = BatchResult(config=BatchConfig())
            processor.process_directory(tmp_path)

            # Should find all supported files
            call_args = mock_process.call_args[0][0]
            assert len(call_args) >= 1

    @patch("persona.core.batch.processor.GenerationPipeline")
    @patch("persona.core.batch.processor.ProviderFactory")
    def test_progress_callback_called(
        self, mock_factory, mock_pipeline, tmp_path: Path
    ):
        """Test progress callback is called."""
        file1 = tmp_path / "file1.csv"
        file1.write_text("id,data\n1,test\n")
        file2 = tmp_path / "file2.csv"
        file2.write_text("id,data\n2,test\n")

        mock_provider = Mock()
        mock_factory.create.return_value = mock_provider

        mock_result = Mock()
        mock_result.personas = []
        mock_result.input_tokens = 0
        mock_result.output_tokens = 0
        mock_pipeline.return_value.generate.return_value = mock_result

        progress_calls = []

        def callback(file, current, total):
            progress_calls.append((current, total))

        processor = BatchProcessor()
        processor.set_progress_callback(callback)
        processor.process_files([file1, file2])

        assert len(progress_calls) == 2
        assert progress_calls[0] == (1, 2)
        assert progress_calls[1] == (2, 2)
