"""Content retrieval engine implementing TF-IDF, dense Sentence Embeddings, and Hybrid ranking.

Retrieval Formulations:
1. TF-IDF Cosine:
   sim_tfidf(q, c) = (v_q . v_c) / (||v_q|| * ||v_c||)
2. Dense Embedding Cosine:
   sim_emb(q, c) = (e_q . e_c) / (||e_q|| * ||e_c||)
3. Min-Max Normalised Hybrid Score:
   norm(s) = (s - min(s)) / (max(s) - min(s) + 1e-8)
   score_hybrid = alpha * norm(sim_tfidf) + (1 - alpha) * norm(sim_emb)
"""

from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
from app.config import settings
from app.logging_config import logger

# Lazy model loader for SentenceTransformer to allow fast startup and offline fallback
_sentence_transformer_model = None


def get_embedding_model():
    global _sentence_transformer_model
    if _sentence_transformer_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            logger.info(f"Loading SentenceTransformer model: {settings.EMBEDDING_MODEL_NAME}")
            _sentence_transformer_model = SentenceTransformer(
                settings.EMBEDDING_MODEL_NAME,
                device=settings.EMBEDDING_DEVICE,
                cache_folder=str(settings.get_model_cache_path())
            )
        except Exception as e:
            logger.warning(f"Could not load SentenceTransformer model ({e}). Dense retrieval fallback will be used.")
            _sentence_transformer_model = None
    return _sentence_transformer_model


class RetrievalEngine:
    def __init__(self):
        self.vectorizers: Dict[str, TfidfVectorizer] = {}

    def fit_tfidf(self, course_id: str, texts: List[str]) -> Optional[TfidfVectorizer]:
        """Fit a course-scoped TF-IDF vectorizer."""
        if not texts:
            return None
        vec = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            stop_words="english",
            max_df=1.0,
            min_df=1,
        )
        vec.fit(texts)
        self.vectorizers[course_id] = vec
        return vec

    def encode_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Encode texts into dense unit-normalized embedding vectors."""
        model = get_embedding_model()
        if model is None:
            # Fallback to zero vectors if model unavailable
            return [[0.0] * 384 for _ in texts]
        embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return [emb.tolist() for emb in embeddings]

    def encode_query(self, query: str) -> Optional[List[float]]:
        """Encode single query string into unit vector."""
        model = get_embedding_model()
        if model is None:
            return None
        emb = model.encode([query], normalize_embeddings=True, show_progress_bar=False)
        return emb[0].tolist()

    def search_hybrid(
        self,
        course_id: str,
        query: str,
        chunks: List[Dict[str, Any]],
        alpha: float = settings.HYBRID_ALPHA,
        top_k: int = settings.TOP_K_RETRIEVAL,
        mode: str = "hybrid",
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Execute query retrieval against candidate course chunks.
        Modes: 'tfidf', 'embedding', 'hybrid'
        Returns list of (chunk_dict, score) sorted descending by score.
        """
        if not chunks:
            return []

        chunk_texts = [c["text_content"] for c in chunks]
        n_chunks = len(chunks)

        # 1. TF-IDF Cosine Scores
        tfidf_scores = np.zeros(n_chunks)
        if mode in ("tfidf", "hybrid"):
            vec = self.vectorizers.get(course_id)
            if vec is None:
                vec = self.fit_tfidf(course_id, chunk_texts)

            if vec is not None:
                try:
                    q_vec = vec.transform([query])
                    c_matrix = vec.transform(chunk_texts)
                    sims = cosine_similarity(q_vec, c_matrix)[0]
                    tfidf_scores = np.nan_to_num(sims, nan=0.0)
                except Exception as e:
                    logger.error(f"TF-IDF scoring failed: {e}")

        # 2. Dense Semantic Cosine Scores
        dense_scores = np.zeros(n_chunks)
        has_dense = False
        if mode in ("embedding", "hybrid"):
            q_emb = self.encode_query(query)
            if q_emb is not None:
                has_dense = True
                q_vec = np.array(q_emb).reshape(1, -1)
                chunk_embs = []
                for c in chunks:
                    emb = c.get("embedding_vector")
                    if isinstance(emb, str) and emb:
                        try:
                            chunk_embs.append(json.loads(emb))
                        except Exception:
                            chunk_embs.append([0.0] * 384)
                    elif isinstance(emb, list):
                        chunk_embs.append(emb)
                    else:
                        chunk_embs.append([0.0] * 384)

                c_matrix = np.array(chunk_embs)
                if c_matrix.shape[0] == n_chunks and c_matrix.shape[1] > 0:
                    sims = cosine_similarity(q_vec, c_matrix)[0]
                    dense_scores = np.nan_to_num(sims, nan=0.0)

        # 3. Score Normalisation & Fusion
        if mode == "tfidf" or (mode == "hybrid" and not has_dense):
            final_scores = tfidf_scores
        elif mode == "embedding":
            final_scores = dense_scores
        else:  # hybrid with both
            def min_max_norm(arr: np.ndarray) -> np.ndarray:
                mn, mx = np.min(arr), np.max(arr)
                if mx - mn < 1e-9:
                    return np.zeros_like(arr) if mx == 0 else np.ones_like(arr) * 0.5
                return (arr - mn) / (mx - mn)

            norm_tfidf = min_max_norm(tfidf_scores)
            norm_dense = min_max_norm(dense_scores)
            final_scores = alpha * norm_tfidf + (1.0 - alpha) * norm_dense

        # Rank and return top_k
        ranked_indices = np.argsort(final_scores)[::-1]
        results = []
        for idx in ranked_indices[:top_k]:
            score = float(final_scores[idx])
            results.append((chunks[idx], score))

        return results


retrieval_engine = RetrievalEngine()
