"""Pydantic schemas for request validation and response serialisation."""

from datetime import datetime
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, EmailStr, Field


# ==========================================
# Common / Auth Schemas
# ==========================================

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserOut"


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)
    display_name: str = Field(min_length=2, max_length=100)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: str
    email: str
    display_name: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# Course Schemas
# ==========================================

class CourseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: Optional[str] = None


class CourseUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=200)
    description: Optional[str] = None


class CourseOut(BaseModel):
    id: str
    owner_id: str
    name: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    document_count: Optional[int] = 0
    topic_count: Optional[int] = 0

    class Config:
        from_attributes = True


# ==========================================
# Document Schemas
# ==========================================

class DocumentOut(BaseModel):
    id: str
    course_id: str
    original_filename: str
    file_type: str
    file_size_bytes: int
    processing_status: str
    error_message: Optional[str] = None
    total_pages: Optional[int] = None
    chunk_count: int
    uploaded_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DocumentStatusOut(BaseModel):
    id: str
    processing_status: str
    error_message: Optional[str] = None
    chunk_count: int
    completed_at: Optional[datetime] = None


class DocumentChunkOut(BaseModel):
    id: str
    chunk_index: int
    text_content: str
    page_number: Optional[int] = None
    word_count: int
    topic_id: Optional[str] = None

    class Config:
        from_attributes = True


# ==========================================
# Topic Schemas
# ==========================================

class TopicUpdate(BaseModel):
    label: str = Field(min_length=1, max_length=100)


class TopicOut(BaseModel):
    id: str
    course_id: str
    cluster_index: int
    label: str
    is_custom_label: bool
    keywords: Optional[str] = None
    summary: Optional[str] = None
    chunk_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class TopicRelatedContentOut(BaseModel):
    topic_id: str
    label: str
    representative_chunks: List[DocumentChunkOut]
    contributing_documents: List[str]


# ==========================================
# Search Schemas
# ==========================================

class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    retrieval_method: Optional[str] = "hybrid"  # "tfidf", "embedding", "hybrid"
    top_k: Optional[int] = Field(default=5, ge=1, le=20)


class SearchResultItem(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str
    passage: str
    page_number: Optional[int] = None
    similarity_score: float
    retrieval_method: str
    topic_label: Optional[str] = None


class SearchResponse(BaseModel):
    query: str
    retrieval_method_used: str
    total_results: int
    results: List[SearchResultItem]


# ==========================================
# Quiz Schemas
# ==========================================

class QuizQuestionOut(BaseModel):
    id: str
    topic_id: str
    question_text: str
    options: List[str]
    difficulty: str
    provenance: str

    class Config:
        from_attributes = True


class QuizSessionCreate(BaseModel):
    topic_id: Optional[str] = None  # None for mixed quiz
    question_count: int = Field(default=5, ge=1, le=20)


class QuizSessionOut(BaseModel):
    session_id: str
    course_id: str
    topic_id: Optional[str] = None
    total_questions: int
    questions: List[QuizQuestionOut]


class QuizAnswerSubmit(BaseModel):
    question_id: str
    selected_option_index: int = Field(ge=0, le=5)
    response_time_ms: Optional[int] = None


class QuizAnswerResult(BaseModel):
    question_id: str
    selected_option_index: int
    correct_option_index: int
    is_correct: bool
    explanation: Optional[str] = None
    updated_mastery_probability: float
    feedback: str


class QuizSessionCompleteResult(BaseModel):
    session_id: str
    total_questions: int
    correct_answers: int
    score_percentage: float
    topic_mastery_updates: Dict[str, float]


# ==========================================
# Learner / Progress Schemas
# ==========================================

class LearnerTopicStateOut(BaseModel):
    topic_id: str
    topic_label: str
    mastery_probability: float
    total_attempts: int
    correct_attempts: int
    last_practiced_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CourseProgressOverview(BaseModel):
    course_id: str
    overall_mastery: float
    total_quizzes_taken: int
    total_questions_answered: int
    overall_accuracy: float
    topics_state: List[LearnerTopicStateOut]
    mastery_timeline: List[Dict[str, Any]]


# ==========================================
# Recommendation Schemas
# ==========================================

class RecommendationItem(BaseModel):
    topic_id: str
    topic_label: str
    priority_rank: int
    revision_score: float
    mastery_probability: float
    weakness_probability: Optional[float] = None
    has_attempted_quizzes: bool
    primary_reason: str
    recommended_action: str
    suggested_passages: List[SearchResultItem]
    contributing_scores: Dict[str, float]


class RecommendationResponse(BaseModel):
    course_id: str
    is_cold_start: bool
    recommendation_mode: str  # "content-based" or "personalised-learner"
    recommendations: List[RecommendationItem]
