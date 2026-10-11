import requests
from pathlib import Path
import time


# Configuration
OUTPUT_DIR = Path("data/raw/hypertension/medlineplus")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

HEADERS = {"User-Agent": "Medical-RAG-Research-Project/1.0"}

# MedlinePlus documents
MEDLINEPLUS_DOCUMENTS = {
    #"health_topic": "https://medlineplus.gov/highbloodpressure.html",
    "medical_encyclopedia": "https://medlineplus.gov/ency/article/000468.htm",
    "blood_pressure_measurement": "https://medlineplus.gov/lab-tests/measuring-blood-pressure/",
}


# Download a webpage
def download_page(url):

    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()

    return response.text

# Save the raw HTML
def save_html(document_name, html):

    file_path = (OUTPUT_DIR / f"{document_name}.html")
    file_path.write_text(html, encoding="utf-8")

    return file_path


def main():

    print(f"Collecting {len(MEDLINEPLUS_DOCUMENTS)} MedlinePlus documents")

    for document_name, url in MEDLINEPLUS_DOCUMENTS.items():

        print()
        print(f"Processing: {document_name}")
        print(f"URL: {url}")

        try:
            html = download_page(url)
            file_path = save_html(document_name, html)
            print(f"Saved: {file_path}")

        except Exception as error:
            print(f"Error: {error}")

        time.sleep(1)


    print()
    print("MedlinePlus collection completed.")


if __name__ == "__main__":

    main()