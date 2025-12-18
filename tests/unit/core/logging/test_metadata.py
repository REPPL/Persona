"""Tests for metadata recording (F-076)."""

import json
import tempfile
from pathlib import Path

import pytest
from persona.core.logging.metadata import (
    CostInfo,
    DataSourceInfo,
    EnvironmentInfo,
    GenerationConfig,
    GenerationMetadata,
    MetadataRecorder,
    calculate_checksum,
    record_metadata,
)


class TestGenerationConfig:
    """Tests for GenerationConfig dataclass."""

    def test_create_config(self) -> None:
        """Can create a generation config."""
        config = GenerationConfig(
            model="claude-sonnet-4",
            provider="anthropic",
            persona_count=3,
            complexity="high",
            detail_level="comprehensive",
        )

        assert config.model == "claude-sonnet-4"
        assert config.provider == "anthropic"
        assert config.persona_count == 3
        assert config.complexity == "high"

    def test_config_defaults(self) -> None:
        """Config has sensible defaults."""
        config = GenerationConfig()

        assert config.model == ""
        assert config.provider == ""
        assert config.persona_count == 0
        assert config.complexity == "moderate"
        assert config.detail_level == "standard"
        assert config.temperature == 0.7
        assert config.max_tokens == 4096

    def test_config_extra_fields(self) -> None:
        """Config can hold extra fields."""
        config = GenerationConfig(
            model="test",
            extra={"custom_setting": "value"},
        )

        assert config.extra["custom_setting"] == "value"

    def test_to_dict(self) -> None:
        """Config can be converted to dict."""
        config = GenerationConfig(
            model="claude",
            persona_count=5,
            extra={"custom": "field"},
        )

        result = config.to_dict()

        assert result["model"] == "claude"
        assert result["persona_count"] == 5
        assert result["custom"] == "field"


class TestDataSourceInfo:
    """Tests for DataSourceInfo dataclass."""

    def test_create_data_source_info(self) -> None:
        """Can create data source info."""
        info = DataSourceInfo(
            files=["file1.csv", "file2.json"],
            total_files=2,
            total_tokens=5000,
            total_bytes=10240,
        )

        assert info.files == ["file1.csv", "file2.json"]
        assert info.total_files == 2
        assert info.total_tokens == 5000

    def test_defaults(self) -> None:
        """Has sensible defaults."""
        info = DataSourceInfo()

        assert info.files == []
        assert info.total_files == 0
        assert info.total_tokens == 0
        assert info.total_bytes == 0
        assert info.checksums == {}

    def test_with_checksums(self) -> None:
        """Can include file checksums."""
        info = DataSourceInfo(
            files=["data.csv"],
            checksums={"data.csv": "sha256:abc123"},
        )

        assert info.checksums["data.csv"] == "sha256:abc123"

    def test_to_dict(self) -> None:
        """Can convert to dict."""
        info = DataSourceInfo(
            files=["test.csv"],
            total_files=1,
            total_tokens=1000,
        )

        result = info.to_dict()

        assert result["files"] == ["test.csv"]
        assert result["total_files"] == 1
        assert result["total_tokens"] == 1000


class TestEnvironmentInfo:
    """Tests for EnvironmentInfo dataclass."""

    def test_create_environment_info(self) -> None:
        """Can create environment info."""
        info = EnvironmentInfo(
            persona_version="0.9.0",
            python_version="3.12.0",
            platform="darwin",
        )

        assert info.persona_version == "0.9.0"
        assert info.python_version == "3.12.0"
        assert info.platform == "darwin"

    def test_capture_current_environment(self) -> None:
        """Can capture current environment."""
        info = EnvironmentInfo.capture()

        assert info.python_version.startswith("3.")
        assert info.platform in ["darwin", "linux", "win32"]
        assert info.timezone is not None

    def test_to_dict(self) -> None:
        """Can convert to dict."""
        info = EnvironmentInfo(
            persona_version="0.9.0",
            python_version="3.12.0",
            platform="darwin",
        )

        result = info.to_dict()

        assert result["persona_version"] == "0.9.0"
        assert result["python_version"] == "3.12.0"

    def test_to_dict_excludes_empty_hostname(self) -> None:
        """Hostname excluded if empty."""
        info = EnvironmentInfo(hostname="")

        result = info.to_dict()

        assert "hostname" not in result

    def test_to_dict_includes_hostname_if_set(self) -> None:
        """Hostname included if set."""
        info = EnvironmentInfo(hostname="myhost")

        result = info.to_dict()

        assert result["hostname"] == "myhost"


