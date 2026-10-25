"""Documents API router: file upload, background extraction, chunking, and embedding generation."""

import os
import uuid
import json
from datetime import datetime, timezone
from typing import List
from pathlib import Path
from fastapi import APIRouter, Depends, UploadFile, File, BackgroundTasks, status
from sqlalchemy.orm import Session
from app.db.session import get_db, SessionLocal
from app.db.models import Document, DocumentChunk, Course, User, Topic
from app.schemas import DocumentOut, DocumentStatusOut, DocumentChunkOut
from app.dependencies import get_current_user, get_user_course
from app.config import settings
from app.logging_config import logger
from app.core.exceptions import (
    EntityNotFoundException,
    UnsupportedFileFormatException,
    StudyPalException,
    ForbiddenCourseAccessException,
)
from app.ml.ingestion.chunker import (
    compute_sha256,
    extract_text_from_pdf,
    extract_text_from_txt,
    chunk_document,
)
from app.ml.content.retrieval import retrieval_engine
from app.ml.content.clustering import topic_clusterer

router = APIRouter(tags=["Documents"])


def process_document_pipeline(document_id: str):
    """
    Background worker function for extraction, chunking, embedding generation,
    and automatic topic discovery update.
    """
    db: Session = SessionLocal()
    try:
        doc = db.query(Document).filter(Document.id == document_id).first()
        if not doc:
            logger.error(f"Worker cannot find document {document_id}")
            return

        doc.processing_status = "processing"
        db.commit()

        storage_path = Path(doc.storage_identifier)
        if not storage_path.exists():
            doc.processing_status = "failed"
            doc.error_message = "Uploaded file was missing from local storage."
            db.commit()
            return

        # 1. Extraction
        if doc.file_type == "pdf":
            pages = extract_text_from_pdf(storage_path)
            doc.total_pages = len(pages)
        else:
            pages = extract_text_from_txt(storage_path)
            doc.total_pages = 1

        total_extracted_words = sum(len(p["text"].split()) for p in pages)
        if total_extracted_words == 0:
            doc.processing_status = "failed"
            doc.error_message = "No extractable text found. Scanned or image-only documents require OCR, which is not supported."
            db.commit()
            return

        # 2. Chunking
        raw_chunks = chunk_document(pages)
        if not raw_chunks:
            doc.processing_status = "failed"
            doc.error_message = "Document text was too short to produce valid semantic chunks."
            db.commit()
            return

        # 3. Dense Embeddings
        chunk_texts = [c["text_content"] for c in raw_chunks]
        embeddings = retrieval_engine.encode_embeddings(chunk_texts)

        # 4. Save Chunks to Database
        created_chunks = []
        for i, c in enumerate(raw_chunks):
            chunk_record = DocumentChunk(
                document_id=doc.id,
                course_id=doc.course_id,
                chunk_index=c["chunk_index"],
                text_content=c["text_content"],
                word_count=c["word_count"],
                page_number=c.get("page_number"),
                start_char=c.get("start_char"),
                end_char=c.get("end_char"),
                embedding_vector=json.dumps(embeddings[i]),
            )
            db.add(chunk_record)
            created_chunks.append(chunk_record)

        doc.chunk_count = len(created_chunks)
        doc.processing_status = "completed"
        doc.completed_at = datetime.now(timezone.utc)
        db.commit()
        logger.info(f"Document {doc.id} processed successfully with {doc.chunk_count} chunks.")

        # 5. Fit or update TF-IDF for the course
        all_course_chunks = db.query(DocumentChunk).filter(DocumentChunk.course_id == doc.course_id).all()
        retrieval_engine.fit_tfidf(doc.course_id, [c.text_content for c in all_course_chunks])

        # 6. Run Unsupervised Topic Clustering for the course
        chunk_dicts = [
            {
                "id": c.id,
                "text_content": c.text_content,
                "embedding_vector": c.embedding_vector,
            }
            for c in all_course_chunks
        ]
        cluster_res = topic_clusterer.discover_topics(chunk_dicts)

        if cluster_res.get("topics"):
            # Update or create course topics
            for top_data in cluster_res["topics"]:
                c_idx = top_data["cluster_index"]
                existing_topic = db.query(Topic).filter(
                    Topic.course_id == doc.course_id,
                    Topic.cluster_index == c_idx
                ).first()

                if existing_topic:
                    if not existing_topic.is_custom_label:
                        existing_topic.label = top_data["label"]
                    existing_topic.keywords = top_data["keywords"]
                    existing_topic.chunk_count = len(top_data["chunk_indices"])
                    target_topic_id = existing_topic.id
                else:
                    new_topic = Topic(
                        course_id=doc.course_id,
                        cluster_index=c_idx,
                        label=top_data["label"],
                        keywords=top_data["keywords"],
                        chunk_count=len(top_data["chunk_indices"]),
                    )
                    db.add(new_topic)
                    db.flush()
                    target_topic_id = new_topic.id

                # Assign topic ID to corresponding chunks
                for chunk_idx in top_data["chunk_indices"]:
                    all_course_chunks[chunk_idx].topic_id = target_topic_id

            db.commit()
            logger.info(f"Updated {len(cluster_res['topics'])} topics for course {doc.course_id}.")

    except Exception as e:
        logger.error(f"Error processing document {document_id}: {e}")
        db.rollback()
        doc = db.query(Document).filter(Document.id == document_id).first()
        if doc:
            doc.processing_status = "failed"
            doc.error_message = f"Processing error: {str(e)}"
            db.commit()
    finally:
        db.close()


