
import re


# ---------------------------------------------------------
# 1. CONTENT DETECTION
# ---------------------------------------------------------

def is_list_item(line):
    """Check whether a line begins a numbered or bulleted item."""

    return bool(
        re.match(
            r"^\s*(?:"
            r"\d+[.)]\s+|"
            r"[•●▪◦‣]\s*|"
            r"[-*]\s+|"
            r"[☐☑✓✔]\s*"
            r")",
            line
        )
    )


def is_table_line(line):
    """Identify Markdown table rows."""

    return "|" in line and len(line.split("|")) >= 3


def is_formula_line(line):
    """Identify common mathematical block markers."""

    stripped = line.strip().lower()

    return (
        stripped.startswith("$$")
        or stripped.endswith("$$")
        or stripped.startswith(r"\[")
        or stripped.endswith(r"\]")
        or stripped.startswith(r"\begin{")
        or stripped.startswith("<!-- formula")
        or stripped.startswith("<math")
    )


def is_heading_line(line):
    """Identify Markdown headings."""

    return bool(
        re.match(r"^\s{0,3}#{1,6}\s+", line)
    )


def is_heading_only(text):
    """
    Return True when a section contains only Markdown headings.
    """

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    return bool(lines) and all(
        is_heading_line(line)
        for line in lines
    )


# ---------------------------------------------------------
# 2. SENTENCE SPLITTING
# ---------------------------------------------------------

def split_into_sentences(text):
    """Split prose at sentence boundaries."""

    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return []

    sentences = re.split(
        r'(?<=[.!?])\s+',
        text
    )

    return [
        sentence.strip()
        for sentence in sentences
        if sentence.strip()
    ]


# ---------------------------------------------------------
# 3. SPLIT CONTENT INTO MEANINGFUL UNITS
# ---------------------------------------------------------

def split_into_units(text):
    """
    Divide text into meaningful units.

    Tables and formula blocks remain together.
    List items retain continuation lines.
    Paragraphs retain their sentence structure.
    """

    lines = text.splitlines()

    units = []
    current_unit = []
    current_type = "paragraph"

    def save_unit():
        nonlocal current_unit

        content = "\n".join(current_unit).strip()

        if content:
            units.append({
                "text": content,
                "type": current_type
            })

        current_unit = []

    for line in lines:

        line = line.rstrip()

        if not line.strip():
            save_unit()
            current_type = "paragraph"
            continue

        if is_formula_line(line):

            if current_type != "formula":
                save_unit()
                current_type = "formula"

            current_unit.append(line)

            if (
                line.strip().startswith("$$")
                and line.strip().endswith("$$")
                and line.strip() != "$$"
            ):
                save_unit()
                current_type = "paragraph"

            elif (
                line.strip().startswith("<!-- formula")
                and line.strip().endswith("-->")
            ):
                save_unit()
                current_type = "paragraph"

            continue

        if current_type == "formula":

            current_unit.append(line)

            if (
                line.strip().endswith("$$")
                or line.strip() == r"\]"
                or line.strip().startswith(r"\end{")
                or line.strip().endswith("-->")
            ):
                save_unit()
                current_type = "paragraph"

            continue

        if is_table_line(line):

            if current_type != "table":
                save_unit()
                current_type = "table"

            current_unit.append(line)
            continue

        if current_type == "table":
            save_unit()
            current_type = "paragraph"

        if is_heading_line(line):

            save_unit()
            current_type = "heading"
            current_unit.append(line)
            save_unit()
            current_type = "paragraph"
            continue

        if is_list_item(line):

            save_unit()
            current_type = "list"
            current_unit.append(line)
            continue

        if not current_unit:
            current_type = "paragraph"

        current_unit.append(line)

    save_unit()

    return units


# ---------------------------------------------------------
# 4. PAGE CONTINUITY
# ---------------------------------------------------------

