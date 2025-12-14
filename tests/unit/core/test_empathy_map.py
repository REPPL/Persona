"""
Tests for empathy map loading functionality (F-029).
"""

import pytest
import json
from pathlib import Path

from persona.core.data import (
    EmpathyMap,
    EmpathyMapDimension,
    EmpathyMapLoader,
    EmpathyMapValidationResult,
    ParticipantTypeMap,
)


class TestEmpathyMapDimension:
    """Tests for EmpathyMapDimension enum."""

    def test_dimension_values(self):
        """Test dimension enum values."""
        assert EmpathyMapDimension.TASKS.value == "tasks"
        assert EmpathyMapDimension.FEELINGS.value == "feelings"
        assert EmpathyMapDimension.INFLUENCES.value == "influences"
        assert EmpathyMapDimension.PAIN_POINTS.value == "pain_points"
        assert EmpathyMapDimension.GOALS.value == "goals"

    def test_all_dimensions(self):
        """Test all five dimensions are defined."""
        assert len(EmpathyMapDimension) == 5


class TestParticipantTypeMap:
    """Tests for ParticipantTypeMap dataclass."""

    def test_basic_creation(self):
        """Test basic participant type map creation."""
        ptm = ParticipantTypeMap(
            participant_type="music_fan",
        )

        assert ptm.participant_type == "music_fan"
        assert ptm.tasks == []
        assert ptm.feelings == []
        assert ptm.influences == []
        assert ptm.pain_points == []
        assert ptm.goals == []

    def test_full_creation(self):
        """Test participant type map with all dimensions."""
        ptm = ParticipantTypeMap(
            participant_type="music_fan",
            tasks=["Collecting vinyl", "Attending concerts"],
            feelings=["Excited", "Nostalgic"],
            influences=["Friends", "Music blogs"],
            pain_points=["High prices", "Limited editions"],
            goals=["Complete collection", "Share with community"],
        )

        assert len(ptm.tasks) == 2
        assert len(ptm.feelings) == 2
        assert len(ptm.influences) == 2
        assert len(ptm.pain_points) == 2
        assert len(ptm.goals) == 2

    def test_get_dimension(self):
        """Test getting dimension by enum."""
        ptm = ParticipantTypeMap(
            participant_type="test",
            tasks=["Task 1"],
            feelings=["Feeling 1"],
        )

        assert ptm.get_dimension(EmpathyMapDimension.TASKS) == ["Task 1"]
        assert ptm.get_dimension(EmpathyMapDimension.FEELINGS) == ["Feeling 1"]
        assert ptm.get_dimension(EmpathyMapDimension.GOALS) == []

    def test_to_dict(self):
        """Test conversion to dictionary."""
        ptm = ParticipantTypeMap(
            participant_type="music_fan",
            tasks=["Task 1"],
            goals=["Goal 1"],
        )

        data = ptm.to_dict()

        assert data["participant_type"] == "music_fan"
        assert data["tasks"] == ["Task 1"]
        assert data["goals"] == ["Goal 1"]
        assert data["feelings"] == []

    def test_to_text(self):
        """Test conversion to readable text."""
        ptm = ParticipantTypeMap(
            participant_type="music_fan",
            tasks=["Collecting vinyl"],
            feelings=["Excited"],
        )

        text = ptm.to_text()

        assert "## Participant Type: music_fan" in text
        assert "### Tasks" in text
        assert "- Collecting vinyl" in text
        assert "### Feelings" in text
        assert "- Excited" in text


