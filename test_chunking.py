from modules.chunking import chunk_pages

# Sample text containing 450 words
pages = [
    {
        "page": 1,
        "text": "research " * 450
    }
]

# Generate chunks
chunks = chunk_pages(pages, "test.pdf")

# Display results
print("Total chunks:", len(chunks))

for chunk in chunks:
    print("\nChunk ID:", chunk["chunk_id"])
    print("Paper:", chunk["paper"])
    print("Page:", chunk["page"])
    print("Number of words:", len(chunk["text"].split()))
