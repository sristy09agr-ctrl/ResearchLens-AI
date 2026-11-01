"""
Academic chunking module with section awareness, table-caption retention,
and reference section filtering.
"""

from typing import List, Dict, Any
from modules.chunking import chunk_pages as base_chunk_pages

REFERENCE_SECTIONS = {"references", "bibliography", "works cited", "literature cited"}


def chunk_academic_pages(
    pages: List[Dict[str, Any]],
    paper_name: str,
    chunk_size: int = 250,
    overlap: int = 40,
    exclude_references: bool = True
) -> List[Dict[str, Any]]:
    """
    Chunk extracted pages into semantic retrieval passages, binding tables to captions
    and excluding or tagging bibliographic references.
    """
    raw_chunks = base_chunk_pages(
        pages=pages,
        paper_name=paper_name,
        chunk_size=chunk_size,
        overlap=overlap
    )

    processed_chunks = []
    for chunk in raw_chunks:
        section = (chunk.get("section") or "").strip()
        section_lower = section.lower()

        # Detect chunk type: table, formula, or standard text
        text = chunk.get("text", "")
        chunk_type = "text"
        if "|" in text and len(text.split("|")) >= 4:
            chunk_type = "table"
        elif "$$" in text or r"\[" in text:
            chunk_type = "formula"
        elif section_lower in ["caption", "figure caption", "table caption"]:
            chunk_type = "caption"

        chunk["chunk_type"] = chunk_type

        # Check if reference section
        if exclude_references and section_lower in REFERENCE_SECTIONS:
            # Tag reference so it's not indexed into search
            chunk["is_reference"] = True
            continue

        chunk["is_reference"] = False
        processed_chunks.append(chunk)

    return processed_chunks