@router.post("/courses/{course_id}/documents", response_model=DocumentOut, status_code=status.HTTP_202_ACCEPTED)
async def upload_document(
    course_id: str,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    course: Course = Depends(get_user_course),
    db: Session = Depends(get_db),
):
    """Upload a PDF or TXT study document to course for ingestion and indexing."""
    filename = file.filename or "uploaded_document"
    ext = filename.split(".")[-1].lower() if "." in filename else ""

    if ext not in settings.ALLOWED_EXTENSIONS:
        raise UnsupportedFileFormatException(ext)

    # Save to disk safely
    upload_dir = settings.get_upload_path()
    safe_storage_id = str(upload_dir / f"{uuid.uuid4()}.{ext}")

    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE_BYTES:
        raise StudyPalException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            code="FILE_TOO_LARGE",
            message=f"File exceeds maximum allowed size of {settings.MAX_UPLOAD_SIZE_BYTES // (1024 * 1024)} MB.",
        )

    with open(safe_storage_id, "wb") as f:
        f.write(content)

    checksum = compute_sha256(Path(safe_storage_id))

    # Check for duplicate in course
    existing = db.query(Document).filter(
        Document.course_id == course_id,
        Document.content_checksum == checksum
    ).first()
    if existing:
        # Remove uploaded temp copy
        if os.path.exists(safe_storage_id):
            os.remove(safe_storage_id)
        raise StudyPalException(
            status_code=status.HTTP_409_CONFLICT,
            code="DUPLICATE_DOCUMENT",
            message=f"This document has already been uploaded to this course ('{existing.original_filename}').",
        )

    document = Document(
        course_id=course.id,
        original_filename=filename,
        storage_identifier=safe_storage_id,
        file_type=ext,
        file_size_bytes=len(content),
        content_checksum=checksum,
        processing_status="pending",
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    # Queue background task
    background_tasks.add_task(process_document_pipeline, document.id)

    return document


@router.get("/courses/{course_id}/documents", response_model=List[DocumentOut])
def list_documents(
    course: Course = Depends(get_user_course),
    db: Session = Depends(get_db),
):
    """List all documents uploaded to this course."""
    return db.query(Document).filter(Document.course_id == course.id).order_by(Document.uploaded_at.desc()).all()


@router.get("/documents/{document_id}", response_model=DocumentOut)
def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Retrieve document details with ownership protection."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise EntityNotFoundException("Document", document_id)
    course = db.query(Course).filter(Course.id == doc.course_id, Course.owner_id == current_user.id).first()
    if not course:
        raise ForbiddenCourseAccessException(doc.course_id)
    return doc


@router.get("/documents/{document_id}/status", response_model=DocumentStatusOut)
def get_document_status(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Check processing status of an uploaded document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise EntityNotFoundException("Document", document_id)
    return doc


@router.delete("/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete document, stored file, and associated chunks."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise EntityNotFoundException("Document", document_id)
    course = db.query(Course).filter(Course.id == doc.course_id, Course.owner_id == current_user.id).first()
    if not course:
        raise ForbiddenCourseAccessException(doc.course_id)

    if os.path.exists(doc.storage_identifier):
        try:
            os.remove(doc.storage_identifier)
        except Exception as e:
            logger.warning(f"Failed to delete file {doc.storage_identifier}: {e}")

    db.delete(doc)
    db.commit()
    return None


@router.post("/documents/{document_id}/reprocess", response_model=DocumentStatusOut)
def reprocess_document(
    document_id: str,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Trigger complete re-extraction, re-chunking, and re-indexing of a document."""
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise EntityNotFoundException("Document", document_id)
    course = db.query(Course).filter(Course.id == doc.course_id, Course.owner_id == current_user.id).first()
    if not course:
        raise ForbiddenCourseAccessException(doc.course_id)

    # Clean existing chunks
    db.query(DocumentChunk).filter(DocumentChunk.document_id == doc.id).delete()
    doc.processing_status = "pending"
    doc.error_message = None
    doc.chunk_count = 0
    db.commit()

    background_tasks.add_task(process_document_pipeline, doc.id)
    return doc
