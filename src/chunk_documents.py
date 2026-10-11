import json
from pathlib import Path
from typing import Any

from transformers import AutoTokenizer


# Configuration
PROCESSED_ROOT = Path("data/processed/hypertension")
OUTPUT_FILE = Path("data/chunks/hypertension_chunks.jsonl")

MAX_TOKENS = 500
OVERLAP_TOKENS = 100
TOKENIZER_NAME = "BAAI/bge-m3"

INPUT_FILES = [
    PROCESSED_ROOT / "who/who.json",
    PROCESSED_ROOT / "medlineplus/medical_encyclopedia.json",
    PROCESSED_ROOT / "medlineplus/blood_pressure_measurement.json",
    PROCESSED_ROOT / "cdc/hypertension_management_toolkit.json",
]


# Tokenization helpers
def load_tokenizer():
    """Load the same tokenizer used by BAAI/bge-m3 downstream."""
    return AutoTokenizer.from_pretrained(
        TOKENIZER_NAME,
        use_fast=True,
    )


def encode_content(text: str, tokenizer) -> list[int]:
    """Tokenize content without special tokens for safe text splitting."""
    return tokenizer.encode(text, add_special_tokens=False)


def count_tokens(text: str, tokenizer) -> int:
    """
    Count tokens as a model input would be tokenized, including special tokens.
    This mirrors the tokenizer's default special-token behavior used by the
    downstream Sentence Transformers embedding pipeline.
    """
    if not text:
        return 0

    return len(
        tokenizer.encode(
            text,
            add_special_tokens=True,
        )
    )


def decode(token_ids: list[int], tokenizer) -> str:
    """Convert token IDs back to text."""
    return tokenizer.decode(
        token_ids,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False,
    ).strip()


# Content normalization
def normalize_content(content: Any) -> list[str]:
    """Convert content into separate non-empty paragraphs/items."""
    if content is None:
        return []

    if isinstance(content, list):
        result = []
        for item in content:
            if item is None:
                continue
            text = str(item).strip()
            if text:
                result.append(text)
        return result

    if isinstance(content, str):
        return [
            line.strip()
            for line in content.splitlines()
            if line.strip()
        ]

    text = str(content).strip()
    return [text] if text else []


def elements_to_text(elements: list[str]) -> str:
    """Join elements while preserving their boundaries."""
    return "\n".join(
        element.strip()
        for element in elements
        if element.strip()
    )


# Section context
def build_prefix(document_title: str, section_path: list[str]) -> str:
    """Build document and section context prepended to every chunk."""
    section = " > ".join(section_path)
    return (
        f"Document: {document_title}\n"
        f"Section: {section}\n\n"
    )


# Section extraction
def extract_sections(document: dict) -> list[dict]:
    """Extract content-bearing sections from flat or hierarchical JSON."""
    sections = document.get("sections", [])
    if not isinstance(sections, list):
        raise ValueError("Document does not contain a valid 'sections' list.")

    result = []

    def walk(nodes, parent_path):
        for node in nodes:
            if not isinstance(node, dict):
                continue

            title = (
                node.get("title")
                or node.get("section")
                or "Untitled Section"
            )
            current_path = parent_path + [title]

            if "content" in node:
                content = node["content"]
            elif "lines" in node:
                content = node["lines"]
            elif "text" in node:
                content = node["text"]
            else:
                content = []

            elements = normalize_content(content)
            if elements:
                result.append({
                    "title": title,
                    "path": current_path,
                    "elements": elements,
                })

            children = node.get("children", [])
            if children:
                walk(children, current_path)

    walk(sections, [])
    return result


# Oversized element handling
def split_oversized_element(
    text: str,
    tokenizer,
    max_tokens: int,
) -> list[str]:
    """
    Split a long element into pieces. Each returned piece is re-tokenized
    and checked including special tokens, so decoded pieces cannot silently
    exceed the configured token budget.
    """
    token_ids = encode_content(text, tokenizer)

    if count_tokens(text, tokenizer) <= max_tokens:
        return [text]

    pieces = []
    start = 0

    while start < len(token_ids):
        end = min(start + max_tokens, len(token_ids))
        piece = decode(token_ids[start:end], tokenizer)

        # Decoding and re-tokenizing can alter token boundaries. Shrink until
        # the actual decoded piece fits the budget.
        while end > start and count_tokens(piece, tokenizer) > max_tokens:
            end -= 1
            piece = decode(token_ids[start:end], tokenizer)

        if end == start:
            raise ValueError(
                "Unable to split an oversized element into a token-safe piece."
            )

        if piece:
            pieces.append(piece)

        start = end

    # Final safeguard: every piece must fit when independently tokenized.
    for piece in pieces:
        piece_tokens = count_tokens(piece, tokenizer)
        if piece_tokens > max_tokens:
            raise ValueError(
                f"Split piece has {piece_tokens} tokens; maximum is {max_tokens}."
            )

    return pieces


