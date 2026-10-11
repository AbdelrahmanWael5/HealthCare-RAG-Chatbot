from pypdf import PdfReader
from pathlib import Path

# Configuration
INPUT_FILE = Path(
    "data/raw/hypertension/cdc/hypertension_management_toolkit.pdf")

OUTPUT_FILE = Path("data/raw/hypertension/cdc/hypertension_management_toolkit.txt")

# Extract text from the PDF
def extract_pdf(pdf_path):

    reader = PdfReader(pdf_path)
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):

        text = page.extract_text()

        if text is None:
            text = ""

        pages.append({"page": page_number, "text": text})

    return pages

# Convert pages to readable text
def convert_to_text(pages):

    lines = []
    lines.append("CDC Hypertension Management Program Implementation Toolkit")
    lines.append("")

    for page in pages:

        lines.append(f"PAGE {page['page']}")
        lines.append("")

        text = page["text"].strip()

        if text:
            lines.append(text)

        lines.append("")

    return "\n".join(lines)

# Save extracted text
def save_text(text, output_path):
    output_path.write_text(text, encoding="utf-8")
    print(f"Saved extracted text to: {output_path}")


def main():

    print("Extracting CDC hypertension management toolkit")

    # Extract every PDF page
    pages = extract_pdf(INPUT_FILE)
    print(f"Pages extracted: {len(pages)}")

    # Convert to readable text
    text = convert_to_text(pages)

    # Save the result
    save_text(text, OUTPUT_FILE)
    print("CDC extraction completed.")

if __name__ == "__main__":

    main()