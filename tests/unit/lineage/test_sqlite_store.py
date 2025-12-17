"""Tests for SQLite lineage store."""

import tempfile
from pathlib import Path

import pytest

from persona.core.lineage import (
    SQLiteLineageStore,
    hash_content,
)


@pytest.fixture
def store():
    """Create a temporary SQLite lineage store."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)

    store = SQLiteLineageStore(db_path)
    yield store
    store.close()
    db_path.unlink()


class TestEntityOperations:
    """Tests for entity CRUD operations."""

    def test_create_entity(self, store):
        """Test creating an entity."""
        entity_id = store.create_entity(
            entity_type="input_file",
            name="test.csv",
            hash="sha256:" + "a" * 64,
            path="/data/test.csv",
        )
        assert entity_id.startswith("ent-")

    def test_get_entity(self, store):
        """Test retrieving an entity."""
        entity_id = store.create_entity(
            entity_type="input_file",
            name="test.csv",
            hash="sha256:" + "a" * 64,
        )

        entity = store.get_entity(entity_id)
        assert entity is not None
        assert entity.name == "test.csv"
        assert entity.entity_type == "input_file"

    def test_get_entity_not_found(self, store):
        """Test retrieving non-existent entity."""
        assert store.get_entity("ent-nonexistent") is None

    def test_get_entity_by_hash(self, store):
        """Test finding entity by hash."""
        h = "sha256:" + "b" * 64
        store.create_entity(
            entity_type="persona",
            name="persona.json",
            hash=h,
        )

        entity = store.get_entity_by_hash(h)
        assert entity is not None
        assert entity.hash == h

    def test_list_entities(self, store):
        """Test listing entities."""
        store.create_entity("input_file", "file1.csv", "sha256:" + "a" * 64)
        store.create_entity("persona", "persona1.json", "sha256:" + "b" * 64)

        all_entities = store.list_entities()
        assert len(all_entities) == 2

        input_entities = store.list_entities(entity_type="input_file")
        assert len(input_entities) == 1

    def test_update_entity(self, store):
        """Test updating an entity."""
        entity_id = store.create_entity(
            entity_type="input_file",
            name="old_name.csv",
            hash="sha256:" + "a" * 64,
        )

        result = store.update_entity(entity_id, name="new_name.csv")
        assert result is True

        entity = store.get_entity(entity_id)
        assert entity.name == "new_name.csv"

    def test_delete_entity(self, store):
        """Test deleting an entity."""
        entity_id = store.create_entity(
            entity_type="input_file",
            name="test.csv",
            hash="sha256:" + "a" * 64,
        )

        result = store.delete_entity(entity_id)
        assert result is True
        assert store.get_entity(entity_id) is None


class TestAgentOperations:
    """Tests for agent CRUD operations."""

    def test_create_agent(self, store):
        """Test creating an agent."""
        agent_id = store.create_agent(
            agent_type="llm_model",
            name="claude-sonnet",
            version="4",
            provider="anthropic",
        )
        assert agent_id.startswith("agt-")

    def test_get_agent(self, store):
        """Test retrieving an agent."""
        agent_id = store.create_agent(
            agent_type="llm_model",
            name="gpt-4",
            provider="openai",
        )

        agent = store.get_agent(agent_id)
        assert agent is not None
        assert agent.name == "gpt-4"

    def test_get_or_create_agent_creates(self, store):
        """Test get_or_create creates new agent."""
        agent_id = store.get_or_create_agent(
            agent_type="llm_model",
            name="new-model",
            version="1.0",
        )
        assert agent_id.startswith("agt-")

    def test_get_or_create_agent_gets_existing(self, store):
        """Test get_or_create returns existing agent."""
        agent_id1 = store.get_or_create_agent(
            agent_type="llm_model",
            name="same-model",
            version="1.0",
        )
        agent_id2 = store.get_or_create_agent(
            agent_type="llm_model",
            name="same-model",
            version="1.0",
        )
        assert agent_id1 == agent_id2

    def test_list_agents(self, store):
        """Test listing agents."""
        store.create_agent("llm_model", "model1", provider="anthropic")
        store.create_agent("validator", "validator1")

        all_agents = store.list_agents()
        assert len(all_agents) == 2

        llm_agents = store.list_agents(agent_type="llm_model")
        assert len(llm_agents) == 1


class TestActivityOperations:
    """Tests for activity CRUD operations."""

    def test_create_activity(self, store):
        """Test creating an activity."""
        agent_id = store.create_agent("llm_model", "claude")

        activity_id = store.create_activity(
            activity_type="llm_generation",
            name="Generate personas",
            agent_id=agent_id,
        )
        assert activity_id.startswith("act-")

    def test_create_activity_with_entities(self, store):
        """Test creating activity with input/output entities."""
        agent_id = store.create_agent("llm_model", "claude")
        input_id = store.create_entity("input_file", "input.csv", "sha256:" + "a" * 64)

        activity_id = store.create_activity(
            activity_type="llm_generation",
            name="Generate personas",
            agent_id=agent_id,
            used_entities=[input_id],
        )

        activity = store.get_activity(activity_id)
        assert input_id in activity.used_entities

    def test_get_activity(self, store):
        """Test retrieving an activity."""
        agent_id = store.create_agent("llm_model", "claude")
        activity_id = store.create_activity(
            activity_type="data_load",
            name="Load data",
            agent_id=agent_id,
        )

        activity = store.get_activity(activity_id)
        assert activity is not None
        assert activity.name == "Load data"

    def test_complete_activity(self, store):
        """Test completing an activity."""
        agent_id = store.create_agent("llm_model", "claude")
        activity_id = store.create_activity(
            activity_type="llm_generation",
            name="Generate",
            agent_id=agent_id,
        )

        output_id = store.create_entity("persona", "output.json", "sha256:" + "b" * 64)
        result = store.complete_activity(
            activity_id,
            status="completed",
            generated_entities=[output_id],
        )

        assert result is True
        activity = store.get_activity(activity_id)
        assert activity.status == "completed"
        assert activity.ended_at is not None

    def test_list_activities(self, store):
        """Test listing activities."""
        agent_id = store.create_agent("llm_model", "claude")
        store.create_activity("llm_generation", "act1", agent_id)
        store.create_activity("data_load", "act2", agent_id)

        all_activities = store.list_activities()
        assert len(all_activities) == 2

        gen_activities = store.list_activities(activity_type="llm_generation")
        assert len(gen_activities) == 1


class TestRelations:
    """Tests for relation operations."""

    def test_add_relation(self, store):
        """Test adding a relation."""
        entity_id = store.create_entity("input_file", "test.csv", "sha256:" + "a" * 64)
        agent_id = store.create_agent("user", "researcher")

        store.add_relation("wasAttributedTo", entity_id, agent_id)

        relations = store.get_relations(source_id=entity_id)
        assert len(relations) == 1
        assert relations[0].relation_type == "wasAttributedTo"

    def test_get_relations_by_type(self, store):
        """Test filtering relations by type."""
        entity_id = store.create_entity("input_file", "test.csv", "sha256:" + "a" * 64)
        agent_id = store.create_agent("user", "researcher")

        store.add_relation("wasAttributedTo", entity_id, agent_id)
        store.add_relation("wasDerivedFrom", entity_id, entity_id)

        relations = store.get_relations(relation_type="wasAttributedTo")
        assert len(relations) == 1


class TestGraphTraversal:
    """Tests for graph traversal operations."""

    def test_get_ancestors(self, store):
        """Test getting ancestor graph."""
        # Create a simple lineage chain:
        # input_file -> activity -> output_persona
        agent_id = store.create_agent("llm_model", "claude")
        input_id = store.create_entity("input_file", "input.csv", "sha256:" + "a" * 64)

        activity_id = store.create_activity(
            activity_type="llm_generation",
            name="Generate",
            agent_id=agent_id,
            used_entities=[input_id],
        )

        output_id = store.create_entity(
            entity_type="persona",
            name="output.json",
            hash="sha256:" + "b" * 64,
            generated_by=activity_id,
        )
        store.complete_activity(activity_id, generated_entities=[output_id])

        # Get ancestors of output
        graph = store.get_ancestors(output_id)

        assert len(graph.entities) == 2  # input + output
        assert len(graph.activities) == 1
        assert len(graph.agents) == 1

    def test_get_descendants(self, store):
        """Test getting descendant graph."""
        agent_id = store.create_agent("llm_model", "claude")
        input_id = store.create_entity("input_file", "input.csv", "sha256:" + "a" * 64)

        activity_id = store.create_activity(
            activity_type="llm_generation",
            name="Generate",
            agent_id=agent_id,
            used_entities=[input_id],
        )

        output_id = store.create_entity(
            entity_type="persona",
            name="output.json",
            hash="sha256:" + "b" * 64,
            generated_by=activity_id,
        )
        store.complete_activity(activity_id, generated_entities=[output_id])

        # Get descendants of input
        graph = store.get_descendants(input_id)

        assert len(graph.entities) == 2  # input + output
        assert len(graph.activities) == 1

    def test_get_full_lineage(self, store):
        """Test getting complete lineage graph."""
        agent_id = store.create_agent("llm_model", "claude")
        input_id = store.create_entity("input_file", "input.csv", "sha256:" + "a" * 64)

        activity_id = store.create_activity(
            activity_type="llm_generation",
            name="Generate",
            agent_id=agent_id,
            used_entities=[input_id],
        )

        output_id = store.create_entity(
            entity_type="persona",
            name="output.json",
            hash="sha256:" + "b" * 64,
            generated_by=activity_id,
        )
        store.complete_activity(activity_id, generated_entities=[output_id])

        # Get full lineage from middle (activity is not an entity, test with output)
        graph = store.get_full_lineage(output_id)

        assert len(graph.entities) == 2
        assert len(graph.activities) == 1
        assert len(graph.agents) == 1


class TestVerification:
    """Tests for verification operations."""

    def test_verify_entity_no_path(self, store):
        """Test verifying entity without path."""
        entity_id = store.create_entity(
            entity_type="persona",
            name="persona.json",
            hash="sha256:" + "a" * 64,
        )

        result = store.verify_entity(entity_id)
        assert result["verified"] is True
        assert "note" in result

    def test_verify_entity_file_matches(self, store):
        """Test verifying entity with matching file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            temp_path = Path(f.name)

        try:
            h = hash_content("test content")
            entity_id = store.create_entity(
                entity_type="input_file",
                name="test.txt",
                hash=h,
                path=str(temp_path),
            )

            result = store.verify_entity(entity_id)
            assert result["verified"] is True
        finally:
            temp_path.unlink()

    def test_verify_entity_file_mismatch(self, store):
        """Test verifying entity with modified file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("original content")
            temp_path = Path(f.name)

        try:
            h = hash_content("original content")
            entity_id = store.create_entity(
                entity_type="input_file",
                name="test.txt",
                hash=h,
                path=str(temp_path),
            )

            # Modify the file
            temp_path.write_text("modified content")

            result = store.verify_entity(entity_id)
            assert result["verified"] is False
            assert "mismatch" in result["error"].lower()
        finally:
            temp_path.unlink()

    def test_verify_chain(self, store):
        """Test verifying entire lineage chain."""
        agent_id = store.create_agent("llm_model", "claude")
        input_id = store.create_entity("input_file", "input.csv", "sha256:" + "a" * 64)

        activity_id = store.create_activity(
            activity_type="llm_generation",
            name="Generate",
            agent_id=agent_id,
            used_entities=[input_id],
        )

        output_id = store.create_entity(
            entity_type="persona",
            name="output.json",
            hash="sha256:" + "b" * 64,
            generated_by=activity_id,
        )
        store.complete_activity(activity_id, generated_entities=[output_id])

        result = store.verify_chain(output_id)
        # Both entities have no paths, so they should verify
        assert result["entities_checked"] == 2
        assert result["verified"] is True


class TestExport:
    """Tests for PROV-JSON export."""

    def test_export_prov_json(self, store):
        """Test exporting lineage as PROV-JSON."""
        agent_id = store.create_agent("llm_model", "claude", provider="anthropic")
        entity_id = store.create_entity("input_file", "test.csv", "sha256:" + "a" * 64)
        store.create_activity(
            activity_type="data_load",
            name="Load data",
            agent_id=agent_id,
            used_entities=[entity_id],
        )

        prov = store.export_prov_json()

        assert "prefix" in prov
        assert "entity" in prov
        assert "activity" in prov
        assert "agent" in prov

    def test_export_prov_json_for_entity(self, store):
        """Test exporting lineage for specific entity."""
        agent_id = store.create_agent("llm_model", "claude")
        input_id = store.create_entity("input_file", "input.csv", "sha256:" + "a" * 64)

        activity_id = store.create_activity(
            activity_type="llm_generation",
            name="Generate",
            agent_id=agent_id,
            used_entities=[input_id],
        )

        output_id = store.create_entity(
            entity_type="persona",
            name="output.json",
            hash="sha256:" + "b" * 64,
            generated_by=activity_id,
        )
        store.complete_activity(activity_id, generated_entities=[output_id])

        prov = store.export_prov_json(output_id)
        assert "entity" in prov
        assert len(prov["entity"]) == 2  # input + output


class TestContextManager:
    """Tests for context manager support."""

    def test_context_manager(self):
        """Test using store as context manager."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = Path(f.name)

        try:
            with SQLiteLineageStore(db_path) as store:
                entity_id = store.create_entity(
                    entity_type="input_file",
                    name="test.csv",
                    hash="sha256:" + "a" * 64,
                )
                assert entity_id.startswith("ent-")
        finally:
            db_path.unlink()
