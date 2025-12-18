"""
Tests for workshop data import functionality (F-031).
"""

from pathlib import Path

import pytest
from persona.core.data import (
    MockVisionExtractor,
    PostItNote,
    WorkshopCategory,
    WorkshopExtractionResult,
    WorkshopImportConfig,
    WorkshopImporter,
)


class TestWorkshopCategory:
    """Tests for WorkshopCategory enum."""

    def test_category_values(self):
        """Test category enum values."""
        assert WorkshopCategory.TASKS.value == "tasks"
        assert WorkshopCategory.FEELINGS.value == "feelings"
        assert WorkshopCategory.INFLUENCES.value == "influences"
        assert WorkshopCategory.PAIN_POINTS.value == "pain_points"
        assert WorkshopCategory.GOALS.value == "goals"
        assert WorkshopCategory.UNCATEGORISED.value == "uncategorised"

    def test_all_categories(self):
        """Test all categories are defined."""
        assert len(WorkshopCategory) == 6


class TestPostItNote:
    """Tests for PostItNote dataclass."""

    def test_basic_creation(self):
        """Test basic post-it note creation."""
        note = PostItNote(text="Test note")

        assert note.text == "Test note"
        assert note.confidence == 1.0
        assert note.category == WorkshopCategory.UNCATEGORISED
        assert note.position is None
        assert note.colour is None

    def test_full_creation(self):
        """Test post-it with all attributes."""
        note = PostItNote(
            text="Important task",
            confidence=0.95,
            category=WorkshopCategory.TASKS,
            position=(100, 200),
            colour="yellow",
        )

        assert note.text == "Important task"
        assert note.confidence == 0.95
        assert note.category == WorkshopCategory.TASKS
        assert note.position == (100, 200)
        assert note.colour == "yellow"

    def test_to_dict(self):
        """Test conversion to dictionary."""
        note = PostItNote(
            text="My goal",
            confidence=0.8,
            category=WorkshopCategory.GOALS,
        )

        data = note.to_dict()

        assert data["text"] == "My goal"
        assert data["confidence"] == 0.8
        assert data["category"] == "goals"


class TestWorkshopExtractionResult:
    """Tests for WorkshopExtractionResult dataclass."""

    def test_basic_creation(self, tmp_path: Path):
        """Test basic result creation."""
        result = WorkshopExtractionResult(
            source_image=tmp_path / "test.jpg",
        )

        assert result.source_image == tmp_path / "test.jpg"
        assert result.post_its == []
        assert result.clusters == []
        assert result.overall_confidence == 0.0

    def test_full_creation(self, tmp_path: Path):
        """Test result with all attributes."""
        notes = [
            PostItNote(text="Note 1"),
            PostItNote(text="Note 2"),
        ]

        result = WorkshopExtractionResult(
            source_image=tmp_path / "workshop.jpg",
            post_its=notes,
            clusters=[[0], [1]],
            raw_response='{"test": true}',
            overall_confidence=0.9,
        )

        assert len(result.post_its) == 2
        assert len(result.clusters) == 2
        assert result.overall_confidence == 0.9

    def test_to_dict(self, tmp_path: Path):
        """Test conversion to dictionary."""
        result = WorkshopExtractionResult(
            source_image=tmp_path / "test.jpg",
            post_its=[PostItNote(text="Test")],
            overall_confidence=0.85,
        )

        data = result.to_dict()

        assert "test.jpg" in data["source_image"]
        assert len(data["post_its"]) == 1
        assert data["overall_confidence"] == 0.85


class TestWorkshopImportConfig:
    """Tests for WorkshopImportConfig."""

    def test_default_config(self):
        """Test default configuration."""
        config = WorkshopImportConfig()

        assert config.confidence_threshold == 0.5
        assert config.auto_categorise is True
        assert config.detect_clusters is True
        assert ".jpg" in config.supported_formats

    def test_custom_config(self):
        """Test custom configuration."""
        config = WorkshopImportConfig(
            confidence_threshold=0.8,
            auto_categorise=False,
            detect_clusters=False,
        )

        assert config.confidence_threshold == 0.8
        assert config.auto_categorise is False


class TestMockVisionExtractor:
    """Tests for MockVisionExtractor."""

    def test_extract_returns_result(self, tmp_path: Path):
        """Test extraction returns valid result."""
        # Create a mock image file
        image_path = tmp_path / "workshop.jpg"
        image_path.write_bytes(b"mock image data")

        extractor = MockVisionExtractor()
        result = extractor.extract_from_image(image_path)

        assert isinstance(result, WorkshopExtractionResult)
        assert result.source_image == image_path
        assert len(result.post_its) > 0
        assert result.overall_confidence > 0

    def test_extract_category_from_filename(self, tmp_path: Path):
        """Test extraction picks category from filename."""
        # Create image with category hint in name
        image_path = tmp_path / "tasks_board.jpg"
        image_path.write_bytes(b"mock image data")

        extractor = MockVisionExtractor()
        result = extractor.extract_from_image(image_path)

        # Should have tasks-focused extraction
        task_notes = [
            n for n in result.post_its if n.category == WorkshopCategory.TASKS
        ]
        assert len(task_notes) > 0


