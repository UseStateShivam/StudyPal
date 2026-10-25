"""Quizzes API router: sessions, curated question banks, answer submissions, and BKT updates."""

import json
import random
from datetime import datetime, timezone
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import (
    Course,
    QuizQuestion,
    QuizSession,
    QuizAttempt,
    LearnerTopicState,
    User,
    Topic,
)
from app.schemas import (
    QuizQuestionOut,
    QuizSessionCreate,
    QuizSessionOut,
    QuizAnswerSubmit,
    QuizAnswerResult,
    QuizSessionCompleteResult,
)
from app.dependencies import get_current_user, get_user_course
from app.core.exceptions import EntityNotFoundException, StudyPalException
from app.ml.learner.bkt import bkt_engine
from app.logging_config import logger

router = APIRouter(tags=["Quizzes"])


@router.get("/courses/{course_id}/quizzes", response_model=List[QuizQuestionOut])
def list_course_quiz_questions(
    course: Course = Depends(get_user_course),
    db: Session = Depends(get_db),
):
    """List available quiz questions for this course without exposing correct answers."""
    questions = db.query(QuizQuestion).filter(
        QuizQuestion.course_id == course.id,
        QuizQuestion.is_active == True
    ).all()
    results = []
    for q in questions:
        try:
            opts = json.loads(q.options_json)
        except Exception:
            opts = []
        results.append(
            QuizQuestionOut(
                id=q.id,
                topic_id=q.topic_id,
                question_text=q.question_text,
                options=opts,
                difficulty=q.difficulty,
                provenance=q.provenance,
            )
        )
    return results


