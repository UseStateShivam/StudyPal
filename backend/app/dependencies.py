"""FastAPI dependency injection for database session and authentication."""

from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import User, Course
from app.core.security import decode_access_token
from app.core.exceptions import UnauthorizedAccessException, ForbiddenCourseAccessException

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Validate JWT token and return active User object."""
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise UnauthorizedAccessException("Could not validate credentials or token expired.")

    user_id = payload["sub"]
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        raise UnauthorizedAccessException("User not found or disabled.")

    return user


def get_user_course(
    course_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Course:
    """Enforce strict ownership access control for course resources."""
    course = db.query(Course).filter(Course.id == course_id, Course.owner_id == current_user.id).first()
    if not course:
        raise ForbiddenCourseAccessException(course_id)
    return course
