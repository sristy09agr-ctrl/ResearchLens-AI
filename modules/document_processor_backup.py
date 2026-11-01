
import re

import pymupdf
import pymupdf4llm


"""
General-purpose research paper PDF parser.

Design:
- PyMuPDF4LLM performs layout-aware extraction.
- Layout boxes identify document elements and their reading order.
- Mathematical formulas, tables, lists, and paragraphs are preserved.
- Standard academic headings receive semantic section labels.
- Unknown headings are preserved rather than discarded.
- Duplicate overlapping layout elements are filtered conservatively.

Backend output contract:
[
    {
        "page": int,
        "text": str,
        "sections": [
            {
                "section": str,
                "text": str
            }
        ]
    }
]
"""


# -------------------------------------------------------------------
# STANDARD ACADEMIC SECTION NAMES
# -------------------------------------------------------------------

SECTION_HEADINGS = {
    "abstract": "Abstract",
    "summary": "Abstract",

    "introduction": "Introduction",
    "background": "Background",
    "theoretical background": "Background",

    "related work": "Related Work",
    "related studies": "Related Work",
    "literature review": "Literature Review",

    "problem statement": "Problem Statement",
    "research problem": "Problem Statement",

    "motivation": "Motivation",
    "objectives": "Objectives",
    "research objectives": "Research Objectives",
    "research questions": "Research Questions",

    "materials and methods": "Methodology",
    "materials and methods used": "Methodology",
    "methodology": "Methodology",
    "methods": "Methodology",

    "experimental setup": "Experimental Setup",
    "experimental design": "Experimental Design",
    "experiments": "Experiments",

    "results": "Results",
    "experimental results": "Results",
    "findings": "Results",

    "discussion": "Discussion",
    "results and discussion": "Results and Discussion",

    "limitations": "Limitations",
    "study limitations": "Limitations",

    "conclusion": "Conclusion",
    "conclusions": "Conclusion",

    "future work": "Future Work",
    "future directions": "Future Work",

    "references": "References",
    "bibliography": "References",

    "acknowledgements": "Acknowledgements",
    "acknowledgments": "Acknowledgements",

    "appendix": "Appendix",
    "appendices": "Appendix",

    "evaluation": "Evaluation",
    "evaluation metrics": "Evaluation Metrics",

    "case study": "Case Study",
    "case studies": "Case Studies",

    "data availability": "Data Availability",
    "conflict of interest": "Conflict of Interest",
    "conflicts of interest": "Conflict of Interest",

    "author contributions": "Author Contributions",
    "funding": "Funding",
    "supplementary material": "Supplementary Material",
}


# -------------------------------------------------------------------
# TEXT UTILITIES
# -------------------------------------------------------------------

def clean_extracted_text(text):
    """
    Perform conservative cleanup.

    Do not collapse all whitespace because line breaks,
    mathematical formatting, tables, and lists matter.
    """

    if not text:
        return ""

    text = str(text)

    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")
    text = text.replace("\u00a0", " ")
    text = text.replace("\u200b", "")
    text = text.replace("\ufeff", "")
    text = text.replace("\x00", "")

    text = "\n".join(
        line.rstrip()
        for line in text.split("\n")
    )

    return text.strip()


def normalize_text(text):
    """Normalize text for comparisons without changing stored content."""

    text = str(text).lower()
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def normalize_for_duplicate_check(text):
    """
    Normalize Markdown and whitespace for conservative
    duplicate detection.

    This is only used for comparison, never for displayed text.
    """

    text = clean_extracted_text(text)

    text = re.sub(
        r"<!--.*?-->",
        "",
        text,
        flags=re.DOTALL
    )

    text = re.sub(
        r"<br\s*/?>",
        " ",
        text,
        flags=re.IGNORECASE
    )

    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"[*_`#]", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip().lower()


def clean_heading_candidate(text):
    """Remove Markdown heading and formatting syntax."""

    heading = clean_extracted_text(text)

    heading = re.sub(
        r"^\s{0,3}#{1,6}\s*",
        "",
        heading
    )

    heading = re.sub(
        r"^\s*\*\*(.*?)\*\*\s*$",
        r"\1",
        heading
    )

    heading = re.sub(
        r"^\s*(?:chapter\s+)?\d+(?:\.\d+)*[.)]?\s*",
        "",
        heading,
        flags=re.IGNORECASE
    )

    heading = re.sub(
        r"\s*\([^)]*\)\s*$",
        "",
        heading
    )

    heading = re.sub(
        r"[*_`]",
        "",
        heading
    )

    return heading.strip(" :.-–—\n")


# -------------------------------------------------------------------
# HEADING RECOGNITION
# -------------------------------------------------------------------

def identify_section(text):
    """Return a standard academic section label if recognized."""

    heading = normalize_text(
        clean_heading_candidate(text)
    )

    if not heading:
        return None

    return SECTION_HEADINGS.get(heading)


