import pytest
from app.ml.content.retrieval import RetrievalEngine


def test_tfidf_retrieval_ranking():
    engine = RetrievalEngine()
    course_id = "test-course-1"
    chunks = [
        {"id": "c1", "text_content": "Photosynthesis is the process by which green plants use sunlight to synthesize nutrients."},
        {"id": "c2", "text_content": "Newtonian mechanics describes the motion of macroscopic objects from projectiles to parts of machinery."},
        {"id": "c3", "text_content": "Plant cells contain chloroplasts where sunlight is converted into chemical energy during photosynthesis."},
    ]

    engine.fit_tfidf(course_id, [c["text_content"] for c in chunks])
    results = engine.search_hybrid(course_id, "How do plants convert sunlight in chloroplasts?", chunks, mode="tfidf", top_k=2)

    assert len(results) == 2
    # c3 or c1 should rank first due to photosynthesis/chloroplasts/sunlight terms
    top_chunk, score = results[0]
    assert top_chunk["id"] in ("c1", "c3")
    assert score > 0.0


def test_retrieval_handles_empty_query():
    engine = RetrievalEngine()
    course_id = "test-course-2"
    chunks = [{"id": "c1", "text_content": "Algorithm analysis and time complexity big O notation."}]
    results = engine.search_hybrid(course_id, "", chunks, mode="tfidf")
    assert len(results) == 1
