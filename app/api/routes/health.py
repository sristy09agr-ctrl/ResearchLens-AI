"""
Health and readiness check endpoints.
"""

from fastapi import APIRouter, Response, status
from app.config import settings
from app.db.database import get_connection

router = APIRouter(tags=["Health"])


@router.get("/health")
def liveness():
    """Liveness probe: verifies that the web service is responsive."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version
    }


@router.get("/ready")
def readiness(response: Response):
    """
    Readiness probe: verifies that the database and external resources are accessible.
    """
    db_ok = False
    try:
        with get_connection() as conn:
            conn.execute("SELECT 1")
            db_ok = True
    except Exception:
        db_ok = False

    # Check Qdrant availability (non-blocking)
    qdrant_ok = False
    try:
        import httpx
        r = httpx.get(f"http://{settings.qdrant_host}:{settings.qdrant_port}/healthz", timeout=1.0)
        qdrant_ok = (r.status_code == 200)
    except Exception:
        qdrant_ok = False

    is_ready = db_ok

    if not is_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return {
        "status": "ready" if is_ready else "not_ready",
        "database": "connected" if db_ok else "disconnected",
        "qdrant": "connected" if qdrant_ok else "not_configured_or_unreachable",
        "version": settings.app_version
    }

