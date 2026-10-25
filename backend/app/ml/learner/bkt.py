"""Bayesian Knowledge Tracing (BKT) engine for dynamic student mastery estimation.

Standard BKT Formulation:
- P(L0): Prior mastery probability
- P(T): Probability of skill transition / learning after opportunity
- P(G): Probability of guess (correct without knowing)
- P(S): Probability of slip (incorrect despite knowing)

Update equations:
Correct response:
  P(L_t | obs=1) = [P(L_t-1) * (1 - P(S))] / [P(L_t-1) * (1 - P(S)) + (1 - P(L_t-1)) * P(G)]

Incorrect response:
  P(L_t | obs=0) = [P(L_t-1) * P(S)] / [P(L_t-1) * P(S) + (1 - P(L_t-1)) * (1 - P(G))]

Learning transition:
  P(L_t+1) = P(L_t | obs) + (1 - P(L_t | obs)) * P(T)
"""

from typing import Tuple
from app.config import settings


class BayesianKnowledgeTracer:
    def __init__(
        self,
        p_l0: float = settings.BKT_P_L0,
        p_t: float = settings.BKT_P_T,
        p_g: float = settings.BKT_P_G,
        p_s: float = settings.BKT_P_S,
    ):
        self.p_l0 = float(p_l0)
        self.p_t = float(p_t)
        self.p_g = float(p_g)
        self.p_s = float(p_s)
        self._validate_params()

    def _validate_params(self) -> None:
        for name, val in [
            ("P(L0)", self.p_l0),
            ("P(T)", self.p_t),
            ("P(G)", self.p_g),
            ("P(S)", self.p_s),
        ]:
            if not (0.0 <= val <= 1.0):
                raise ValueError(f"BKT parameter {name}={val} must be in [0.0, 1.0]")

    def compute_next_mastery(self, prior_p: float, is_correct: bool) -> float:
        """
        Compute updated mastery probability after a single student response opportunity.
        Includes numerical safeguards against zero-division and clamps result to [0.001, 0.999].
        """
        p = max(0.0001, min(0.9999, float(prior_p)))

        if is_correct:
            # P(obs=1 | know) = 1 - P(S)
            p_know_obs = p * (1.0 - self.p_s)
            # P(obs=1 | ~know) = P(G)
            p_not_know_obs = (1.0 - p) * self.p_g
            denom = p_know_obs + p_not_know_obs
            p_posterior = p_know_obs / denom if denom > 1e-12 else p
        else:
            # P(obs=0 | know) = P(S)
            p_know_obs = p * self.p_s
            # P(obs=0 | ~know) = 1 - P(G)
            p_not_know_obs = (1.0 - p) * (1.0 - self.p_g)
            denom = p_know_obs + p_not_know_obs
            p_posterior = p_know_obs / denom if denom > 1e-12 else p

        # Learning transition after opportunity
        p_next = p_posterior + (1.0 - p_posterior) * self.p_t

        # Bounded probability
        return float(max(0.001, min(0.999, p_next)))


bkt_engine = BayesianKnowledgeTracer()
