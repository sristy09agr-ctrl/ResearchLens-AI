
import pymupdf
import glob
import os

pdf_files = glob.glob("data/uploads/*.pdf")

if not pdf_files:
    print("No PDFs found in data/uploads/")
    raise SystemExit

pdf_path = pdf_files[0]

print("Inspecting:", os.path.basename(pdf_path))

doc = pymupdf.open(pdf_path)

for page_number in [1, 2]:
    if page_number >= len(doc):
        continue

    page = doc[page_number]

    print("\n" + "=" * 60)
    print("PAGE", page_number + 1)
    print("=" * 60)

    print("\n--- TABLE DETECTION ---")

    for strategy in ["lines", "text"]:

        try:
            finder = page.find_tables(strategy=strategy)

            print(f"\nStrategy: {strategy}")
            print("Tables found:", len(finder.tables))

            for i, table in enumerate(finder.tables):
                print(f"\nTable {i + 1}")
                print("Bounding box:", table.bbox)
                print("Extracted rows:")

                for row in table.extract():
                    print(row)

        except Exception as error:
            print("Detection error:", error)

    print("\n--- WORD POSITIONS ---")

    words = page.get_text("words", sort=True)

    for word in words:
        x0, y0, x1, y1, text = word[:5]

        print(
            f"x={x0:7.1f} y={y0:7.1f} "
            f"-> {text}"
        )

doc.close()
