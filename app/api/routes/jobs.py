"""
Ingestion job tracking endpoints.
"""

from fastapi import APIRouter, HTTPException
from app.db.database import get_job

router = APIRouter(tags=["Jobs"])


@router.get("/v1/jobs/{job_id}")
@router.get("/jobs/{job_id}")
def get_job_status(job_id: str):
    """Poll asynchronous PDF ingestion progress."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")
    return {
        "status": "success",
        "job": job
    }