class TestCostInfo:
    """Tests for CostInfo dataclass."""

    def test_create_cost_info(self) -> None:
        """Can create cost info."""
        info = CostInfo(
            input_tokens=10000,
            output_tokens=2000,
            total_cost_usd=0.15,
            cost_per_persona=0.05,
        )

        assert info.input_tokens == 10000
        assert info.output_tokens == 2000
        assert info.total_cost_usd == 0.15
        assert info.cost_per_persona == 0.05

    def test_defaults(self) -> None:
        """Has sensible defaults."""
        info = CostInfo()

        assert info.input_tokens == 0
        assert info.output_tokens == 0
        assert info.total_cost_usd == 0.0
        assert info.cost_per_persona == 0.0

    def test_to_dict(self) -> None:
        """Can convert to dict."""
        info = CostInfo(
            input_tokens=5000,
            total_cost_usd=0.10,
        )

        result = info.to_dict()

        assert result["input_tokens"] == 5000
        assert result["total_cost_usd"] == 0.10


class TestGenerationMetadata:
    """Tests for GenerationMetadata dataclass."""

    def test_create_metadata(self) -> None:
        """Can create generation metadata."""
        metadata = GenerationMetadata(
            experiment_id="exp-123",
            run_id="run-456",
        )

        assert metadata.experiment_id == "exp-123"
        assert metadata.run_id == "run-456"
        assert metadata.metadata_version == "1.0"

    def test_defaults(self) -> None:
        """Has sensible defaults."""
        metadata = GenerationMetadata()

        assert metadata.metadata_version == "1.0"
        assert isinstance(metadata.configuration, GenerationConfig)
        assert isinstance(metadata.data_sources, DataSourceInfo)
        assert isinstance(metadata.environment, EnvironmentInfo)
        assert isinstance(metadata.costs, CostInfo)
        assert metadata.errors == []
        assert metadata.warnings == []

    def test_to_dict(self) -> None:
        """Can convert to dict."""
        metadata = GenerationMetadata(
            experiment_id="exp-123",
            run_id="run-456",
            timestamp_start="2025-01-01T00:00:00+00:00",
            timestamp_end="2025-01-01T00:01:00+00:00",
            duration_seconds=60.0,
        )

        result = metadata.to_dict()

        assert result["metadata_version"] == "1.0"
        assert result["generation"]["experiment_id"] == "exp-123"
        assert result["generation"]["run_id"] == "run-456"
        assert result["generation"]["duration_seconds"] == 60.0

    def test_to_json(self) -> None:
        """Can serialize to JSON."""
        metadata = GenerationMetadata(
            experiment_id="exp-123",
        )

        json_str = metadata.to_json()
        parsed = json.loads(json_str)

        assert parsed["generation"]["experiment_id"] == "exp-123"

    def test_from_dict(self) -> None:
        """Can create from dict."""
        data = {
            "metadata_version": "1.0",
            "generation": {
                "experiment_id": "exp-123",
                "run_id": "run-456",
                "timestamp_start": "2025-01-01T00:00:00+00:00",
                "timestamp_end": "2025-01-01T00:01:00+00:00",
                "duration_seconds": 60.0,
            },
            "configuration": {
                "model": "claude",
                "persona_count": 3,
            },
            "data_sources": {
                "files": ["test.csv"],
                "total_files": 1,
            },
            "environment": {
                "python_version": "3.12.0",
            },
            "costs": {
                "total_cost_usd": 0.15,
            },
            "checksums": {},
            "errors": [],
            "warnings": ["Test warning"],
        }

        metadata = GenerationMetadata.from_dict(data)

        assert metadata.experiment_id == "exp-123"
        assert metadata.run_id == "run-456"
        assert metadata.configuration.model == "claude"
        assert metadata.configuration.persona_count == 3
        assert metadata.warnings == ["Test warning"]


