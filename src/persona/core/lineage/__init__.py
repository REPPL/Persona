"""
Data lineage and provenance module.

This module provides functionality for tracking data provenance
throughout the persona generation pipeline using the W3C PROV data model.

Key concepts:
- Entity: Data artefacts (files, personas, prompts)
- Activity: Transformations (generation, parsing, export)
- Agent: Tools, models, or users performing activities

Example:
    ```python
    from persona.core.lineage import SQLiteLineageStore, hash_file

    with SQLiteLineageStore() as store:
        # Track input file
        input_hash = hash_file("./data/interviews.csv")
        input_id = store.create_entity(
            entity_type="input_file",
            name="interviews.csv",
            hash=input_hash,
            path="./data/interviews.csv",
        )

        # Register the LLM agent
        agent_id = store.get_or_create_agent(
            agent_type="llm_model",
            name="claude-sonnet-4-20250514",
            provider="anthropic",
        )

        # Track generation activity
        activity_id = store.create_activity(
            activity_type="llm_generation",
            name="Generate personas from interviews",
            agent_id=agent_id,
            used_entities=[input_id],
        )

        # Track output
        output_id = store.create_entity(
            entity_type="persona_set",
            name="generated_personas.json",
            hash=hash_file("./output/personas.json"),
            path="./output/personas.json",
            generated_by=activity_id,
        )

        # Complete the activity
        store.complete_activity(
            activity_id,
            generated_entities=[output_id],
        )

        # Verify lineage chain
        result = store.verify_chain(output_id)
        print(f"Chain verified: {result['verified']}")

        # Export as PROV-JSON
        prov = store.export_prov_json(output_id)
    ```

Reference: https://www.w3.org/TR/prov-dm/
"""

# Hashing utilities
from persona.core.lineage.hashing import (
    extract_digest,
    hash_content,
    hash_dict,
    hash_file,
    hash_persona,
    is_valid_hash,
    verify_file_hash,
    verify_hash,
)

# Models
from persona.core.lineage.models import (
    ActivityType,
    AgentType,
    EntityType,
    LineageActivity,
    LineageAgent,
    LineageEntity,
    LineageGraph,
    LineageRelation,
)

# SQLite store
from persona.core.lineage.sqlite_store import (
    SQLiteLineageStore,
    get_default_lineage_db_path,
)

# Abstract store
from persona.core.lineage.store import LineageStore

__all__ = [
    # Hashing
    "hash_content",
    "hash_file",
    "hash_dict",
    "hash_persona",
    "verify_hash",
    "verify_file_hash",
    "extract_digest",
    "is_valid_hash",
    # Enums
    "EntityType",
    "ActivityType",
    "AgentType",
    # Models
    "LineageEntity",
    "LineageActivity",
    "LineageAgent",
    "LineageRelation",
    "LineageGraph",
    # Abstract store
    "LineageStore",
    # SQLite store
    "SQLiteLineageStore",
    "get_default_lineage_db_path",
]
