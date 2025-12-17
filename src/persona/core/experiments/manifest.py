"""
Experiment manifest for fast lookup without filesystem scanning.

This module provides a JSON-based index of experiments and their runs,
enabling fast queries and aggregate statistics.
"""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional

from pydantic import BaseModel, Field


class ExperimentSummary(BaseModel):
    """Summary information about an experiment."""

    name: str
    path: str
    description: str = ""
    run_count: int = 0
    last_run: Optional[datetime] = None
    total_personas: int = 0
    total_tokens: int = 0
    providers_used: list[str] = Field(default_factory=list)


class ExperimentManifest(BaseModel):
    """
    Index of experiments for fast lookup.

    Stored at experiments/.manifest.json and updated when experiments
    are created, modified, or when runs complete.

    Example:
        ```python
        manifest = ExperimentManifest.load()
        for name, summary in manifest.experiments.items():
            print(f"{name}: {summary.run_count} runs")
        ```
    """

    experiments: dict[str, ExperimentSummary] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=lambda: datetime.now(UTC))
    version: int = 1

    def get_experiment(self, name: str) -> Optional[ExperimentSummary]:
        """Get summary for an experiment."""
        return self.experiments.get(name)

    def add_experiment(
        self,
        name: str,
        path: str,
        description: str = "",
    ) -> ExperimentSummary:
        """Add or update an experiment in the manifest."""
        summary = ExperimentSummary(
            name=name,
            path=path,
            description=description,
        )
        self.experiments[name] = summary
        self.last_updated = datetime.now(UTC)
        return summary

    def remove_experiment(self, name: str) -> bool:
        """Remove an experiment from the manifest."""
        if name in self.experiments:
            del self.experiments[name]
            self.last_updated = datetime.now(UTC)
            return True
        return False

    def update_run_stats(
        self,
        name: str,
        persona_count: int,
        token_count: int,
        provider: str,
        run_time: Optional[datetime] = None,
    ) -> None:
        """Update statistics after a run completes."""
        if name not in self.experiments:
            return

        summary = self.experiments[name]
        summary.run_count += 1
        summary.total_personas += persona_count
        summary.total_tokens += token_count
        summary.last_run = run_time or datetime.now(UTC)

        if provider and provider not in summary.providers_used:
            summary.providers_used.append(provider)

        self.last_updated = datetime.now(UTC)

    def list_experiments(
        self,
        *,
        has_runs: Optional[bool] = None,
        provider: Optional[str] = None,
    ) -> list[ExperimentSummary]:
        """
        List experiments with optional filtering.

        Args:
            has_runs: Filter to experiments with/without runs.
            provider: Filter to experiments using a specific provider.

        Returns:
            List of matching experiment summaries.
        """
        results = list(self.experiments.values())

        if has_runs is not None:
            if has_runs:
                results = [e for e in results if e.run_count > 0]
            else:
                results = [e for e in results if e.run_count == 0]

        if provider:
            results = [e for e in results if provider in e.providers_used]

        return sorted(results, key=lambda e: e.name)

    def get_statistics(self) -> dict[str, Any]:
        """Get aggregate statistics across all experiments."""
        experiments = list(self.experiments.values())

        return {
            "experiment_count": len(experiments),
            "total_runs": sum(e.run_count for e in experiments),
            "total_personas": sum(e.total_personas for e in experiments),
            "total_tokens": sum(e.total_tokens for e in experiments),
            "providers": sorted(
                set(p for e in experiments for p in e.providers_used)
            ),
        }