def prepare_elements(
    elements: list[str],
    tokenizer,
    prefix: str,
    max_tokens: int,
) -> list[str]:
    """
    Keep elements intact where possible. If an element is too large once
    combined with its prefix, split it and verify every piece with that prefix.
    """
    prepared = []
    prefix_tokens = count_tokens(prefix, tokenizer)
    initial_budget = max_tokens - prefix_tokens - 4

    if initial_budget <= 0:
        raise ValueError(
            f"Prefix leaves insufficient room for content: {prefix_tokens} tokens."
        )

    for element in elements:
        if count_tokens(prefix + element, tokenizer) <= max_tokens:
            prepared.append(element)
            continue

        # Start with a conservative budget, then verify the actual combined
        # prefix + decoded piece. Shrink pieces if tokenization boundaries differ.
        pieces = split_oversized_element(
            element,
            tokenizer,
            initial_budget,
        )

        for piece in pieces:
            while count_tokens(prefix + piece, tokenizer) > max_tokens:
                piece_ids = encode_content(piece, tokenizer)
                if len(piece_ids) <= 1:
                    raise ValueError(
                        "A content piece cannot fit together with its section prefix."
                    )
                piece = decode(piece_ids[:-1], tokenizer)
            if piece:
                prepared.append(piece)

    return prepared


# Section chunking
def chunk_section(
    elements: list[str],
    tokenizer,
    prefix: str,
    max_tokens: int,
) -> list[str]:
    """
    Chunk one section by measuring the exact final input: prefix + joined text.
    Chunks do not cross section boundaries. Overlap prefers complete elements.
    """
    elements = prepare_elements(elements, tokenizer, prefix, max_tokens)
    if not elements:
        return []

    chunks = []
    current_elements = []

    def fits(items):
        candidate_text = elements_to_text(items)
        return count_tokens(prefix + candidate_text, tokenizer) <= max_tokens

    for element in elements:
        if not current_elements:
            if not fits([element]):
                raise ValueError(
                    "An element cannot fit within the maximum size with its prefix."
                )
            current_elements = [element]
            continue

        candidate = current_elements + [element]

        # Count the exact final model input, including prefix and separators.
        if fits(candidate):
            current_elements = candidate
            continue

        chunks.append(elements_to_text(current_elements))

        # Select complete trailing elements for overlap.
        overlap_elements = []
        for previous in reversed(current_elements):
            candidate_overlap = [previous] + overlap_elements
            if count_tokens(
                elements_to_text(candidate_overlap),
                tokenizer,
            ) <= OVERLAP_TOKENS:
                overlap_elements = candidate_overlap
            else:
                break

        # Ensure overlap plus the new element fits the exact final input.
        while overlap_elements and not fits(overlap_elements + [element]):
            overlap_elements.pop(0)

        current_elements = overlap_elements + [element]

        if not fits(current_elements):
            raise ValueError(
                "Unable to create a chunk within the configured token budget."
            )

    if current_elements:
        chunks.append(elements_to_text(current_elements))

    # Final exact validation, including the prefix.
    for index, chunk in enumerate(chunks, start=1):
        actual_tokens = count_tokens(prefix + chunk, tokenizer)
        if actual_tokens > max_tokens:
            raise ValueError(
                f"Section chunk {index} has {actual_tokens} final tokens; "
                f"maximum is {max_tokens}."
            )

    return chunks


