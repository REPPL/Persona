"""
SQLite implementation of lineage storage.

Provides persistent storage for data lineage with graph traversal
and PROV-JSON export capabilities.
"""

import json
import sqlite3
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from persona.core.lineage.hashing import hash_file
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
from persona.core.lineage.store import LineageStore


def get_default_lineage_db_path() -> Path:
    """Get default lineage database path."""
    return Path.home() / ".persona" / "lineage.db"


class SQLiteLineageStore(LineageStore):
    """
    SQLite implementation of LineageStore.

    Provides persistent storage for lineage data with support for
    graph traversal and PROV-JSON export.

    Example:
        ```python
        with SQLiteLineageStore("./lineage.db") as store:
            entity_id = store.create_entity(
                entity_type="input_file",
                name="data.csv",
                hash="sha256:abc123...",
            )
            activity_id = store.create_activity(
                activity_type="llm_generation",
                name="Generate personas",
                agent_id=agent_id,
                used_entities=[entity_id],
            )
        ```
    """

    def __init__(self, db_path: Path | str | None = None) -> None:
        """
        Initialise SQLite lineage store.

        Args:
            db_path: Path to SQLite database. Defaults to ~/.persona/lineage.db.
        """
        if db_path is None:
            db_path = get_default_lineage_db_path()

        self._db_path = Path(db_path)
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn: sqlite3.Connection | None = None
        self._init_schema()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get database connection with proper setup."""
        if self._conn is None:
            self._conn = sqlite3.connect(
                str(self._db_path),
                detect_types=sqlite3.PARSE_DECLTYPES,
            )
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON")

        yield self._conn

    def _init_schema(self) -> None:
        """Initialise database schema."""
        with self._get_connection() as conn:
            conn.executescript(
                """
                -- Entities (data artefacts)
                CREATE TABLE IF NOT EXISTS lineage_entities (
                    entity_id TEXT PRIMARY KEY,
                    entity_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    hash TEXT NOT NULL,
                    path TEXT,
                    size_bytes INTEGER,
                    metadata_json TEXT DEFAULT '{}',
                    generated_by TEXT,
                    generated_at TEXT NOT NULL,
                    FOREIGN KEY (generated_by)
                        REFERENCES lineage_activities(activity_id)
                        ON DELETE SET NULL
                );

                CREATE INDEX IF NOT EXISTS idx_entities_type
                    ON lineage_entities(entity_type);
                CREATE INDEX IF NOT EXISTS idx_entities_hash
                    ON lineage_entities(hash);
                CREATE INDEX IF NOT EXISTS idx_entities_generated_by
                    ON lineage_entities(generated_by);

                -- Activities (transformations)
                CREATE TABLE IF NOT EXISTS lineage_activities (
                    activity_id TEXT PRIMARY KEY,
                    activity_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    run_id TEXT,
                    parameters_json TEXT DEFAULT '{}',
                    started_at TEXT NOT NULL,
                    ended_at TEXT,
                    status TEXT DEFAULT 'running',
                    FOREIGN KEY (agent_id) REFERENCES lineage_agents(agent_id)
                        ON DELETE RESTRICT
                );

                CREATE INDEX IF NOT EXISTS idx_activities_type
                    ON lineage_activities(activity_type);
                CREATE INDEX IF NOT EXISTS idx_activities_agent
                    ON lineage_activities(agent_id);
                CREATE INDEX IF NOT EXISTS idx_activities_run
                    ON lineage_activities(run_id);

                -- Agents (tools, models, users)
                CREATE TABLE IF NOT EXISTS lineage_agents (
                    agent_id TEXT PRIMARY KEY,
                    agent_type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    version TEXT,
                    provider TEXT,
                    metadata_json TEXT DEFAULT '{}'
                );

                CREATE INDEX IF NOT EXISTS idx_agents_type
                    ON lineage_agents(agent_type);
                CREATE UNIQUE INDEX IF NOT EXISTS idx_agents_unique
                    ON lineage_agents(agent_type, name, version);

                -- Relations (edges in the graph)
                CREATE TABLE IF NOT EXISTS lineage_relations (
                    relation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    relation_type TEXT NOT NULL,
                    source_id TEXT NOT NULL,
                    target_id TEXT NOT NULL,
                    metadata_json TEXT DEFAULT '{}'
                );

                CREATE INDEX IF NOT EXISTS idx_relations_type
                    ON lineage_relations(relation_type);
                CREATE INDEX IF NOT EXISTS idx_relations_source
                    ON lineage_relations(source_id);
                CREATE INDEX IF NOT EXISTS idx_relations_target
                    ON lineage_relations(target_id);
                CREATE UNIQUE INDEX IF NOT EXISTS idx_relations_unique
                    ON lineage_relations(relation_type, source_id, target_id);

                -- Activity-Entity usage junction table
                CREATE TABLE IF NOT EXISTS activity_used_entities (
                    activity_id TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    PRIMARY KEY (activity_id, entity_id),
                    FOREIGN KEY (activity_id) REFERENCES lineage_activities(activity_id)
                        ON DELETE CASCADE,
                    FOREIGN KEY (entity_id) REFERENCES lineage_entities(entity_id)
                        ON DELETE CASCADE
                );

                -- Activity-Entity generation junction table
                CREATE TABLE IF NOT EXISTS activity_generated_entities (
                    activity_id TEXT NOT NULL,
                    entity_id TEXT NOT NULL,
                    PRIMARY KEY (activity_id, entity_id),
                    FOREIGN KEY (activity_id) REFERENCES lineage_activities(activity_id)
                        ON DELETE CASCADE,
                    FOREIGN KEY (entity_id) REFERENCES lineage_entities(entity_id)
                        ON DELETE CASCADE
                );
                """
            )
            conn.commit()

    def _generate_id(self, prefix: str) -> str:
        """Generate unique ID with prefix."""
        return f"{prefix}-{uuid.uuid4().hex[:12]}"

    # =========================================================================
    # Entity Operations
    # =========================================================================

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
        """Create a new entity."""
        entity_id = self._generate_id("ent")
        now = datetime.now(UTC).isoformat()

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO lineage_entities
                (entity_id, entity_type, name, hash, path, size_bytes,
                 metadata_json, generated_by, generated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    entity_id,
                    entity_type,
                    name,
                    hash,
                    path,
                    size_bytes,
                    json.dumps(metadata or {}),
                    generated_by,
                    now,
                ),
            )
            conn.commit()

        return entity_id

    def get_entity(self, entity_id: str) -> LineageEntity | None:
        """Get entity by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM lineage_entities WHERE entity_id = ?",
                (entity_id,),
            ).fetchone()

            if row is None:
                return None

            return self._row_to_entity(row)

    def get_entity_by_hash(self, hash: str) -> LineageEntity | None:
        """Get entity by content hash."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM lineage_entities WHERE hash = ?",
                (hash,),
            ).fetchone()

            if row is None:
                return None

            return self._row_to_entity(row)

    def list_entities(
        self,
        *,
        entity_type: str | None = None,
        generated_by: str | None = None,
        limit: int | None = None,
    ) -> list[LineageEntity]:
        """List entities with optional filters."""
        query = "SELECT * FROM lineage_entities WHERE 1=1"
        params: list[Any] = []

        if entity_type:
            query += " AND entity_type = ?"
            params.append(entity_type)

        if generated_by:
            query += " AND generated_by = ?"
            params.append(generated_by)

        query += " ORDER BY generated_at DESC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [self._row_to_entity(row) for row in rows]

    def update_entity(self, entity_id: str, **updates: Any) -> bool:
        """Update entity fields."""
        if not updates:
            return False

        # Handle metadata specially
        if "metadata" in updates:
            updates["metadata_json"] = json.dumps(updates.pop("metadata"))

        set_clause = ", ".join(f"{k} = ?" for k in updates.keys())
        values = list(updates.values())
        values.append(entity_id)

        with self._get_connection() as conn:
            # Column names are from internal **updates, not user input
            query = f"UPDATE lineage_entities SET {set_clause} WHERE entity_id = ?"  # nosec B608
            cursor = conn.execute(query, values)
            conn.commit()
            return cursor.rowcount > 0

    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM lineage_entities WHERE entity_id = ?",
                (entity_id,),
            )
            conn.commit()
            return cursor.rowcount > 0

    def _row_to_entity(self, row: sqlite3.Row) -> LineageEntity:
        """Convert database row to LineageEntity."""
        return LineageEntity(
            entity_id=row["entity_id"],
            entity_type=EntityType(row["entity_type"]),
            name=row["name"],
            hash=row["hash"],
            path=row["path"],
            size_bytes=row["size_bytes"],
            metadata=json.loads(row["metadata_json"]),
            generated_by=row["generated_by"],
            generated_at=datetime.fromisoformat(row["generated_at"]),
        )

    # =========================================================================
    # Activity Operations
    # =========================================================================

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
        """Create a new activity."""
        activity_id = self._generate_id("act")
        now = datetime.now(UTC).isoformat()

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO lineage_activities
                (activity_id, activity_type, name, agent_id, run_id,
                 parameters_json, started_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'running')
                """,
                (
                    activity_id,
                    activity_type,
                    name,
                    agent_id,
                    run_id,
                    json.dumps(parameters or {}),
                    now,
                ),
            )

            # Link used entities
            if used_entities:
                for entity_id in used_entities:
                    conn.execute(
                        """
                        INSERT INTO activity_used_entities (activity_id, entity_id)
                        VALUES (?, ?)
                        """,
                        (activity_id, entity_id),
                    )
                    # Add PROV relation
                    self._add_relation_internal(
                        conn, "used", activity_id, entity_id, {}
                    )

            # Link generated entities
            if generated_entities:
                for entity_id in generated_entities:
                    conn.execute(
                        """
                        INSERT INTO activity_generated_entities (activity_id, entity_id)
                        VALUES (?, ?)
                        """,
                        (activity_id, entity_id),
                    )
                    # Add PROV relation
                    self._add_relation_internal(
                        conn, "wasGeneratedBy", entity_id, activity_id, {}
                    )

            # Add agent association
            self._add_relation_internal(
                conn, "wasAssociatedWith", activity_id, agent_id, {}
            )

            conn.commit()

        return activity_id

    def get_activity(self, activity_id: str) -> LineageActivity | None:
        """Get activity by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM lineage_activities WHERE activity_id = ?",
                (activity_id,),
            ).fetchone()

            if row is None:
                return None

            return self._row_to_activity(conn, row)

    def list_activities(
        self,
        *,
        activity_type: str | None = None,
        agent_id: str | None = None,
        run_id: str | None = None,
        limit: int | None = None,
    ) -> list[LineageActivity]:
        """List activities with optional filters."""
        query = "SELECT * FROM lineage_activities WHERE 1=1"
        params: list[Any] = []

        if activity_type:
            query += " AND activity_type = ?"
            params.append(activity_type)

        if agent_id:
            query += " AND agent_id = ?"
            params.append(agent_id)

        if run_id:
            query += " AND run_id = ?"
            params.append(run_id)

        query += " ORDER BY started_at DESC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [self._row_to_activity(conn, row) for row in rows]

    def complete_activity(
        self,
        activity_id: str,
        *,
        status: str = "completed",
        generated_entities: list[str] | None = None,
    ) -> bool:
        """Mark activity as complete."""
        now = datetime.now(UTC).isoformat()

        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE lineage_activities
                SET status = ?, ended_at = ?
                WHERE activity_id = ?
                """,
                (status, now, activity_id),
            )

            if cursor.rowcount == 0:
                return False

            # Link generated entities
            if generated_entities:
                for entity_id in generated_entities:
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO activity_generated_entities
                        (activity_id, entity_id)
                        VALUES (?, ?)
                        """,
                        (activity_id, entity_id),
                    )
                    # Update entity's generated_by if not set
                    conn.execute(
                        """
                        UPDATE lineage_entities
                        SET generated_by = ?
                        WHERE entity_id = ? AND generated_by IS NULL
                        """,
                        (activity_id, entity_id),
                    )
                    # Add PROV relation
                    self._add_relation_internal(
                        conn, "wasGeneratedBy", entity_id, activity_id, {}
                    )

            conn.commit()
            return True

    def delete_activity(self, activity_id: str) -> bool:
        """Delete an activity."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM lineage_activities WHERE activity_id = ?",
                (activity_id,),
            )
            conn.commit()
            return cursor.rowcount > 0

    def _row_to_activity(
        self, conn: sqlite3.Connection, row: sqlite3.Row
    ) -> LineageActivity:
        """Convert database row to LineageActivity."""
        # Get used entities
        used_rows = conn.execute(
            "SELECT entity_id FROM activity_used_entities WHERE activity_id = ?",
            (row["activity_id"],),
        ).fetchall()
        used_entities = [r["entity_id"] for r in used_rows]

        # Get generated entities
        gen_rows = conn.execute(
            "SELECT entity_id FROM activity_generated_entities WHERE activity_id = ?",
            (row["activity_id"],),
        ).fetchall()
        generated_entities = [r["entity_id"] for r in gen_rows]

        ended_at = None
        if row["ended_at"]:
            ended_at = datetime.fromisoformat(row["ended_at"])

        return LineageActivity(
            activity_id=row["activity_id"],
            activity_type=ActivityType(row["activity_type"]),
            name=row["name"],
            agent_id=row["agent_id"],
            run_id=row["run_id"],
            used_entities=used_entities,
            generated_entities=generated_entities,
            parameters=json.loads(row["parameters_json"]),
            started_at=datetime.fromisoformat(row["started_at"]),
            ended_at=ended_at,
            status=row["status"],
        )

    # =========================================================================
    # Agent Operations
    # =========================================================================

    def create_agent(
        self,
        agent_type: str,
        name: str,
        *,
        version: str | None = None,
        provider: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """Create a new agent."""
        agent_id = self._generate_id("agt")

        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO lineage_agents
                (agent_id, agent_type, name, version, provider, metadata_json)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    agent_id,
                    agent_type,
                    name,
                    version,
                    provider,
                    json.dumps(metadata or {}),
                ),
            )
            conn.commit()

        return agent_id

    def get_agent(self, agent_id: str) -> LineageAgent | None:
        """Get agent by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM lineage_agents WHERE agent_id = ?",
                (agent_id,),
            ).fetchone()

            if row is None:
                return None

            return self._row_to_agent(row)

    def get_or_create_agent(
        self,
        agent_type: str,
        name: str,
        *,
        version: str | None = None,
        provider: str | None = None,
    ) -> str:
        """Get existing agent or create new one."""
        with self._get_connection() as conn:
            # Try to find existing
            if version:
                row = conn.execute(
                    """
                    SELECT agent_id FROM lineage_agents
                    WHERE agent_type = ? AND name = ? AND version = ?
                    """,
                    (agent_type, name, version),
                ).fetchone()
            else:
                row = conn.execute(
                    """
                    SELECT agent_id FROM lineage_agents
                    WHERE agent_type = ? AND name = ? AND version IS NULL
                    """,
                    (agent_type, name),
                ).fetchone()

            if row:
                return str(row["agent_id"])

        # Create new
        return self.create_agent(
            agent_type, name, version=version, provider=provider
        )

    def list_agents(
        self,
        *,
        agent_type: str | None = None,
        provider: str | None = None,
    ) -> list[LineageAgent]:
        """List agents with optional filters."""
        query = "SELECT * FROM lineage_agents WHERE 1=1"
        params: list[Any] = []

        if agent_type:
            query += " AND agent_type = ?"
            params.append(agent_type)

        if provider:
            query += " AND provider = ?"
            params.append(provider)

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [self._row_to_agent(row) for row in rows]

    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM lineage_agents WHERE agent_id = ?",
                (agent_id,),
            )
            conn.commit()
            return cursor.rowcount > 0

    def _row_to_agent(self, row: sqlite3.Row) -> LineageAgent:
        """Convert database row to LineageAgent."""
        return LineageAgent(
            agent_id=row["agent_id"],
            agent_type=AgentType(row["agent_type"]),
            name=row["name"],
            version=row["version"],
            provider=row["provider"],
            metadata=json.loads(row["metadata_json"]),
        )

    # =========================================================================
    # Relation Operations
    # =========================================================================

    def add_relation(
        self,
        relation_type: str,
        source_id: str,
        target_id: str,
        *,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add a relationship between nodes."""
        with self._get_connection() as conn:
            self._add_relation_internal(
                conn, relation_type, source_id, target_id, metadata or {}
            )
            conn.commit()

    def _add_relation_internal(
        self,
        conn: sqlite3.Connection,
        relation_type: str,
        source_id: str,
        target_id: str,
        metadata: dict[str, Any],
    ) -> None:
        """Add relation without committing."""
        conn.execute(
            """
            INSERT OR IGNORE INTO lineage_relations
            (relation_type, source_id, target_id, metadata_json)
            VALUES (?, ?, ?, ?)
            """,
            (relation_type, source_id, target_id, json.dumps(metadata)),
        )

    def get_relations(
        self,
        *,
        relation_type: str | None = None,
        source_id: str | None = None,
        target_id: str | None = None,
    ) -> list[LineageRelation]:
        """Get relationships with optional filters."""
        query = "SELECT * FROM lineage_relations WHERE 1=1"
        params: list[Any] = []

        if relation_type:
            query += " AND relation_type = ?"
            params.append(relation_type)

        if source_id:
            query += " AND source_id = ?"
            params.append(source_id)

        if target_id:
            query += " AND target_id = ?"
            params.append(target_id)

        with self._get_connection() as conn:
            rows = conn.execute(query, params).fetchall()
            return [
                LineageRelation(
                    relation_type=row["relation_type"],
                    source_id=row["source_id"],
                    target_id=row["target_id"],
                    metadata=json.loads(row["metadata_json"]),
                )
                for row in rows
            ]

    # =========================================================================
    # Graph Traversal
    # =========================================================================

    def get_ancestors(
        self,
        entity_id: str,
        *,
        max_depth: int | None = None,
    ) -> LineageGraph:
        """Get all ancestors (inputs) of an entity."""
        entities: dict[str, LineageEntity] = {}
        activities: dict[str, LineageActivity] = {}
        agents: dict[str, LineageAgent] = {}
        relations: list[LineageRelation] = []

        with self._get_connection() as conn:
            self._traverse_ancestors(
                conn,
                entity_id,
                entities,
                activities,
                agents,
                relations,
                depth=0,
                max_depth=max_depth,
            )

        return LineageGraph(
            entities=list(entities.values()),
            activities=list(activities.values()),
            agents=list(agents.values()),
            relations=relations,
        )

    def _traverse_ancestors(
        self,
        conn: sqlite3.Connection,
        entity_id: str,
        entities: dict[str, LineageEntity],
        activities: dict[str, LineageActivity],
        agents: dict[str, LineageAgent],
        relations: list[LineageRelation],
        depth: int,
        max_depth: int | None,
    ) -> None:
        """Recursively traverse ancestor graph."""
        if max_depth is not None and depth > max_depth:
            return

        if entity_id in entities:
            return

        # Get entity
        row = conn.execute(
            "SELECT * FROM lineage_entities WHERE entity_id = ?",
            (entity_id,),
        ).fetchone()

        if row is None:
            return

        entity = self._row_to_entity(row)
        entities[entity_id] = entity

        # Get generating activity
        if entity.generated_by:
            act_row = conn.execute(
                "SELECT * FROM lineage_activities WHERE activity_id = ?",
                (entity.generated_by,),
            ).fetchone()

            if act_row and act_row["activity_id"] not in activities:
                activity = self._row_to_activity(conn, act_row)
                activities[activity.activity_id] = activity

                # Add wasGeneratedBy relation
                relations.append(
                    LineageRelation(
                        relation_type="wasGeneratedBy",
                        source_id=entity_id,
                        target_id=activity.activity_id,
                        metadata={},
                    )
                )

                # Get agent
                if activity.agent_id not in agents:
                    agent = self.get_agent(activity.agent_id)
                    if agent:
                        agents[agent.agent_id] = agent
                        relations.append(
                            LineageRelation(
                                relation_type="wasAssociatedWith",
                                source_id=activity.activity_id,
                                target_id=agent.agent_id,
                                metadata={},
                            )
                        )

                # Traverse used entities
                for used_id in activity.used_entities:
                    relations.append(
                        LineageRelation(
                            relation_type="used",
                            source_id=activity.activity_id,
                            target_id=used_id,
                            metadata={},
                        )
                    )
                    self._traverse_ancestors(
                        conn,
                        used_id,
                        entities,
                        activities,
                        agents,
                        relations,
                        depth + 1,
                        max_depth,
                    )

    def get_descendants(
        self,
        entity_id: str,
        *,
        max_depth: int | None = None,
    ) -> LineageGraph:
        """Get all descendants (outputs) of an entity."""
        entities: dict[str, LineageEntity] = {}
        activities: dict[str, LineageActivity] = {}
        agents: dict[str, LineageAgent] = {}
        relations: list[LineageRelation] = []

        with self._get_connection() as conn:
            self._traverse_descendants(
                conn,
                entity_id,
                entities,
                activities,
                agents,
                relations,
                depth=0,
                max_depth=max_depth,
            )

        return LineageGraph(
            entities=list(entities.values()),
            activities=list(activities.values()),
            agents=list(agents.values()),
            relations=relations,
        )

    def _traverse_descendants(
        self,
        conn: sqlite3.Connection,
        entity_id: str,
        entities: dict[str, LineageEntity],
        activities: dict[str, LineageActivity],
        agents: dict[str, LineageAgent],
        relations: list[LineageRelation],
        depth: int,
        max_depth: int | None,
    ) -> None:
        """Recursively traverse descendant graph."""
        if max_depth is not None and depth > max_depth:
            return

        if entity_id in entities:
            return

        # Get entity
        row = conn.execute(
            "SELECT * FROM lineage_entities WHERE entity_id = ?",
            (entity_id,),
        ).fetchone()

        if row is None:
            return

        entity = self._row_to_entity(row)
        entities[entity_id] = entity

        # Find activities that used this entity
        act_rows = conn.execute(
            """
            SELECT a.* FROM lineage_activities a
            JOIN activity_used_entities u ON a.activity_id = u.activity_id
            WHERE u.entity_id = ?
            """,
            (entity_id,),
        ).fetchall()

        for act_row in act_rows:
            if act_row["activity_id"] in activities:
                continue

            activity = self._row_to_activity(conn, act_row)
            activities[activity.activity_id] = activity

            # Add used relation
            relations.append(
                LineageRelation(
                    relation_type="used",
                    source_id=activity.activity_id,
                    target_id=entity_id,
                    metadata={},
                )
            )

            # Get agent
            if activity.agent_id not in agents:
                agent = self.get_agent(activity.agent_id)
                if agent:
                    agents[agent.agent_id] = agent
                    relations.append(
                        LineageRelation(
                            relation_type="wasAssociatedWith",
                            source_id=activity.activity_id,
                            target_id=agent.agent_id,
                            metadata={},
                        )
                    )

            # Traverse generated entities
            for gen_id in activity.generated_entities:
                relations.append(
                    LineageRelation(
                        relation_type="wasGeneratedBy",
                        source_id=gen_id,
                        target_id=activity.activity_id,
                        metadata={},
                    )
                )
                self._traverse_descendants(
                    conn,
                    gen_id,
                    entities,
                    activities,
                    agents,
                    relations,
                    depth + 1,
                    max_depth,
                )

    def get_full_lineage(self, entity_id: str) -> LineageGraph:
        """Get complete lineage graph for an entity."""
        ancestors = self.get_ancestors(entity_id)
        descendants = self.get_descendants(entity_id)

        # Merge graphs
        entities = {e.entity_id: e for e in ancestors.entities}
        entities.update({e.entity_id: e for e in descendants.entities})

        activities = {a.activity_id: a for a in ancestors.activities}
        activities.update({a.activity_id: a for a in descendants.activities})

        agents = {a.agent_id: a for a in ancestors.agents}
        agents.update({a.agent_id: a for a in descendants.agents})

        # Deduplicate relations
        relations_set: set[tuple[str, str, str]] = set()
        relations: list[LineageRelation] = []
        for rel in ancestors.relations + descendants.relations:
            key = (rel.relation_type, rel.source_id, rel.target_id)
            if key not in relations_set:
                relations_set.add(key)
                relations.append(rel)

        return LineageGraph(
            entities=list(entities.values()),
            activities=list(activities.values()),
            agents=list(agents.values()),
            relations=relations,
        )

    # =========================================================================
    # Verification
    # =========================================================================

    def verify_entity(self, entity_id: str) -> dict[str, Any]:
        """Verify entity integrity."""
        entity = self.get_entity(entity_id)

        if entity is None:
            return {
                "verified": False,
                "entity_id": entity_id,
                "error": "Entity not found",
            }

        if not entity.path:
            return {
                "verified": True,
                "entity_id": entity_id,
                "stored_hash": entity.hash,
                "note": "No file path - hash not verifiable",
            }

        path = Path(entity.path)
        if not path.exists():
            return {
                "verified": False,
                "entity_id": entity_id,
                "stored_hash": entity.hash,
                "error": f"File not found: {entity.path}",
            }

        try:
            current_hash = hash_file(path)
            verified = current_hash == entity.hash

            result: dict[str, Any] = {
                "verified": verified,
                "entity_id": entity_id,
                "stored_hash": entity.hash,
                "current_hash": current_hash,
            }

            if not verified:
                result["error"] = "Hash mismatch - file has been modified"

            return result

        except (OSError, PermissionError) as e:
            return {
                "verified": False,
                "entity_id": entity_id,
                "stored_hash": entity.hash,
                "error": f"Cannot read file: {e}",
            }

    def verify_chain(self, entity_id: str) -> dict[str, Any]:
        """Verify integrity of entire lineage chain."""
        graph = self.get_ancestors(entity_id)

        entities_checked = 0
        entities_valid = 0
        entities_invalid: list[str] = []
        details: list[dict[str, Any]] = []

        for entity in graph.entities:
            result = self.verify_entity(entity.entity_id)
            details.append(result)
            entities_checked += 1

            if result["verified"]:
                entities_valid += 1
            else:
                entities_invalid.append(entity.entity_id)

        return {
            "verified": len(entities_invalid) == 0,
            "entities_checked": entities_checked,
            "entities_valid": entities_valid,
            "entities_invalid": entities_invalid,
            "details": details,
        }

    # =========================================================================
    # Export
    # =========================================================================

    def export_prov_json(
        self,
        entity_id: str | None = None,
    ) -> dict[str, Any]:
        """Export lineage as PROV-JSON."""
        if entity_id:
            graph = self.get_full_lineage(entity_id)
        else:
            # Export all
            graph = LineageGraph(
                entities=self.list_entities(),
                activities=self.list_activities(),
                agents=self.list_agents(),
                relations=self.get_relations(),
            )

        return graph.to_prov_dict()

    # =========================================================================
    # Lifecycle
    # =========================================================================

    def close(self) -> None:
        """Close the store and release resources."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None
