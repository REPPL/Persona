"""
Tests for interactive refinement functionality (F-025).
"""

import pytest
from pathlib import Path

from persona.core.generation.parser import Persona
from persona.core.refinement import (
    PersonaRefiner,
    RefinementSession,
    RefinementInstruction,
    RefinementResult,
    RefinementHistory,
)


class TestRefinementInstruction:
    """Tests for RefinementInstruction dataclass."""

    def test_basic_instruction(self):
        """Test creating basic instruction."""
        instr = RefinementInstruction(instruction="Make more technical")

        assert instr.instruction == "Make more technical"
        assert instr.timestamp != ""
        assert len(instr.target_fields) == 0

    def test_instruction_with_targets(self):
        """Test instruction with target fields."""
        instr = RefinementInstruction(
            instruction="Update goals",
            target_fields=["goals", "summary"],
        )

        assert len(instr.target_fields) == 2
        assert "goals" in instr.target_fields

    def test_to_dict(self):
        """Test conversion to dictionary."""
        instr = RefinementInstruction(
            instruction="Test",
            target_fields=["goals"],
        )

        data = instr.to_dict()

        assert data["instruction"] == "Test"
        assert data["target_fields"] == ["goals"]

    def test_from_dict(self):
        """Test creation from dictionary."""
        data = {
            "instruction": "Update",
            "target_fields": ["name"],
            "timestamp": "2025-01-01T00:00:00",
        }

        instr = RefinementInstruction.from_dict(data)

        assert instr.instruction == "Update"
        assert instr.target_fields == ["name"]


class TestRefinementResult:
    """Tests for RefinementResult dataclass."""

    def test_success_result(self):
        """Test successful result."""
        persona = Persona(id="p001", name="Alice")
        result = RefinementResult(
            success=True,
            persona=persona,
            changes=["Added goal"],
            version=1,
        )

        assert result.success is True
        assert result.persona is not None
        assert len(result.changes) == 1
        assert result.version == 1

    def test_failed_result(self):
        """Test failed result."""
        result = RefinementResult(
            success=False,
            error="Invalid instruction",
        )

        assert result.success is False
        assert result.error == "Invalid instruction"
        assert result.persona is None

    def test_to_dict(self):
        """Test conversion to dictionary."""
        result = RefinementResult(
            success=True,
            changes=["Change 1"],
            version=2,
        )

        data = result.to_dict()

        assert data["success"] is True
        assert data["version"] == 2


class TestRefinementHistory:
    """Tests for RefinementHistory dataclass."""

    def test_empty_history(self):
        """Test empty history."""
        history = RefinementHistory(persona_id="p001")

        assert history.persona_id == "p001"
        assert history.version_count == 0
        assert history.can_undo is False
        assert history.can_redo is False

    def test_history_with_versions(self):
        """Test history with versions."""
        history = RefinementHistory(
            persona_id="p001",
            versions=[
                Persona(id="p001", name="V1"),
                Persona(id="p001", name="V2"),
            ],
            current_version=1,
        )

        assert history.version_count == 2
        assert history.can_undo is True
        assert history.can_redo is False
        assert history.current.name == "V2"

    def test_can_redo(self):
        """Test can_redo property."""
        history = RefinementHistory(
            persona_id="p001",
            versions=[
                Persona(id="p001", name="V1"),
                Persona(id="p001", name="V2"),
            ],
            current_version=0,  # At first version
        )

        assert history.can_redo is True

    def test_to_dict(self):
        """Test conversion to dictionary."""
        history = RefinementHistory(
            persona_id="p001",
            versions=[Persona(id="p001", name="V1")],
            current_version=0,
        )

        data = history.to_dict()

        assert data["persona_id"] == "p001"
        assert data["version_count"] == 1


