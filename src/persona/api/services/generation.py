"""
Generation service.

This module handles async persona generation with job tracking.
"""

import asyncio
import logging
import uuid
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Optional

from persona.sdk import AsyncPersonaGenerator, PersonaConfig
from persona.sdk.exceptions import PersonaError

logger = logging.getLogger(__name__)


class JobStatus(str, Enum):
    """Generation job status."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerationJob:
    """
    Represents a generation job.
    """

    def __init__(
        self,
        job_id: str,
        data: str,
        count: int,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        config: Optional[dict[str, Any]] = None,
        webhook_url: Optional[str] = None,
    ):
        """
        Initialise generation job.

        Args:
            job_id: Unique job identifier.
            data: Data source path.
            count: Number of personas to generate.
            provider: LLM provider.
            model: Model identifier.
            config: Generation configuration.
            webhook_url: Optional webhook URL for notifications.
        """
        self.job_id = job_id
        self.data = data
        self.count = count
        self.provider = provider
        self.model = model
        self.config = config or {}
        self.webhook_url = webhook_url

        self.status = JobStatus.PENDING
        self.progress = 0
        self.created_at = datetime.now()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None
        self.result: Optional[dict[str, Any]] = None

    def to_dict(self) -> dict[str, Any]:
        """Convert job to dictionary."""
        return {
            "job_id": self.job_id,
            "status": self.status.value,
            "progress": self.progress,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "error": self.error,
            "result": self.result,
        }


class GenerationService:
    """
    Manages persona generation jobs.

    Handles job creation, tracking, and async execution.
    """

    def __init__(self):
        """Initialise generation service."""
        self.jobs: dict[str, GenerationJob] = {}
        self.webhook_manager: Optional[Any] = None  # Set by app

    def set_webhook_manager(self, webhook_manager: Any) -> None:
        """Set webhook manager for notifications."""
        self.webhook_manager = webhook_manager

    def create_job(
        self,
        data: str,
        count: int,
        provider: Optional[str] = None,
        model: Optional[str] = None,
        config: Optional[dict[str, Any]] = None,
        webhook_url: Optional[str] = None,
    ) -> GenerationJob:
        """
        Create a new generation job.

        Args:
            data: Data source path.
            count: Number of personas to generate.
            provider: LLM provider.
            model: Model identifier.
            config: Generation configuration.
            webhook_url: Optional webhook URL.

        Returns:
            Created job.
        """
        job_id = f"job-{uuid.uuid4().hex[:12]}"
        job = GenerationJob(
            job_id=job_id,
            data=data,
            count=count,
            provider=provider,
            model=model,
            config=config,
            webhook_url=webhook_url,
        )
        self.jobs[job_id] = job

        logger.info(f"Created generation job {job_id}")
        return job

    def get_job(self, job_id: str) -> Optional[GenerationJob]:
        """Get job by ID."""
        return self.jobs.get(job_id)

    def list_jobs(self) -> list[GenerationJob]:
        """List all jobs."""
        return list(self.jobs.values())

    async def execute_job(self, job_id: str) -> None:
        """
        Execute generation job asynchronously.

        Args:
            job_id: Job identifier.
        """
        job = self.get_job(job_id)
        if not job:
            logger.error(f"Job {job_id} not found")
            return

        logger.info(f"Executing job {job_id}")

        # Update status
        job.status = JobStatus.RUNNING
        job.started_at = datetime.now()

        # Notify started
        if self.webhook_manager and job.webhook_url:
            await self.webhook_manager.notify_generation_started(
                job_id=job_id,
                webhook_url=job.webhook_url,
            )

        try:
            # Create generator
            generator = AsyncPersonaGenerator(
                provider=job.provider or "anthropic",
                model=job.model,
            )

            # Build config
            persona_config = PersonaConfig(
                count=job.count,
                **job.config,
            )

            # Progress callback
            async def on_progress(current: int, total: int) -> None:
                job.progress = int((current / total) * 100)
                logger.info(f"Job {job_id} progress: {job.progress}%")

                # Notify progress
                if self.webhook_manager and job.webhook_url:
                    await self.webhook_manager.notify_generation_progress(
                        job_id=job_id,
                        progress=job.progress,
                        webhook_url=job.webhook_url,
                    )

            # Set progress callback
            generator.set_progress_callback(
                lambda msg, step, total: asyncio.create_task(on_progress(step, total))
            )

            # Generate personas
            result = await generator.agenerate(
                data_path=Path(job.data),
                config=persona_config,
            )

            # Update job
            job.status = JobStatus.COMPLETED
            job.progress = 100
            job.completed_at = datetime.now()
            job.result = {
                "personas": [p.model_dump() for p in result.personas],
                "metadata": result.metadata,
            }

            logger.info(f"Job {job_id} completed successfully")

            # Notify completed
            if self.webhook_manager and job.webhook_url:
                await self.webhook_manager.notify_generation_completed(
                    job_id=job_id,
                    result=job.result,
                    webhook_url=job.webhook_url,
                )

        except PersonaError as e:
            # Update job
            job.status = JobStatus.FAILED
            job.completed_at = datetime.now()
            job.error = str(e)

            logger.error(f"Job {job_id} failed: {e}")

            # Notify failed
            if self.webhook_manager and job.webhook_url:
                await self.webhook_manager.notify_generation_failed(
                    job_id=job_id,
                    error=job.error,
                    webhook_url=job.webhook_url,
                )

        except Exception as e:
            # Unexpected error
            job.status = JobStatus.FAILED
            job.completed_at = datetime.now()
            job.error = f"Unexpected error: {str(e)}"

            logger.exception(f"Job {job_id} failed with unexpected error")

            # Notify failed
            if self.webhook_manager and job.webhook_url:
                await self.webhook_manager.notify_generation_failed(
                    job_id=job_id,
                    error=job.error,
                    webhook_url=job.webhook_url,
                )

    def start_job(self, job_id: str) -> None:
        """
        Start job execution in background.

        Args:
            job_id: Job identifier.
        """
        asyncio.create_task(self.execute_job(job_id))