class TestEmpathyMap:
    """Tests for EmpathyMap dataclass."""

    def test_basic_creation(self):
        """Test basic empathy map creation."""
        em = EmpathyMap()

        assert em.participants == 0
        assert em.method == ""
        assert em.data == []
        assert em.metadata == {}

    def test_full_creation(self):
        """Test empathy map with all fields."""
        ptm = ParticipantTypeMap(
            participant_type="user",
            tasks=["Task 1"],
        )

        em = EmpathyMap(
            participants=22,
            method="co-creation workshop",
            data=[ptm],
            metadata={"date": "2024-01-15"},
        )

        assert em.participants == 22
        assert em.method == "co-creation workshop"
        assert len(em.data) == 1
        assert em.metadata["date"] == "2024-01-15"

    def test_participant_types_property(self):
        """Test participant_types property."""
        em = EmpathyMap(
            data=[
                ParticipantTypeMap(participant_type="type_a"),
                ParticipantTypeMap(participant_type="type_b"),
            ]
        )

        assert em.participant_types == ["type_a", "type_b"]

    def test_get_participant_type(self):
        """Test getting specific participant type."""
        ptm_a = ParticipantTypeMap(participant_type="type_a", tasks=["A"])
        ptm_b = ParticipantTypeMap(participant_type="type_b", tasks=["B"])

        em = EmpathyMap(data=[ptm_a, ptm_b])

        found = em.get_participant_type("type_a")
        assert found is not None
        assert found.tasks == ["A"]

        not_found = em.get_participant_type("type_c")
        assert not_found is None

    def test_to_dict(self):
        """Test conversion to dictionary."""
        em = EmpathyMap(
            participants=10,
            method="workshop",
            data=[ParticipantTypeMap(participant_type="user")],
        )

        data = em.to_dict()

        assert data["participants"] == 10
        assert data["method"] == "workshop"
        assert len(data["data"]) == 1
        assert data["data"][0]["participant_type"] == "user"

    def test_to_text(self):
        """Test conversion to readable text."""
        em = EmpathyMap(
            participants=22,
            method="co-creation workshop",
            data=[
                ParticipantTypeMap(
                    participant_type="music_fan",
                    tasks=["Collecting"],
                )
            ],
        )

        text = em.to_text()

        assert "# Empathy Map Data" in text
        assert "**Participants:** 22" in text
        assert "**Method:** co-creation workshop" in text
        assert "## Participant Type: music_fan" in text


