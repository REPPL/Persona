"""
Abstract storage interface for data lineage.

Provides a base class for lineage storage backends.
"""

from abc import ABC, abstractmethod
from typing import Any

from persona.core.lineage.models import (
    LineageActivity,
    LineageAgent,
    LineageEntity,
    LineageGraph,
    LineageRelation,
)


class LineageStore(ABC):
    """
    Abstract base class for lineage storage.

    Implementations should handle:
    - Entity, Activity, Agent CRUD operations
    - Relationship management
    - Graph traversal queries
    - Hash verification

    Example:
        ```python
        store = SQLiteLineageStore(db_path)
        entity_id = store.create_entity(
            entity_type="input_file",
            name="interviews.csv",
            hash="sha256:abc123...",
            path="/data/interviews.csv"
        )
        ```
    """

    # =========================================================================
    # Entity Operations
    # =========================================================================

    @abstractmethod
    def create_entity(
        self,
        entity_type: str,
        name: str,
        hash: str,
        *,
        path: str | None = None,
        size_bytes: int | None = None,
        metadata: dict[str, Any] | None = None,
        generated_by: str | None = None,
    ) -> str:
        """
        Create a new entity.

        Args:
            entity_type: Type of entity (input_file, persona, etc.).
            name: Human-readable name.
            hash: Content hash (sha256:...).
            path: File path if applicable.
            size_bytes: Size in bytes if applicable.
            metadata: Additional metadata.
            generated_by: Activity ID that generated this entity.

        Returns:
            Unique entity ID.
        """
        ...

    @abstractmethod
    def get_entity(self, entity_id: str) -> LineageEntity | None:
        """
        Get entity by ID.

        Args:
            entity_id: Unique entity identifier.

        Returns:
            LineageEntity or None if not found.
        """
        ...

    @abstractmethod
    def get_entity_by_hash(self, hash: str) -> LineageEntity | None:
        """
        Get entity by content hash.

        Args:
            hash: Content hash to look up.

        Returns:
            LineageEntity or None if not found.
        """
        ...

    @abstractmethod
    def list_entities(
        self,
        *,
        entity_type: str | None = None,
        generated_by: str | None = None,
        limit: int | None = None,
    ) -> list[LineageEntity]:
        """
        List entities with optional filters.

        Args:
            entity_type: Filter by type.
            generated_by: Filter by generating activity.
            limit: Maximum number to return.

        Returns:
            List of LineageEntity objects.
        """
        ...

    @abstractmethod
    def update_entity(self, entity_id: str, **updates: Any) -> bool:
        """
        Update entity fields.

        Args:
            entity_id: Entity to update.
            **updates: Fields to update.

        Returns:
            True if updated, False if not found.
        """
        ...

    @abstractmethod
    def delete_entity(self, entity_id: str) -> bool:
        """
        Delete an entity.

        Args:
            entity_id: Entity to delete.

        Returns:
            True if deleted, False if not found.
        """
        ...

    # =========================================================================
    # Activity Operations
    # =========================================================================

    @abstractmethod
    def create_activity(
        self,
        activity_type: str,
        name: str,
        agent_id: str,
        *,
        run_id: str | None = None,
        used_entities: list[str] | None = None,
        generated_entities: list[str] | None = None,
        parameters: dict[str, Any] | None = None,
    ) -> str:
        """
        Create a new activity.

        Args:
            activity_type: Type of activity.
            name: Human-readable name.
            agent_id: Agent performing this activity.
            run_id: Optional link to experiment run.
            used_entities: Entity IDs used as inputs.
            generated_entities: Entity IDs generated as outputs.
            parameters: Activity parameters.

        Returns:
            Unique activity ID.
        """
        ...

    @abstractmethod
    def get_activity(self, activity_id: str) -> LineageActivity | None:
        """
        Get activity by ID.

        Args:
            activity_id: Unique activity identifier.

        Returns:
            LineageActivity or None if not found.
        """
        ...

    @abstractmethod
    def list_activities(
        self,
        *,
        activity_type: str | None = None,
        agent_id: str | None = None,
        run_id: str | None = None,
        limit: int | None = None,
    ) -> list[LineageActivity]:
        """
        List activities with optional filters.

        Args:
            activity_type: Filter by type.
            agent_id: Filter by agent.
            run_id: Filter by experiment run.
            limit: Maximum number to return.

        Returns:
            List of LineageActivity objects.
        """
        ...

    @abstractmethod
    def complete_activity(
        self,
        activity_id: str,
        *,
        status: str = "completed",
        generated_entities: list[str] | None = None,
    ) -> bool:
        """
        Mark activity as complete.

        Args:
            activity_id: Activity to complete.
            status: Final status (completed, failed).
            generated_entities: Entity IDs generated.

        Returns:
            True if updated, False if not found.
        """
        ...

    @abstractmethod
    def delete_activity(self, activity_id: str) -> bool:
        """
        Delete an activity.

        Args:
            activity_id: Activity to delete.

        Returns:
            True if deleted, False if not found.
        """
        ...

    # =========================================================================
    # Agent Operations
    # =========================================================================

    @abstractmethod
    def create_agent(
        self,
        agent_type: str,
        name: str,
        *,
        version: str | None = None,
        provider: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Create a new agent.

        Args:
            agent_type: Type of agent.
            name: Agent name (model ID, tool name, etc.).
            version: Version string.
            provider: Provider or vendor.
            metadata: Additional metadata.

        Returns:
            Unique agent ID.
        """
        ...

    @abstractmethod
    def get_agent(self, agent_id: str) -> LineageAgent | None:
        """
        Get agent by ID.

        Args:
            agent_id: Unique agent identifier.

        Returns:
            LineageAgent or None if not found.
        """
        ...

    @abstractmethod
    def get_or_create_agent(
        self,
        agent_type: str,
        name: str,
        *,
        version: str | None = None,
        provider: str | None = None,
    ) -> str:
        """
        Get existing agent or create new one.

        Looks up by type + name + version, creates if not found.

        Args:
            agent_type: Type of agent.
            name: Agent name.
            version: Version string.
            provider: Provider or vendor.

        Returns:
            Agent ID (existing or newly created).
        """
        ...

    @abstractmethod
    def list_agents(
        self,
        *,
        agent_type: str | None = None,
        provider: str | None = None,
    ) -> list[LineageAgent]:
        """
        List agents with optional filters.

        Args:
            agent_type: Filter by type.
            provider: Filter by provider.

        Returns:
            List of LineageAgent objects.
        """
        ...

    @abstractmethod
    def delete_agent(self, agent_id: str) -> bool:
        """
        Delete an agent.

        Args:
            agent_id: Agent to delete.

        Returns:
            True if deleted, False if not found.
        """
        ...

    # =========================================================================
    # Relation Operations
    # =========================================================================

    @abstractmethod
    def add_relation(
        self,
        relation_type: str,
        source_id: str,
        target_id: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Add a relationship between nodes.

        Relation types follow W3C PROV:
        - wasGeneratedBy: Entity -> Activity
        - used: Activity -> Entity
        - wasAttributedTo: Entity -> Agent
        - wasAssociatedWith: Activity -> Agent
        - wasDerivedFrom: Entity -> Entity

        Args:
            relation_type: Type of relationship.
            source_id: Source node ID.
            target_id: Target node ID.
            metadata: Optional relation metadata.
        """
        ...

    @abstractmethod
    def get_relations(
        self,
        *,
        relation_type: str | None = None,
        source_id: str | None = None,
        target_id: str | None = None,
    ) -> list[LineageRelation]:
        """
        Get relationships with optional filters.

        Args:
            relation_type: Filter by type.
            source_id: Filter by source.
            target_id: Filter by target.

        Returns:
            List of LineageRelation objects.
        """
        ...

    # =========================================================================
    # Graph Traversal
    # =========================================================================

    @abstractmethod
    def get_ancestors(
        self,
        entity_id: str,
        *,
        max_depth: int | None = None,
    ) -> LineageGraph:
        """
        Get all ancestors (inputs) of an entity.

        Traverses the lineage graph upward to find all entities
        and activities that contributed to this entity.

        Args:
            entity_id: Starting entity.
            max_depth: Maximum traversal depth (None for unlimited).

        Returns:
            LineageGraph containing ancestor nodes and relationships.
        """
        ...

    @abstractmethod
    def get_descendants(
        self,
        entity_id: str,
        *,
        max_depth: int | None = None,
    ) -> LineageGraph:
        """
        Get all descendants (outputs) of an entity.

        Traverses the lineage graph downward to find all entities
        derived from this entity.

        Args:
            entity_id: Starting entity.
            max_depth: Maximum traversal depth (None for unlimited).

        Returns:
            LineageGraph containing descendant nodes and relationships.
        """
        ...

    @abstractmethod
    def get_full_lineage(self, entity_id: str) -> LineageGraph:
        """
        Get complete lineage graph for an entity.

        Combines ancestors and descendants into a full graph.

        Args:
            entity_id: Central entity.

        Returns:
            Complete LineageGraph.
        """
        ...

    # =========================================================================
    # Verification
    # =========================================================================

    @abstractmethod
    def verify_entity(self, entity_id: str) -> dict[str, Any]:
        """
        Verify entity integrity.

        Checks that the entity's stored hash matches current content.

        Args:
            entity_id: Entity to verify.

        Returns:
            Dictionary with verification result:
            - verified: bool
            - entity_id: str
            - stored_hash: str
            - current_hash: str (if file exists)
            - error: str (if verification failed)
        """
        ...

    @abstractmethod
    def verify_chain(self, entity_id: str) -> dict[str, Any]:
        """
        Verify integrity of entire lineage chain.

        Verifies all entities in the ancestor chain.

        Args:
            entity_id: Terminal entity to verify chain for.

        Returns:
            Dictionary with verification results:
            - verified: bool (all entities valid)
            - entities_checked: int
            - entities_valid: int
            - entities_invalid: list of entity IDs
            - details: list of individual results
        """
        ...

    # =========================================================================
    # Export
    # =========================================================================

    @abstractmethod
    def export_prov_json(
        self,
        entity_id: str | None = None,
    ) -> dict[str, Any]:
        """
        Export lineage as PROV-JSON.

        Args:
            entity_id: Export lineage for specific entity (None for all).

        Returns:
            Dictionary conforming to PROV-JSON schema.
        """
        ...

    # =========================================================================
    # Lifecycle
    # =========================================================================

    @abstractmethod
    def close(self) -> None:
        """Close the store and release resources."""
        ...

    def __enter__(self) -> "LineageStore":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
