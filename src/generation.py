import json
import logging
from pathlib import Path
from typing import Any

import torch
from pydantic import BaseModel, ConfigDict, Field, field_validator
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
)

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.output_parsers import PydanticOutputParser


# --------------------------------------------------
# 1. Configuration
# --------------------------------------------------

VECTOR_DB_DIR = Path("data/vector_db/hypertension")

EMBEDDING_MODEL_NAME = "BAAI/bge-m3"
GENERATION_MODEL_NAME = "mistralai/Mistral-7B-Instruct-v0.2"

TOP_K = 4
MAX_NEW_TOKENS = 500
MAX_INPUT_TOKENS = 12000

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# --------------------------------------------------
# 2. Structured output schema
# --------------------------------------------------

class MedicalAnswer(BaseModel):
    """Schema expected from the generation model."""

    model_config = ConfigDict(extra="forbid")

    answer: str = Field(
        min_length=1,
        description="The answer to the user's medical question.",
    )
    used_source_numbers: list[int] = Field(
        default_factory=list,
        description=(
            "1-based numbers of supplied context sources that directly "
            "support the answer."
        ),
    )
    insufficient_information: bool = Field(
        description=(
            "True if the retrieved context is not sufficient to answer "
            "the question reliably."
        ),
    )

    @field_validator("used_source_numbers")
    @classmethod
    def validate_source_numbers(cls, values: list[int]) -> list[int]:
        if any(number < 1 for number in values):
            raise ValueError("Source numbers must be positive integers.")
        if len(values) != len(set(values)):
            raise ValueError("Duplicate source numbers are not allowed.")
        return values


output_parser = PydanticOutputParser(pydantic_object=MedicalAnswer)


# --------------------------------------------------
# 3. Load the embedding model and FAISS database
# --------------------------------------------------

def load_vector_store() -> FAISS:
    """Load the existing medical FAISS vector store."""

    if not VECTOR_DB_DIR.exists():
        raise FileNotFoundError(
            f"Vector store directory not found: {VECTOR_DB_DIR}"
        )

    embedding_model = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    # Only load a local index.pkl that you created and trust.
    vector_store = FAISS.load_local(
        str(VECTOR_DB_DIR),
        embedding_model,
        allow_dangerous_deserialization=True,
    )

    logger.info(
        "Loaded medical vector store: %s vectors",
        vector_store.index.ntotal,
    )
    return vector_store


# --------------------------------------------------
# 4. Load Mistral with 4-bit quantization
# --------------------------------------------------

def load_generation_model():
    """Load Mistral 7B using bitsandbytes 4-bit quantization."""

    if not torch.cuda.is_available():
        raise RuntimeError(
            "This 4-bit bitsandbytes configuration requires a compatible "
            "CUDA environment. A CPU-only fallback is not configured."
        )

    tokenizer = AutoTokenizer.from_pretrained(GENERATION_MODEL_NAME)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    quantization_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=torch.float16,
    )

    model = AutoModelForCausalLM.from_pretrained(
        GENERATION_MODEL_NAME,
        quantization_config=quantization_config,
        device_map="auto",
        torch_dtype=torch.float16,
    )

    model.eval()
    return tokenizer, model


# --------------------------------------------------
# 5. Generate text
# --------------------------------------------------

def generate_text(prompt: str, tokenizer, model) -> str:
    """Generate only new tokens; do not silently truncate the prompt."""

    inputs = tokenizer(
        prompt,
        return_tensors="pt",
        truncation=False,
    )

    input_token_count = inputs["input_ids"].shape[1]
    if input_token_count > MAX_INPUT_TOKENS:
        raise ValueError(
            f"Prompt is too long ({input_token_count} tokens). "
            f"Maximum configured input length is {MAX_INPUT_TOKENS}. "
            "Reduce the retrieved context or shorten the question."
        )

    input_device = model.get_input_embeddings().weight.device
    inputs = {key: value.to(input_device) for key, value in inputs.items()}

    with torch.inference_mode():
        outputs = model.generate(
            **inputs,
            max_new_tokens=MAX_NEW_TOKENS,
            do_sample=False,
            pad_token_id=tokenizer.pad_token_id,
            eos_token_id=tokenizer.eos_token_id,
        )

    generated_tokens = outputs[0][input_token_count:]
    return tokenizer.decode(
        generated_tokens,
        skip_special_tokens=True,
    ).strip()


# --------------------------------------------------
# 6. Build the RAG prompt
# --------------------------------------------------

