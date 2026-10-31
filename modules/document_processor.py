
import pymupdf
import re


# Common research-paper section headings
SECTION_HEADINGS = {
    "abstract": "Abstract",
    "introduction": "Introduction",
    "background": "Background",
    "related work": "Related Work",
    "literature review": "Literature Review",
    "materials and methods": "Methodology",
    "materials and methods": "Methodology",
    "methodology": "Methodology",
    "methods": "Methodology",
    "experimental setup": "Experiments",
    "experimental design": "Experiments",
    "experiments": "Experiments",
    "results": "Results",
    "experimental results": "Results",
    "discussion": "Discussion",
    "results and discussion": "Results and Discussion",
    "limitations": "Limitations",
    "study limitations": "Limitations",
    "conclusion": "Conclusion",
    "conclusions": "Conclusion",
    "future work": "Future Work",
    "references": "References",
    "acknowledgements": "Acknowledgements",
    "acknowledgments": "Acknowledgements"
}


def identify_section(line):

    # Remove numbering such as 1. Introduction or 2.3 Methods
    heading = re.sub(
        r"^\s*\d+(?:\.\d+)*[.)]?\s*",
        "",
        line.strip()
    )

    heading = heading.strip(" :.-–—").lower()

    if len(heading) > 80:
        return None

    return SECTION_HEADINGS.get(heading)


def extract_text_from_pdf(pdf_bytes):

    if not pdf_bytes:
        raise ValueError("The uploaded PDF is empty.")

    pages = []
    current_section = "Unidentified"

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

            for page_number, page in enumerate(
                document,
                start=1
            ):

                full_text = page.get_text().strip()
                lines = full_text.splitlines()

                segments = []
                segment_lines = []
                segment_section = current_section

                for line in lines:

                    detected_section = identify_section(line)

                    if detected_section:

                        # Save the previous section's content
                        if segment_lines:
                            segments.append({
                                "section": segment_section,
                                "text": "\n".join(segment_lines).strip()
                            })

                        current_section = detected_section
                        segment_section = current_section
                        segment_lines = [line]

                    else:
                        segment_lines.append(line)

                # Save the final section segment on this page
                if segment_lines:
                    segments.append({
                        "section": segment_section,
                        "text": "\n".join(segment_lines).strip()
                    })

                pages.append({
                    "page": page_number,
                    "text": full_text,
                    "sections": segments
                })

    except ValueError:
        raise

    except Exception as error:
        raise ValueError(
            "Unable to read this PDF. It may be corrupted or invalid."
        ) from error

    # Check whether selectable text was extracted
    if not any(page["text"] for page in pages):
        raise ValueError(
            "No selectable text found. "
            "This may be a scanned or image-based PDF."
        )

    return pages
