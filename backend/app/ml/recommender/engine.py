"""Study recommendation engine combining BKT mastery, weakness classifier predictions, and practice recency.

Revision Scoring Formula:
  recency_factor = min(1.0, hours_since_practice / 72.0)
  revision_score = w_m * (1.0 - mastery) + w_w * weakness_prob + w_r * recency_factor

Cold-start Handling:
- For learners with 0 completed quizzes, recommendations are marked as 'content-based' (cold-start)
  with prior assumptions clearly identified.
- After quiz attempts, personalised learner-state rankings are calculated with traceable explanations.
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from app.config import settings
from app.logging_config import logger


class RecommendationEngine:
    def __init__(
        self,
        weight_mastery: float = settings.REC_WEIGHT_MASTERY,
        weight_weakness: float = settings.REC_WEIGHT_WEAKNESS,
        weight_recency: float = settings.REC_WEIGHT_RECENCY,
    ):
        self.w_m = weight_mastery
        self.w_w = weight_weakness
        self.w_r = weight_recency

    def rank_revision_topics(
        self,
        topics: List[Dict[str, Any]],
        learner_states: Dict[str, Dict[str, Any]],
        weakness_predictions: Dict[str, Tuple[Optional[float], str]],
    ) -> List[Dict[str, Any]]:
        """
        Rank course topics by revision priority.
        topics: list of {"id": str, "label": str, ...}
        learner_states: map of topic_id -> {"mastery_probability": float, "last_practiced_at": datetime, "total_attempts": int}
        weakness_predictions: map of topic_id -> (weakness_prob, explanation_str)
        """
        scored_topics = []
        now = datetime.now(timezone.utc)

        for topic in topics:
            t_id = topic["id"]
            state = learner_states.get(t_id)

            if state and state.get("total_attempts", 0) > 0:
                has_history = True
                mastery = float(state.get("mastery_probability", settings.BKT_P_L0))
                last_practiced = state.get("last_practiced_at")

                if last_practiced:
                    if last_practiced.tzinfo is None:
                        last_practiced = last_practiced.replace(tzinfo=timezone.utc)
                    delta_hours = max(0.0, (now - last_practiced).total_seconds() / 3600.0)
                else:
                    delta_hours = 72.0

                recency_factor = min(1.0, delta_hours / 72.0)
                weakness_info = weakness_predictions.get(t_id, (None, "no_prediction"))
                weakness_prob = weakness_info[0] if weakness_info[0] is not None else (1.0 - mastery)

                # Score fusion
                revision_score = (
                    self.w_m * (1.0 - mastery)
                    + self.w_w * weakness_prob
                    + self.w_r * recency_factor
                )

                # Explainability logic
                reasons = []
                if mastery < 0.4:
                    reasons.append("Mastery estimate is currently low.")
                elif weakness_prob > 0.5:
                    reasons.append("Recent quiz performance indicates difficulty with this topic.")
                if recency_factor > 0.7:
                    reasons.append("This topic has not been reviewed recently.")
                if not reasons:
                    reasons.append("Scheduled for refresher practice to maintain mastery.")

                primary_reason = " ".join(reasons)
                action = "Review note passages and retake topic quiz"

            else:
                has_history = False
                mastery = settings.BKT_P_L0
                weakness_prob = None
                recency_factor = 1.0
                revision_score = 0.5  # Neutral baseline priority for unattempted topics
                primary_reason = "You have not completed a quiz for this topic yet."
                action = "Start with a 5-question diagnostic quiz"

            scored_topics.append({
                "topic_id": t_id,
                "topic_label": topic["label"],
                "revision_score": round(float(revision_score), 4),
                "mastery_probability": round(float(mastery), 4),
                "weakness_probability": round(float(weakness_prob), 4) if weakness_prob is not None else None,
                "has_attempted_quizzes": has_history,
                "primary_reason": primary_reason,
                "recommended_action": action,
                "contributing_scores": {
                    "mastery_weight_contrib": round(self.w_m * (1.0 - mastery), 4),
                    "weakness_weight_contrib": round(self.w_w * (weakness_prob or 0.0), 4),
                    "recency_weight_contrib": round(self.w_r * recency_factor, 4),
                }
            })

        # Sort descending by revision priority score
        scored_topics.sort(key=lambda x: x["revision_score"], reverse=True)

        for rank, item in enumerate(scored_topics, 1):
            item["priority_rank"] = rank

        return scored_topics


recommendation_engine = RecommendationEngine()
