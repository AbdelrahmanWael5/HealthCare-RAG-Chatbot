from bs4 import BeautifulSoup
from pathlib import Path


# File locations
INPUT_FILE = Path("data/raw/hypertension/who/hypertension_who.html")
OUTPUT_FILE = Path("data/raw/hypertension/who/hypertension_who.txt")

# Read the HTML file
def read_html(file_path):

    html = file_path.read_text(encoding="utf-8")
    return html

# Extract the article content
def extract_article(html):

    soup = BeautifulSoup(html, "html.parser")

    # Find the WHO fact-sheet article
    article = soup.find("article", class_="sf-detail-body-wrapper")

    if article is None:
        raise ValueError("Could not find the WHO article.")

    # Remove elements that are not part of the actual article
    unwanted_elements = ["script", "style"]

    for element_name in unwanted_elements:

        for element in article.find_all(element_name):
            element.decompose()

    # Convert the article into text
    text = article.get_text(separator="\n", strip=True)
    return text

# Save the extracted text
def save_text(text, file_path):
    file_path.write_text(text, encoding="utf-8")
    print(f"Saved extracted text to: {file_path}")

# Main program
def main():

    print("Extracting WHO hypertension article")

    # Read the raw HTML
    html = read_html(INPUT_FILE)

    # Extract the article
    text = extract_article(html)

    # Save the extracted text
    save_text(text, OUTPUT_FILE)

    print("Extraction completed.")


if __name__ == "__main__":

    main()