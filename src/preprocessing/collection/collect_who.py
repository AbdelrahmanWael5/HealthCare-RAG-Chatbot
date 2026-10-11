import requests
from pathlib import Path


# Configuration
OUTPUT_DIR = Path("data/raw/hypertension/who")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# WHO source
WHO_URL = ("https://www.who.int/news-room/fact-sheets/detail/hypertension")
HEADERS = {"User-Agent": "Medical-RAG-Research-Project/1.0"}


# Download the webpage
def download_page(url):

    print("Downloading WHO page")
    response = requests.get(url, headers=HEADERS, timeout=30)

    # Raise an error if the request failed
    response.raise_for_status()

    return response.text

# Save the original HTML
def save_html(html):

    file_path = (OUTPUT_DIR / "hypertension_who.html")
    file_path.write_text(html, encoding="utf-8")
    print(f"Saved HTML to: {file_path}")


# Main program
def main():

    print("Collecting hypertension data from WHO")
    html = download_page(WHO_URL)

    save_html(html)
    print("\nCollection completed successfully.")

if __name__ == "__main__":

    main()