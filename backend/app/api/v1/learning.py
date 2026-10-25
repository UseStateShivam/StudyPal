"""Learning and Progress API router: mastery overviews, time-series progress data, and topic history."""

import json
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Course, LearnerTopicState, QuizAttempt, Topic, User
from app.schemas import CourseProgressOverview, LearnerTopicStateOut
from app.dependencies import get_current_user, get_user_course
from app.core.exceptions import EntityNotFoundException, ForbiddenCourseAccessException

router = APIRouter(tags=["Learning & Progress"])


@router.get("/courses/{course_id}/progress", response_model=CourseProgressOverview)
def get_course_progress(
    course: Course = Depends(get_user_course),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Retrieve comprehensive learning analytics and real Bayesian mastery progression for a course.
    Honest reporting: returns empty trends when student has no attempts, never fake data.
    """
    topics = db.query(Topic).filter(Topic.course_id == course.id).all()
    states = db.query(LearnerTopicState).filter(
        LearnerTopicState.course_id == course.id,
        LearnerTopicState.user_id == current_user.id
    ).all()
    state_by_topic = {s.topic_id: s for s in states}

    topic_states_out = []
    total_mastery_sum = 0.0
    topics_with_state = 0

    mastery_timeline: List[Dict[str, Any]] = []

    for t in topics:
        s = state_by_topic.get(t.id)
        if s:
            mastery_val = s.mastery_probability
            total_mastery_sum += mastery_val
            topics_with_state += 1
            topic_states_out.append(
                LearnerTopicStateOut(
                    topic_id=t.id,
                    topic_label=t.label,
                    mastery_probability=round(mastery_val, 4),
                    total_attempts=s.total_attempts,
                    correct_attempts=s.correct_attempts,
                    last_practiced_at=s.last_practiced_at,
                )
            )
            # Collect points for timeline
            try:
                hist = json.loads(s.history_json)
                for pt in hist:
                    mastery_timeline.append({
                        "timestamp": pt.get("timestamp"),
                        "topic_label": t.label,
                        "mastery": pt.get("mastery"),
                        "is_correct": pt.get("is_correct"),
                    })
            except Exception:
                pass
        else:
            # Topic not yet practiced
            topic_states_out.append(
                LearnerTopicStateOut(
                    topic_id=t.id,
                    topic_label=t.label,
                    mastery_probability=0.20,
                    total_attempts=0,
                    correct_attempts=0,
                    last_practiced_at=None,
                )
            )

    # Sort timeline chronologically
    mastery_timeline.sort(key=lambda x: x.get("timestamp") or "")

    # Aggregate quiz attempts
    attempts = db.query(QuizAttempt).filter(
        QuizAttempt.course_id == course.id,
        QuizAttempt.user_id == current_user.id
    ).all()

    total_attempts = len(attempts)
    correct_attempts = sum(1 for a in attempts if a.is_correct)
    overall_accuracy = (correct_attempts / total_attempts * 100.0) if total_attempts > 0 else 0.0
    overall_mastery = (total_mastery_sum / topics_with_state) if topics_with_state > 0 else 0.20

    return CourseProgressOverview(
        course_id=course.id,
        overall_mastery=round(overall_mastery, 4),
        total_quizzes_taken=db.query(QuizAttempt.session_id).filter(
            QuizAttempt.course_id == course.id,
            QuizAttempt.user_id == current_user.id
        ).distinct().count(),
        total_questions_answered=total_attempts,
        overall_accuracy=round(overall_accuracy, 2),
        topics_state=topic_states_out,
        mastery_timeline=mastery_timeline,
    )


@router.get("/topics/{topic_id}/mastery-history")
def get_topic_mastery_history(
    topic_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get the granular BKT mastery progression for a single topic."""
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if not topic:
        raise EntityNotFoundException("Topic", topic_id)
    course = db.query(Course).filter(Course.id == topic.course_id, Course.owner_id == current_user.id).first()
    if not course:
        raise ForbiddenCourseAccessException(topic.course_id)

    state = db.query(LearnerTopicState).filter(
        LearnerTopicState.topic_id == topic_id,
        LearnerTopicState.user_id == current_user.id
    ).first()

    if not state:
        return {"topic_id": topic_id, "label": topic.label, "history": []}

    try:
        hist = json.loads(state.history_json)
    except Exception:
        hist = []

    return {
        "topic_id": topic_id,
        "label": topic.label,
        "current_mastery": round(state.mastery_probability, 4),
        "total_attempts": state.total_attempts,
        "correct_attempts": state.correct_attempts,
        "history": hist,
    }
