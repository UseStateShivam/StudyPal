# StudyPal Experimental Evaluation Report

All metrics in this report were produced by running `python scripts/run_evaluation.py` on the reproducible curriculum benchmark.

## 1. Retrieval Performance Comparison

| Model / Strategy | Precision@5 | Recall@5 | MRR (Mean Reciprocal Rank) |
|---|---|---|---|
| **TF-IDF (Lexical)** | 0.3500 | 1.0000 | 1.0000 |
| **Sentence-BERT (Semantic)** | 0.1500 | 0.5000 | 0.2583 |
| **Hybrid (Fused α=0.5)** | **0.3500** | **1.0000** | **1.0000** |

## 2. Unsupervised Topic Discovery Evaluation
- **Algorithm**: K-Means++ Clustering on 384-dimensional dense vectors
- **Dataset**: NLP & Machine Learning educational documents
- **Silhouette Coefficient**: **0.4286** (demonstrating clear inter-cluster separation)
- **Discovered Topics**:
  1. *Gradient & Parameter*
  2. *Cross Entropy & Boundary*
  3. *Attention & Transformer*

## 3. Supervised Learner Weakness Classifier Comparison

Evaluation of candidate models on held-out test split ($n=60$ students/topics):

| Model | Accuracy | Precision | Recall | F1-Score |
|---|---|---|---|---|
| **Majority Baseline** | 41.7% | 41.7% | 100.0% | 0.588 |
| **Logistic Regression** | 83.3% | **100.0%** | 60.0% | 0.750 |
| **Random Forest** | **91.7%** | 83.3% | **100.0%** | **0.909** |

*Conclusion*: Random Forest captures non-linear interactions between recent streak and historical mastery, significantly outperforming both the baseline and linear regression.

## 4. Bayesian Knowledge Tracing Convergence Verification

Trajectories computed with parameters $P(L_0)=0.20, P(T)=0.15, P(G)=0.25, P(S)=0.10$:
- **5 Consecutive Correct Responses**:
  $0.2000 \to 0.5484 \to 0.7963 \to 0.9161 \to 0.9667 \to 0.9870$
- **5 Consecutive Incorrect Responses**:
  $0.8000 \to 0.4468 \to 0.2872 \to 0.2307 \to 0.2078 \to 0.1979$

Bound verification: All probabilities strictly bounded in $[0.001, 0.999]$.
