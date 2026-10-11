
import json
from pathlib import Path

import numpy as np

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_community.vectorstores.utils import DistanceStrategy
from langchain_huggingface import HuggingFaceEmbeddings


INPUT_FILE = Path("data/embeddings/hypertension_embeddings.jsonl")
OUTPUT_DIR = Path("data/vector_db/hypertension")

MODEL_NAME = "BAAI/bge-m3"
EMBEDDING_DIMENSION = 1024


def load_embeddings(input_file: Path) -> list[dict]:
    """Load and validate embedding records from JSONL."""

    if not input_file.exists():
        raise FileNotFoundError(
            f"Input file not found: {input_file}"
        )

    records = []

    with input_file.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number}: {exc}"
                ) from exc

            required_fields = {
                "chunk_id",
                "text",
                "metadata",
                "embedding",
            }

            missing_fields = required_fields - record.keys()

            if missing_fields:
                raise ValueError(
                    f"Missing fields on line {line_number}: "
                    f"{sorted(missing_fields)}"
                )

            if not isinstance(record["chunk_id"], str) or not record["chunk_id"].strip():
                raise ValueError(
                    f"Invalid chunk_id on line {line_number}"
                )

            if not isinstance(record["text"], str) or not record["text"].strip():
                raise ValueError(
                    f"Invalid text on line {line_number}"
                )

            if not isinstance(record["metadata"], dict):
                raise ValueError(
                    f"Invalid metadata on line {line_number}"
                )

            records.append(record)

    if not records:
        raise ValueError("No embedding records found.")

    return records


def validate_embeddings(records: list[dict]) -> np.ndarray:
    """Validate vector dimensions, IDs, and numerical values."""

    chunk_ids = [record["chunk_id"] for record in records]

    if len(chunk_ids) != len(set(chunk_ids)):
        raise ValueError("Duplicate chunk IDs found.")

    try:
        embeddings = np.asarray(
            [record["embedding"] for record in records],
            dtype=np.float32,
        )
    except (TypeError, ValueError) as exc:
        raise ValueError(
            "Embeddings must contain numeric values."
        ) from exc

    expected_shape = (len(records), EMBEDDING_DIMENSION)

    if embeddings.shape != expected_shape:
        raise ValueError(
            f"Unexpected embedding shape: {embeddings.shape}. "
            f"Expected: {expected_shape}"
        )

    if not np.isfinite(embeddings).all():
        raise ValueError(
            "Embeddings contain NaN or infinite values."
        )

    return embeddings


def load_embedding_model() -> HuggingFaceEmbeddings:
    """Load the model used to embed incoming search queries."""

    return HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs={
            "device": "cpu",
        },
        encode_kwargs={
            "normalize_embeddings": True,
        },
    )


def build_vector_store(
    records: list[dict],
    embeddings: np.ndarray,
    embedding_model: HuggingFaceEmbeddings,
) -> FAISS:
    """Build a LangChain FAISS store from existing embeddings."""

    documents = []
    ids = []

    for record in records:
        metadata = {
            **record["metadata"],
            "chunk_id": record["chunk_id"],
        }

        for field in ("content_token_count", "token_count"):
            if field in record:
                metadata[field] = record[field]

        documents.append(
            Document(
                page_content=record["text"],
                metadata=metadata,
            )
        )

        ids.append(record["chunk_id"])

    # Build the FAISS index using the embeddings already generated.
    vector_store = FAISS.from_embeddings(
        text_embeddings=[
            (document.page_content, embedding.tolist())
            for document, embedding in zip(documents, embeddings)
        ],
        embedding=embedding_model,
        metadatas=[document.metadata for document in documents],
        ids=ids,
        distance_strategy=DistanceStrategy.MAX_INNER_PRODUCT,
    )

    return vector_store


def main():
    """Build, save, reload, and validate the vector store."""

    records = load_embeddings(INPUT_FILE)
    print(f"Loaded {len(records)} embedding records.")

    embeddings = validate_embeddings(records)
    print(f"Validated embeddings: {embeddings.shape}")

    embedding_model = load_embedding_model()

    vector_store = build_vector_store(
        records,
        embeddings,
        embedding_model,
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    vector_store.save_local(str(OUTPUT_DIR))

    print(f"Vector store saved to: {OUTPUT_DIR}")

    # Reload the saved store and validate it.
    loaded_store = FAISS.load_local(
        str(OUTPUT_DIR),
        embedding_model,
        allow_dangerous_deserialization=True,
    )

    if loaded_store.index.ntotal != len(records):
        raise ValueError(
            f"Expected {len(records)} vectors, "
            f"found {loaded_store.index.ntotal}"
        )

    if loaded_store.index.d != EMBEDDING_DIMENSION:
        raise ValueError(
            f"Expected dimension {EMBEDDING_DIMENSION}, "
            f"found {loaded_store.index.d}"
        )

    print("Vector store built and reloaded successfully.")
    print(f"Vectors: {loaded_store.index.ntotal}")
    print(f"Dimensions: {loaded_store.index.d}")


if __name__ == "__main__":
    main()
