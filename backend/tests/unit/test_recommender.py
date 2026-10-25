import pytest
from app.ml.recommender.engine import RecommendationEngine


def test_recommender_ranks_low_mastery_first():
    rec = RecommendationEngine(weight_mastery=0.6, weight_weakness=0.2, weight_recency=0.2)
    topics = [
        {"id": "t1", "label": "Calculus"},
        {"id": "t2", "label": "Linear Algebra"},
    ]
    # Topic 1 has low mastery (0.2), Topic 2 has high mastery (0.85)
    learner_states = {
        "t1": {"mastery_probability": 0.20, "last_practiced_at": None, "total_attempts": 5},
        "t2": {"mastery_probability": 0.85, "last_practiced_at": None, "total_attempts": 5},
    }
    weakness_predictions = {
        "t1": (0.6, "trained_model"),
        "t2": (0.1, "trained_model"),
    }

    ranked = rec.rank_revision_topics(topics, learner_states, weakness_predictions)

    assert len(ranked) == 2
    assert ranked[0]["topic_id"] == "t1"
    assert ranked[0]["priority_rank"] == 1
    assert ranked[0]["revision_score"] > ranked[1]["revision_score"]


def test_recommender_cold_start():
    rec = RecommendationEngine()
    topics = [{"id": "t1", "label": "Operating Systems"}]
    ranked = rec.rank_revision_topics(topics, learner_states={}, weakness_predictions={})

    assert len(ranked) == 1
    assert ranked[0]["has_attempted_quizzes"] is False
    assert "not completed a quiz" in ranked[0]["primary_reason"]
