"""
Generation endpoints.

This module provides endpoints for persona generation.
"""

from fastapi import APIRouter, Depends, HTTPException, Request, status

from persona.api.dependencies import ConfigDep, verify_token
from persona.api.models.requests import GenerateRequest
from persona.api.models.responses import ErrorResponse, GenerateResponse, JobStatusResponse
from persona.api.services.generation import GenerationService

router = APIRouter(prefix="/api/v1", tags=["generation"])


def get_generation_service(request: Request) -> GenerationService:
    """Get generation service from app state."""
    return request.app.state.generation_service


@router.post("/generate", response_model=GenerateResponse, dependencies=[Depends(verify_token)])
async def create_generation(
    request: GenerateRequest,
    config: ConfigDep,
    service: GenerationService = Depends(get_generation_service),
) -> GenerateResponse:
    """
    Start persona generation job.

    This endpoint creates an async generation job and returns immediately
    with a job ID for status tracking.

    Args:
        request: Generation request parameters.
        config: API configuration.
        service: Generation service.

    Returns:
        GenerateResponse with job ID and status URL.

    Raises:
        HTTPException: If validation fails.
    """
    # Create job
    job = service.create_job(
        data=request.data,
        count=request.count or 3,
        provider=request.provider,
        model=request.model,
        config=request.config,
        webhook_url=request.webhook_url,
    )

    # Start job in background
    service.start_job(job.job_id)

    return GenerateResponse(
        job_id=job.job_id,
        status="pending",
        message="Generation job created successfully",
        status_url=f"/api/v1/generate/{job.job_id}",
    )


@router.get("/generate/{job_id}", response_model=JobStatusResponse)
async def get_generation_status(
    job_id: str,
    service: GenerationService = Depends(get_generation_service),
) -> JobStatusResponse:
    """
    Get generation job status.

    Args:
        job_id: Job identifier.
        service: Generation service.

    Returns:
        JobStatusResponse with current status and results.

    Raises:
        HTTPException: If job not found.
    """
    job = service.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job {job_id} not found",
        )

    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status.value,
        progress=job.progress,
        created_at=job.created_at,
        started_at=job.started_at,
        completed_at=job.completed_at,
        error=job.error,
        result=job.result,
    )


@router.get("/generate", response_model=list[JobStatusResponse])
async def list_generations(
    service: GenerationService = Depends(get_generation_service),
) -> list[JobStatusResponse]:
    """
    List all generation jobs.

    Args:
        service: Generation service.

    Returns:
        List of job statuses.
    """
    jobs = service.list_jobs()
    return [
        JobStatusResponse(
            job_id=job.job_id,
            status=job.status.value,
            progress=job.progress,
            created_at=job.created_at,
            started_at=job.started_at,
            completed_at=job.completed_at,
            error=job.error,
            result=job.result,
        )
        for job in jobs
    ]
