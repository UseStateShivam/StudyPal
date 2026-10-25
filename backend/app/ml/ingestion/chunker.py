"""Document chunking and text extraction pipeline with paragraph awareness."""

import re
import hashlib
from typing import List, Dict, Any, Optional
from pathlib import Path
import fitz  # PyMuPDF
from app.config import settings
from app.logging_config import logger


def compute_sha256(file_path: Path) -> str:
    """Compute SHA256 checksum of a file."""
    sha = hashlib.sha256()
    with open(file_path, "rb") as f:
        while chunk := f.read(8192):
            sha.update(chunk)
    return sha.hexdigest()


def normalize_text(text: str) -> str:
    """Normalize extracted text by removing extra whitespaces, line breaks and control characters."""
    if not text:
        return ""
    # Replace non-breaking spaces and tabs
    text = text.replace("\u00a0", " ").replace("\t", " ")
    # Replace multiple spaces with a single space
    text = re.sub(r"[ ]{2,}", " ", text)
    # Normalize multiple newlines to double newlines (paragraph boundary)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def extract_text_from_pdf(pdf_path: Path) -> List[Dict[str, Any]]:
    """
    Extract text page-by-page using PyMuPDF.
    Returns list of {"page_number": int, "text": str}.
    """
    pages_content = []
    try:
        doc = fitz.open(pdf_path)
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            text = page.get_text("text")
            pages_content.append({
                "page_number": page_idx + 1,
                "text": normalize_text(text),
            })
        doc.close()
    except Exception as e:
        logger.error(f"Failed to extract PDF {pdf_path}: {e}")
        raise ValueError(f"Could not read PDF: {str(e)}")

    return pages_content


def extract_text_from_txt(txt_path: Path) -> List[Dict[str, Any]]:
    """Extract text from plain-text file."""
    try:
        with open(txt_path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        return [{"page_number": 1, "text": normalize_text(text)}]
    except Exception as e:
        logger.error(f"Failed to read TXT {txt_path}: {e}")
        raise ValueError(f"Could not read TXT file: {str(e)}")


def chunk_document(
    pages: List[Dict[str, Any]],
    target_words: int = settings.CHUNK_TARGET_WORDS,
    min_words: int = settings.CHUNK_MIN_WORDS,
    max_words: int = settings.CHUNK_MAX_WORDS,
    overlap_words: int = settings.CHUNK_OVERLAP_WORDS,
) -> List[Dict[str, Any]]:
    """
    Paragraph-aware chunking preserving page metadata.
    Splits text along paragraph boundaries and joins sentences to achieve target word count.
    """
    chunks = []
    chunk_index = 0

    for page_data in pages:
        page_num = page_data["page_number"]
        page_text = page_data["text"]
        if not page_text or len(page_text.strip()) == 0:
            continue

        # Split into paragraphs
        paragraphs = [p.strip() for p in page_text.split("\n\n") if p.strip()]

        current_words: List[str] = []
        current_start_char = 0

        for para in paragraphs:
            para_words = para.split()
            if not para_words:
                continue

            # If adding this paragraph exceeds max_words, flush current chunk
            if len(current_words) + len(para_words) > max_words and len(current_words) >= min_words:
                chunk_str = " ".join(current_words)
                chunks.append({
                    "chunk_index": chunk_index,
                    "text_content": chunk_str,
                    "word_count": len(current_words),
                    "page_number": page_num,
                    "start_char": current_start_char,
                    "end_char": current_start_char + len(chunk_str),
                })
                chunk_index += 1
                # Handle overlap
                current_words = current_words[-overlap_words:] if overlap_words < len(current_words) else []

            current_words.extend(para_words)

        # Flush any remaining words for the page
        if len(current_words) >= min_words:
            chunk_str = " ".join(current_words)
            chunks.append({
                "chunk_index": chunk_index,
                "text_content": chunk_str,
                "word_count": len(current_words),
                "page_number": page_num,
                "start_char": current_start_char,
                "end_char": current_start_char + len(chunk_str),
            })
            chunk_index += 1
        elif current_words and chunks:
            # Append small trailing words to previous chunk if within reasonable bounds
            last_chunk = chunks[-1]
            last_chunk["text_content"] += " " + " ".join(current_words)
            last_chunk["word_count"] += len(current_words)

    return chunks