# Document processing
def process_document(
    input_file: Path,
    tokenizer,
    starting_chunk_id: int,
):
    """Process one JSON document and return its chunks and next ID."""
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found:\n{input_file}")

    with input_file.open("r", encoding="utf-8") as f:
        document = json.load(f)

    metadata = document.get("metadata", {})

    document_title = (
        metadata.get("document_title")
        or metadata.get("title")
        or document.get("title")
        or input_file.stem
    )
    source = metadata.get("source") or document.get("source") or "Unknown"
    document_type = (
        metadata.get("document_type")
        or metadata.get("source_type")
    )
    topic = (
        metadata.get("topic")
        or document.get("topic")
        or document.get("disease")
    )

    sections = extract_sections(document)
    chunks = []
    next_chunk_id = starting_chunk_id

    for section in sections:
        section_title = section["title"]
        section_path = section["path"]
        elements = section["elements"]

        if not elements:
            continue

        prefix = build_prefix(document_title, section_path)
        prefix_tokens = count_tokens(prefix, tokenizer)

        if prefix_tokens >= MAX_TOKENS:
            raise ValueError(
                "Section prefix leaves no token budget for content.\n"
                f"Document: {document_title}\n"
                f"Section: {section_path}\n"
                f"Prefix tokens: {prefix_tokens}\n"
                f"Maximum: {MAX_TOKENS}"
            )

        section_chunks = chunk_section(
            elements,
            tokenizer,
            prefix,
            MAX_TOKENS,
        )
        total_section_chunks = len(section_chunks)

        for chunk_index, content in enumerate(section_chunks, start=1):
            final_text = prefix + content
            final_token_count = count_tokens(final_text, tokenizer)
            content_token_count = count_tokens(content, tokenizer)

            if final_token_count > MAX_TOKENS:
                raise ValueError(
                    "CHUNK EXCEEDS MAXIMUM SIZE\n"
                    f"Document: {document_title}\n"
                    f"Section: {section_path}\n"
                    f"Chunk: {chunk_index}/{total_section_chunks}\n"
                    f"Tokens: {final_token_count}\n"
                    f"Maximum: {MAX_TOKENS}"
                )

            chunks.append({
                "chunk_id": f"chunk_{next_chunk_id:06d}",
                "text": final_text,
                "metadata": {
                    "source": source,
                    "document_title": document_title,
                    "document_type": document_type,
                    "topic": topic,
                    "section": section_title,
                    "section_path": section_path,
                    "chunk_index": chunk_index,
                    "total_section_chunks": total_section_chunks,
                },
                "content_token_count": content_token_count,
                "token_count": final_token_count,
            })
            next_chunk_id += 1

    return chunks, next_chunk_id


# Validation
def validate_chunks(chunks: list[dict], tokenizer):
    """Validate IDs, exact token counts, size limits, and metadata."""
    if not chunks:
        raise ValueError("No chunks were generated.")

    chunk_ids = [chunk["chunk_id"] for chunk in chunks]
    if len(chunk_ids) != len(set(chunk_ids)):
        raise ValueError("Duplicate chunk IDs detected.")

    required_fields = [
        "source",
        "document_title",
        "section",
        "section_path",
    ]

    for chunk in chunks:
        actual_tokens = count_tokens(chunk["text"], tokenizer)
        stored_tokens = chunk["token_count"]

        if actual_tokens != stored_tokens:
            raise ValueError(
                f"Token count mismatch for {chunk['chunk_id']}: "
                f"stored={stored_tokens}, actual={actual_tokens}"
            )

        if actual_tokens > MAX_TOKENS:
            raise ValueError(
                f"Chunk {chunk['chunk_id']} has {actual_tokens} tokens; "
                f"maximum is {MAX_TOKENS}."
            )

        if not chunk["text"].strip():
            raise ValueError(f"Empty chunk: {chunk['chunk_id']}")

        metadata = chunk.get("metadata", {})
        for field in required_fields:
            if field not in metadata:
                raise ValueError(
                    f"Missing metadata '{field}' in {chunk['chunk_id']}"
                )


# Output
def save_jsonl(chunks: list[dict], output_file: Path):
    """Save each chunk as one JSON object per line."""
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with output_file.open("w", encoding="utf-8") as f:
        for chunk in chunks:
            f.write(json.dumps(chunk, ensure_ascii=False) + "\n")


# Main pipeline
def main():
    tokenizer = load_tokenizer()
    print(f"Tokenizer: {TOKENIZER_NAME}")
    print(f"Maximum final chunk size: {MAX_TOKENS} tokens")
    print(f"Overlap target: {OVERLAP_TOKENS} tokens")

    all_chunks = []
    next_chunk_id = 1

    for input_file in INPUT_FILES:
        document_chunks, next_chunk_id = process_document(
            input_file,
            tokenizer,
            next_chunk_id,
        )
        print(f"{input_file}: {len(document_chunks)} chunks")
        all_chunks.extend(document_chunks)

    validate_chunks(all_chunks, tokenizer)
    save_jsonl(all_chunks, OUTPUT_FILE)

    print(
        f"Chunking completed successfully: "
        f"{len(all_chunks)} chunks saved to {OUTPUT_FILE}"
    )


if __name__ == "__main__":
    main()