def is_numbered_heading(text):
    """
    Recognize common numbered heading structures.

    Examples:
    1 Introduction
    1.1 Background
    2.3.1 Experimental Setup
    Chapter 2: Methodology
    """

    return bool(
        re.match(
            r"^\s*(?:chapter\s+)?\d+(?:\.\d+)*(?:[.)])?\s+\S",
            text,
            flags=re.IGNORECASE
        )
    )


def looks_like_author_metadata(text):
    """
    Avoid treating common author and affiliation information
    as section headings.

    This is a conservative filter, not a complete author detector.
    """

    normalized = normalize_text(text)

    metadata_indicators = (
        "ph.d.",
        "phd",
        "department of ",
        "university of ",
        "institute of ",
        "school of ",
        "corresponding author",
        "email:",
        "e-mail:",
        "orcid",
    )

    if any(
        indicator in normalized
        for indicator in metadata_indicators
    ):
        return True

    if "@" in normalized:
        return True

    return False


def is_valid_section_header(text):
    """
    Accept layout-detected section headers.

    Standard headings and numbered headings are recognized.
    Unfamiliar headings are preserved.

    Obvious author metadata is not treated as a section.
    """

    heading = clean_heading_candidate(text)

    if not heading:
        return False

    if len(heading) > 180:
        return False

    if looks_like_author_metadata(heading):
        return False

    if identify_section(heading):
        return True

    if is_numbered_heading(text):
        return True

    # Preserve unfamiliar layout-detected section headings.
    return True


def heading_section_name(text):
    """Return a semantic label or preserve the original heading."""

    known = identify_section(text)

    if known:
        return known

    heading = clean_heading_candidate(text)

    if not heading:
        return "Unidentified"

    return heading[:180]


# -------------------------------------------------------------------
# LAYOUT ELEMENT EXTRACTION
# -------------------------------------------------------------------

IGNORED_LAYOUT_CLASSES = {
    "page-header",
    "page-footer",
}


def extract_layout_elements(page_chunk):
    """
    Extract content using PyMuPDF4LLM's page layout boxes.

    Each box provides:
    - index: reading-order position
    - class: semantic element type
    - bbox: position on the page
    - pos: substring range in the extracted Markdown
    """

    original_page_text = page_chunk.get("text", "")

    page_text = clean_extracted_text(
        original_page_text
    )

    page_boxes = page_chunk.get("page_boxes", [])

    elements = []

    if not page_boxes:

        if page_text:
            elements.append({
                "index": 0,
                "class": "text",
                "text": page_text,
                "bbox": None,
            })

        return elements

    for box in page_boxes:

        try:
            element_class = box.get(
                "class",
                "text"
            )

            if element_class in IGNORED_LAYOUT_CLASSES:
                continue

            position = box.get("pos")

            if not position or len(position) != 2:
                continue

            start, end = position

            if (
                not isinstance(start, int)
                or not isinstance(end, int)
                or start < 0
                or end > len(original_page_text)
                or start >= end
            ):
                continue

            original_text = original_page_text[start:end]

            element_text = clean_extracted_text(
                original_text
            )

            if not element_text:
                continue

            elements.append({
                "index": box.get("index", len(elements)),
                "class": element_class,
                "text": element_text,
                "bbox": box.get("bbox"),
            })

        except (TypeError, ValueError, KeyError):
            continue

    elements.sort(
        key=lambda element: element["index"]
    )

    return elements


# -------------------------------------------------------------------
# DUPLICATE ELEMENT DETECTION
# -------------------------------------------------------------------

def bbox_contains(outer, inner, tolerance=2):
    """Check whether one bounding box contains another."""

    if not outer or not inner:
        return False

    try:
        ox0, oy0, ox1, oy1 = outer
        ix0, iy0, ix1, iy1 = inner

        return (
            ox0 - tolerance <= ix0
            and oy0 - tolerance <= iy0
            and ox1 + tolerance >= ix1
            and oy1 + tolerance >= iy1
        )

    except (TypeError, ValueError):
        return False


def boxes_overlap(first, second):
    """Check whether two bounding boxes overlap."""

    if not first or not second:
        return False

    try:
        ax0, ay0, ax1, ay1 = first
        bx0, by0, bx1, by1 = second

        intersection_width = max(
            0,
            min(ax1, bx1) - max(ax0, bx0)
        )

        intersection_height = max(
            0,
            min(ay1, by1) - max(ay0, by0)
        )

        intersection_area = (
            intersection_width * intersection_height
        )

        area_a = max(0, ax1 - ax0) * max(0, ay1 - ay0)
        area_b = max(0, bx1 - bx0) * max(0, by1 - by0)

        smaller_area = min(area_a, area_b)

        if smaller_area == 0:
            return False

        return intersection_area / smaller_area >= 0.80

    except (TypeError, ValueError):
        return False


def is_duplicate_element(candidate, existing):
    """
    Detect duplicate content only when there is strong evidence.
    """

    candidate_text = normalize_for_duplicate_check(
        candidate["text"]
    )

    if len(candidate_text) < 12:
        return False

    for previous in existing:

        previous_text = normalize_for_duplicate_check(
            previous["text"]
        )

        if len(previous_text) < 12:
            continue

        if (
            candidate_text == previous_text
            and boxes_overlap(
                candidate["bbox"],
                previous["bbox"]
            )
        ):
            return True

        if (
            len(candidate_text) < len(previous_text)
            and candidate_text in previous_text
            and bbox_contains(
                previous["bbox"],
                candidate["bbox"]
            )
        ):
            return True

    return False


