"""
PDF validation utilities: magic-byte checks, size caps, and corruption guards.
"""

from typing import Tuple
from app.config import settings
from app.core.security import validate_pdf_content


def validate_uploaded_pdf(
    filename: str,
    pdf_bytes: bytes,
    max_size: int = settings.max_file_size_bytes
) -> Tuple[bool, str]:
    """
    Validate that an uploaded file is a legitimate PDF within size boundaries.
    """
    cleaned_name = (filename or "document.pdf").replace("\\", "/").split("/")[-1]

    if not cleaned_name.lower().endswith(".pdf"):
        return False, f"File '{cleaned_name}' is not a PDF (must have .pdf extension)."

    if not pdf_bytes or len(pdf_bytes) == 0:
        return False, f"File '{cleaned_name}' is completely empty."

    if len(pdf_bytes) > max_size:
        size_mb = len(pdf_bytes) / (1024 * 1024)
        max_mb = max_size / (1024 * 1024)
        return False, f"File '{cleaned_name}' ({size_mb:.1f} MB) exceeds maximum allowed size ({max_mb:.0f} MB)."

    is_valid_format, reason = validate_pdf_content(pdf_bytes)
    if not is_valid_format:
        return False, f"File '{cleaned_name}' failed format validation: {reason}"

    return True, ""

