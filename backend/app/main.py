"""StudyPal FastAPI main application entrypoint."""

from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.logging_config import setup_logging, logger
from app.db.session import engine, Base
from app.api.router import api_router
from app.core.exceptions import StudyPalException


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    setup_logging()
    logger.info("Initializing StudyPal database tables...")
    # Auto-create tables for local development / SQLite
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized successfully.")
    yield
    logger.info("Shutting down StudyPal...")


app = FastAPI(
    title="StudyPal API",
    description="Personalised Learning and Intelligent Study Recommendation Platform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Custom Exception Handler
@app.exception_handler(StudyPalException)
async def studypal_exception_handler(request: Request, exc: StudyPalException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )


# Include API routes with version prefix
app.include_router(api_router, prefix=settings.API_V1_PREFIX)
# Also mount health directly at root /health for container orchestrators
from app.api.v1.health import router as health_router
app.include_router(health_router)


@app.get("/")
def root():
    return {
        "name": "StudyPal API",
        "version": "1.0.0",
        "documentation": "/docs",
        "health": "/health/ready"
    }