class ManifestManager:
    """
    Manager for the experiments manifest file.

    Handles loading, saving, and rebuilding the manifest from filesystem.

    Example:
        ```python
        manager = ManifestManager()
        manifest = manager.load()

        # Update after creating experiment
        manager.update_experiment("new-exp", "experiments/new-exp")

        # Rebuild from filesystem
        manager.rebuild()
        ```
    """

    MANIFEST_FILE = ".manifest.json"

    def __init__(self, base_dir: Path | str = "experiments"):
        """
        Initialise the manifest manager.

        Args:
            base_dir: Base directory containing experiments.
        """
        self._base_dir = Path(base_dir)
        self._manifest: Optional[ExperimentManifest] = None

    @property
    def manifest_path(self) -> Path:
        """Path to the manifest file."""
        return self._base_dir / self.MANIFEST_FILE

    def load(self) -> ExperimentManifest:
        """
        Load manifest from disk.

        Creates empty manifest if file doesn't exist.

        Returns:
            ExperimentManifest instance.
        """
        if self._manifest is not None:
            return self._manifest

        if self.manifest_path.exists():
            try:
                data = json.loads(self.manifest_path.read_text())
                self._manifest = ExperimentManifest.model_validate(data)
            except (json.JSONDecodeError, ValueError):
                # Corrupted file - rebuild
                self._manifest = self._rebuild_manifest()
        else:
            self._manifest = ExperimentManifest()

        return self._manifest

    def save(self) -> None:
        """Save manifest to disk."""
        if self._manifest is None:
            return

        self._manifest.last_updated = datetime.now(UTC)
        self._base_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path.write_text(
            self._manifest.model_dump_json(indent=2, exclude_none=True)
        )

    def update_experiment(
        self,
        name: str,
        path: str,
        description: str = "",
    ) -> None:
        """Add or update an experiment in the manifest."""
        manifest = self.load()
        manifest.add_experiment(name, path, description)
        self.save()

    def remove_experiment(self, name: str) -> None:
        """Remove an experiment from the manifest."""
        manifest = self.load()
        manifest.remove_experiment(name)
        self.save()

    def record_run(
        self,
        experiment_name: str,
        persona_count: int,
        token_count: int,
        provider: str,
    ) -> None:
        """Update manifest after a run completes."""
        manifest = self.load()
        manifest.update_run_stats(
            name=experiment_name,
            persona_count=persona_count,
            token_count=token_count,
            provider=provider,
        )
        self.save()

    def rebuild(self) -> ExperimentManifest:
        """
        Rebuild manifest from filesystem.

        Scans the experiments directory and reconstructs the manifest
        from individual experiment history files.

        Returns:
            Rebuilt manifest.
        """
        self._manifest = self._rebuild_manifest()
        self.save()
        return self._manifest

    def _rebuild_manifest(self) -> ExperimentManifest:
        """Rebuild manifest from filesystem."""
        manifest = ExperimentManifest()

        if not self._base_dir.exists():
            return manifest

        # Scan for experiment directories
        for exp_dir in self._base_dir.iterdir():
            if not exp_dir.is_dir():
                continue
            if exp_dir.name.startswith("."):
                continue

            # Check if it's a valid experiment (has config.yaml or data/)
            if not (exp_dir / "config.yaml").exists() and not (exp_dir / "data").exists():
                continue

            # Load description from config
            description = ""
            config_path = exp_dir / "config.yaml"
            if config_path.exists():
                try:
                    import yaml
                    with open(config_path) as f:
                        config = yaml.safe_load(f) or {}
                    description = config.get("description", "")
                except Exception:
                    pass

            summary = ExperimentSummary(
                name=exp_dir.name,
                path=str(exp_dir),
                description=description,
            )

            # Load run statistics from history.json
            history_path = exp_dir / "history.json"
            if history_path.exists():
                try:
                    history_data = json.loads(history_path.read_text())
                    runs = history_data.get("runs", [])

                    summary.run_count = len(runs)
                    summary.total_personas = sum(r.get("persona_count", 0) for r in runs)
                    summary.total_tokens = sum(
                        r.get("tokens", {}).get("input", 0) +
                        r.get("tokens", {}).get("output", 0)
                        for r in runs
                    )
                    summary.providers_used = sorted(
                        set(r.get("provider", "") for r in runs if r.get("provider"))
                    )

                    if runs:
                        # Get most recent run time
                        latest_run = max(
                            runs,
                            key=lambda r: r.get("completed_at", r.get("started_at", "")),
                        )
                        time_str = latest_run.get("completed_at") or latest_run.get("started_at")
                        if time_str:
                            try:
                                summary.last_run = datetime.fromisoformat(
                                    time_str.replace("Z", "+00:00")
                                )
                            except ValueError:
                                pass
                except (json.JSONDecodeError, KeyError):
                    pass

            manifest.experiments[exp_dir.name] = summary

        return manifest
