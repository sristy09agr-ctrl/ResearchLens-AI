"""
Security module for PDF validation and prompt-injection defense.
"""

import re
from typing import Tuple

# PDF files must start with %PDF- header magic bytes
PDF_MAGIC_BYTES = b"%PDF-"


def validate_pdf_content(content: bytes) -> Tuple[bool, str]:
    """
    Validate that bytes represent a legitimate, non-empty PDF file.
    Returns (is_valid, error_reason).
    """
    if not content or len(content) == 0:
        return False, "File is completely empty."

    if not content.startswith(PDF_MAGIC_BYTES):
        return False, "Invalid file format: Missing '%PDF-' magic bytes header."

    # Look for the %%EOF marker within the trailing bytes of the document
    trailing = content[-1024:]
    if b"%%EOF" not in trailing and b"stream" not in content:
        return False, "Corrupt or truncated PDF: Missing EOF marker."

    return True, ""


def sanitize_evidence_text(text: str) -> str:
    """
    Neutralize potential prompt-injection payloads from untrusted academic PDFs
    while maintaining scientific notation and factual claims.
    """
    if not text:
        return ""

    # Strip dangerous LLM instruction overrides
    patterns = [
        r"(?i)ignore\s+(all\s+)?(previous|above)\s+instructions?",
        r"(?i)system\s*:\s*you\s+are",
        r"(?i)you\s+must\s+now\s+act\s+as",
        r"(?i)disregard\s+the\s+system\s+prompt",
        r"(?i)new\s+system\s+directive",
    ]

    sanitized = text
    for pattern in patterns:
        sanitized = re.sub(pattern, "[FILTERED_INSTRUCTION]", sanitized)

    return sanitized


def wrap_evidence_boundary(passage_text: str, passage_id: int) -> str:
    """
    Encapsulate evidence passages inside strict boundaries to ensure the LLM
    treats them solely as passive context data and never as executable directives.
    """
    cleaned = sanitize_evidence_text(passage_text)
    return (
        f"<<<BEGIN_EVIDENCE id={passage_id}>>>\n"
        f"{cleaned}\n"
        f"<<<END_EVIDENCE id={passage_id}>>>"
    )

