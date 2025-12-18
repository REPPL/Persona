"""
Interactive persona refinement functionality.

This module provides the PersonaRefiner class for iteratively
refining personas through natural language instructions.
"""

import copy
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from persona.core.generation.parser import Persona


@dataclass
class RefinementInstruction:
    """
    An instruction for refining a persona.

    Attributes:
        instruction: Natural language instruction.
        target_fields: Specific fields to modify (optional).
        timestamp: When the instruction was given.
    """

    instruction: str
    target_fields: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "instruction": self.instruction,
            "target_fields": self.target_fields,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RefinementInstruction":
        """Create from dictionary."""
        return cls(
            instruction=data["instruction"],
            target_fields=data.get("target_fields", []),
            timestamp=data.get("timestamp", ""),
        )


@dataclass
class RefinementResult:
    """
    Result of a refinement operation.

    Attributes:
        success: Whether refinement succeeded.
        persona: The refined persona.
        changes: Description of changes made.
        instruction: The instruction that was applied.
        version: Version number after refinement.
    """

    success: bool
    persona: Persona | None = None
    changes: list[str] = field(default_factory=list)
    instruction: RefinementInstruction | None = None
    version: int = 0
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "success": self.success,
            "changes": self.changes,
            "version": self.version,
            "error": self.error,
            "instruction": (self.instruction.to_dict() if self.instruction else None),
        }


@dataclass
class RefinementHistory:
    """
    History of refinements for a persona.

    Attributes:
        persona_id: ID of the persona.
        versions: List of persona versions (snapshots).
        instructions: List of refinement instructions.
        current_version: Current version index.
    """

    persona_id: str
    versions: list[Persona] = field(default_factory=list)
    instructions: list[RefinementInstruction] = field(default_factory=list)
    current_version: int = 0

    @property
    def version_count(self) -> int:
        """Number of versions."""
        return len(self.versions)

    @property
    def can_undo(self) -> bool:
        """Check if undo is available."""
        return self.current_version > 0

    @property
    def can_redo(self) -> bool:
        """Check if redo is available."""
        return self.current_version < len(self.versions) - 1

    @property
    def current(self) -> Persona | None:
        """Get current persona version."""
        if 0 <= self.current_version < len(self.versions):
            return self.versions[self.current_version]
        return None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "persona_id": self.persona_id,
            "version_count": self.version_count,
            "current_version": self.current_version,
            "can_undo": self.can_undo,
            "can_redo": self.can_redo,
            "instructions": [i.to_dict() for i in self.instructions],
        }


@dataclass
class RefinementSession:
    """
    A refinement session for a persona.

    Tracks the history of refinements and enables undo/redo.

    Attributes:
        persona: Current persona.
        history: Refinement history.
        refiner: Reference to refiner (for operations).
    """

    persona: Persona
    history: RefinementHistory | None = None

    def __post_init__(self):
        """Initialise history if needed."""
        if self.history is None:
            self.history = RefinementHistory(
                persona_id=self.persona.id,
                versions=[copy.deepcopy(self.persona)],
                current_version=0,
            )
        elif not self.history.versions:
            self.history.versions = [copy.deepcopy(self.persona)]
            self.history.current_version = 0

    @property
    def version(self) -> int:
        """Current version number."""
        return self.history.current_version

    def add_version(
        self,
        persona: Persona,
        instruction: RefinementInstruction,
    ) -> None:
        """
        Add a new version to history.

        Args:
            persona: The new persona version.
            instruction: The instruction that created it.
        """
        # Truncate any redo history
        if self.history.current_version < len(self.history.versions) - 1:
            self.history.versions = self.history.versions[
                : self.history.current_version + 1
            ]
            self.history.instructions = self.history.instructions[
                : self.history.current_version
            ]

        # Add new version
        self.history.versions.append(copy.deepcopy(persona))
        self.history.instructions.append(instruction)
        self.history.current_version = len(self.history.versions) - 1
        self.persona = persona

    def undo(self) -> Persona | None:
        """
        Undo the last refinement.

        Returns:
            Previous persona version, or None if can't undo.
        """
        if not self.history.can_undo:
            return None

        self.history.current_version -= 1
        self.persona = copy.deepcopy(self.history.current)
        return self.persona

    def redo(self) -> Persona | None:
        """
        Redo the last undone refinement.

        Returns:
            Next persona version, or None if can't redo.
        """
        if not self.history.can_redo:
            return None

        self.history.current_version += 1
        self.persona = copy.deepcopy(self.history.current)
        return self.persona

    def get_version(self, version: int) -> Persona | None:
        """
        Get a specific version.

        Args:
            version: Version number.

        Returns:
            Persona at that version, or None if invalid.
        """
        if 0 <= version < len(self.history.versions):
            return self.history.versions[version]
        return None

    def get_diff(self, version_a: int, version_b: int) -> dict[str, Any]:
        """
        Get differences between two versions.

        Args:
            version_a: First version.
            version_b: Second version.

        Returns:
            Dictionary of differences.
        """
        persona_a = self.get_version(version_a)
        persona_b = self.get_version(version_b)

        if persona_a is None or persona_b is None:
            return {"error": "Invalid version"}

        changes = {}

        # Compare basic fields
        if persona_a.name != persona_b.name:
            changes["name"] = {"from": persona_a.name, "to": persona_b.name}

        # Compare lists
        for field_name in ["goals", "pain_points", "behaviours"]:
            val_a = getattr(persona_a, field_name, []) or []
            val_b = getattr(persona_b, field_name, []) or []

            if set(val_a) != set(val_b):
                added = [v for v in val_b if v not in val_a]
                removed = [v for v in val_a if v not in val_b]
                if added or removed:
                    changes[field_name] = {"added": added, "removed": removed}

        # Compare demographics
        demo_a = persona_a.demographics or {}
        demo_b = persona_b.demographics or {}

        if demo_a != demo_b:
            demo_changes = {}
            all_keys = set(demo_a.keys()) | set(demo_b.keys())
            for key in all_keys:
                if demo_a.get(key) != demo_b.get(key):
                    demo_changes[key] = {
                        "from": demo_a.get(key),
                        "to": demo_b.get(key),
                    }
            if demo_changes:
                changes["demographics"] = demo_changes

        return changes


