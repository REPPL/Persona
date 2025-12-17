"""
SQLite implementation of experiment storage.

Provides persistent, queryable storage for experiments, variants, and runs
using SQLite.
"""

import json
import sqlite3
import uuid
from collections.abc import Generator
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from persona.core.experiments.store import ExperimentStore


def _generate_id() -> str:
    """Generate a unique ID."""
    return str(uuid.uuid4())


def _now() -> datetime:
    """Get current UTC datetime."""
    return datetime.now(UTC)


def _to_json(data: dict[str, Any] | None) -> str | None:
    """Convert dict to JSON string."""
    if data is None:
        return None
    return json.dumps(data)


def _from_json(data: str | None) -> dict[str, Any] | None:
    """Convert JSON string to dict."""
    if data is None:
        return None
    return json.loads(data)


class SQLiteExperimentStore(ExperimentStore):
    """
    SQLite-based experiment storage.

    Stores experiments, variants, and runs in a SQLite database,
    providing efficient querying and persistent storage.

    Example:
        ```python
        store = SQLiteExperimentStore("./experiments.db")
        exp_id = store.create_experiment("my-research")
        store.create_run(exp_id, "claude-sonnet", "anthropic")
        store.close()
        ```

    Attributes:
        db_path: Path to SQLite database file.
    """

    SCHEMA_VERSION = 1

    def __init__(self, db_path: str | Path) -> None:
        """
        Initialise SQLite store.

        Args:
            db_path: Path to database file. Use ":memory:" for in-memory DB.
        """
        self._db_path = Path(db_path) if db_path != ":memory:" else db_path
        self._conn: sqlite3.Connection | None = None
        self._initialise_db()

    @property
    def db_path(self) -> Path | str:
        """Get database path."""
        return self._db_path

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Get database connection with automatic transaction handling."""
        if self._conn is None:
            if isinstance(self._db_path, Path):
                self._db_path.parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(
                str(self._db_path),
                detect_types=sqlite3.PARSE_DECLTYPES,
            )
            self._conn.row_factory = sqlite3.Row
            # Enable foreign key constraints for CASCADE to work
            self._conn.execute("PRAGMA foreign_keys = ON")

        try:
            yield self._conn
            self._conn.commit()
        except Exception:
            self._conn.rollback()
            raise

    def _initialise_db(self) -> None:
        """Create database schema if not exists."""
        with self._get_connection() as conn:
            conn.executescript(
                """
                -- Schema version tracking
                CREATE TABLE IF NOT EXISTS schema_version (
                    version INTEGER PRIMARY KEY
                );

                -- Experiments
                CREATE TABLE IF NOT EXISTS experiments (
                    experiment_id TEXT PRIMARY KEY,
                    project_id TEXT,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    hypothesis TEXT,
                    status TEXT DEFAULT 'planned',
                    config_json TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(project_id, name)
                );

                CREATE INDEX IF NOT EXISTS idx_experiments_project
                ON experiments(project_id);

                CREATE INDEX IF NOT EXISTS idx_experiments_status
                ON experiments(status);

                -- Variants (named parameter sets)
                CREATE TABLE IF NOT EXISTS variants (
                    variant_id TEXT PRIMARY KEY,
                    experiment_id TEXT NOT NULL REFERENCES experiments(experiment_id)
                        ON DELETE CASCADE,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    parameters_json TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    UNIQUE(experiment_id, name)
                );

                CREATE INDEX IF NOT EXISTS idx_variants_experiment
                ON variants(experiment_id);

                -- Runs
                CREATE TABLE IF NOT EXISTS runs (
                    run_id TEXT PRIMARY KEY,
                    experiment_id TEXT NOT NULL REFERENCES experiments(experiment_id)
                        ON DELETE CASCADE,
                    variant_id TEXT REFERENCES variants(variant_id)
                        ON DELETE SET NULL,
                    run_number INTEGER NOT NULL,
                    model TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    status TEXT DEFAULT 'running',
                    parameters_json TEXT,
                    output_dir TEXT DEFAULT '',
                    persona_count INTEGER DEFAULT 0,
                    input_tokens INTEGER DEFAULT 0,
                    output_tokens INTEGER DEFAULT 0,
                    cost REAL DEFAULT 0.0,
                    duration_seconds REAL DEFAULT 0.0,
                    metrics_json TEXT,
                    audit_id TEXT,
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    UNIQUE(experiment_id, run_number)
                );

                CREATE INDEX IF NOT EXISTS idx_runs_experiment
                ON runs(experiment_id);

                CREATE INDEX IF NOT EXISTS idx_runs_variant
                ON runs(variant_id);

                CREATE INDEX IF NOT EXISTS idx_runs_status
                ON runs(status);

                CREATE INDEX IF NOT EXISTS idx_runs_started
                ON runs(started_at);
                """
            )

            # Check and update schema version
            cursor = conn.execute("SELECT version FROM schema_version LIMIT 1")
            row = cursor.fetchone()
            if row is None:
                conn.execute(
                    "INSERT INTO schema_version (version) VALUES (?)",
                    (self.SCHEMA_VERSION,),
                )

    # =========================================================================
    # Experiment Operations
    # =========================================================================

    def create_experiment(
        self,
        name: str,
        *,
        project_id: str | None = None,
        description: str = "",
        hypothesis: str | None = None,
        config: dict[str, Any] | None = None,
    ) -> str:
        """Create a new experiment."""
        experiment_id = _generate_id()
        now = _now().isoformat()

        with self._get_connection() as conn:
            # Check for duplicate name (SQLite UNIQUE doesn't work with NULL)
            if project_id is None:
                cursor = conn.execute(
                    "SELECT 1 FROM experiments WHERE name = ? AND project_id IS NULL",
                    (name,),
                )
            else:
                cursor = conn.execute(
                    "SELECT 1 FROM experiments WHERE name = ? AND project_id = ?",
                    (name, project_id),
                )
            if cursor.fetchone() is not None:
                raise ValueError(
                    f"Experiment '{name}' already exists"
                    + (f" in project '{project_id}'" if project_id else "")
                )

            try:
                conn.execute(
                    """
                    INSERT INTO experiments
                    (experiment_id, project_id, name, description, hypothesis,
                     config_json, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        experiment_id,
                        project_id,
                        name,
                        description,
                        hypothesis,
                        _to_json(config),
                        now,
                        now,
                    ),
                )
            except sqlite3.IntegrityError as e:
                if "UNIQUE constraint" in str(e):
                    raise ValueError(
                        f"Experiment '{name}' already exists"
                        + (f" in project '{project_id}'" if project_id else "")
                    ) from e
                raise

        return experiment_id

    def get_experiment(self, experiment_id: str) -> dict[str, Any] | None:
        """Get experiment by ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM experiments WHERE experiment_id = ?",
                (experiment_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_experiment(row)

    def get_experiment_by_name(
        self,
        name: str,
        project_id: str | None = None,
    ) -> dict[str, Any] | None:
        """Get experiment by name."""
        with self._get_connection() as conn:
            if project_id is not None:
                cursor = conn.execute(
                    "SELECT * FROM experiments WHERE name = ? AND project_id = ?",
                    (name, project_id),
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM experiments WHERE name = ? AND project_id IS NULL",
                    (name,),
                )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_experiment(row)

    def list_experiments(
        self,
        project_id: str | None = None,
        status: str | None = None,
    ) -> list[dict[str, Any]]:
        """List experiments."""
        with self._get_connection() as conn:
            query = "SELECT * FROM experiments WHERE 1=1"
            params: list[Any] = []

            if project_id is not None:
                query += " AND project_id = ?"
                params.append(project_id)

            if status is not None:
                query += " AND status = ?"
                params.append(status)

            query += " ORDER BY created_at DESC"

            cursor = conn.execute(query, params)
            return [self._row_to_experiment(row) for row in cursor.fetchall()]

    def update_experiment(
        self,
        experiment_id: str,
        **updates: Any,
    ) -> bool:
        """Update experiment fields."""
        if not updates:
            return False

        # Handle config separately (needs JSON encoding)
        if "config" in updates:
            updates["config_json"] = _to_json(updates.pop("config"))

        updates["updated_at"] = _now().isoformat()

        # Build UPDATE statement
        set_clause = ", ".join(f"{key} = ?" for key in updates.keys())
        values = list(updates.values()) + [experiment_id]

        with self._get_connection() as conn:
            cursor = conn.execute(
                f"UPDATE experiments SET {set_clause} WHERE experiment_id = ?",
                values,
            )
            return cursor.rowcount > 0

    def delete_experiment(self, experiment_id: str) -> bool:
        """Delete an experiment."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM experiments WHERE experiment_id = ?",
                (experiment_id,),
            )
            return cursor.rowcount > 0

    def _row_to_experiment(self, row: sqlite3.Row) -> dict[str, Any]:
        """Convert database row to experiment dictionary."""
        return {
            "experiment_id": row["experiment_id"],
            "project_id": row["project_id"],
            "name": row["name"],
            "description": row["description"],
            "hypothesis": row["hypothesis"],
            "status": row["status"],
            "config": _from_json(row["config_json"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"],
        }

    # =========================================================================
    # Variant Operations
    # =========================================================================

    def create_variant(
        self,
        experiment_id: str,
        name: str,
        parameters: dict[str, Any],
        *,
        description: str = "",
    ) -> str:
        """Create a variant for an experiment."""
        variant_id = _generate_id()
        now = _now().isoformat()

        with self._get_connection() as conn:
            try:
                conn.execute(
                    """
                    INSERT INTO variants
                    (variant_id, experiment_id, name, description,
                     parameters_json, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        variant_id,
                        experiment_id,
                        name,
                        description,
                        _to_json(parameters),
                        now,
                    ),
                )
            except sqlite3.IntegrityError as e:
                if "UNIQUE constraint" in str(e):
                    raise ValueError(
                        f"Variant '{name}' already exists in experiment"
                    ) from e
                if "FOREIGN KEY" in str(e):
                    raise ValueError(f"Experiment '{experiment_id}' not found") from e
                raise

        return variant_id

    def get_variant(self, variant_id: str) -> dict[str, Any] | None:
        """Get variant by ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM variants WHERE variant_id = ?",
                (variant_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_variant(row)

    def list_variants(self, experiment_id: str) -> list[dict[str, Any]]:
        """List variants for an experiment."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM variants WHERE experiment_id = ? ORDER BY created_at",
                (experiment_id,),
            )
            return [self._row_to_variant(row) for row in cursor.fetchall()]

    def update_variant(
        self,
        variant_id: str,
        **updates: Any,
    ) -> bool:
        """Update variant fields."""
        if not updates:
            return False

        # Handle parameters separately (needs JSON encoding)
        if "parameters" in updates:
            updates["parameters_json"] = _to_json(updates.pop("parameters"))

        set_clause = ", ".join(f"{key} = ?" for key in updates.keys())
        values = list(updates.values()) + [variant_id]

        with self._get_connection() as conn:
            cursor = conn.execute(
                f"UPDATE variants SET {set_clause} WHERE variant_id = ?",
                values,
            )
            return cursor.rowcount > 0

    def delete_variant(self, variant_id: str) -> bool:
        """Delete a variant."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM variants WHERE variant_id = ?",
                (variant_id,),
            )
            return cursor.rowcount > 0

    def _row_to_variant(self, row: sqlite3.Row) -> dict[str, Any]:
        """Convert database row to variant dictionary."""
        return {
            "variant_id": row["variant_id"],
            "experiment_id": row["experiment_id"],
            "name": row["name"],
            "description": row["description"],
            "parameters": _from_json(row["parameters_json"]),
            "created_at": row["created_at"],
        }

    # =========================================================================
    # Run Operations
    # =========================================================================

    def create_run(
        self,
        experiment_id: str,
        model: str,
        provider: str,
        *,
        variant_id: str | None = None,
        parameters: dict[str, Any] | None = None,
        output_dir: str = "",
    ) -> str:
        """Create a new run."""
        run_id = _generate_id()
        now = _now().isoformat()

        with self._get_connection() as conn:
            # Get next run number for this experiment
            cursor = conn.execute(
                "SELECT COALESCE(MAX(run_number), 0) + 1 FROM runs "
                "WHERE experiment_id = ?",
                (experiment_id,),
            )
            run_number = cursor.fetchone()[0]

            try:
                conn.execute(
                    """
                    INSERT INTO runs
                    (run_id, experiment_id, variant_id, run_number, model, provider,
                     parameters_json, output_dir, started_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        experiment_id,
                        variant_id,
                        run_number,
                        model,
                        provider,
                        _to_json(parameters),
                        output_dir,
                        now,
                    ),
                )
            except sqlite3.IntegrityError as e:
                if "FOREIGN KEY" in str(e):
                    raise ValueError(f"Experiment '{experiment_id}' not found") from e
                raise

        return run_id

    def get_run(self, run_id: str) -> dict[str, Any] | None:
        """Get run by ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM runs WHERE run_id = ?",
                (run_id,),
            )
            row = cursor.fetchone()
            if row is None:
                return None
            return self._row_to_run(row)

    def list_runs(
        self,
        experiment_id: str,
        *,
        variant_id: str | None = None,
        status: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """List runs for an experiment."""
        with self._get_connection() as conn:
            query = "SELECT * FROM runs WHERE experiment_id = ?"
            params: list[Any] = [experiment_id]

            if variant_id is not None:
                query += " AND variant_id = ?"
                params.append(variant_id)

            if status is not None:
                query += " AND status = ?"
                params.append(status)

            query += " ORDER BY started_at DESC"

            if limit is not None:
                query += " LIMIT ?"
                params.append(limit)

            cursor = conn.execute(query, params)
            return [self._row_to_run(row) for row in cursor.fetchall()]

    def update_run(
        self,
        run_id: str,
        **updates: Any,
    ) -> bool:
        """Update run fields."""
        if not updates:
            return False

        # Handle JSON fields
        if "parameters" in updates:
            updates["parameters_json"] = _to_json(updates.pop("parameters"))
        if "metrics" in updates:
            updates["metrics_json"] = _to_json(updates.pop("metrics"))

        set_clause = ", ".join(f"{key} = ?" for key in updates.keys())
        values = list(updates.values()) + [run_id]

        with self._get_connection() as conn:
            cursor = conn.execute(
                f"UPDATE runs SET {set_clause} WHERE run_id = ?",
                values,
            )
            return cursor.rowcount > 0

    def complete_run(
        self,
        run_id: str,
        *,
        persona_count: int = 0,
        input_tokens: int = 0,
        output_tokens: int = 0,
        cost: float = 0.0,
        duration_seconds: float = 0.0,
        metrics: dict[str, Any] | None = None,
        status: str = "completed",
    ) -> bool:
        """Mark a run as complete with final metrics."""
        now = _now().isoformat()

        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                UPDATE runs SET
                    status = ?,
                    persona_count = ?,
                    input_tokens = ?,
                    output_tokens = ?,
                    cost = ?,
                    duration_seconds = ?,
                    metrics_json = ?,
                    completed_at = ?
                WHERE run_id = ?
                """,
                (
                    status,
                    persona_count,
                    input_tokens,
                    output_tokens,
                    cost,
                    duration_seconds,
                    _to_json(metrics),
                    now,
                    run_id,
                ),
            )
            return cursor.rowcount > 0

    def delete_run(self, run_id: str) -> bool:
        """Delete a run."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM runs WHERE run_id = ?",
                (run_id,),
            )
            return cursor.rowcount > 0

    def _row_to_run(self, row: sqlite3.Row) -> dict[str, Any]:
        """Convert database row to run dictionary."""
        return {
            "run_id": row["run_id"],
            "experiment_id": row["experiment_id"],
            "variant_id": row["variant_id"],
            "run_number": row["run_number"],
            "model": row["model"],
            "provider": row["provider"],
            "status": row["status"],
            "parameters": _from_json(row["parameters_json"]),
            "output_dir": row["output_dir"],
            "persona_count": row["persona_count"],
            "input_tokens": row["input_tokens"],
            "output_tokens": row["output_tokens"],
            "cost": row["cost"],
            "duration_seconds": row["duration_seconds"],
            "metrics": _from_json(row["metrics_json"]),
            "audit_id": row["audit_id"],
            "started_at": row["started_at"],
            "completed_at": row["completed_at"],
        }

    # =========================================================================
    # Statistics and Queries
    # =========================================================================

    def get_experiment_statistics(self, experiment_id: str) -> dict[str, Any]:
        """Get aggregate statistics for an experiment."""
        with self._get_connection() as conn:
            # Basic counts
            cursor = conn.execute(
                """
                SELECT
                    COUNT(*) as total_runs,
                    SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END)
                        as completed_runs,
                    SUM(CASE WHEN status = 'failed' THEN 1 ELSE 0 END) as failed_runs,
                    SUM(CASE WHEN status = 'running' THEN 1 ELSE 0 END) as running_runs,
                    SUM(persona_count) as total_personas,
                    SUM(cost) as total_cost,
                    SUM(input_tokens) as total_input_tokens,
                    SUM(output_tokens) as total_output_tokens,
                    AVG(CASE WHEN status = 'completed' THEN cost ELSE NULL END)
                        as avg_cost_per_run,
                    AVG(CASE WHEN status = 'completed' THEN persona_count ELSE NULL END)
                        as avg_personas_per_run
                FROM runs
                WHERE experiment_id = ?
                """,
                (experiment_id,),
            )
            row = cursor.fetchone()

            # Get distinct models and providers
            cursor = conn.execute(
                "SELECT DISTINCT model FROM runs WHERE experiment_id = ?",
                (experiment_id,),
            )
            models = [r[0] for r in cursor.fetchall()]

            cursor = conn.execute(
                "SELECT DISTINCT provider FROM runs WHERE experiment_id = ?",
                (experiment_id,),
            )
            providers = [r[0] for r in cursor.fetchall()]

            return {
                "total_runs": row["total_runs"] or 0,
                "completed_runs": row["completed_runs"] or 0,
                "failed_runs": row["failed_runs"] or 0,
                "running_runs": row["running_runs"] or 0,
                "total_personas": row["total_personas"] or 0,
                "total_cost": row["total_cost"] or 0.0,
                "total_input_tokens": row["total_input_tokens"] or 0,
                "total_output_tokens": row["total_output_tokens"] or 0,
                "avg_cost_per_run": row["avg_cost_per_run"] or 0.0,
                "avg_personas_per_run": row["avg_personas_per_run"] or 0.0,
                "models_used": models,
                "providers_used": providers,
            }

    def compare_runs(
        self,
        run_id_1: str,
        run_id_2: str,
    ) -> dict[str, Any]:
        """Compare two runs."""
        run1 = self.get_run(run_id_1)
        run2 = self.get_run(run_id_2)

        if run1 is None:
            raise ValueError(f"Run '{run_id_1}' not found")
        if run2 is None:
            raise ValueError(f"Run '{run_id_2}' not found")

        # Find differences
        differences = {}
        fields_to_compare = ["model", "provider", "persona_count", "cost", "status"]

        for field in fields_to_compare:
            if run1[field] != run2[field]:
                differences[field] = {
                    "run_1": run1[field],
                    "run_2": run2[field],
                }

        # Calculate deltas
        delta = {
            "persona_count": (run2["persona_count"] or 0)
            - (run1["persona_count"] or 0),
            "cost": (run2["cost"] or 0.0) - (run1["cost"] or 0.0),
            "input_tokens": (run2["input_tokens"] or 0) - (run1["input_tokens"] or 0),
            "output_tokens": (run2["output_tokens"] or 0)
            - (run1["output_tokens"] or 0),
            "duration_seconds": (run2["duration_seconds"] or 0.0)
            - (run1["duration_seconds"] or 0.0),
        }

        return {
            "run_1": run1,
            "run_2": run2,
            "differences": differences,
            "delta": delta,
        }

    # =========================================================================
    # Lifecycle
    # =========================================================================

    def close(self) -> None:
        """Close database connection."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None


def get_default_db_path() -> Path:
    """
    Get default path for experiments database.

    Returns:
        Path to experiments.db in user's config directory.
    """
    import os
    import sys

    if sys.platform.startswith("linux"):
        xdg = os.environ.get("XDG_DATA_HOME")
        if xdg:
            return Path(xdg) / "persona" / "experiments.db"
        return Path.home() / ".local" / "share" / "persona" / "experiments.db"

    # macOS / Windows
    return Path.home() / ".persona" / "experiments.db"
