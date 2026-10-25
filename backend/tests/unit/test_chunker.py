import pytest
from app.ml.ingestion.chunker import normalize_text, chunk_document


def test_normalize_text():
    dirty = "This is  a  test\u00a0with  tabs\tand\n\n\n\nmultiple lines."
    clean = normalize_text(dirty)
    assert "  " not in clean
    assert "\u00a0" not in clean
    assert "\t" not in clean
    assert "\n\n\n" not in clean


def test_chunk_document_basic():
    pages = [
        {
            "page_number": 1,
            "text": " ".join([f"word{i}" for i in range(250)])
        }
    ]
    chunks = chunk_document(pages, target_words=100, min_words=20, max_words=150, overlap_words=20)
    assert len(chunks) > 0
    assert all(c["word_count"] >= 20 for c in chunks)
    assert all(c["page_number"] == 1 for c in chunks)


def test_chunk_document_empty_page():
    pages = [{"page_number": 1, "text": ""}]
    chunks = chunk_document(pages)
    assert len(chunks) == 0