def can_join_page_continuation(previous_text, next_text):
    """Conservatively detect a paragraph continuing onto the next page."""

    previous = previous_text.strip()
    following = next_text.strip()

    if not previous or not following:
        return False

    first_line = following.splitlines()[0]

    if (
        is_list_item(first_line)
        or is_heading_line(first_line)
        or is_table_line(first_line)
        or is_formula_line(first_line)
    ):
        return False

    if re.search(r'[.!?]["\')\]]?$', previous):
        return False

    if previous.endswith(":"):
        return False

    if following[0].islower():
        return True

    if previous.endswith("-"):
        return True

    return False


def merge_page_continuations(page_units):
    """Join likely paragraph continuations across pages."""

    if not page_units:
        return []

    merged = []

    for unit in page_units:

        if (
            merged
            and merged[-1]["type"] == "paragraph"
            and unit["type"] == "paragraph"
            and merged[-1]["page_end"] < unit["page_start"]
            and can_join_page_continuation(
                merged[-1]["text"],
                unit["text"]
            )
        ):

            previous_text = merged[-1]["text"].rstrip()
            next_text = unit["text"].lstrip()

            if previous_text.endswith("-"):
                merged[-1]["text"] = (
                    previous_text[:-1] + next_text
                )
            else:
                merged[-1]["text"] = (
                    previous_text + " " + next_text
                )

            merged[-1]["page_end"] = unit["page_end"]

        else:
            merged.append(unit.copy())

    return merged


# ---------------------------------------------------------
# 5. SECTION GROUPING
# ---------------------------------------------------------

def create_section_groups(pages):
    """
    Combine consecutive occurrences of the same section.

    Genuine heading-only sections are attached to the next
    section containing actual content.

    Unidentified content, including document titles and author
    metadata, is always preserved separately.
    """

    groups = []
    pending_headings = []

    for page in pages:

        page_number = page.get("page")

        sections = page.get("sections", [])

        if not sections and page.get("text", "").strip():

            sections = [{
                "section": "Unidentified",
                "text": page["text"]
            }]

        for section_data in sections:

            section_name = section_data.get(
                "section",
                "Unidentified"
            )

            section_text = section_data.get(
                "text",
                ""
            ).strip()

            if not section_text:
                continue

            page_entry = {
                "page": page_number,
                "text": section_text
            }

            # IMPORTANT:
            # Never carry Unidentified content forward.
            # It may contain the document title or author details.
            if (
                section_name != "Unidentified"
                and is_heading_only(section_text)
            ):

                pending_headings.append(page_entry)
                continue

            # Attach genuine pending section headings.
            combined_pages = (
                pending_headings + [page_entry]
            )

            pending_headings = []

            if (
                groups
                and groups[-1]["section"] == section_name
            ):

                groups[-1]["pages"].extend(
                    combined_pages
                )

            else:

                groups.append({
                    "section": section_name,
                    "pages": combined_pages
                })

    # Preserve heading-only sections at the end of the document.
    for heading_page in pending_headings:

        groups.append({
            "section": "Unidentified",
            "pages": [heading_page]
        })

    return groups


# ---------------------------------------------------------
# 6. PREPARE SENTENCE-LEVEL UNITS
# ---------------------------------------------------------

def prepare_units(section_group, chunk_size):
    """Prepare content units with original source positions."""

    page_units = []

    for page_data in section_group["pages"]:

        units = split_into_units(page_data["text"])

        for unit in units:

            page_units.append({
                "text": unit["text"],
                "type": unit["type"],
                "page_start": page_data["page"],
                "page_end": page_data["page"]
            })

    page_units = merge_page_continuations(page_units)

    prepared = []
    word_position = 0

    for unit in page_units:

        unit_type = unit["type"]
        unit_text = unit["text"]

        if unit_type == "paragraph":
            pieces = split_into_sentences(unit_text)
        else:
            pieces = [unit_text]

        for piece in pieces:

            piece_word_count = len(piece.split())

            if not piece_word_count:
                continue

            prepared.append({
                "text": piece,
                "type": unit_type,
                "page_start": unit["page_start"],
                "page_end": unit["page_end"],
                "word_start": word_position,
                "word_end": word_position + piece_word_count
            })

            word_position += piece_word_count

    return prepared