def remove_duplicate_elements(elements):
    """Remove only confidently identified duplicate layout boxes."""

    unique_elements = []

    for element in elements:

        if is_duplicate_element(
            element,
            unique_elements
        ):
            continue

        unique_elements.append(element)

    return unique_elements


# -------------------------------------------------------------------
# PAGE TEXT RECONSTRUCTION
# -------------------------------------------------------------------

def build_page_text(elements):
    """
    Reconstruct page text in layout reading order.

    Markdown generated by PyMuPDF4LLM is retained.
    """

    parts = []

    for element in elements:

        text = element["text"].strip()

        if not text:
            continue

        parts.append(text)

    return "\n\n".join(parts).strip()


# -------------------------------------------------------------------
# SECTION CONSTRUCTION
# -------------------------------------------------------------------

def split_elements_into_sections(
    elements,
    current_section="Unidentified",
    page_number=1
):
    """
    Split page elements using layout-detected section headings.

    Special first-page handling:
    - An explicit 'title' layout box is never a section heading.
    - The first unnumbered, unrecognized section-header on
      page 1 is conservatively treated as a possible document title.
    - Its text is preserved in the extracted content.
    - Recognized and numbered headings remain valid sections.

    Section state continues across page boundaries.
    """

    sections = []
    current_content = []

    first_page_title_skipped = False

    for element in elements:

        element_class = element["class"]
        element_text = element["text"]

        # A layout box explicitly classified as a title
        # must never become a research-paper section.
        is_heading = (
            element_class == "section-header"
            and is_valid_section_header(element_text)
        )

        # First-page title safeguard.
        #
        # Some PDFs have their document title incorrectly
        # classified as a section-header by the layout engine.
        #
        # Only the first unnumbered, unrecognized heading
        # is treated as a possible document title.
        if (
            page_number == 1
            and not first_page_title_skipped
            and is_heading
            and not identify_section(element_text)
            and not is_numbered_heading(element_text)
        ):
            is_heading = False
            first_page_title_skipped = True

        if is_heading:

            if current_content:

                section_text = "\n\n".join(
                    current_content
                ).strip()

                if section_text:
                    sections.append({
                        "section": current_section,
                        "text": section_text,
                    })

            current_section = heading_section_name(
                element_text
            )

            current_content = [element_text]

        else:
            current_content.append(element_text)

    if current_content:

        section_text = "\n\n".join(
            current_content
        ).strip()

        if section_text:
            sections.append({
                "section": current_section,
                "text": section_text,
            })

    return sections, current_section


# -------------------------------------------------------------------
# MAIN PDF EXTRACTION FUNCTION
# -------------------------------------------------------------------

def extract_text_from_pdf(pdf_bytes):
    """
    Extract a PDF into page-level text and section information.

    Uses PyMuPDF4LLM for general-purpose layout-aware extraction.

    The function signature and output structure are compatible
    with the existing ResearchLens backend.
    """

    if not pdf_bytes:
        raise ValueError(
            "The uploaded PDF is empty."
        )

    pages = []

    try:

        with pymupdf.open(
            stream=pdf_bytes,
            filetype="pdf"
        ) as document:

            if document.needs_pass:
                raise ValueError(
                    "This PDF is password-protected."
                )

            if len(document) == 0:
                raise ValueError(
                    "The PDF does not contain any pages."
                )

            extracted_pages = pymupdf4llm.to_markdown(
                document,
                page_chunks=True,
                header=False,
                footer=False,
                use_ocr=True,
            )

            if not isinstance(extracted_pages, list):
                raise ValueError(
                    "The PDF parser returned an unexpected result."
                )

            if len(extracted_pages) != len(document):
                raise ValueError(
                    "The parser did not return content for every page."
                )

            current_section = "Unidentified"

            for page_number, page_chunk in enumerate(
                extracted_pages,
                start=1
            ):

                elements = extract_layout_elements(
                    page_chunk
                )

                elements = remove_duplicate_elements(
                    elements
                )

                full_text = build_page_text(
                    elements
                )

                if not full_text:
                    pages.append({
                        "page": page_number,
                        "text": "",
                        "sections": [],
                    })
                    continue

                sections, current_section = (
                    split_elements_into_sections(
                        elements,
                        current_section,
                        page_number
                    )
                )

                pages.append({
                    "page": page_number,
                    "text": full_text,
                    "sections": sections,
                })

    except ValueError:
        raise

    except Exception as error:
        raise ValueError(
            "Unable to read this PDF. "
            "It may be corrupted, invalid, or unsupported."
        ) from error

    if not any(
        page["text"].strip()
        for page in pages
    ):
        raise ValueError(
            "No readable text was extracted from this PDF. "
            "It may be scanned or image-based and require OCR."
        )

    return pages
