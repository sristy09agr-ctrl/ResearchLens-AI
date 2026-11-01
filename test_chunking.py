
from modules.chunking import chunk_pages


# Create realistic sample content with sentence boundaries.
sentence = (
    "Research papers present important findings and explain "
    "the methods used to obtain reliable scientific results."
)

# Two pages belonging to the same section.
pages = [
    {
        "page": 1,
        "sections": [
            {
                "section": "Introduction",
                "text": " ".join([sentence] * 25)
            }
        ]
    },
    {
        "page": 2,
        "sections": [
            {
                "section": "Introduction",
                "text": " ".join([sentence] * 10)
            }
        ]
    }
]


# Generate chunks.
chunks = chunk_pages(
    pages,
    "test.pdf",
    chunk_size=200,
    overlap=40
)


# Display results.
print("Total chunks:", len(chunks))

for chunk in chunks:

    print("\n" + "=" * 50)

    print("Chunk ID:", chunk["chunk_id"])
    print("Paper:", chunk["paper"])
    print(
        "Pages:",
        chunk["page_start"],
        "to",
        chunk["page_end"]
    )
    print("Section:", chunk["section"])
    print("Word start:", chunk["word_start"])
    print("Word end:", chunk["word_end"])
    print("Number of words:", len(chunk["text"].split()))

    print("\nChunk text:")
    print(chunk["text"])


# Basic validation.
assert len(chunks) > 1, "Expected multiple chunks."

assert [
    chunk["chunk_id"] for chunk in chunks
] == list(range(1, len(chunks) + 1)), "Chunk IDs are not sequential."

for chunk in chunks:

    assert chunk["page_start"] <= chunk["page_end"]
    assert chunk["word_start"] <= chunk["word_end"]
    assert chunk["text"].strip()

print("\nAll basic chunking tests passed.")
