"""Supervised student weakness prediction pipeline.

Target: will_answer_next_question_incorrectly (binary classification: 1 for incorrect, 0 for correct).
Models compared:
1. Majority Class Baseline
2. Logistic Regression
3. Random Forest Classifier
Safeguards:
- Explicit feature extraction using historical features strictly prior to attempt (no target leakage).
- Minimum samples threshold check before fitting/inference.
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import joblib
from pathlib import Path
from app.config import settings
from app.logging_config import logger


FEATURE_NAMES = [
    "recent_accuracy",
    "total_attempts",
    "recent_incorrect_count",
    "current_streak",
    "time_since_last_sec",
    "prior_mastery",
]


def extract_attempt_features(
    history_attempts: List[Dict[str, Any]],
    current_attempt_time: Optional[float] = None,
    current_mastery: float = 0.20,
) -> Dict[str, float]:
    """
    Extract features from strictly past attempts prior to the current target attempt.
    Prevents any future data leakage.
    """
    if not history_attempts:
        return {
            "recent_accuracy": 0.5,
            "total_attempts": 0.0,
            "recent_incorrect_count": 0.0,
            "current_streak": 0.0,
            "time_since_last_sec": 3600.0,
            "prior_mastery": float(current_mastery),
        }

    total = len(history_attempts)
    correct_count = sum(1 for a in history_attempts if a["is_correct"])
    recent = history_attempts[-5:]
    recent_correct = sum(1 for a in recent if a["is_correct"])
    recent_accuracy = recent_correct / len(recent) if recent else 0.5
    recent_incorrect = sum(1 for a in recent if not a["is_correct"])

    # Current streak (positive for correct, negative for incorrect)
    streak = 0
    for a in reversed(history_attempts):
        if a["is_correct"]:
            if streak >= 0:
                streak += 1
            else:
                break
        else:
            if streak <= 0:
                streak -= 1
            else:
                break

    time_since_sec = 3600.0
    if current_attempt_time and "attempted_at_ts" in history_attempts[-1]:
        diff = current_attempt_time - history_attempts[-1]["attempted_at_ts"]
        time_since_sec = max(0.0, diff)

    return {
        "recent_accuracy": float(recent_accuracy),
        "total_attempts": float(total),
        "recent_incorrect_count": float(recent_incorrect),
        "current_streak": float(streak),
        "time_since_last_sec": float(time_since_sec),
        "prior_mastery": float(current_mastery),
    }


class WeaknessPredictor:
    def __init__(self, model_dir: Optional[Path] = None):
        self.model_dir = model_dir or settings.get_model_cache_path()
        self.model: Optional[Any] = None
        self.model_type: Optional[str] = None
        self.is_fitted = False
        self.metrics: Dict[str, Any] = {}

    def fit_and_compare(
        self,
        X: np.ndarray,
        y: np.ndarray,
        test_size: float = 0.2,
        random_state: int = 42,
    ) -> Dict[str, Any]:
        """
        Fit baseline, logistic regression, and random forest models.
        Selects best performer based on F1-score for predicting weakness (incorrect response).
        """
        n_samples = len(y)
        if n_samples < settings.MIN_SAMPLES_FOR_TRAINING:
            logger.warning(
                f"Insufficient data for weakness classifier training: {n_samples} < {settings.MIN_SAMPLES_FOR_TRAINING}"
            )
            return {"status": "insufficient_data", "n_samples": n_samples}

        # Temporal/sequential split or simple stratified split
        split_idx = int(n_samples * (1.0 - test_size))
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]

        if len(np.unique(y_train)) < 2:
            return {"status": "single_class_in_train", "n_samples": n_samples}

        candidates = {
            "baseline_majority": DummyClassifier(strategy="most_frequent"),
            "logistic_regression": LogisticRegression(random_state=random_state, max_iter=200),
            "random_forest": RandomForestClassifier(n_estimators=30, max_depth=4, random_state=random_state),
        }

        results = {}
        best_f1 = -1.0
        best_model = None
        best_type = None

        for name, clf in candidates.items():
            clf.fit(X_train, y_train)
            preds = clf.predict(X_test)
            acc = float(accuracy_score(y_test, preds))
            prec = float(precision_score(y_test, preds, zero_division=0))
            rec = float(recall_score(y_test, preds, zero_division=0))
            f1 = float(f1_score(y_test, preds, zero_division=0))

            results[name] = {
                "accuracy": acc,
                "precision": prec,
                "recall": rec,
                "f1": f1,
            }

            if f1 > best_f1:
                best_f1 = f1
                best_model = clf
                best_type = name

        self.model = best_model or candidates["logistic_regression"]
        self.model_type = best_type or "logistic_regression"
        self.is_fitted = True
        self.metrics = results

        # Persist model
        save_path = self.model_dir / "weakness_classifier.joblib"
        joblib.dump({"model": self.model, "type": self.model_type, "metrics": self.metrics}, save_path)
        logger.info(f"Fitted weakness classifier [{self.model_type}] saved to {save_path}")

        return {
            "status": "success",
            "best_model": self.model_type,
            "metrics": self.metrics,
            "n_samples": n_samples,
        }

    def predict_weakness_prob(self, feature_dict: Dict[str, float]) -> Tuple[Optional[float], str]:
        """
        Predict probability of answering incorrectly on next question.
        Returns: (probability, explanation/status)
        """
        if not self.is_fitted or self.model is None:
            # Fallback estimation using prior mastery: 1 - mastery
            prior_m = feature_dict.get("prior_mastery", 0.5)
            fallback_prob = 1.0 - prior_m
            return fallback_prob, "fallback_insufficient_training_history"

        vector = [feature_dict.get(k, 0.0) for k in FEATURE_NAMES]
        X = np.array([vector])

        try:
            if hasattr(self.model, "predict_proba"):
                probs = self.model.predict_proba(X)
                # Probability of class 1 (incorrect)
                prob_incorrect = float(probs[0][1]) if probs.shape[1] > 1 else float(probs[0][0])
            else:
                pred = self.model.predict(X)[0]
                prob_incorrect = 1.0 if pred == 1 else 0.0

            return prob_incorrect, f"trained_model_{self.model_type}"
        except Exception as e:
            logger.error(f"Error predicting weakness probability: {e}")
            prior_m = feature_dict.get("prior_mastery", 0.5)
            return 1.0 - prior_m, "fallback_inference_error"


weakness_predictor = WeaknessPredictor()
