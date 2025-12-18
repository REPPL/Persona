"""
Batch processing for multiple data files.

This module provides the BatchProcessor class for processing
multiple files and generating personas in batch operations.
"""

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from persona.core.data import DataLoader
from persona.core.generation import (
    GenerationConfig,
    GenerationPipeline,
)
from persona.core.generation.parser import Persona
from persona.core.providers import LLMProvider, ProviderFactory


@dataclass
class BatchConfig:
    """
    Configuration for batch processing.

    Attributes:
        provider: LLM provider to use.
        model: Model identifier.
        personas_per_file: Number of personas to generate per file.
        workflow: Workflow to use for generation.
        parallel: Whether to process files in parallel (future).
        continue_on_error: Whether to continue if a file fails.
        output_dir: Directory for batch outputs.
    """

    provider: str = "anthropic"
    model: str | None = None
    personas_per_file: int = 3
    workflow: str = "default"
    parallel: bool = False
    continue_on_error: bool = True
    output_dir: Path | None = None


@dataclass
class FileResult:
    """
    Result for a single file in a batch.

    Attributes:
        file_path: Path to the processed file.
        success: Whether processing succeeded.
        personas: Generated personas (if successful).
        error: Error message (if failed).
        tokens_used: Total tokens used.
        processing_time: Time taken in seconds.
    """

    file_path: Path
    success: bool = True
    personas: list[Persona] = field(default_factory=list)
    error: str | None = None
    tokens_used: int = 0
    processing_time: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "file": str(self.file_path),
            "success": self.success,
            "persona_count": len(self.personas),
            "error": self.error,
            "tokens_used": self.tokens_used,
            "processing_time": self.processing_time,
        }


@dataclass
class BatchResult:
    """
    Result of a batch processing operation.

    Attributes:
        config: Configuration used.
        file_results: Results for each file.
        total_personas: Total personas generated.
        total_tokens: Total tokens used.
        total_time: Total processing time.
        started_at: When processing started.
        completed_at: When processing completed.
    """

    config: BatchConfig
    file_results: list[FileResult] = field(default_factory=list)
    total_personas: int = 0
    total_tokens: int = 0
    total_time: float = 0.0
    started_at: datetime | None = None
    completed_at: datetime | None = None

    @property
    def success_count(self) -> int:
        """Number of successfully processed files."""
        return sum(1 for r in self.file_results if r.success)

    @property
    def failure_count(self) -> int:
        """Number of failed files."""
        return sum(1 for r in self.file_results if not r.success)

    @property
    def all_personas(self) -> list[Persona]:
        """All personas from all successful files."""
        personas = []
        for result in self.file_results:
            if result.success:
                personas.extend(result.personas)
        return personas

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_files": len(self.file_results),
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "total_personas": self.total_personas,
            "total_tokens": self.total_tokens,
            "total_time_seconds": self.total_time,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "files": [r.to_dict() for r in self.file_results],
        }


class BatchProcessor:
    """
    Processes multiple data files in batch.

    Generates personas from each file independently and aggregates results.

    Example:
        processor = BatchProcessor(provider)
        result = processor.process_directory(Path("./data"), config)
        print(f"Generated {result.total_personas} personas")
    """

    def __init__(
        self,
        provider: LLMProvider | None = None,
        config: BatchConfig | None = None,
    ) -> None:
        """
        Initialise the batch processor.

        Args:
            provider: LLM provider to use (created from config if not provided).
            config: Batch configuration.
        """
        self._config = config or BatchConfig()
        self._provider = provider
        self._loader = DataLoader()
        self._progress_callback: Callable[[str, int, int], None] | None = None

    def set_progress_callback(
        self,
        callback: Callable[[str, int, int], None],
    ) -> None:
        """
        Set a callback for progress updates.

        Args:
            callback: Function called with (file_path, current, total).
        """
        self._progress_callback = callback

    def process_files(
        self,
        files: list[Path],
        config: BatchConfig | None = None,
    ) -> BatchResult:
        """
        Process a list of files.

        Args:
            files: List of file paths to process.
            config: Optional config override.

        Returns:
            BatchResult with all file results.
        """
        cfg = config or self._config
        result = BatchResult(
            config=cfg,
            started_at=datetime.now(),
        )

        # Get or create provider
        provider = self._provider or ProviderFactory.create(cfg.provider)

        # Create pipeline
        pipeline = GenerationPipeline(provider)

        import time

        for i, file_path in enumerate(files):
            if self._progress_callback:
                self._progress_callback(str(file_path), i + 1, len(files))

            start_time = time.time()

            try:
                file_result = self._process_single_file(
                    file_path=file_path,
                    pipeline=pipeline,
                    config=cfg,
                )
                file_result.processing_time = time.time() - start_time
                result.file_results.append(file_result)

                result.total_personas += len(file_result.personas)
                result.total_tokens += file_result.tokens_used

            except Exception as e:
                file_result = FileResult(
                    file_path=file_path,
                    success=False,
                    error=str(e),
                    processing_time=time.time() - start_time,
                )
                result.file_results.append(file_result)

                if not cfg.continue_on_error:
                    break

        result.completed_at = datetime.now()
        result.total_time = (result.completed_at - result.started_at).total_seconds()

        return result

    def process_directory(
        self,
        directory: Path,
        config: BatchConfig | None = None,
        pattern: str = "*",
    ) -> BatchResult:
        """
        Process all matching files in a directory.

        Args:
            directory: Directory to process.
            config: Optional config override.
            pattern: Glob pattern for files.

        Returns:
            BatchResult with all file results.
        """
        files = self._loader.discover_files(directory)

        if pattern != "*":
            files = [f for f in files if f.match(pattern)]

        return self.process_files(files, config)

    def _process_single_file(
        self,
        file_path: Path,
        pipeline: GenerationPipeline,
        config: BatchConfig,
    ) -> FileResult:
        """Process a single file."""
        # Load data
        data = self._loader.load_file(file_path)

        # Create generation config
        gen_config = GenerationConfig(
            data_path=file_path,
            provider=config.provider,
            model=config.model,
            count=config.personas_per_file,
            workflow=config.workflow,
        )

        # Generate
        gen_result = pipeline.generate(
            data=data,
            config=gen_config,
            source_files=[file_path],
        )

        return FileResult(
            file_path=file_path,
            success=True,
            personas=gen_result.personas,
            tokens_used=gen_result.input_tokens + gen_result.output_tokens,
        )

    def estimate_batch(
        self,
        files: list[Path],
        config: BatchConfig | None = None,
    ) -> dict[str, Any]:
        """
        Estimate cost and tokens for a batch operation.

        Args:
            files: List of files to estimate.
            config: Optional config override.

        Returns:
            Dictionary with estimation details.
        """
        cfg = config or self._config
        total_tokens = 0
        file_estimates = []

        for file_path in files:
            try:
                data = self._loader.load_file(file_path)
                tokens = self._loader.count_tokens(data)
                total_tokens += tokens

                file_estimates.append(
                    {
                        "file": str(file_path),
                        "tokens": tokens,
                    }
                )
            except Exception as e:
                file_estimates.append(
                    {
                        "file": str(file_path),
                        "error": str(e),
                    }
                )

        # Estimate output tokens
        output_per_file = 800 * cfg.personas_per_file
        total_output = output_per_file * len(files)

        return {
            "total_files": len(files),
            "total_input_tokens": total_tokens,
            "estimated_output_tokens": total_output,
            "estimated_total_tokens": total_tokens + total_output,
            "personas_per_file": cfg.personas_per_file,
            "estimated_total_personas": len(files) * cfg.personas_per_file,
            "files": file_estimates,
        }
