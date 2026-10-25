"""Topics API router: list topics, get topic details, update labels, and inspect related content."""

from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Topic, DocumentChunk, Document, Course, User
from app.schemas import TopicOut, TopicUpdate, TopicRelatedContentOut, DocumentChunkOut
from app.dependencies import get_current_user, get_user_course
from app.core.exceptions import EntityNotFoundException, ForbiddenCourseAccessException

router = APIRouter(tags=["Topics"])


@router.get("/courses/{course_id}/topics", response_model=List[TopicOut])
def list_topics(
    course: Course = Depends(get_user_course),
    db: Session = Depends(get_db),
):
    """List all discovered topics for a course."""
    topics = db.query(Topic).filter(Topic.course_id == course.id).order_by(Topic.cluster_index.asc()).all()
    # Refresh chunk counts
    for t in topics:
        t.chunk_count = db.query(DocumentChunk).filter(DocumentChunk.topic_id == t.id).count()
    return topics


@router.get("/topics/{topic_id}", response_model=TopicOut)
def get_topic(
    topic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get topic details."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise EntityNotFoundException("Topic", topic_id)
    course = db.query(Course).filter(Course.id == topic.course_id, Course.owner_id == current_user.id).first()
    if not course:
        raise ForbiddenCourseAccessException(topic.course_id)
    topic.chunk_count = db.query(DocumentChunk).filter(DocumentChunk.topic_id == topic.id).count()
    return topic


@router.patch("/topics/{topic_id}", response_model=TopicOut)
def update_topic_label(
    topic_id: str,
    topic_in: TopicUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Allow student to customize a topic label without altering cluster assignments."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise EntityNotFoundException("Topic", topic_id)
    course = db.query(Course).filter(Course.id == topic.course_id, Course.owner_id == current_user.id).first()
    if not course:
        raise ForbiddenCourseAccessException(topic.course_id)

    topic.label = topic_in.label
    topic.is_custom_label = True
    db.commit()
    db.refresh(topic)
    topic.chunk_count = db.query(DocumentChunk).filter(DocumentChunk.topic_id == topic.id).count()
    return topic


@router.get("/topics/{topic_id}/related-content", response_model=TopicRelatedContentOut)
def get_topic_related_content(
    topic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve representative chunks and source documents associated with this topic."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise EntityNotFoundException("Topic", topic_id)
    course = db.query(Course).filter(Course.id == topic.course_id, Course.owner_id == current_user.id).first()
    if not course:
        raise ForbiddenCourseAccessException(topic.course_id)

    chunks = db.query(DocumentChunk).filter(DocumentChunk.topic_id == topic.id).limit(10).all()

    # Get distinct source document filenames
    doc_ids = list(set([c.document_id for c in chunks]))
    docs = db.query(Document).filter(Document.id.in_(doc_ids)).all() if doc_ids else []
    doc_names = [d.original_filename for d in docs]

    chunk_outs = [
        DocumentChunkOut(
            id=c.id,
            chunk_index=c.chunk_index,
            text_content=c.text_content,
            page_number=c.page_number,
            word_count=c.word_count,
            topic_id=c.topic_id,
        )
        for c in chunks
    ]

    return TopicRelatedContentOut(
        topic_id=topic.id,
        label=topic.label,
        representative_chunks=chunk_outs,
        contributing_documents=doc_names,
    )
