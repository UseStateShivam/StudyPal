"""StudyPal API router aggregating all v1 domain modules."""

from fastapi import APIRouter
from app.api.v1 import (
    auth,
    courses,
    documents,
    topics,
    search,
    quizzes,
    learning,
    recommendations,
    health,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(courses.router)
api_router.include_router(documents.router)
api_router.include_router(topics.router)
api_router.include_router(search.router)
api_router.include_router(quizzes.router)
api_router.include_router(learning.router)
api_router.include_router(recommendations.router)
api_router.include_router(health.router)
