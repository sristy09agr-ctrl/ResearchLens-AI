
def chunk_pages(pages, paper_name, chunk_size=200, overlap=40):

    # Validate chunking parameters
    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than zero.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "Overlap must be non-negative and smaller than chunk size."
        )

    chunks = []
    chunk_id = 1

    for page in pages:

        text = page.get("text", "")
        page_number = page.get("page")

        # Convert page text into words
        words = text.split()

        # Skip empty pages
        if not words:
            continue

        start = 0

        while start < len(words):

            end = min(start + chunk_size, len(words))

            # Extract the current chunk
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)

            chunks.append({
                "text": chunk_text,
                "paper": paper_name,
                "chunk_id": chunk_id,
                "page_start": page_number,
                "page_end": page_number,
                "section": page.get("section", "Unidentified"),
                "word_start": start,
                "word_end": end
            })

            chunk_id += 1

            # Move forward while retaining overlapping words
            start += chunk_size - overlap

    return chunks
