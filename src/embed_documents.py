
import json
from pathlib import Path

import torch
from tqdm import tqdm
from langchain_huggingface import HuggingFaceEmbeddings


INPUT_FILE = Path("data/chunks/hypertension_chunks.jsonl")
OUTPUT_FILE = Path("data/embeddings/hypertension_embeddings.jsonl")

MODEL_NAME = "BAAI/bge-m3"

BATCH_SIZE = 16
EXPECTED_DIMENSION = 1024


def get_device():
    """Return the available computation device."""
    return "cuda" if torch.cuda.is_available() else "cpu"


def load_chunks(input_file):
    """Load and validate chunk records from JSONL."""
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found:\n{input_file}")

    chunks = []

    with input_file.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                chunk = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid JSON on line {line_number}: {e}"
                ) from e

            if not chunk.get("chunk_id"):
                raise ValueError(
                    f"Missing chunk_id on line {line_number}"
                )

            if not isinstance(chunk.get("text"), str):
                raise ValueError(
                    f"Missing or invalid text on line {line_number}"
                )

            if not chunk["text"].strip():
                raise ValueError(
                    f"Empty text for {chunk['chunk_id']}"
                )

            chunks.append(chunk)

    if not chunks:
        raise ValueError("No chunks were loaded.")

    return chunks


def load_embedding_model(device):
    """Load BGE-M3 through Sentence Transformers via LangChain."""
    return HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs={
            "device": device,
        },
        encode_kwargs={
            "batch_size": BATCH_SIZE,
            "normalize_embeddings": True,
        },
        show_progress=True,
    )


def generate_embeddings(chunks, embedding_model):
    """Generate one dense embedding per chunk."""
    all_embeddings = []

    for start in tqdm(
        range(0, len(chunks), BATCH_SIZE),
        desc="Generating embeddings",
        unit="batch",
    ):
        batch = chunks[start:start + BATCH_SIZE]

        texts = [chunk["text"] for chunk in batch]

        batch_embeddings = embedding_model.embed_documents(texts)

        all_embeddings.extend(batch_embeddings)

    if len(all_embeddings) != len(chunks):
        raise ValueError(
            "Number of embeddings does not match number of chunks."
        )

    return all_embeddings


def validate_embeddings(chunks, embeddings):
    """Validate dimensions and numeric values."""
    if not embeddings:
        raise ValueError("No embeddings were generated.")

    for chunk, embedding in zip(chunks, embeddings):
        if len(embedding) != EXPECTED_DIMENSION:
            raise ValueError(
                f"Wrong embedding dimension for {chunk['chunk_id']}. "
                f"Expected: {EXPECTED_DIMENSION}; "
                f"actual: {len(embedding)}"
            )

        if not all(
            isinstance(value, (float, int))
            for value in embedding
        ):
            raise ValueError(
                f"Non-numeric embedding for {chunk['chunk_id']}"
            )


def save_embeddings(chunks, embeddings, output_file):
    """Save each chunk with its embedding and metadata."""
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as f:
        for chunk, embedding in zip(chunks, embeddings):
            record = {
                **chunk,
                "embedding": embedding,
            }

            f.write(
                json.dumps(record, ensure_ascii=False) + "\n"
            )


def main():
    device = get_device()
    print(f"Using device: {device}")

    chunks = load_chunks(INPUT_FILE)
    print(f"Loaded {len(chunks)} chunks.")

    embedding_model = load_embedding_model(device)

    embeddings = generate_embeddings(
        chunks,
        embedding_model,
    )

    validate_embeddings(chunks, embeddings)

    save_embeddings(
        chunks,
        embeddings,
        OUTPUT_FILE,
    )

    print(
        f"Embedding completed successfully: "
        f"{len(embeddings)} vectors, "
        f"{EXPECTED_DIMENSION} dimensions each."
    )
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