def build_prompt(query: str, documents) -> str:
    """Construct a grounded medical prompt with numbered sources."""

    context_parts = []

    for source_number, document in enumerate(documents, start=1):
        metadata = document.metadata
        source_name = metadata.get("source", "Unknown")
        title = metadata.get("document_title", "Untitled")
        section = metadata.get("section", "Unknown section")

        context_parts.append(
            f"[Source {source_number}]\n"
            f"Source: {source_name}\n"
            f"Document: {title}\n"
            f"Section: {section}\n"
            f"Content:\n{document.page_content}"
        )

    context = "\n\n".join(context_parts)
    format_instructions = output_parser.get_format_instructions()

    return f"""<s>[INST]
You are a medical information assistant specializing in hypertension.

Answer the user's question using only the supplied context.

Rules:
1. Use only information directly supported by the supplied context.
2. Prioritize sources that directly answer the question.
3. Do not combine specialized clinical protocols with general patient
   instructions unless the user explicitly asks about those protocols.
4. Do not invent facts, recommendations, medication doses, or diagnoses.
5. If the context is insufficient to answer reliably, say so and set
   insufficient_information to true.
6. Do not provide an individualized diagnosis or medication dose.
7. Include only source numbers that directly support your answer.
8. Source numbers are the 1-based labels [Source 1], [Source 2], etc.
9. Keep the answer concise and understandable to a patient.
10. If you cannot provide the requested answer from the retrieved context,
set insufficient_information to true, even if the context contains
related information about the topic.
11. Return only one valid JSON object matching the schema. Do not wrap it
    in Markdown fences and do not add text before or after the JSON.

Context:
{context}

User question:
{query}

{format_instructions}
[/INST]"""


# --------------------------------------------------
# 7. Stable response helpers
# --------------------------------------------------

def _response(
    answer: str,
    sources: list[dict[str, Any]] | None = None,
    insufficient_information: bool = True,
    error: str | None = None,
) -> dict[str, Any]:
    """Return the same response shape for success and failure cases."""

    return {
        "answer": answer,
        "sources": sources or [],
        "insufficient_information": insufficient_information,
        "error": error,
    }


def _map_sources(parsed_answer: MedicalAnswer, documents) -> list[dict[str, Any]]:
    """Map model-selected source numbers to actual retrieved documents."""

    valid_numbers = set(range(1, len(documents) + 1))
    selected_numbers = set(parsed_answer.used_source_numbers)

    if not selected_numbers.issubset(valid_numbers):
        invalid = sorted(selected_numbers - valid_numbers)
        raise ValueError(f"Model returned invalid source numbers: {invalid}")

    source_map = {
        number: document
        for number, document in enumerate(documents, start=1)
    }

    sources = []
    for number in parsed_answer.used_source_numbers:
        metadata = source_map[number].metadata
        sources.append({
            "source": metadata.get("source", "Unknown"),
            "document_title": metadata.get("document_title", "Untitled"),
            "section": metadata.get("section", "Unknown section"),
            "chunk_id": metadata.get("chunk_id"),
        })

    return sources


# --------------------------------------------------
# 8. Ask a question
# --------------------------------------------------

def ask_question(query: str, vector_store: FAISS, tokenizer, model) -> dict:
    """
    Retrieve context, generate and parse an answer.

    Stable return shape:
    {
        "answer": str,
        "sources": list[dict],
        "insufficient_information": bool,
        "error": str | None
    }
    """

    if not isinstance(query, str) or not query.strip():
        return _response(
            answer="Please enter a question.",
            insufficient_information=True,
            error="invalid_query",
        )

    try:
        documents = vector_store.similarity_search(
            query.strip(),
            k=TOP_K,
        )

        if not documents:
            return _response(
                answer=(
                    "I could not find relevant information in the "
                    "available medical sources."
                ),
                insufficient_information=True,
            )

        prompt = build_prompt(query.strip(), documents)
        raw_output = generate_text(prompt, tokenizer, model)

        try:
            parsed_answer = output_parser.parse(raw_output)
        except Exception as exc:
            logger.warning("Output parsing failed: %s", exc)
            logger.debug("Raw model output: %s", raw_output)
            return _response(
                answer=(
                    "I couldn't reliably format an answer from the "
                    "available information. Please try rephrasing your question."
                ),
                insufficient_information=True,
                error="output_parse_error",
            )

        try:
            sources = _map_sources(parsed_answer, documents)
        except ValueError as exc:
            logger.warning("Source validation failed: %s", exc)
            return _response(
                answer=(
                    "I couldn't verify the sources for the generated answer, "
                    "so I can't provide it reliably."
                ),
                insufficient_information=True,
                error="source_validation_error",
            )

        return _response(
            answer=parsed_answer.answer,
            sources=sources,
            insufficient_information=parsed_answer.insufficient_information,
        )

    except Exception:
        logger.exception("Medical RAG request failed")
        return _response(
            answer=(
                "Sorry, I couldn't process your question right now. "
                "Please try again."
            ),
            insufficient_information=True,
            error="request_failed",
        )


# --------------------------------------------------
# 9. Run the application
# --------------------------------------------------

def main():
    print("Loading medical RAG components...")

    vector_store = load_vector_store()
    tokenizer, model = load_generation_model()

    print("\nHypertension Medical RAG is ready.")
    print("Type 'exit' to stop.\n")

    while True:
        query = input("Ask a medical question: ").strip()

        if query.lower() == "exit":
            break

        result = ask_question(query, vector_store, tokenizer, model)

        print("\nResponse:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("\n" + "-" * 70 + "\n")


if __name__ == "__main__":
    main()