class PersonaRefiner:
    """
    Refines personas through natural language instructions.

    Provides iterative refinement with history tracking,
    undo/redo support, and change summaries.

    Example:
        refiner = PersonaRefiner()
        session = refiner.create_session(persona)
        result = refiner.refine(session, "Make more technical")
        print(f"Changes: {result.changes}")
    """

    # Default refinement templates
    TEMPLATES = {
        "make_more_technical": {
            "affects": ["goals", "behaviours", "demographics"],
            "description": "Increase technical depth and expertise",
        },
        "simplify": {
            "affects": ["summary", "goals"],
            "description": "Simplify language and reduce complexity",
        },
        "add_demographic": {
            "affects": ["demographics"],
            "description": "Add or enhance demographic details",
        },
        "emphasize_pain_points": {
            "affects": ["pain_points", "summary"],
            "description": "Emphasise frustrations and challenges",
        },
    }

    def __init__(self) -> None:
        """Initialise the refiner."""
        self._sessions: dict[str, RefinementSession] = {}

    def create_session(self, persona: Persona) -> RefinementSession:
        """
        Create a refinement session for a persona.

        Args:
            persona: Persona to refine.

        Returns:
            New RefinementSession.
        """
        session = RefinementSession(persona=copy.deepcopy(persona))
        self._sessions[persona.id] = session
        return session

    def get_session(self, persona_id: str) -> RefinementSession | None:
        """
        Get an existing session.

        Args:
            persona_id: Persona ID.

        Returns:
            Session if exists, None otherwise.
        """
        return self._sessions.get(persona_id)

    def refine(
        self,
        session: RefinementSession,
        instruction: str,
        target_fields: list[str] | None = None,
    ) -> RefinementResult:
        """
        Apply a refinement instruction.

        Args:
            session: Refinement session.
            instruction: Natural language instruction.
            target_fields: Specific fields to modify.

        Returns:
            RefinementResult with outcome.
        """
        # Create instruction record
        instr = RefinementInstruction(
            instruction=instruction,
            target_fields=target_fields or [],
        )

        # Parse and apply the instruction
        try:
            refined_persona, changes = self._apply_instruction(
                session.persona,
                instruction,
                target_fields,
            )

            # Add to history
            session.add_version(refined_persona, instr)

            return RefinementResult(
                success=True,
                persona=refined_persona,
                changes=changes,
                instruction=instr,
                version=session.version,
            )

        except Exception as e:
            return RefinementResult(
                success=False,
                error=str(e),
                instruction=instr,
            )

    def undo(self, session: RefinementSession) -> RefinementResult:
        """
        Undo the last refinement.

        Args:
            session: Refinement session.

        Returns:
            RefinementResult with previous state.
        """
        if not session.history.can_undo:
            return RefinementResult(
                success=False,
                error="Nothing to undo",
            )

        persona = session.undo()
        return RefinementResult(
            success=True,
            persona=persona,
            changes=["Reverted to previous version"],
            version=session.version,
        )

    def redo(self, session: RefinementSession) -> RefinementResult:
        """
        Redo the last undone refinement.

        Args:
            session: Refinement session.

        Returns:
            RefinementResult with next state.
        """
        if not session.history.can_redo:
            return RefinementResult(
                success=False,
                error="Nothing to redo",
            )

        persona = session.redo()
        return RefinementResult(
            success=True,
            persona=persona,
            changes=["Restored next version"],
            version=session.version,
        )

    def revert_to_version(
        self,
        session: RefinementSession,
        version: int,
    ) -> RefinementResult:
        """
        Revert to a specific version.

        Args:
            session: Refinement session.
            version: Version number to revert to.

        Returns:
            RefinementResult with that version.
        """
        persona = session.get_version(version)
        if persona is None:
            return RefinementResult(
                success=False,
                error=f"Invalid version: {version}",
            )

        # Create as new version (not just changing pointer)
        instr = RefinementInstruction(
            instruction=f"Revert to version {version}",
        )

        session.add_version(copy.deepcopy(persona), instr)

        return RefinementResult(
            success=True,
            persona=session.persona,
            changes=[f"Reverted to version {version}"],
            instruction=instr,
            version=session.version,
        )

    def get_diff(
        self,
        session: RefinementSession,
        version_a: int | None = None,
        version_b: int | None = None,
    ) -> dict[str, Any]:
        """
        Get differences between versions.

        Args:
            session: Refinement session.
            version_a: First version (default: 0).
            version_b: Second version (default: current).

        Returns:
            Dictionary of differences.
        """
        if version_a is None:
            version_a = 0
        if version_b is None:
            version_b = session.version

        return session.get_diff(version_a, version_b)

    def _apply_instruction(
        self,
        persona: Persona,
        instruction: str,
        target_fields: list[str] | None = None,
    ) -> tuple[Persona, list[str]]:
        """
        Apply an instruction to a persona.

        This is a simplified implementation that handles common
        patterns. A full implementation would use an LLM.

        Args:
            persona: Persona to modify.
            instruction: Natural language instruction.
            target_fields: Fields to modify.

        Returns:
            Tuple of (modified persona, list of changes).
        """
        # Create a copy to modify
        modified = copy.deepcopy(persona)
        changes = []
        instruction_lower = instruction.lower()

        # Handle common instruction patterns
        if "add" in instruction_lower and "goal" in instruction_lower:
            # Extract quoted content or use generic
            if '"' in instruction:
                new_goal = instruction.split('"')[1]
            else:
                new_goal = "New goal from refinement"

            modified.goals = list(modified.goals or []) + [new_goal]
            changes.append(f"Added goal: {new_goal}")

        elif "remove" in instruction_lower and "goal" in instruction_lower:
            if modified.goals:
                removed = modified.goals[-1]
                modified.goals = list(modified.goals)[:-1]
                changes.append(f"Removed goal: {removed}")

        elif "add" in instruction_lower and "pain" in instruction_lower:
            if '"' in instruction:
                new_pain = instruction.split('"')[1]
            else:
                new_pain = "New pain point from refinement"

            modified.pain_points = list(modified.pain_points or []) + [new_pain]
            changes.append(f"Added pain point: {new_pain}")

        elif "more technical" in instruction_lower:
            # Add technical indicators
            if modified.demographics is None:
                modified.demographics = {}
            modified.demographics["technical_level"] = "advanced"
            changes.append("Increased technical level")

        elif "simplify" in instruction_lower:
            # Simplify summary if exists
            if modified.summary:
                # Simple truncation as placeholder
                if len(modified.summary) > 100:
                    modified.summary = modified.summary[:100] + "..."
                    changes.append("Simplified summary")

        elif "rename" in instruction_lower:
            if '"' in instruction:
                parts = instruction.split('"')
                if len(parts) >= 2:
                    new_name = parts[1]
                    old_name = modified.name
                    modified.name = new_name
                    changes.append(f"Renamed from {old_name} to {new_name}")

        elif target_fields:
            # Generic field update
            for field_name in target_fields:
                changes.append(f"Modified {field_name}")

        if not changes:
            changes.append("Applied refinement (no structural changes)")

        return modified, changes

    def list_templates(self) -> dict[str, dict[str, Any]]:
        """
        List available refinement templates.

        Returns:
            Dictionary of template names to details.
        """
        return self.TEMPLATES.copy()

    def close_session(self, persona_id: str) -> bool:
        """
        Close a refinement session.

        Args:
            persona_id: Persona ID.

        Returns:
            True if session was closed, False if not found.
        """
        if persona_id in self._sessions:
            del self._sessions[persona_id]
            return True
        return False
