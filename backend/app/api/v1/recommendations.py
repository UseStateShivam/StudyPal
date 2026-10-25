"""Recommendations API router: ranked personalised revision plans linked directly to course notes."""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Course, Topic, LearnerTopicState, DocumentChunk, Document, QuizAttempt, User
from app.schemas import RecommendationResponse, RecommendationItem, SearchResultItem
from app.dependencies import get_user_course, get_current_user
from app.ml.recommender.engine import recommendation_engine
from app.ml.learner.weakness_predictor import weakness_predictor, extract_attempt_features
from app.config import settings

router = APIRouter(tags=["Recommendations"])


@router.get("/courses/{course_id}/recommendations", response_model=RecommendationResponse)
def get_study_recommendations(
    course: Course = Depends(get_user_course),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Generate ranked revision suggestions for a course.
    Combines BKT mastery, weakness classifier predictions, and practice recency.
    Gracefully identifies cold-start state when no quiz history is present.
    """
    topics = db.query(Topic).filter(Topic.course_id == course.id).all()
    if not topics:
        return RecommendationResponse(
            course_id=course.id,
            is_cold_start=True,
            recommendation_mode="content-based",
            recommendations=[],
        )

    states = db.query(LearnerTopicState).filter(
        LearnerTopicState.course_id == course.id,
        LearnerTopicState.user_id == current_user.id
    ).all()
    state_map = {
        s.topic_id: {
            "mastery_probability": s.mastery_probability,
            "last_practiced_at": s.last_practiced_at,
            "total_attempts": s.total_attempts,
            "recent_incorrect_count": s.recent_incorrect_count,
            "current_streak": s.current_streak,
        }
        for s in states
    }

    # Retrieve all student attempts for this course to construct leak-free weakness features
    all_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.course_id == course.id,
        QuizAttempt.user_id == current_user.id
    ).order_by(QuizAttempt.attempted_at.asc()).all()

    is_cold_start = (len(all_attempts) == 0)

    # Compute weakness prediction per topic
    weakness_predictions: Dict[str, Any] = {}
    for t in topics:
        topic_attempts = [
            {
                "is_correct": a.is_correct,
                "attempted_at_ts": a.attempted_at.timestamp() if a.attempted_at else 0.0
            }
            for a in all_attempts if a.topic_id == t.id
        ]
        topic_state = state_map.get(t.id)
        current_m = topic_state["mastery_probability"] if topic_state else settings.BKT_P_L0
        features = extract_attempt_features(
            topic_attempts,
            current_mastery=current_m
        )
        prob, explanation = weakness_predictor.predict_weakness_prob(features)
        weakness_predictions[t.id] = (prob, explanation)

    topic_dicts = [{"id": t.id, "label": t.label} for t in topics]
    ranked = recommendation_engine.rank_revision_topics(
        topics=topic_dicts,
        learner_states=state_map,
        weakness_predictions=weakness_predictions,
    )

    # Attach supporting note passages for each recommended topic
    recommendation_items = []
    for item in ranked:
        t_id = item["topic_id"]
        # Find chunks tagged to this topic
        topic_chunks = db.query(DocumentChunk).filter(DocumentChunk.topic_id == t_id).limit(3).all()

        passages = []
        for c in topic_chunks:
            doc = db.query(Document).filter(Document.id == c.document_id).first()
            passages.append(
                SearchResultItem(
                    chunk_id=c.id,
                    document_id=c.document_id,
                    document_title=doc.original_filename if doc else "Course Document",
                    passage=c.text_content[:300] + ("..." if len(c.text_content) > 300 else ""),
                    page_number=c.page_number,
                    similarity_score=1.0,
                    retrieval_method="topic_membership",
                    topic_label=item["topic_label"],
                )
            )

        recommendation_items.append(
            RecommendationItem(
                topic_id=item["topic_id"],
                topic_label=item["topic_label"],
                priority_rank=item["priority_rank"],
                revision_score=item["revision_score"],
                mastery_probability=item["mastery_probability"],
                weakness_probability=item["weakness_probability"],
                has_attempted_quizzes=item["has_attempted_quizzes"],
                primary_reason=item["primary_reason"],
                recommended_action=item["recommended_action"],
                suggested_passages=passages,
                contributing_scores=item["contributing_scores"],
            )
        )

    return RecommendationResponse(
        course_id=course.id,
        is_cold_start=is_cold_start,
        recommendation_mode="content-based" if is_cold_start else "personalised-learner",
        recommendations=recommendation_items,
    )