@router.post("/courses/{course_id}/quizzes/sessions", response_model=QuizSessionOut, status_code=status.HTTP_201_CREATED)
def start_quiz_session(
    session_in: QuizSessionCreate,
    course: Course = Depends(get_user_course),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Initiate a new quiz practice session.
    Randomly selects questions without replacement from stored question bank for this course/topic.
    """
    query = db.query(QuizQuestion).filter(
        QuizQuestion.course_id == course.id,
        QuizQuestion.is_active == True
    )
    if session_in.topic_id:
        query = query.filter(QuizQuestion.topic_id == session_in.topic_id)

    available = query.all()
    if not available:
        raise StudyPalException(
            status_code=status.HTTP_404_NOT_FOUND,
            code="NO_QUIZ_QUESTIONS",
            message="No active quiz questions found for this course/topic. Seed or import questions first.",
        )

    # Random selection without replacement
    sample_size = min(len(available), session_in.question_count)
    selected_questions = random.sample(available, sample_size)
    q_ids = [q.id for q in selected_questions]

    new_session = QuizSession(
        user_id=current_user.id,
        course_id=course.id,
        topic_id=session_in.topic_id,
        is_completed=False,
        total_questions=len(q_ids),
        correct_answers=0,
        question_ids_json=json.dumps(q_ids),
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    # Return question list without correct answers
    q_outs = []
    for q in selected_questions:
        try:
            opts = json.loads(q.options_json)
        except Exception:
            opts = []
        q_outs.append(
            QuizQuestionOut(
                id=q.id,
                topic_id=q.topic_id,
                question_text=q.question_text,
                options=opts,
                difficulty=q.difficulty,
                provenance=q.provenance,
            )
        )

    return QuizSessionOut(
        session_id=new_session.id,
        course_id=course.id,
        topic_id=new_session.topic_id,
        total_questions=len(q_outs),
        questions=q_outs,
    )


@router.post("/quiz-sessions/{session_id}/answers", response_model=QuizAnswerResult)
def submit_quiz_answer(
    session_id: str,
    answer_in: QuizAnswerSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Submit an answer for a question within an active quiz session.
    Server evaluates correctness, records immutable attempt, and dynamically updates Bayesian Knowledge Tracing.
    """
    session = db.query(QuizSession).filter(
        QuizSession.id == session_id,
        QuizSession.user_id == current_user.id
    ).first()
    if not session:
        raise EntityNotFoundException("QuizSession", session_id)

    question = db.query(QuizQuestion).filter(QuizQuestion.id == answer_in.question_id).first()
    if not question:
        raise EntityNotFoundException("QuizQuestion", answer_in.question_id)

    # Verify correctness on server (never trust browser)
    is_correct = (answer_in.selected_option_index == question.correct_option_index)

    # Record immutable attempt
    attempt = QuizAttempt(
        user_id=current_user.id,
        course_id=session.course_id,
        session_id=session.id,
        question_id=question.id,
        topic_id=question.topic_id,
        selected_option_index=answer_in.selected_option_index,
        is_correct=is_correct,
        response_time_ms=answer_in.response_time_ms,
    )
    db.add(attempt)

    # Update session tally
    if is_correct:
        session.correct_answers += 1

    # Update Bayesian Knowledge Tracing State for this User / Topic
    state = db.query(LearnerTopicState).filter(
        LearnerTopicState.user_id == current_user.id,
        LearnerTopicState.course_id == session.course_id,
        LearnerTopicState.topic_id == question.topic_id,
    ).first()

    now = datetime.now(timezone.utc)
    if not state:
        state = LearnerTopicState(
            user_id=current_user.id,
            course_id=session.course_id,
            topic_id=question.topic_id,
            mastery_probability=bkt_engine.p_l0,
            total_attempts=0,
            correct_attempts=0,
            recent_incorrect_count=0,
            current_streak=0,
            last_practiced_at=now,
            history_json="[]",
        )
        db.add(state)
        db.flush()

    # Apply BKT update equations
    prior_m = state.mastery_probability
    next_m = bkt_engine.compute_next_mastery(prior_m, is_correct)
    state.mastery_probability = next_m
    state.total_attempts += 1
    if is_correct:
        state.correct_attempts += 1
        state.recent_incorrect_count = max(0, state.recent_incorrect_count - 1)
        state.current_streak = state.current_streak + 1 if state.current_streak >= 0 else 1
    else:
        state.recent_incorrect_count += 1
        state.current_streak = state.current_streak - 1 if state.current_streak <= 0 else -1

    state.last_practiced_at = now

    # Append to timeline history
    try:
        history = json.loads(state.history_json)
    except Exception:
        history = []
    history.append({
        "timestamp": now.isoformat(),
        "is_correct": is_correct,
        "mastery": round(next_m, 4),
    })
    state.history_json = json.dumps(history[-50:])  # Keep last 50 data points

    db.commit()

    feedback = "Correct! Great job." if is_correct else "Incorrect. Review the explanation and source passage."
    return QuizAnswerResult(
        question_id=question.id,
        selected_option_index=answer_in.selected_option_index,
        correct_option_index=question.correct_option_index,
        is_correct=is_correct,
        explanation=question.explanation,
        updated_mastery_probability=round(next_m, 4),
        feedback=feedback,
    )


@router.post("/quiz-sessions/{session_id}/submit", response_model=QuizSessionCompleteResult)
def complete_quiz_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Finalize a quiz session and return score summary and updated mastery levels."""
    session = db.query(QuizSession).filter(
        QuizSession.id == session_id,
        QuizSession.user_id == current_user.id
    ).first()
    if not session:
        raise EntityNotFoundException("QuizSession", session_id)

    session.is_completed = True
    session.completed_at = datetime.now(timezone.utc)
    db.commit()

    score_pct = (session.correct_answers / session.total_questions * 100.0) if session.total_questions > 0 else 0.0

    # Retrieve all updated learner states for this course
    states = db.query(LearnerTopicState).filter(
        LearnerTopicState.user_id == current_user.id,
        LearnerTopicState.course_id == session.course_id,
    ).all()
    topic_map = {s.topic_id: round(s.mastery_probability, 4) for s in states}

    return QuizSessionCompleteResult(
        session_id=session.id,
        total_questions=session.total_questions,
        correct_answers=session.correct_answers,
        score_percentage=round(score_pct, 2),
        topic_mastery_updates=topic_map,
    )
