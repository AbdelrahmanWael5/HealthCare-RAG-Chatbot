from bs4 import BeautifulSoup
from pathlib import Path

# Configuration
INPUT_FILE = Path("data/raw/hypertension/medlineplus/blood_pressure_measurement.html")
OUTPUT_FILE = Path("data/raw/hypertension/medlineplus/blood_pressure_measurement.txt")

# Read the HTML file
def read_html(file_path):
    html = file_path.read_text(encoding="utf-8")
    return html

# Clean text from an HTML element
def clean_text(element):
    text = element.get_text(" ", strip=True)
    return text

# Extract one content block
def extract_content_block(block):

    # Find the section title
    title_element = block.find("h2")

    if title_element is None:
        return None

    title = clean_text(title_element)

    # Ignore the references block

    if title == "References":
        return None

    lines = []

    # Extract paragraphs and lists
    for element in block.find_all(["p", "ul", "ol"], recursive=False):

        # Paragraph
        if element.name == "p":

            text = clean_text(element)
            if text:
                lines.append(text)

        # Lists
        elif element.name in ["ul", "ol"]:

            for item in element.find_all("li", recursive=False):
                text = clean_text(item)
                if text:
                    lines.append(f"- {text}")


    # Ignore empty blocks
    if not lines:
        return None

    return {"title": title, "lines": lines}


# 5. Extract the complete document
def extract_document(html):

    soup = BeautifulSoup(html, "html.parser")

    # Find the main content
    main_content = soup.find("div", class_="main")

    if main_content is None:
        raise ValueError(
            "Could not find the main "
            "MedlinePlus content."
        )

    # Find all content blocks
    content_blocks = main_content.find_all("div", class_="mp-content")

    if not content_blocks:
        raise ValueError(
            "Could not find any "
            "mp-content blocks."
        )

    sections = []

    # Extract each content block
    for block in content_blocks:

        section = extract_content_block(block)
        if section is not None:
            sections.append(section)

    return sections

# Convert sections to text
def convert_to_text(sections):

    lines = []

    # Document title
    lines.append("Blood Pressure Measurement")
    lines.append("")

    # Add each section
    for section in sections:

        lines.append(section["title"])
        lines.append("")

        for line in section["lines"]:
            lines.append(line)

        lines.append("")

    return "\n".join(lines)

# Save extracted text
def save_text(text, file_path):

    file_path.write_text(text, encoding="utf-8")
    print(f"Saved extracted text to: {file_path}")

def main():

    print(
        "Extracting MedlinePlus "
        "blood pressure measurement")

    # Read raw HTML
    html = read_html(INPUT_FILE)

    # Extract content
    sections = extract_document(html)

    # Convert to readable text
    text = convert_to_text(sections)

    # Save the result
    save_text(text, OUTPUT_FILE)

    print()
    print(f"Content sections extracted: {len(sections)}")
    print()
    print("Sections:")

    for section in sections:
        print(f"- {section['title']}")

    print()
    print("Extraction completed.")

if __name__ == "__main__":

    main()