class TestRefinementSession:
    """Tests for RefinementSession dataclass."""

    def test_create_session(self):
        """Test creating a session."""
        persona = Persona(id="p001", name="Alice")
        session = RefinementSession(persona=persona)

        assert session.persona.name == "Alice"
        assert session.version == 0
        assert session.history.version_count == 1

    def test_add_version(self):
        """Test adding a version."""
        persona = Persona(id="p001", name="Alice")
        session = RefinementSession(persona=persona)

        new_persona = Persona(id="p001", name="Alice Updated")
        instr = RefinementInstruction(instruction="Update name")

        session.add_version(new_persona, instr)

        assert session.version == 1
        assert session.persona.name == "Alice Updated"
        assert session.history.version_count == 2

    def test_undo(self):
        """Test undo."""
        persona = Persona(id="p001", name="Alice")
        session = RefinementSession(persona=persona)

        # Add a version
        new_persona = Persona(id="p001", name="Updated")
        instr = RefinementInstruction(instruction="Update")
        session.add_version(new_persona, instr)

        # Undo
        result = session.undo()

        assert result is not None
        assert result.name == "Alice"
        assert session.version == 0

    def test_undo_fails_at_start(self):
        """Test undo fails when at first version."""
        persona = Persona(id="p001", name="Alice")
        session = RefinementSession(persona=persona)

        result = session.undo()
        assert result is None

    def test_redo(self):
        """Test redo."""
        persona = Persona(id="p001", name="Alice")
        session = RefinementSession(persona=persona)

        # Add then undo
        new_persona = Persona(id="p001", name="Updated")
        instr = RefinementInstruction(instruction="Update")
        session.add_version(new_persona, instr)
        session.undo()

        # Redo
        result = session.redo()

        assert result is not None
        assert result.name == "Updated"
        assert session.version == 1

    def test_redo_fails_at_end(self):
        """Test redo fails when at last version."""
        persona = Persona(id="p001", name="Alice")
        session = RefinementSession(persona=persona)

        result = session.redo()
        assert result is None

    def test_get_version(self):
        """Test getting specific version."""
        persona = Persona(id="p001", name="V0")
        session = RefinementSession(persona=persona)

        # Add versions
        session.add_version(
            Persona(id="p001", name="V1"),
            RefinementInstruction(instruction=""),
        )
        session.add_version(
            Persona(id="p001", name="V2"),
            RefinementInstruction(instruction=""),
        )

        v0 = session.get_version(0)
        v1 = session.get_version(1)
        v2 = session.get_version(2)
        invalid = session.get_version(99)

        assert v0.name == "V0"
        assert v1.name == "V1"
        assert v2.name == "V2"
        assert invalid is None

    def test_get_diff(self):
        """Test getting diff between versions."""
        persona = Persona(
            id="p001",
            name="Alice",
            goals=["Goal A"],
        )
        session = RefinementSession(persona=persona)

        # Add version with different goals
        new_persona = Persona(
            id="p001",
            name="Alice Updated",
            goals=["Goal A", "Goal B"],
        )
        session.add_version(
            new_persona,
            RefinementInstruction(instruction="Add goal"),
        )

        diff = session.get_diff(0, 1)

        assert "name" in diff
        assert diff["name"]["from"] == "Alice"
        assert diff["name"]["to"] == "Alice Updated"
        assert "goals" in diff
        assert "Goal B" in diff["goals"]["added"]

    def test_add_version_truncates_redo(self):
        """Test adding version truncates redo history."""
        persona = Persona(id="p001", name="V0")
        session = RefinementSession(persona=persona)

        # Add two versions
        session.add_version(
            Persona(id="p001", name="V1"),
            RefinementInstruction(instruction=""),
        )
        session.add_version(
            Persona(id="p001", name="V2"),
            RefinementInstruction(instruction=""),
        )

        # Undo twice
        session.undo()
        session.undo()
        assert session.version == 0

        # Add new version (should truncate V1 and V2)
        session.add_version(
            Persona(id="p001", name="V1-new"),
            RefinementInstruction(instruction=""),
        )

        assert session.history.version_count == 2
        assert session.persona.name == "V1-new"