class TestEmpathyMapLoader:
    """Tests for EmpathyMapLoader class."""

    @pytest.fixture
    def sample_yaml(self, tmp_path: Path) -> Path:
        """Create a sample YAML empathy map file."""
        content = """
participants: 22
method: "co-creation workshop with interviews"
data:
  - participant_type: "music_fan"
    tasks:
      - "Expanding and exhibiting collection(s)"
      - "Engaging with community"
    feelings:
      - "Easy to navigate"
      - "Curation is critical"
    influences:
      - "Community (artists, other superfans)"
      - "Concerts (organiser & venues)"
    pain_points:
      - "Collecting becomes increasingly time-consuming"
      - "Inaccurate/missing information"
    goals:
      - "Expand and share collection"
      - "Safe interactions with others"
"""
        file_path = tmp_path / "workshop.yaml"
        file_path.write_text(content)
        return file_path

    @pytest.fixture
    def sample_json(self, tmp_path: Path) -> Path:
        """Create a sample JSON empathy map file."""
        content = {
            "participants": 15,
            "method": "workshop",
            "data": [
                {
                    "participant_type": "developer",
                    "tasks": ["Writing code"],
                    "feelings": ["Focused"],
                    "influences": ["Documentation"],
                    "pain_points": ["Complex APIs"],
                    "goals": ["Ship features"],
                }
            ],
        }
        file_path = tmp_path / "workshop.json"
        file_path.write_text(json.dumps(content))
        return file_path

    def test_load_yaml(self, sample_yaml: Path):
        """Test loading YAML empathy map."""
        loader = EmpathyMapLoader()
        em = loader.load(sample_yaml)

        assert em.participants == 22
        assert em.method == "co-creation workshop with interviews"
        assert len(em.data) == 1
        assert em.data[0].participant_type == "music_fan"
        assert len(em.data[0].tasks) == 2

    def test_load_json(self, sample_json: Path):
        """Test loading JSON empathy map."""
        loader = EmpathyMapLoader()
        em = loader.load(sample_json)

        assert em.participants == 15
        assert em.data[0].participant_type == "developer"

    def test_load_text_yaml(self):
        """Test loading from YAML text content."""
        content = """
participants: 5
data:
  - participant_type: "user"
    tasks:
      - "Task 1"
    feelings:
      - "Happy"
    influences:
      - "Friends"
    pain_points:
      - "Issue 1"
    goals:
      - "Goal 1"
"""
        loader = EmpathyMapLoader()
        em = loader.load_text(content, format="yaml")

        assert em.participants == 5
        assert em.data[0].participant_type == "user"

    def test_load_text_json(self):
        """Test loading from JSON text content."""
        content = json.dumps({
            "participants": 3,
            "data": [
                {
                    "participant_type": "tester",
                    "tasks": ["Test"],
                    "feelings": ["Curious"],
                    "influences": ["Tools"],
                    "pain_points": ["Bugs"],
                    "goals": ["Quality"],
                }
            ],
        })
        loader = EmpathyMapLoader()
        em = loader.load_text(content, format="json")

        assert em.participants == 3

    def test_file_not_found(self, tmp_path: Path):
        """Test error on missing file."""
        loader = EmpathyMapLoader()

        with pytest.raises(FileNotFoundError):
            loader.load(tmp_path / "nonexistent.yaml")

    def test_unsupported_format(self, tmp_path: Path):
        """Test error on unsupported format."""
        file_path = tmp_path / "data.txt"
        file_path.write_text("test")

        loader = EmpathyMapLoader()

        with pytest.raises(ValueError, match="Unsupported empathy map format"):
            loader.load(file_path)

    def test_validation_missing_data(self, tmp_path: Path):
        """Test validation error on empty data."""
        file_path = tmp_path / "empty.yaml"
        file_path.write_text("participants: 10")

        loader = EmpathyMapLoader()

        with pytest.raises(ValueError, match="No participant type data"):
            loader.load(file_path)

    def test_validation_missing_participant_type(self, tmp_path: Path):
        """Test validation error on missing participant type."""
        file_path = tmp_path / "invalid.yaml"
        file_path.write_text("""
data:
  - tasks:
      - "Task 1"
""")
        loader = EmpathyMapLoader()

        with pytest.raises(ValueError, match="Participant type name is required"):
            loader.load(file_path)

    def test_strict_mode_empty_dimension(self, tmp_path: Path):
        """Test strict mode requires all dimensions."""
        file_path = tmp_path / "partial.yaml"
        file_path.write_text("""
data:
  - participant_type: "user"
    tasks:
      - "Task 1"
""")
        loader = EmpathyMapLoader(strict=True)

        with pytest.raises(ValueError, match="has no items"):
            loader.load(file_path)

    def test_non_strict_mode_warnings(self, tmp_path: Path):
        """Test non-strict mode allows empty dimensions with warnings."""
        file_path = tmp_path / "partial.yaml"
        file_path.write_text("""
data:
  - participant_type: "user"
    tasks:
      - "Task 1"
""")
        loader = EmpathyMapLoader(strict=False)
        em = loader.load(file_path)

        # Should load successfully
        assert em.data[0].participant_type == "user"

    def test_freeform_text_preserved(self, tmp_path: Path):
        """Test freeform text entries are preserved."""
        file_path = tmp_path / "freeform.yaml"
        file_path.write_text("""
data:
  - participant_type: "user"
    tasks:
      - "This is a longer, more detailed task description that includes context"
      - "Another task with special characters: @#$%"
    feelings:
      - "Mixed feelings - both excited and nervous"
    influences:
      - "Social media (Instagram, TikTok, etc.)"
    pain_points:
      - "Issue"
    goals:
      - "Goal"
""")
        loader = EmpathyMapLoader()
        em = loader.load(file_path)

        # Verify freeform text is preserved
        assert "longer, more detailed" in em.data[0].tasks[0]
        assert "@#$%" in em.data[0].tasks[1]
        assert "excited and nervous" in em.data[0].feelings[0]
        assert "(Instagram, TikTok, etc.)" in em.data[0].influences[0]

    def test_multiple_participant_types(self, tmp_path: Path):
        """Test loading multiple participant types."""
        file_path = tmp_path / "multi.yaml"
        file_path.write_text("""
participants: 30
data:
  - participant_type: "power_user"
    tasks: ["Advanced task"]
    feelings: ["Confident"]
    influences: ["Documentation"]
    pain_points: ["Lack of features"]
    goals: ["Mastery"]
  - participant_type: "novice"
    tasks: ["Basic task"]
    feelings: ["Uncertain"]
    influences: ["Tutorials"]
    pain_points: ["Complexity"]
    goals: ["Learning"]
""")
        loader = EmpathyMapLoader()
        em = loader.load(file_path)

        assert len(em.data) == 2
        assert em.participant_types == ["power_user", "novice"]

    def test_normalise_single_string(self, tmp_path: Path):
        """Test normalising single string to list."""
        file_path = tmp_path / "single.yaml"
        file_path.write_text("""
data:
  - participant_type: "user"
    tasks: "Single task as string"
    feelings: ["Normal list"]
    influences: ["Influence"]
    pain_points: ["Pain"]
    goals: ["Goal"]
""")
        loader = EmpathyMapLoader()
        em = loader.load(file_path)

        # Single string should be converted to list
        assert em.data[0].tasks == ["Single task as string"]

    def test_metadata_extraction(self, tmp_path: Path):
        """Test extra fields are captured as metadata."""
        file_path = tmp_path / "meta.yaml"
        file_path.write_text("""
participants: 10
method: "workshop"
date: "2024-01-15"
facilitator: "Research Team"
data:
  - participant_type: "user"
    tasks: ["Task"]
    feelings: ["Feeling"]
    influences: ["Influence"]
    pain_points: ["Pain"]
    goals: ["Goal"]
""")
        loader = EmpathyMapLoader()
        em = loader.load(file_path)

        assert em.metadata["date"] == "2024-01-15"
        assert em.metadata["facilitator"] == "Research Team"


