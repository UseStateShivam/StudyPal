"""Health and readiness monitoring endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.session import get_db
from app.config import settings
from app.ml.content.retrieval import get_embedding_model

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("/live")
def liveness():
    """Liveness probe: verifies process is alive and responsive."""
    return {"status": "alive", "service": "studypal-backend"}


@router.get("/ready")
def readiness(db: Session = Depends(get_db)):
    """Readiness probe: verifies database connectivity and ML configuration."""
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    return {
        "status": "ready" if db_ok else "unhealthy",
        "database_connected": db_ok,
        "embedding_model": settings.EMBEDDING_MODEL_NAME,
        "retrieval_method": settings.RETRIEVAL_METHOD,
    }
