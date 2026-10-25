# StudyPal Machine Learning Methodology

## 1. Information Retrieval Engine

### TF-IDF Lexical Retrieval
- **Vector Representation**: Chunks are transformed into sparse term-frequency inverse-document-frequency vectors fitted over course materials.
- **Cosine Similarity**:
  $$\text{sim}_{\text{tfidf}}(q, c) = \frac{\mathbf{v}_q \cdot \mathbf{v}_c}{\|\mathbf{v}_q\|_2 \|\mathbf{v}_c\|_2}$$

### Dense Semantic Embedding Retrieval
- **Sentence Encoder**: Compact open-source SentenceTransformer (`all-MiniLM-L6-v2`, 384 dimensions) running locally on CPU.
- **Unit Normalization**: All vectors are unit-normalized upon inference:
  $$\text{sim}_{\text{emb}}(q, c) = \mathbf{e}_q \cdot \mathbf{e}_c$$

### Hybrid Score Normalization and Fusion
Raw cosine similarities from TF-IDF and dense embeddings exhibit different distributions. StudyPal implements dynamic min-max normalization:
$$\text{norm}(s) = \frac{s - \min(s)}{\max(s) - \min(s) + \epsilon}$$
$$\text{score}_{\text{hybrid}} = \alpha \cdot \text{norm}(\text{sim}_{\text{tfidf}}) + (1 - \alpha) \cdot \text{norm}(\text{sim}_{\text{emb}})$$
Default weight: $\alpha = 0.50$.

---

## 2. Unsupervised Topic Discovery

- **Algorithm**: K-Means clustering with K-Means++ initial seed selection.
- **Feature Space**: Dense embeddings representing chunk semantics.
- **Label Generation**: Cluster centroids are interpreted by extracting top n-gram keywords via TF-IDF over the cluster's text corpus.
- **Validation**: Silhouette Coefficient:
  $$s(i) = \frac{b(i) - a(i)}{\max(a(i), b(i))}$$

---

## 3. Bayesian Knowledge Tracing (BKT)

### Parameters
- $P(L_0) = 0.20$: Prior initial mastery probability.
- $P(T) = 0.15$: Learning transition probability per practice opportunity.
- $P(G) = 0.25$: Guess probability.
- $P(S) = 0.10$: Slip probability.

### Update Equations
Upon observing student answer correctness:
- **Correct response ($obs=1$)**:
  $$P(L_t \mid obs=1) = \frac{P(L_{t-1}) \cdot (1 - P(S))}{P(L_{t-1}) \cdot (1 - P(S)) + (1 - P(L_{t-1})) \cdot P(G)}$$
- **Incorrect response ($obs=0$)**:
  $$P(L_t \mid obs=0) = \frac{P(L_{t-1}) \cdot P(S)}{P(L_{t-1}) \cdot P(S) + (1 - P(L_{t-1})) \cdot (1 - P(G))}$$

### Opportunity Update
$$P(L_{t+1}) = P(L_t \mid obs) + (1 - P(L_t \mid obs)) \cdot P(T)$$

---

## 4. Supervised Weakness Prediction

- **Target**: Binary indicator $y \in \{0, 1\}$ representing whether the student will answer the next question for a topic incorrectly.
- **Feature Engineering**: Strictly past metrics (zero future leakage):
  1. `recent_accuracy` (last 5 attempts)
  2. `total_attempts`
  3. `recent_incorrect_count`
  4. `current_streak`
  5. `time_since_last_sec`
  6. `prior_mastery`
- **Models Evaluated**:
  1. Majority Class Baseline ($F_1 = 0.588$)
  2. Logistic Regression ($F_1 = 0.750$)
  3. Random Forest Classifier ($F_1 = 0.909$)
