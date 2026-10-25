"""StudyPal SQLAlchemy Database Models.

Entities:
- User
- Course
- Document
- DocumentChunk
- Topic
- QuizQuestion
- QuizSession
- QuizAttempt
- LearnerTopicState
- ModelMetadata
"""

import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    Column,
    String,
    Text,
    Integer,
    Float,
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship
from app.db.session import Base


def generate_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    display_name = Column(String(100), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    courses = relationship("Course", back_populates="owner", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="user", cascade="all, delete-orphan")
    learner_states = relationship("LearnerTopicState", back_populates="user", cascade="all, delete-orphan")
    quiz_sessions = relationship("QuizSession", back_populates="user", cascade="all, delete-orphan")


class Course(Base):
    __tablename__ = "courses"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    owner_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    owner = relationship("User", back_populates="courses")
    documents = relationship("Document", back_populates="course", cascade="all, delete-orphan")
    document_chunks = relationship("DocumentChunk", back_populates="course", cascade="all, delete-orphan")
    topics = relationship("Topic", back_populates="course", cascade="all, delete-orphan")
    quiz_questions = relationship("QuizQuestion", back_populates="course", cascade="all, delete-orphan")
    quiz_attempts = relationship("QuizAttempt", back_populates="course", cascade="all, delete-orphan")
    learner_states = relationship("LearnerTopicState", back_populates="course", cascade="all, delete-orphan")
    quiz_sessions = relationship("QuizSession", back_populates="course", cascade="all, delete-orphan")


class Document(Base):
    __tablename__ = "documents"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    course_id = Column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    original_filename = Column(String(255), nullable=False)
    storage_identifier = Column(String(255), nullable=False, unique=True)
    file_type = Column(String(20), nullable=False)  # pdf, txt
    file_size_bytes = Column(Integer, nullable=False)
    content_checksum = Column(String(64), nullable=False)  # sha256
    processing_status = Column(String(20), default="pending", nullable=False)  # pending, processing, completed, failed
    error_message = Column(Text, nullable=True)
    total_pages = Column(Integer, nullable=True)
    chunk_count = Column(Integer, default=0, nullable=False)
    pipeline_version = Column(String(50), default="v1.0", nullable=False)
    uploaded_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    course = relationship("Course", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_documents_course_checksum", "course_id", "content_checksum"),
    )


class Topic(Base):
    __tablename__ = "topics"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    course_id = Column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    cluster_index = Column(Integer, nullable=False)
    label = Column(String(100), nullable=False)
    is_custom_label = Column(Boolean, default=False, nullable=False)
    keywords = Column(Text, nullable=True)  # JSON or comma-separated top terms
    summary = Column(Text, nullable=True)
    chunk_count = Column(Integer, default=0, nullable=False)
    model_version = Column(String(50), default="kmeans_v1", nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="topics")
    chunks = relationship("DocumentChunk", back_populates="topic")
    quiz_questions = relationship("QuizQuestion", back_populates="topic", cascade="all, delete-orphan")
    learner_states = relationship("LearnerTopicState", back_populates="topic", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    document_id = Column(String(36), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="SET NULL"), nullable=True, index=True)
    chunk_index = Column(Integer, nullable=False)
    text_content = Column(Text, nullable=False)
    word_count = Column(Integer, nullable=False)
    page_number = Column(Integer, nullable=True)
    start_char = Column(Integer, nullable=True)
    end_char = Column(Integer, nullable=True)
    embedding_vector = Column(Text, nullable=True)  # Serialised JSON array of floats for exact CPU cosine
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    document = relationship("Document", back_populates="chunks")
    course = relationship("Course", back_populates="document_chunks")
    topic = relationship("Topic", back_populates="chunks")

    __table_args__ = (
        Index("ix_chunks_course_topic", "course_id", "topic_id"),
    )


class QuizQuestion(Base):
    __tablename__ = "quiz_questions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    course_id = Column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    question_text = Column(Text, nullable=False)
    options_json = Column(Text, nullable=False)  # JSON array of strings e.g. ["A", "B", "C", "D"]
    correct_option_index = Column(Integer, nullable=False)
    explanation = Column(Text, nullable=True)
    difficulty = Column(String(20), default="medium", nullable=False)  # easy, medium, hard
    provenance = Column(String(50), default="curated", nullable=False)  # curated, imported, synthetic
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    course = relationship("Course", back_populates="quiz_questions")
    topic = relationship("Topic", back_populates="quiz_questions")
    attempts = relationship("QuizAttempt", back_populates="question")


class QuizSession(Base):
    __tablename__ = "quiz_sessions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=True)  # Null if mixed
    is_completed = Column(Boolean, default=False, nullable=False)
    total_questions = Column(Integer, default=0, nullable=False)
    correct_answers = Column(Integer, default=0, nullable=False)
    question_ids_json = Column(Text, nullable=False)  # JSON array of question IDs in this session
    started_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="quiz_sessions")
    course = relationship("Course", back_populates="quiz_sessions")
    attempts = relationship("QuizAttempt", back_populates="session", cascade="all, delete-orphan")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(String(36), ForeignKey("quiz_sessions.id", ondelete="CASCADE"), nullable=True, index=True)
    question_id = Column(String(36), ForeignKey("quiz_questions.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    selected_option_index = Column(Integer, nullable=False)
    is_correct = Column(Boolean, nullable=False)
    response_time_ms = Column(Integer, nullable=True)
    attempted_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)

    # Relationships
    user = relationship("User", back_populates="quiz_attempts")
    course = relationship("Course", back_populates="quiz_attempts")
    session = relationship("QuizSession", back_populates="attempts")
    question = relationship("QuizQuestion", back_populates="attempts")

    __table_args__ = (
        Index("ix_quiz_attempts_user_topic", "user_id", "topic_id", "attempted_at"),
    )


class LearnerTopicState(Base):
    __tablename__ = "learner_topic_states"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)
    topic_id = Column(String(36), ForeignKey("topics.id", ondelete="CASCADE"), nullable=False, index=True)
    mastery_probability = Column(Float, default=0.20, nullable=False)
    total_attempts = Column(Integer, default=0, nullable=False)
    correct_attempts = Column(Integer, default=0, nullable=False)
    recent_incorrect_count = Column(Integer, default=0, nullable=False)
    current_streak = Column(Integer, default=0, nullable=False)
    last_practiced_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now, nullable=False)
    history_json = Column(Text, default="[]", nullable=False)  # JSON array of {timestamp, mastery, is_correct}

    # Relationships
    user = relationship("User", back_populates="learner_states")
    course = relationship("Course", back_populates="learner_states")
    topic = relationship("Topic", back_populates="learner_states")

    __table_args__ = (
        UniqueConstraint("user_id", "course_id", "topic_id", name="uq_user_course_topic_state"),
    )


class ModelMetadata(Base):
    __tablename__ = "model_metadata"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    course_id = Column(String(36), ForeignKey("courses.id", ondelete="CASCADE"), nullable=True, index=True)
    model_type = Column(String(50), nullable=False)  # kmeans, tfidf, weakness_classifier, bkt
    model_version = Column(String(50), nullable=False)
    hyperparameters_json = Column(Text, nullable=True)
    metrics_json = Column(Text, nullable=True)
    artifact_path = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    trained_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
