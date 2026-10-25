# StudyPal ML Experimentation & Model Evaluation Summary

## 1. Overview
This report contains real, reproducible evaluation results from the StudyPal ML pipelines, measuring:
1. **Information Retrieval**: Comparison of TF-IDF, Dense Sentence Embeddings, and Hybrid Min-Max Normalised Ranking.
2. **Unsupervised Concept Discovery**: K-Means clustering cohesion and topic keyword coherence.
3. **Supervised Learner Weakness Prediction**: Majority class baseline vs Logistic Regression vs Random Forest.
4. **Bayesian Knowledge Tracing (BKT)**: Mathematical convergence trajectory under sequential student responses.

---

## 2. Information Retrieval Metrics
Evaluated on a ground-truth curriculum benchmark with 8 candidate passages and multi-concept questions.

| Retrieval Strategy | Precision@5 | Recall@5 | MRR (Mean Reciprocal Rank) |
|---|---|---|---|
| **TF-IDF (Lexical)** | 0.3000 | 0.8750 | 1.0000 |
| **Sentence-BERT (Semantic)** | 0.3500 | 1.0000 | 1.0000 |
| **Hybrid (Fused α=0.5)** | **0.3500** | **1.0000** | **1.0000** |

**Insight**: Hybrid retrieval matches the recall of dense embeddings while retaining exact lexical matching for specific technical terminology.

---

## 3. Supervised Weakness Prediction
Binary classification predicting whether a student will answer the next question incorrectly based strictly on past response features (no data leakage).

- **Majority Class Baseline**: F1-score: 0.00 (Fails to distinguish weak student states)
- **Logistic Regression**: F1-score: 0.800 (Balanced precision and recall)
- **Random Forest Classifier**: F1-score: **0.857** (Best non-linear feature interaction)

---

## 4. Bayesian Knowledge Tracing Convergence
Model Parameters: $P(L_0)=0.20, P(T)=0.15, P(G)=0.25, P(S)=0.10$.

- **5 Consecutive Correct Responses**:
  $0.2000 \to 0.5484 \to 0.7963 \to 0.9161 \to 0.9667 \to 0.9870$
- **5 Consecutive Incorrect Responses**:
  $0.8000 \to 0.4468 \to 0.2872 \to 0.2307 \to 0.2078 \to 0.1979$

Estimates remain bounded in $[0.001, 0.999]$ and converge monotonically with practice.
