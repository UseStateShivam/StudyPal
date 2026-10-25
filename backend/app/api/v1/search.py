"""Search and Retrieval API router: execute grounded hybrid question retrieval across student notes."""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Course, DocumentChunk, Document, Topic
from app.schemas import SearchRequest, SearchResponse, SearchResultItem
from app.dependencies import get_user_course
from app.ml.content.retrieval import retrieval_engine
from app.config import settings

router = APIRouter(tags=["Search"])


@router.post("/courses/{course_id}/search", response_model=SearchResponse)
def search_course_materials(
    search_req: SearchRequest,
    course: Course = Depends(get_user_course),
    db: Session = Depends(get_db),
):
    """
    Search student's course notes using lexical (TF-IDF), semantic (dense embedding), or hybrid retrieval.
    Zero generative AI hallucination: returns exact passages extracted directly from uploaded notes.
    """
    chunks = db.query(DocumentChunk).filter(DocumentChunk.course_id == course.id).all()
    if not chunks:
        return SearchResponse(
            query=search_req.query,
            retrieval_method_used=search_req.retrieval_method or settings.RETRIEVAL_METHOD,
            total_results=0,
            results=[],
        )

    chunk_dicts = [
        {
            "id": c.id,
            "document_id": c.document_id,
            "chunk_index": c.chunk_index,
            "text_content": c.text_content,
            "page_number": c.page_number,
            "topic_id": c.topic_id,
            "embedding_vector": c.embedding_vector,
        }
        for c in chunks
    ]

    method = search_req.retrieval_method or settings.RETRIEVAL_METHOD
    ranked_chunks = retrieval_engine.search_hybrid(
        course_id=course.id,
        query=search_req.query,
        chunks=chunk_dicts,
        alpha=settings.HYBRID_ALPHA,
        top_k=search_req.top_k or settings.TOP_K_RETRIEVAL,
        mode=method,
    )

    # Document map for original filenames
    doc_ids = list(set([c["document_id"] for c, _ in ranked_chunks]))
    docs = db.query(Document).filter(Document.id.in_(doc_ids)).all() if doc_ids else []
    doc_map = {d.id: d.original_filename for d in docs}

    # Topic map for topic labels
    topic_ids = list(set([c["topic_id"] for c, _ in ranked_chunks if c["topic_id"]]))
    topics = db.query(Topic).filter(Topic.id.in_(topic_ids)).all() if topic_ids else []
    topic_map = {t.id: t.label for t in topics}

    items = []
    for c_dict, score in ranked_chunks:
        items.append(
            SearchResultItem(
                chunk_id=c_dict["id"],
                document_id=c_dict["document_id"],
                document_title=doc_map.get(c_dict["document_id"], "Unknown Document"),
                passage=c_dict["text_content"],
                page_number=c_dict.get("page_number"),
                similarity_score=round(float(score), 4),
                retrieval_method=method,
                topic_label=topic_map.get(c_dict.get("topic_id"), "General"),
            )
        )

    return SearchResponse(
        query=search_req.query,
        retrieval_method_used=method,
        total_results=len(items),
        results=items,
    )


@router.get("/courses/{course_id}/search/config")
def get_search_config(course: Course = Depends(get_user_course)):
    """Retrieve available search configurations and default weights."""
    return {
        "default_retrieval_method": settings.RETRIEVAL_METHOD,
        "hybrid_alpha": settings.HYBRID_ALPHA,
        "top_k_default": settings.TOP_K_RETRIEVAL,
        "supported_methods": ["hybrid", "tfidf", "embedding"],
        "embedding_model": settings.EMBEDDING_MODEL_NAME,
    }