class TestWorkshopImporter:
    """Tests for WorkshopImporter class."""

    @pytest.fixture
    def sample_images(self, tmp_path: Path) -> list[Path]:
        """Create sample image files."""
        images = []
        for name in ["workshop1.jpg", "workshop2.png", "notes.webp"]:
            path = tmp_path / name
            path.write_bytes(b"mock image data")
            images.append(path)
        return images

    @pytest.fixture
    def importer(self) -> WorkshopImporter:
        """Create an importer instance."""
        return WorkshopImporter()

    def test_init_default(self):
        """Test default initialisation."""
        importer = WorkshopImporter()

        assert importer.config.confidence_threshold == 0.5
        assert isinstance(importer.extractor, MockVisionExtractor)

    def test_init_with_config(self):
        """Test initialisation with custom config."""
        config = WorkshopImportConfig(confidence_threshold=0.9)
        importer = WorkshopImporter(config=config)

        assert importer.config.confidence_threshold == 0.9

    def test_import_images(self, importer, sample_images):
        """Test importing multiple images."""
        results = importer.import_images(sample_images)

        assert len(results) == 3
        for result in results:
            assert isinstance(result, WorkshopExtractionResult)
            assert len(result.post_its) > 0

    def test_import_images_skips_nonexistent(self, importer, tmp_path: Path):
        """Test import skips non-existent files."""
        paths = [
            tmp_path / "exists.jpg",
            tmp_path / "missing.jpg",
        ]
        paths[0].write_bytes(b"image data")

        results = importer.import_images(paths)

        assert len(results) == 1

    def test_import_images_filters_formats(self, importer, tmp_path: Path):
        """Test import filters by supported formats."""
        # Create files with different extensions
        jpg = tmp_path / "image.jpg"
        txt = tmp_path / "document.txt"
        jpg.write_bytes(b"image")
        txt.write_bytes(b"text")

        results = importer.import_images([jpg, txt])

        assert len(results) == 1

    def test_import_directory(self, importer, tmp_path: Path):
        """Test importing all images from directory."""
        # Create images in directory
        for name in ["a.jpg", "b.png", "c.txt"]:
            (tmp_path / name).write_bytes(b"data")

        results = importer.import_directory(tmp_path)

        # Should find 2 images (not txt)
        assert len(results) == 2

    def test_import_directory_recursive(self, importer, tmp_path: Path):
        """Test recursive directory import."""
        # Create nested structure
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (tmp_path / "root.jpg").write_bytes(b"data")
        (subdir / "nested.jpg").write_bytes(b"data")

        # Non-recursive
        results = importer.import_directory(tmp_path, recursive=False)
        assert len(results) == 1

        # Recursive
        results = importer.import_directory(tmp_path, recursive=True)
        assert len(results) == 2

    def test_to_editable_yaml(self, importer, sample_images):
        """Test YAML export for editing."""
        results = importer.import_images(sample_images[:1])
        yaml_content = importer.to_editable_yaml(results)

        # Check structure
        assert "# Workshop Import Results" in yaml_content
        assert "participants:" in yaml_content
        assert "method:" in yaml_content
        assert "data:" in yaml_content

    def test_to_editable_yaml_custom_participant(self, importer, sample_images):
        """Test YAML export with custom participant type."""
        results = importer.import_images(sample_images[:1])
        yaml_content = importer.to_editable_yaml(
            results,
            participant_type="music_enthusiast",
        )

        assert "music_enthusiast" in yaml_content

    def test_to_json(self, importer, sample_images):
        """Test JSON export."""
        results = importer.import_images(sample_images[:1])
        json_content = importer.to_json(results)

        import json

        data = json.loads(json_content)

        assert "workshop_results" in data
        assert data["total_images"] == 1
        assert "total_post_its" in data

    def test_filter_by_confidence(self, importer, tmp_path: Path):
        """Test filtering by confidence threshold."""
        # Create image
        image = tmp_path / "test.jpg"
        image.write_bytes(b"data")

        results = importer.import_images([image])

        # Filter with high threshold
        filtered = importer.filter_by_confidence(results, threshold=0.9)

        # Should have fewer post-its (mock confidence is ~0.85)
        original_count = sum(len(r.post_its) for r in results)
        filtered_count = sum(len(r.post_its) for r in filtered)
        assert filtered_count <= original_count


class TestWorkshopImportIntegration:
    """Integration tests for workshop import workflow."""

    def test_full_import_workflow(self, tmp_path: Path):
        """Test complete import workflow."""
        # Create mock workshop images
        images_dir = tmp_path / "workshop_photos"
        images_dir.mkdir()

        for name in ["board_tasks.jpg", "board_feelings.jpg", "board_goals.jpg"]:
            (images_dir / name).write_bytes(b"mock image data")

        # Import images
        importer = WorkshopImporter()
        results = importer.import_directory(images_dir)

        assert len(results) == 3

        # Generate editable YAML
        yaml_content = importer.to_editable_yaml(
            results,
            participant_type="workshop_attendee",
        )

        # Verify YAML is valid
        import yaml

        parsed = yaml.safe_load(yaml_content)

        assert parsed["participants"] == 3
        assert parsed["data"][0]["participant_type"] == "workshop_attendee"

    def test_yaml_can_be_loaded_as_empathy_map(self, tmp_path: Path):
        """Test generated YAML is compatible with empathy map loader."""
        from persona.core.data import EmpathyMapLoader

        # Create and import images
        image = tmp_path / "workshop.jpg"
        image.write_bytes(b"data")

        importer = WorkshopImporter()
        results = importer.import_images([image])

        # Generate YAML
        yaml_content = importer.to_editable_yaml(results)

        # Save and load as empathy map
        yaml_path = tmp_path / "workshop_output.yaml"
        yaml_path.write_text(yaml_content)

        loader = EmpathyMapLoader(strict=False)
        em = loader.load(yaml_path)

        assert len(em.data) == 1
        assert em.data[0].participant_type == "workshop_participant"