class TestPersonaRefiner:
    """Tests for PersonaRefiner class."""

    def test_init(self):
        """Test initialisation."""
        refiner = PersonaRefiner()

        assert len(refiner._sessions) == 0

    def test_create_session(self):
        """Test creating a session."""
        refiner = PersonaRefiner()
        persona = Persona(id="p001", name="Alice")

        session = refiner.create_session(persona)

        assert session.persona.name == "Alice"
        assert "p001" in refiner._sessions

    def test_get_session(self):
        """Test getting a session."""
        refiner = PersonaRefiner()
        persona = Persona(id="p001", name="Alice")
        refiner.create_session(persona)

        session = refiner.get_session("p001")

        assert session is not None
        assert session.persona.name == "Alice"

    def test_get_session_not_found(self):
        """Test getting non-existent session."""
        refiner = PersonaRefiner()

        session = refiner.get_session("nonexistent")
        assert session is None

    def test_refine_add_goal(self):
        """Test refining to add a goal."""
        refiner = PersonaRefiner()
        persona = Persona(id="p001", name="Alice", goals=["Goal 1"])
        session = refiner.create_session(persona)

        result = refiner.refine(session, 'Add goal "Learn Python"')

        assert result.success is True
        assert "Learn Python" in result.persona.goals
        assert result.version == 1

    def test_refine_remove_goal(self):
        """Test refining to remove a goal."""
        refiner = PersonaRefiner()
        persona = Persona(
            id="p001",
            name="Alice",
            goals=["Goal 1", "Goal 2"],
        )
        session = refiner.create_session(persona)

        result = refiner.refine(session, "Remove last goal")

        assert result.success is True
        assert len(result.persona.goals) == 1

    def test_refine_more_technical(self):
        """Test making persona more technical."""
        refiner = PersonaRefiner()
        persona = Persona(id="p001", name="Alice")
        session = refiner.create_session(persona)

        result = refiner.refine(session, "Make more technical")

        assert result.success is True
        assert result.persona.demographics.get("technical_level") == "advanced"

    def test_refine_rename(self):
        """Test renaming persona."""
        refiner = PersonaRefiner()
        persona = Persona(id="p001", name="Alice")
        session = refiner.create_session(persona)

        result = refiner.refine(session, 'Rename to "Bob"')

        assert result.success is True
        assert result.persona.name == "Bob"

    def test_undo(self):
        """Test undo operation."""
        refiner = PersonaRefiner()
        persona = Persona(id="p001", name="Alice")
        session = refiner.create_session(persona)

        refiner.refine(session, 'Rename to "Bob"')
        result = refiner.undo(session)

        assert result.success is True
        assert result.persona.name == "Alice"

    def test_undo_at_start(self):
        """Test undo at first version fails."""
        refiner = PersonaRefiner()
        persona = Persona(id="p001", name="Alice")
        session = refiner.create_session(persona)

        result = refiner.undo(session)

        assert result.success is False
        assert "Nothing to undo" in result.error

    def test_redo(self):
        """Test redo operation."""
        refiner = PersonaRefiner()
        persona = Persona(id="p001", name="Alice")
        session = refiner.create_session(persona)

        refiner.refine(session, 'Rename to "Bob"')
        refiner.undo(session)
        result = refiner.redo(session)

        assert result.success is True
        assert result.persona.name == "Bob"

    def test_redo_at_end(self):
        """Test redo at last version fails."""
        refiner = PersonaRefiner()
        persona = Persona(id="p001", name="Alice")
        session = refiner.create_session(persona)

        result = refiner.redo(session)

        assert result.success is False
        assert "Nothing to redo" in result.error

    def test_revert_to_version(self):
        """Test reverting to specific version."""
        refiner = PersonaRefiner()
        persona = Persona(id="p001", name="V0")
        session = refiner.create_session(persona)

        refiner.refine(session, 'Rename to "V1"')
        refiner.refine(session, 'Rename to "V2"')

        result = refiner.revert_to_version(session, 0)

        assert result.success is True
        assert result.persona.name == "V0"
        # Should create new version (not just move pointer)
        assert session.version == 3

    def test_revert_to_invalid_version(self):
        """Test reverting to invalid version."""
        refiner = PersonaRefiner()
        persona = Persona(id="p001", name="Alice")
        session = refiner.create_session(persona)

        result = refiner.revert_to_version(session, 99)

        assert result.success is False
        assert "Invalid version" in result.error

    def test_get_diff(self):
        """Test getting diff."""
        refiner = PersonaRefiner()
        persona = Persona(id="p001", name="Alice")
        session = refiner.create_session(persona)

        refiner.refine(session, 'Rename to "Bob"')

        diff = refiner.get_diff(session)

        assert "name" in diff
        assert diff["name"]["from"] == "Alice"
        assert diff["name"]["to"] == "Bob"

    def test_list_templates(self):
        """Test listing templates."""
        refiner = PersonaRefiner()
        templates = refiner.list_templates()

        assert "make_more_technical" in templates
        assert "simplify" in templates

    def test_close_session(self):
        """Test closing a session."""
        refiner = PersonaRefiner()
        persona = Persona(id="p001", name="Alice")
        refiner.create_session(persona)

        result = refiner.close_session("p001")

        assert result is True
        assert refiner.get_session("p001") is None

    def test_close_session_not_found(self):
        """Test closing non-existent session."""
        refiner = PersonaRefiner()

        result = refiner.close_session("nonexistent")
        assert result is False

    def test_multiple_refinements(self):
        """Test multiple refinements in sequence."""
        refiner = PersonaRefiner()
        persona = Persona(
            id="p001",
            name="Alice",
            goals=["Goal 1"],
        )
        session = refiner.create_session(persona)

        refiner.refine(session, 'Add goal "Goal 2"')
        refiner.refine(session, 'Add goal "Goal 3"')
        refiner.refine(session, "Make more technical")

        assert session.version == 3
        assert len(session.persona.goals) == 3
        assert session.persona.demographics.get("technical_level") == "advanced"
