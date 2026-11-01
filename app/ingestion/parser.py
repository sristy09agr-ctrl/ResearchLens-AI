"""
PyMuPDF-based academic document layout parser and metadata extractor.
"""

import re
from typing import List, Dict, Any, Optional
import pymupdf
from modules.document_processor import extract_text_from_pdf


def parse_pdf_document(pdf_bytes: bytes, max_pages: int = 100) -> Dict[str, Any]:
    """
    Parse PDF into structured pages with sections, detecting metadata (title, authors, year).
    """
    doc = pymupdf.open(stream=pdf_bytes, filetype="pdf")
    total_pages = len(doc)

    if total_pages == 0:
        raise ValueError("PDF document contains 0 pages.")

    if total_pages > max_pages:
        raise ValueError(f"PDF contains {total_pages} pages, which exceeds the limit of {max_pages} pages.")

    metadata = extract_paper_metadata(doc)
    pages = extract_text_from_pdf(pdf_bytes)

    return {
        "metadata": metadata,
        "total_pages": total_pages,
        "pages": pages
    }


def extract_paper_metadata(doc: pymupdf.Document) -> Dict[str, Optional[str]]:
    """
    Extract title, authors, and year heuristics from PDF document metadata and first page.
    """
    doc_meta = doc.metadata or {}
    title = doc_meta.get("title")
    author = doc_meta.get("author")
    year = None

    creation_date = doc_meta.get("creationDate", "")
    if creation_date:
        match = re.search(r"(\d{4})", creation_date)
        if match:
            year = match.group(1)

    # Heuristic fallback to page 1 text if metadata empty
    if len(doc) > 0 and (not title or len(title.strip()) < 5):
        first_page = doc[0]
        blocks = first_page.get_text("blocks")
        # Typically the highest block with largest font or first substantial block
        for b in blocks:
            text = b[4].strip()
            if text and len(text.split("\n")) <= 3 and len(text) > 10:
                title = text.replace("\n", " ")
                break

    return {
        "title": title.strip() if title else "Untitled Paper",
        "author": author.strip() if author else "Unknown Author",
        "year": year
    }