# ---------------------------------------------------------
# 7. SELECT SENTENCE-AWARE OVERLAP
# ---------------------------------------------------------

def select_overlap_units(previous_units, overlap):
    """Select complete sentences from the previous chunk."""

    if overlap <= 0 or not previous_units:
        return [], 0

    overlap_units = []
    overlap_count = 0

    for unit in reversed(previous_units):

        if unit["type"] != "paragraph":
            break

        unit_words = (
            unit["word_end"] - unit["word_start"]
        )

        if overlap_units and overlap_count + unit_words > overlap:
            break

        overlap_units.insert(0, unit)
        overlap_count += unit_words

        if overlap_count >= overlap:
            break

    return overlap_units, overlap_count


# ---------------------------------------------------------
# 8. BUILD CHUNKS
# ---------------------------------------------------------

def build_chunk(
    current_units,
    paper_name,
    chunk_id,
    section_name
):
    """Build a chunk using the existing database fields."""

    first_unit = current_units[0]
    last_unit = current_units[-1]

    chunk_text = "\n\n".join(
        unit["text"]
        for unit in current_units
    )

    return {
        "text": chunk_text,
        "paper": paper_name,
        "chunk_id": chunk_id,
        "page_start": min(
            unit["page_start"]
            for unit in current_units
        ),
        "page_end": max(
            unit["page_end"]
            for unit in current_units
        ),
        "section": section_name,
        "word_start": first_unit["word_start"],
        "word_end": last_unit["word_end"]
    }


# ---------------------------------------------------------
# 9. CHUNK A CONTINUOUS SECTION
# ---------------------------------------------------------

def chunk_section(
    section_group,
    paper_name,
    chunk_size,
    overlap,
    starting_chunk_id
):
    """Create sequential chunks for one continuous section."""

    section_name = section_group["section"]

    units = prepare_units(
        section_group,
        chunk_size
    )

    chunks = []
    current_units = []
    current_word_count = 0
    chunk_id = starting_chunk_id

    for unit in units:

        unit_word_count = (
            unit["word_end"] - unit["word_start"]
        )

        if (
            current_units
            and current_word_count + unit_word_count > chunk_size
        ):

            chunks.append(
                build_chunk(
                    current_units,
                    paper_name,
                    chunk_id,
                    section_name
                )
            )

            chunk_id += 1

            overlap_units, overlap_count = (
                select_overlap_units(
                    current_units,
                    overlap
                )
            )

            current_units = overlap_units
            current_word_count = overlap_count

        current_units.append(unit)
        current_word_count += unit_word_count

    if current_units:

        chunks.append(
            build_chunk(
                current_units,
                paper_name,
                chunk_id,
                section_name
            )
        )

        chunk_id += 1

    return chunks, chunk_id


# ---------------------------------------------------------
# 10. MAIN FUNCTION
# ---------------------------------------------------------

def chunk_pages(pages, paper_name, chunk_size=200, overlap=40):
    """Convert extracted PDF sections into retrieval-friendly chunks."""

    if chunk_size <= 0:
        raise ValueError(
            "Chunk size must be greater than zero."
        )

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "Overlap must be non-negative and smaller than chunk size."
        )

    chunks = []
    chunk_id = 1

    section_groups = create_section_groups(pages)

    for section_group in section_groups:

        section_chunks, chunk_id = chunk_section(
            section_group=section_group,
            paper_name=paper_name,
            chunk_size=chunk_size,
            overlap=overlap,
            starting_chunk_id=chunk_id
        )

        chunks.extend(section_chunks)

    return chunks
