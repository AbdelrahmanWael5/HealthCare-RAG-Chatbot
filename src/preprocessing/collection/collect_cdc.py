import requests
from pathlib import Path


# Configuration
OUTPUT_DIR = Path("data/raw/hypertension/cdc")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


HEADERS = {"User-Agent": "Medical-RAG-Research-Project/1.0"}

# CDC documents
CDC_DOCUMENTS = {"hypertension_management_toolkit": "https://stacks.cdc.gov/view/cdc/251793/cdc_251793_DS1.pdf",}


# Download a document
def download_document(url, output_path):

    print(f"Downloading: {url}")

    response = requests.get(url, headers=HEADERS, timeout=60)

    response.raise_for_status()

    output_path.write_bytes(response.content)
    print(f"Saved: {output_path}")


def main():

    print(f"Collecting {len(CDC_DOCUMENTS)} CDC documents")

    for document_name, url in CDC_DOCUMENTS.items():

        print()
        print(f"Processing: {document_name}")

        output_path = (OUTPUT_DIR / f"{document_name}.pdf")
        try:
            download_document(url, output_path)

        except Exception as error:
            print(f"Error: {error}")

    print("CDC collection completed.")



if __name__ == "__main__":

    main()