class TestEmpathyMapValidation:
    """Tests for empathy map validation."""

    def test_valid_empathy_map(self):
        """Test validation of valid empathy map."""
        em = EmpathyMap(
            data=[
                ParticipantTypeMap(
                    participant_type="user",
                    tasks=["Task"],
                    feelings=["Feeling"],
                    influences=["Influence"],
                    pain_points=["Pain"],
                    goals=["Goal"],
                )
            ]
        )

        loader = EmpathyMapLoader()
        result = loader.validate(em)

        assert result.is_valid
        assert len(result.errors) == 0

    def test_empty_data_invalid(self):
        """Test empty data is invalid."""
        em = EmpathyMap(data=[])

        loader = EmpathyMapLoader()
        result = loader.validate(em)

        assert not result.is_valid
        assert any("No participant type data" in str(e) for e in result.errors)

    def test_missing_participant_type_invalid(self):
        """Test missing participant type is invalid."""
        em = EmpathyMap(
            data=[
                ParticipantTypeMap(participant_type="")
            ]
        )

        loader = EmpathyMapLoader()
        result = loader.validate(em)

        assert not result.is_valid

    def test_strict_empty_dimension_error(self):
        """Test strict mode errors on empty dimension."""
        em = EmpathyMap(
            data=[
                ParticipantTypeMap(
                    participant_type="user",
                    tasks=["Task"],
                    # Other dimensions empty
                )
            ]
        )

        loader = EmpathyMapLoader(strict=True)
        result = loader.validate(em)

        assert not result.is_valid
        assert len(result.errors) >= 4  # At least 4 empty dimensions

    def test_non_strict_empty_dimension_warning(self):
        """Test non-strict mode warns on empty dimension."""
        em = EmpathyMap(
            data=[
                ParticipantTypeMap(
                    participant_type="user",
                    tasks=["Task"],
                )
            ]
        )

        loader = EmpathyMapLoader(strict=False)
        result = loader.validate(em)

        assert result.is_valid
        assert len(result.warnings) >= 4  # Warnings for empty dimensions


class TestEmpathyMapIntegration:
    """Integration tests for empathy map workflow."""

    def test_load_validate_convert(self, tmp_path: Path):
        """Test full workflow: load, validate, convert to text."""
        file_path = tmp_path / "workshop.yaml"
        file_path.write_text("""
participants: 22
method: "co-creation workshop"
data:
  - participant_type: "music_fan"
    tasks:
      - "Expanding collection"
      - "Sharing discoveries"
    feelings:
      - "Passionate"
      - "Connected"
    influences:
      - "Online communities"
      - "Friends"
    pain_points:
      - "Time constraints"
      - "Cost"
    goals:
      - "Complete collection"
      - "Build community"
""")
        loader = EmpathyMapLoader()
        em = loader.load(file_path)

        # Convert to text for LLM processing
        text = em.to_text()

        assert "# Empathy Map Data" in text
        assert "music_fan" in text
        assert "Expanding collection" in text
        assert "Passionate" in text
        assert "Time constraints" in text

    def test_to_text_preserves_all_data(self, tmp_path: Path):
        """Test to_text includes all empathy map data."""
        file_path = tmp_path / "full.yaml"
        file_path.write_text("""
participants: 10
method: "interviews"
custom_field: "custom_value"
data:
  - participant_type: "type_a"
    tasks: ["Task A1", "Task A2"]
    feelings: ["Feeling A"]
    influences: ["Influence A"]
    pain_points: ["Pain A"]
    goals: ["Goal A"]
  - participant_type: "type_b"
    tasks: ["Task B"]
    feelings: ["Feeling B"]
    influences: ["Influence B"]
    pain_points: ["Pain B"]
    goals: ["Goal B"]
""")
        loader = EmpathyMapLoader()
        em = loader.load(file_path)
        text = em.to_text()

        # All participant types present
        assert "type_a" in text
        assert "type_b" in text

        # All data present
        assert "Task A1" in text
        assert "Task A2" in text
        assert "Task B" in text

        # Metadata present
        assert "custom_field" in text
        assert "custom_value" in text
