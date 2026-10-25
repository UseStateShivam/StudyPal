"""Courses API endpoints: create, list, read, update, and delete with ownership protection."""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Course, User, Document, Topic
from app.schemas import CourseCreate, CourseUpdate, CourseOut
from app.dependencies import get_current_user, get_user_course
from app.core.exceptions import EntityNotFoundException

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.post("", response_model=CourseOut, status_code=status.HTTP_201_CREATED)
def create_course(
    course_in: CourseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new course owned by the current student."""
    course = Course(
        owner_id=current_user.id,
        name=course_in.name,
        description=course_in.description,
    )
    db.add(course)
    db.commit()
    db.refresh(course)

    return CourseOut(
        id=course.id,
        owner_id=course.owner_id,
        name=course.name,
        description=course.description,
        created_at=course.created_at,
        updated_at=course.updated_at,
        document_count=0,
        topic_count=0,
    )


@router.get("", response_model=List[CourseOut])
def list_courses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all courses belonging to the authenticated student."""
    courses = db.query(Course).filter(Course.owner_id == current_user.id).order_by(Course.created_at.desc()).all()
    results = []
    for c in courses:
        doc_count = db.query(Document).filter(Document.course_id == c.id).count()
        topic_count = db.query(Topic).filter(Topic.course_id == c.id).count()
        results.append(
            CourseOut(
                id=c.id,
                owner_id=c.owner_id,
                name=c.name,
                description=c.description,
                created_at=c.created_at,
                updated_at=c.updated_at,
                document_count=doc_count,
                topic_count=topic_count,
            )
        )
    return results


@router.get("/{course_id}", response_model=CourseOut)
def get_course(
    course: Course = Depends(get_user_course),
    db: Session = Depends(get_db)
):
    """Retrieve course details by ID."""
    doc_count = db.query(Document).filter(Document.course_id == course.id).count()
    topic_count = db.query(Topic).filter(Topic.course_id == course.id).count()
    return CourseOut(
        id=course.id,
        owner_id=course.owner_id,
        name=course.name,
        description=course.description,
        created_at=course.created_at,
        updated_at=course.updated_at,
        document_count=doc_count,
        topic_count=topic_count,
    )


@router.patch("/{course_id}", response_model=CourseOut)
def update_course(
    course_in: CourseUpdate,
    course: Course = Depends(get_user_course),
    db: Session = Depends(get_db)
):
    """Update course name or description."""
    if course_in.name is not None:
        course.name = course_in.name
    if course_in.description is not None:
        course.description = course_in.description

    db.commit()
    db.refresh(course)
    doc_count = db.query(Document).filter(Document.course_id == course.id).count()
    topic_count = db.query(Topic).filter(Topic.course_id == course.id).count()
    return CourseOut(
        id=course.id,
        owner_id=course.owner_id,
        name=course.name,
        description=course.description,
        created_at=course.created_at,
        updated_at=course.updated_at,
        document_count=doc_count,
        topic_count=topic_count,
    )


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course: Course = Depends(get_user_course),
    db: Session = Depends(get_db)
):
    """Delete a course and all associated documents, topics, quizzes, and learner state."""
    db.delete(course)
    db.commit()
    return None
