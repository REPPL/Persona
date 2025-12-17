"""
Run history tracking for experiments.

This module provides models and management for tracking generation runs
within experiments, enabling comparison, filtering, and auditing.
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


class TokenUsage(BaseModel):
    """Token usage statistics for a run."""

    input: int = 0
    output: int = 0

    @property
    def total(self) -> int:
        """Total tokens used."""
        return self.input + self.output


class RunInfo(BaseModel):
    """Information about a single generation run.

    Attributes:
        run_id: Unique identifier (typically timestamp-based folder name).
        started_at: When the run began.
        completed_at: When the run finished (None if still running).
        status: Current status of the run.
        provider: LLM provider used.
        model: Model identifier used.
        persona_count: Number of personas generated.
        tokens: Token usage statistics.
        output_dir: Relative path to output directory within experiment.
        data_source: Path to input data used.
        config: Generation configuration parameters.
    """

    run_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: Literal["running", "success", "failed", "partial"] = "running"
    provider: str = ""
    model: str = ""
    persona_count: int = 0
    tokens: TokenUsage = Field(default_factory=TokenUsage)
    output_dir: str = ""
    data_source: str = ""
    config: dict[str, Any] = Field(default_factory=dict)

    @property
    def duration_seconds(self) -> Optional[float]:
        """Duration of the run in seconds, if completed."""
        if self.completed_at and self.started_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None


class RunHistory(BaseModel):
    """History of all runs for an experiment.

    Attributes:
        experiment: Name of the experiment.
        runs: List of all runs, most recent first.
        last_updated: When this history was last modified.
    """

    experiment: str
    runs: list[RunInfo] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RunHistoryManager:
    """Manager for experiment run history.

    Handles loading, saving, and querying run history for experiments.

    Example:
        ```python
        manager = RunHistoryManager(Path("experiments/my-research"))
        run_info = manager.start_run(provider="anthropic", model="claude-sonnet")
        # ... generation happens ...
        manager.complete_run(run_info.run_id, persona_count=3, tokens={"input": 100, "output": 200})
        ```
    """

    HISTORY_FILE = "history.json"

    def __init__(self, experiment_path: Path, experiment_name: Optional[str] = None):
        """Initialise the history manager.

        Args:
            experiment_path: Path to the experiment directory.
            experiment_name: Name of the experiment (defaults to directory name).
        """
        self._path = Path(experiment_path)
        self._name = experiment_name or self._path.name
        self._history: Optional[RunHistory] = None

    @property
    def history_path(self) -> Path:
        """Path to the history.json file."""
        return self._path / self.HISTORY_FILE

    def load(self) -> RunHistory:
        """Load run history from disk.

        Returns:
            RunHistory object (creates empty if file doesn't exist).
        """
        if self._history is not None:
            return self._history

        if self.history_path.exists():
            try:
                data = json.loads(self.history_path.read_text())
                self._history = RunHistory.model_validate(data)
            except (json.JSONDecodeError, ValueError):
                # Corrupted file - start fresh
                self._history = RunHistory(experiment=self._name)
        else:
            self._history = RunHistory(experiment=self._name)

        return self._history

    def save(self) -> None:
        """Save run history to disk."""
        if self._history is None:
            return

        self._history.last_updated = datetime.now(UTC)
        self.history_path.write_text(
            self._history.model_dump_json(indent=2, exclude_none=True)
        )

    def start_run(
        self,
        provider: str,
        model: str,
        data_source: str = "",
        config: Optional[dict[str, Any]] = None,
    ) -> RunInfo:
        """Start a new run and record it in history.

        Args:
            provider: LLM provider name.
            model: Model identifier.
            data_source: Path to input data.
            config: Generation configuration.

        Returns:
            RunInfo for the new run.
        """
        history = self.load()

        run_id = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
        run_info = RunInfo(
            run_id=run_id,
            started_at=datetime.now(UTC),
            status="running",
            provider=provider,
            model=model,
            data_source=data_source,
            config=config or {},
        )

        # Add to front of list (most recent first)
        history.runs.insert(0, run_info)
        self.save()

        return run_info

    def complete_run(
        self,
        run_id: str,
        *,
        status: Literal["success", "failed", "partial"] = "success",
        persona_count: int = 0,
        tokens: Optional[dict[str, int]] = None,
        output_dir: str = "",
    ) -> Optional[RunInfo]:
        """Mark a run as completed.

        Args:
            run_id: ID of the run to complete.
            status: Final status.
            persona_count: Number of personas generated.
            tokens: Token usage ({"input": N, "output": M}).
            output_dir: Relative path to output directory.

        Returns:
            Updated RunInfo, or None if run not found.
        """
        history = self.load()

        for run in history.runs:
            if run.run_id == run_id:
                run.completed_at = datetime.now(UTC)
                run.status = status
                run.persona_count = persona_count
                run.output_dir = output_dir
                if tokens:
                    run.tokens = TokenUsage(
                        input=tokens.get("input", 0),
                        output=tokens.get("output", 0),
                    )
                self.save()
                return run

        return None

    def record_run(
        self,
        provider: str,
        model: str,
        persona_count: int,
        tokens: dict[str, int],
        output_dir: str,
        data_source: str = "",
        config: Optional[dict[str, Any]] = None,
        status: Literal["success", "failed", "partial"] = "success",
        started_at: Optional[datetime] = None,
        completed_at: Optional[datetime] = None,
    ) -> RunInfo:
        """Record a completed run directly (convenience method).

        Use this when you want to record a run after it's already completed,
        rather than using start_run/complete_run pair.

        Args:
            provider: LLM provider name.
            model: Model identifier.
            persona_count: Number of personas generated.
            tokens: Token usage ({"input": N, "output": M}).
            output_dir: Relative path to output directory.
            data_source: Path to input data.
            config: Generation configuration.
            status: Final status.
            started_at: When the run started (defaults to now).
            completed_at: When the run ended (defaults to now).

        Returns:
            The recorded RunInfo.
        """
        history = self.load()

        now = datetime.now(UTC)
        run_id = (started_at or now).strftime("%Y%m%d_%H%M%S")

        run_info = RunInfo(
            run_id=run_id,
            started_at=started_at or now,
            completed_at=completed_at or now,
            status=status,
            provider=provider,
            model=model,
            persona_count=persona_count,
            tokens=TokenUsage(
                input=tokens.get("input", 0),
                output=tokens.get("output", 0),
            ),
            output_dir=output_dir,
            data_source=data_source,
            config=config or {},
        )

        history.runs.insert(0, run_info)
        self.save()

        return run_info

    def get_run(self, run_id: str) -> Optional[RunInfo]:
        """Get a specific run by ID.

        Args:
            run_id: ID of the run to retrieve.

        Returns:
            RunInfo if found, None otherwise.
        """
        history = self.load()
        for run in history.runs:
            if run.run_id == run_id:
                return run
        return None

    def list_runs(
        self,
        *,
        status: Optional[str] = None,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> list[RunInfo]:
        """List runs with optional filtering.

        Args:
            status: Filter by status (success, failed, partial, running).
            provider: Filter by provider name.
            model: Filter by model name.
            limit: Maximum number of runs to return.

        Returns:
            List of matching RunInfo objects.
        """
        history = self.load()
        runs = history.runs

        if status:
            runs = [r for r in runs if r.status == status]
        if provider:
            runs = [r for r in runs if r.provider == provider]
        if model:
            runs = [r for r in runs if r.model == model]
        if limit:
            runs = runs[:limit]

        return runs

    def delete_run(self, run_id: str) -> bool:
        """Delete a run from history.

        Args:
            run_id: ID of the run to delete.

        Returns:
            True if deleted, False if not found.
        """
        history = self.load()
        original_count = len(history.runs)
        history.runs = [r for r in history.runs if r.run_id != run_id]

        if len(history.runs) < original_count:
            self.save()
            return True
        return False

    def clear_history(self) -> int:
        """Clear all run history.

        Returns:
            Number of runs deleted.
        """
        history = self.load()
        count = len(history.runs)
        history.runs = []
        self.save()
        return count