class TestMetadataRecorder:
    """Tests for MetadataRecorder class."""

    def test_create_recorder(self) -> None:
        """Can create a metadata recorder."""
        recorder = MetadataRecorder(
            experiment_id="exp-123",
            run_id="run-456",
        )

        metadata = recorder.get_metadata()
        assert metadata.experiment_id == "exp-123"
        assert metadata.run_id == "run-456"

    def test_captures_environment_on_creation(self) -> None:
        """Recorder captures environment on creation."""
        recorder = MetadataRecorder()

        metadata = recorder.get_metadata()
        assert metadata.environment.python_version.startswith("3.")
        assert metadata.environment.platform != ""

    def test_start(self) -> None:
        """Can mark start of generation."""
        recorder = MetadataRecorder()
        recorder.start()

        metadata = recorder.get_metadata()
        assert metadata.timestamp_start != ""
        assert "T" in metadata.timestamp_start  # ISO format

    def test_set_config(self) -> None:
        """Can set generation config."""
        recorder = MetadataRecorder()
        recorder.set_config(
            model="claude-sonnet-4",
            provider="anthropic",
            persona_count=3,
            complexity="high",
        )

        metadata = recorder.get_metadata()
        assert metadata.configuration.model == "claude-sonnet-4"
        assert metadata.configuration.provider == "anthropic"
        assert metadata.configuration.persona_count == 3
        assert metadata.configuration.complexity == "high"

    def test_set_config_with_extra(self) -> None:
        """Can set config with extra fields."""
        recorder = MetadataRecorder()
        recorder.set_config(
            model="test",
            custom_field="value",
        )

        metadata = recorder.get_metadata()
        assert metadata.configuration.extra["custom_field"] == "value"

    def test_add_data_source(self) -> None:
        """Can add data source."""
        recorder = MetadataRecorder()
        recorder.add_data_source(
            path="data.csv",
            tokens=5000,
            size_bytes=10240,
            checksum="sha256:abc123",
        )

        metadata = recorder.get_metadata()
        assert "data.csv" in metadata.data_sources.files
        assert metadata.data_sources.total_files == 1
        assert metadata.data_sources.total_tokens == 5000
        assert metadata.data_sources.total_bytes == 10240
        assert metadata.data_sources.checksums["data.csv"] == "sha256:abc123"

    def test_add_multiple_data_sources(self) -> None:
        """Can add multiple data sources."""
        recorder = MetadataRecorder()
        recorder.add_data_source("file1.csv", tokens=1000)
        recorder.add_data_source("file2.json", tokens=2000)
        recorder.add_data_source("file3.md", tokens=500)

        metadata = recorder.get_metadata()
        assert metadata.data_sources.total_files == 3
        assert metadata.data_sources.total_tokens == 3500

    def test_set_costs(self) -> None:
        """Can set cost information."""
        recorder = MetadataRecorder()
        recorder.set_config(persona_count=3)
        recorder.set_costs(
            input_tokens=10000,
            output_tokens=2000,
            total_cost_usd=0.15,
        )

        metadata = recorder.get_metadata()
        assert metadata.costs.input_tokens == 10000
        assert metadata.costs.output_tokens == 2000
        assert metadata.costs.total_cost_usd == 0.15
        assert metadata.costs.cost_per_persona == pytest.approx(0.05)

    def test_add_checksum(self) -> None:
        """Can add output checksum."""
        recorder = MetadataRecorder()
        recorder.add_checksum("personas.json", "sha256:def456")

        metadata = recorder.get_metadata()
        assert metadata.checksums["personas.json"] == "sha256:def456"

    def test_add_error(self) -> None:
        """Can record errors."""
        recorder = MetadataRecorder()
        recorder.add_error("Something went wrong")
        recorder.add_error("Another error")

        metadata = recorder.get_metadata()
        assert len(metadata.errors) == 2
        assert "Something went wrong" in metadata.errors

    def test_add_warning(self) -> None:
        """Can record warnings."""
        recorder = MetadataRecorder()
        recorder.add_warning("Be careful")

        metadata = recorder.get_metadata()
        assert "Be careful" in metadata.warnings

    def test_finish(self) -> None:
        """Can finish recording and get final metadata."""
        recorder = MetadataRecorder(experiment_id="exp-123")
        recorder.start()
        recorder.set_config(model="test", persona_count=1)

        metadata = recorder.finish()

        assert metadata.timestamp_end != ""
        assert metadata.duration_seconds >= 0

    def test_finish_calculates_duration(self) -> None:
        """Finish calculates duration from timestamps."""
        recorder = MetadataRecorder()
        recorder.start()

        # Small delay to ensure measurable duration
        import time

        time.sleep(0.1)

        metadata = recorder.finish()

        assert metadata.duration_seconds >= 0.1

    def test_save(self) -> None:
        """Can save metadata to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "subdir" / "metadata.json"

            recorder = MetadataRecorder(experiment_id="exp-123")
            recorder.start()
            recorder.set_config(model="test", persona_count=2)
            recorder.finish()
            recorder.save(path)

            assert path.exists()
            content = path.read_text()
            parsed = json.loads(content)
            assert parsed["generation"]["experiment_id"] == "exp-123"


class TestRecordMetadataConvenience:
    """Tests for record_metadata convenience function."""

    def test_creates_metadata(self) -> None:
        """record_metadata creates complete metadata."""
        metadata = record_metadata(
            experiment_id="exp-123",
            run_id="run-456",
            config={"model": "claude", "persona_count": 3},
            data_files=["file1.csv", "file2.json"],
        )

        assert metadata.experiment_id == "exp-123"
        assert metadata.run_id == "run-456"
        assert metadata.configuration.model == "claude"
        assert len(metadata.data_sources.files) == 2

    def test_with_costs(self) -> None:
        """Can include costs."""
        metadata = record_metadata(
            experiment_id="exp-123",
            run_id="run-456",
            config={"model": "test", "persona_count": 1},
            data_files=[],
            costs={
                "input_tokens": 5000,
                "output_tokens": 1000,
                "total_cost_usd": 0.10,
            },
        )

        assert metadata.costs.input_tokens == 5000
        assert metadata.costs.total_cost_usd == 0.10


class TestCalculateChecksum:
    """Tests for calculate_checksum function."""

    def test_calculates_sha256_from_string(self) -> None:
        """Calculates SHA-256 from string."""
        checksum = calculate_checksum("hello world")

        assert checksum.startswith("sha256:")
        # Known SHA-256 of "hello world"
        assert (
            checksum
            == "sha256:b94d27b9934d3e08a52e52d7da7dabfac484efe37a5380ee9088f7ace2efcde9"
        )

    def test_calculates_sha256_from_bytes(self) -> None:
        """Calculates SHA-256 from bytes."""
        checksum = calculate_checksum(b"hello world")

        assert checksum.startswith("sha256:")

    def test_different_content_different_checksum(self) -> None:
        """Different content produces different checksum."""
        checksum1 = calculate_checksum("content A")
        checksum2 = calculate_checksum("content B")

        assert checksum1 != checksum2

    def test_same_content_same_checksum(self) -> None:
        """Same content produces same checksum."""
        checksum1 = calculate_checksum("identical content")
        checksum2 = calculate_checksum("identical content")

        assert checksum1 == checksum2
