"""Unsupervised concept discovery using K-Means clustering with K-Means++ initialization.

Features:
- Document chunk clustering on dense embeddings or TF-IDF representations.
- Silhouette score evaluation for cluster cohesion.
- Automatic descriptive topic label extraction using top TF-IDF keywords.
- Graceful fallback for small corpora (< 4 chunks).
"""

from typing import List, Dict, Any, Tuple, Optional
import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.feature_extraction.text import TfidfVectorizer
import json
from app.config import settings
from app.logging_config import logger


def extract_keywords_per_cluster(
    cluster_texts: List[str],
    top_n: int = 5
) -> Tuple[str, List[str]]:
    """Extract representative keywords and title from cluster text using TF-IDF."""
    if not cluster_texts:
        return "Topic General", []

    try:
        vec = TfidfVectorizer(stop_words="english", max_features=100, ngram_range=(1, 2))
        matrix = vec.fit_transform(cluster_texts)
        scores = np.asarray(matrix.sum(axis=0)).ravel()
        features = np.array(vec.get_feature_names_out())

        top_indices = np.argsort(scores)[::-1][:top_n]
        top_words = features[top_indices].tolist()

        label = " & ".join([w.title() for w in top_words[:2]]) if top_words else "General Topic"
        return label, top_words
    except Exception as e:
        logger.warning(f"Keyword extraction fallback: {e}")
        return "Study Module", ["study", "concepts", "overview"]


class TopicClusterer:
    def __init__(self, random_state: int = settings.CLUSTERING_RANDOM_STATE):
        self.random_state = random_state

    def discover_topics(
        self,
        chunks: List[Dict[str, Any]],
        n_clusters: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Cluster chunks into educational topics.
        Returns:
        {
            "status": "success" | "fallback",
            "n_clusters": int,
            "silhouette_score": float,
            "topics": [
                {
                    "cluster_index": int,
                    "label": str,
                    "keywords": str,
                    "chunk_indices": List[int]
                }
            ]
        }
        """
        n_chunks = len(chunks)
        if n_chunks < settings.MIN_CHUNKS_FOR_CLUSTERING:
            logger.info(f"Corpus size ({n_chunks}) too small for K-Means clustering. Using single fallback topic.")
            texts = [c["text_content"] for c in chunks]
            label, words = extract_keywords_per_cluster(texts)
            return {
                "status": "fallback",
                "n_clusters": 1,
                "silhouette_score": 0.0,
                "topics": [
                    {
                        "cluster_index": 0,
                        "label": label or "Course Overview",
                        "keywords": ", ".join(words),
                        "chunk_indices": list(range(n_chunks)),
                    }
                ],
            }

        # Prepare vector representations
        vectors = []
        for c in chunks:
            emb = c.get("embedding_vector")
            if isinstance(emb, str) and emb:
                try:
                    vectors.append(json.loads(emb))
                except Exception:
                    vectors.append([0.0] * 384)
            elif isinstance(emb, list):
                vectors.append(emb)
            else:
                vectors.append([0.0] * 384)

        X = np.array(vectors)

        # Determine target cluster count
        k = n_clusters or min(settings.DEFAULT_N_CLUSTERS, max(2, n_chunks // 3))
        k = min(k, n_chunks - 1)  # K must be strictly less than n_chunks for silhouette

        kmeans = KMeans(
            n_clusters=k,
            init="k-means++",
            random_state=self.random_state,
            n_init=10,
        )
        labels = kmeans.fit_predict(X)

        # Compute silhouette score if possible
        sil_score = 0.0
        if len(set(labels)) > 1 and len(set(labels)) < n_chunks:
            try:
                sil_score = float(silhouette_score(X, labels))
            except Exception:
                sil_score = 0.0

        # Build topic metadata and label per cluster
        topics = []
        for c_idx in range(k):
            member_indices = [i for i, lbl in enumerate(labels) if lbl == c_idx]
            member_texts = [chunks[i]["text_content"] for i in member_indices]
            topic_label, keywords = extract_keywords_per_cluster(member_texts)

            topics.append({
                "cluster_index": c_idx,
                "label": topic_label,
                "keywords": ", ".join(keywords),
                "chunk_indices": member_indices,
            })

        return {
            "status": "success",
            "n_clusters": k,
            "silhouette_score": sil_score,
            "topics": topics,
        }


topic_clusterer = TopicClusterer()
