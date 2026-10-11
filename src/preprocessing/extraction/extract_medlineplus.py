from bs4 import BeautifulSoup
from pathlib import Path

# Configuration
INPUT_FILE = Path("data/raw/hypertension/medlineplus/medical_encyclopedia.html")
OUTPUT_FILE = Path("data/raw/hypertension/medlineplus/medical_encyclopedia.txt")

# Sections that belong to our knowledge base
KEEP_SECTIONS = {
    "Causes",
    "Symptoms",
    "Exams and Tests",
    "Treatment",
    "Outlook (Prognosis)",
    "When to Contact a Medical Professional",
    "Prevention",
    "Alternative Names",

}

# Read the HTML file
def read_html(file_path):

    html = file_path.read_text(
        encoding="utf-8"
    )

    return html

# 4. Clean a single text element
def clean_text(element):

    # get_text with a space prevents inline elements such as links from being separated into different lines.
    text = element.get_text(
        " ",
        strip=True
    )

    return text

# Extract the content of one section
def extract_section(section):

    # Find the section title
    title_element = section.find("div", class_="section-title")

    if title_element is None:
        return None

    title = clean_text(title_element)

    # Ignore sections that are not part of our medical knowledge base
    if title not in KEEP_SECTIONS:
        return None

    # Find the section body
    body = section.find("div", class_="section-body")

    if body is None:
        return None

    lines = []

    # Extract paragraphs and lists
    for element in body.find_all(["p", "ul", "ol"], recursive=False):

        # Paragraph
        if element.name == "p":

            text = clean_text(element)
            if text:
                lines.append(text)

        # Unordered or ordered list
        elif element.name in ["ul", "ol"]:

            for item in element.find_all("li", recursive=False):

                text = clean_text(item)
                if text:
                    lines.append(f"- {text}")

    # Return the extracted section
    if not lines:
        return None

    return {"title": title, "lines": lines}

# Extract the medical article
def extract_article(html):

    soup = BeautifulSoup(html, "html.parser")

    # Find the actual encyclopedia article
    article = soup.find("div", id="d-article")

    if article is None:
        raise ValueError(
            "Could not find the MedlinePlus "
            "encyclopedia article."
            )

    # Find the article title
    page_title = soup.find("div", class_="page-title")

    if page_title:
        title = clean_text(page_title)

    else:
        title = "High Blood Pressure"

    # Extract useful medical sections
    sections = []

    for section in article.find_all("div", class_="section"):

        extracted_section = extract_section(section)

        if extracted_section is not None:
            sections.append(extracted_section)

    return {"title": title, "sections": sections}

# Convert the article to readable text
def convert_to_text(article):

    lines = []

    # Article title
    lines.append(article["title"])
    lines.append("")

    # Medical sections
    for section in article["sections"]:

        lines.append(section["title"])
        lines.append("")

        for line in section["lines"]:
            lines.append(line)

        lines.append("")

    return "\n".join(lines)

# Save the extracted text
def save_text(text, file_path):

    file_path.write_text(text, encoding="utf-8")
    print(f"Saved extracted text to: {file_path}")


def main():

    print(
        "Extracting MedlinePlus "
        "medical encyclopedia"
        )

    # Read raw HTML
    html = read_html(INPUT_FILE)

    # Extract the medical article
    article = extract_article(html)

    # Convert to readable text
    text = convert_to_text(article)

    # Save the extracted document
    save_text(text, OUTPUT_FILE)

    print()
    print(f"Medical sections extracted: {len(article['sections'])}")
    print()
    print("Sections:")

    for section in article["sections"]:
        print(f"- {section['title']}")

    print()
    print("Extraction completed.")


if __name__ == "__main__":

    main()