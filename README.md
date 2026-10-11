# Hypertension Healthcare RAG Assistant

An educational medical question-answering assistant focused on
**hypertension (high blood pressure)**. It uses Retrieval-Augmented
Generation (RAG) to retrieve relevant passages from trusted health
resources and generate answers grounded in that context.

> **Medical disclaimer:** This project is for educational and
> informational purposes only. It is not a substitute for professional
> medical advice, diagnosis, or treatment. It must not be used to
> determine an individual's medication or dosage. Consult a qualified
> healthcare professional for personal medical decisions.

## Table of Contents

-   [Project Overview](#project-overview)
-   [Key Features](#key-features)
-   [Architecture](#architecture)
-   [Knowledge Sources](#knowledge-sources)
-   [Technology Stack](#technology-stack)
-   [Project Structure](#project-structure)
-   [Installation](#installation)
-   [Running the Application](#running-the-application)
-   [Pipeline Details](#pipeline-details)
-   [Example Questions](#example-questions)
-   [Evaluation and Limitations](#evaluation-and-limitations)
-   [Safety Considerations](#safety-considerations)
-   [Roadmap](#roadmap)
-   [License](#license)

## Project Overview

General-purpose language models may produce plausible-sounding medical
answers that are incomplete or unsupported. This project explores a more
grounded approach: retrieve relevant content from a curated hypertension
knowledge base, then provide that context to a language model to answer
the user's question.

The current implementation is a **hypertension-focused RAG prototype**
containing document preprocessing, token-aware chunking, embedding
generation, a FAISS vector index, a retrieval-and-generation module, and
a Streamlit chat interface.

## Key Features

-   Domain-specific knowledge base focused on hypertension and
    blood-pressure education.
-   Content collected from WHO, CDC, and MedlinePlus resources.
-   Structured JSON preprocessing and JSONL chunk/embedding artifacts.
-   Token-aware chunks of up to approximately 500 tokens with around 100
    tokens of overlap.
-   Semantic retrieval using `BAAI/bge-m3` embeddings and FAISS.
-   Answer generation with `mistralai/Mistral-7B-Instruct-v0.2`.
-   Structured output validated with Pydantic.
-   Source metadata returned with answers.
-   An `insufficient_information` field intended to identify questions
    the current context cannot adequately answer.
-   Streamlit chat UI with conversation history and source details.
-   Persistent local vector index so it does not need to be rebuilt at
    every application launch.

## Architecture

``` text
WHO / CDC / MedlinePlus source documents
                  |
                  v
       Extraction and preprocessing
                  |
                  v
       Structured JSON documents
                  |
                  v
       Token-aware text chunking
                  |
                  v
      Chunks + source metadata (JSONL)
                  |
                  v
       BAAI/bge-m3 embeddings
                  |
                  v
           FAISS vector index
                  |
                  v
             User question
                  |
                  v
       Query embedding and retrieval
                  |
                  v
      Relevant passages + metadata
                  |
                  v
       Mistral 7B Instruct generation
                  |
                  v
     Answer + sources + status fields
                  |
                  v
           Streamlit chat UI
```

### Retrieval-Augmented Generation (RAG)

1.  **Ingest:** extract text from source documents and normalize it into
    structured records.
2.  **Chunk:** split text into overlapping passages while preserving
    document titles and section paths.
3.  **Embed:** encode chunks using `BAAI/bge-m3`; embeddings are
    normalized and have 1,024 dimensions.
4.  **Index:** store vectors and associated documents in a local FAISS
    index.
5.  **Retrieve:** embed the user's question with the same embedding
    model and retrieve relevant passages.
6.  **Generate:** pass retrieved context to Mistral to produce a
    grounded response.
7.  **Validate and display:** validate the structured response, check
    source-number references against retrieved documents, and display
    the answer and source details in Streamlit.

RAG and schema validation can improve traceability, but they do not
guarantee that every answer is correct or fully supported.

## Knowledge Sources

The current dataset includes material from:

-   **World Health Organization (WHO):** hypertension information and
    public-health guidance.
-   **Centers for Disease Control and Prevention (CDC):** hypertension
    management educational material, including a management toolkit PDF.
-   **MedlinePlus:** medical encyclopedia content and information about
    blood-pressure measurement.

Official websites: - WHO: https://www.who.int/ - CDC:
https://www.cdc.gov/ - MedlinePlus: https://medlineplus.gov/

Current processed files include: - `who.json` -
`medical_encyclopedia.json` - `blood_pressure_measurement.json` -
`hypertension_management_toolkit.json`

These filenames describe the current local dataset; they do not imply
that all content from these organizations has been ingested. Preserve
original URLs, titles, and section metadata when adding sources.

## Technology Stack

  --------------------------------------------------------------------------------------
  Component               Technology                             Purpose
  ----------------------- -------------------------------------- -----------------------
  Language                Python                                 Core implementation

  Embedding model         `BAAI/bge-m3`                          Encodes chunks and
                                                                 questions as vectors

  Embedding integration   Hugging Face and LangChain             Loads and runs
                                                                 embeddings

  Vector database/index   FAISS                                  Similarity search over
                                                                 chunks

  Generation model        `mistralai/Mistral-7B-Instruct-v0.2`   Generates answers using
                                                                 retrieved context

  Model runtime           Hugging Face Transformers              Tokenization and text
                                                                 generation

  Quantization            BitsAndBytes, 4-bit NF4                Reduces model memory
                                                                 use

  RAG integration         LangChain Community                    FAISS vector-store
                                                                 integration

  Output validation       Pydantic                               Validates structured
                                                                 generation output

  User interface          Streamlit                              Interactive chat
                                                                 application
  --------------------------------------------------------------------------------------

## Project Structure

The layout below reflects the current workflow and artifacts. Adjust it
to match the exact contents of your repository.

``` text
healthcare-rag-assistant/
├── app.py
├── src/
│   └── generation.py
├── data/
│   ├── processed/
│   │   └── hypertension/
│   │       ├── who.json
│   │       ├── medical_encyclopedia.json
│   │       ├── blood_pressure_measurement.json
│   │       └── hypertension_management_toolkit.json
│   ├── chunks/
│   │   └── hypertension_chunks.jsonl
│   ├── embeddings/
│   │   └── hypertension_embeddings.jsonl
│   └── vector_db/
│       └── hypertension/
│           ├── index.faiss
│           └── index.pkl
├── requirements.txt
└── README.md
```

The tree includes artifacts used in the workflow. If ingestion,
chunking, and embedding scripts are included in your repository, place
them in a dedicated directory such as `scripts/` or `src/ingestion/` and
document their actual names and commands. `requirements.txt` is
recommended; add a tested, pinned dependency list rather than assuming
one exists.

The persisted FAISS index is located at `data/vector_db/hypertension/`
and currently consists of `index.faiss` and `index.pkl`. Do not commit
model weights or large datasets without considering repository size,
licenses, and data provenance.

## Installation

### 1. Clone the repository

``` bash
git clone <YOUR_REPOSITORY_URL>
cd <YOUR_REPOSITORY_DIRECTORY>
```

Replace the placeholders with your actual repository URL and directory.

### 2. Create a virtual environment

**Windows PowerShell**

``` powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS**

``` bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

If `requirements.txt` is available:

``` bash
pip install -r requirements.txt
```

Core packages used by the current implementation include:

``` bash
pip install streamlit torch transformers accelerate bitsandbytes sentence-transformers langchain langchain-community langchain-huggingface faiss-cpu pydantic
```

Install a PyTorch build compatible with your CUDA version and follow the
BitsAndBytes installation guidance for your OS/GPU. The suitable FAISS
package can vary by environment; avoid mixing incompatible CPU/GPU
packages.

## Running the Application

Run from the repository root, where `app.py` is located:

``` bash
streamlit run app.py
```

Open the local URL printed by Streamlit, usually
`http://localhost:8501`. The app loads the local vector store and
initializes the generation model. The first model load may take time if
model weights need to be downloaded.

### Troubleshooting

-   **Vector store not found:** check that
    `data/vector_db/hypertension/index.faiss` and `index.pkl` exist and
    that you launched Streamlit from the repository root.
-   **Import error for `src.generation`:** verify `src/generation.py`
    exists and run the command from the project root.
-   **CUDA/BitsAndBytes error:** verify the PyTorch/CUDA combination and
    BitsAndBytes installation. The current 4-bit model-loading setup
    expects a compatible NVIDIA GPU environment; CPU-only execution is
    not guaranteed.
-   **Hugging Face warnings or rate limits:** configure a Hugging Face
    token in your environment if needed. Never commit access tokens to
    Git.
-   **Slow startup/high memory use:** loading a 7B model is
    resource-intensive. Consider a smaller model or hardware-appropriate
    configuration.
-   **FAISS optimization warnings:** unavailable CPU instruction-set
    optimizations may cause a slower fallback; check whether an actual
    exception occurs before treating the warning as fatal.

## Pipeline Details

  -------------------------------------------------------------------------------------------------
  Artifact                Path                                              Purpose
  ----------------------- ------------------------------------------------- -----------------------
  Processed source        `data/processed/hypertension/`                    Structured content and
  documents                                                                 metadata

  Text chunks             `data/chunks/hypertension_chunks.jsonl`           One chunk per JSONL
                                                                            record

  Chunk embeddings        `data/embeddings/hypertension_embeddings.jsonl`   Embeddings and
                                                                            associated metadata

  FAISS vectors           `data/vector_db/hypertension/index.faiss`         Similarity-search index

  FAISS document          `data/vector_db/hypertension/index.pkl`           Documents and mappings
  store/mapping                                                             associated with the
                                                                            LangChain FAISS store
  -------------------------------------------------------------------------------------------------

### Updating the knowledge base

When adding a document:

1.  Extract and normalize the text and metadata.
2.  Add it to the processed dataset.
3.  Chunk it using the established chunking rules.
4.  Generate embeddings with the same model and configuration.
5.  Add the vectors and documents to the hypertension index, or rebuild
    the index consistently.
6.  Test retrieval relevance for questions about the new content.
7.  Test answer grounding, source references, and insufficient-context
    behavior.

All vectors in a given index must use the same embedding model and
dimensionality. If the embedding model or important preprocessing rules
change, rebuild the index rather than mixing incompatible vectors.

## Example Questions

-   What are common risk factors for hypertension?
-   How can blood pressure be measured at home?
-   What lifestyle changes can help manage high blood pressure?
-   What complications can hypertension cause?
-   What does the available information say about monitoring blood
    pressure?

For individual treatment decisions---including choosing a medication or
determining a personal dose---the assistant should make the limitations
of its knowledge base clear and direct the user to a qualified
healthcare professional.

## Evaluation and Limitations

The retrieval pipeline has been manually smoke-tested with
representative questions about risk factors, home blood-pressure
measurement, lifestyle changes, and complications. The current local
index contains **172 embedded chunks**. These tests are useful
development checks, not a formal benchmark or evidence of clinical
reliability.

Known limitations:

-   **Limited corpus:** the system covers only the documents in the
    current hypertension dataset.
-   **Potential hallucinations:** retrieval grounding reduces reliance
    on model memory but does not eliminate unsupported statements.
-   **Insufficient-information classification needs work:** a cautious
    answer does not always cause the `insufficient_information` flag to
    be set correctly. This requires explicit tests and improvement.
-   **No clinical validation:** the project has not been established as
    safe for diagnosis, triage, or treatment decisions.
-   **No formal benchmark yet:** retrieval relevance, faithfulness,
    citation correctness, refusal behavior, and latency need systematic
    evaluation.
-   **Hardware requirements:** the current quantized 7B generation model
    expects a compatible GPU setup.
-   **Source freshness:** public-health recommendations may change;
    source versions and update dates should be tracked.

Recommended evaluation work: 1. Build a curated test set with expected
supporting documents and answer criteria. 2. Measure retrieval using
metrics such as Recall@k and MRR. 3. Review answer faithfulness and
source attribution against retrieved passages. 4. Test out-of-scope
questions and personalized medication/dosage requests. 5. Record
latency, memory use, failures, and dependency/model versions. 6. Repeat
tests after changing the corpus, embedding model, prompt, or generation
model.

## Safety Considerations

-   Clearly distinguish educational information from individualized
    medical advice.
-   Do not recommend or calculate personalized prescription doses.
-   Make uncertainty and missing evidence visible.
-   Preserve traceability to the source material and display source
    information.
-   Do not treat retrieved content as automatically correct or
    clinically complete.
-   Do not send personal health information to external services without
    appropriate privacy and security controls.
-   Before real-world or clinical deployment, seek qualified medical
    review, conduct safety testing, and address privacy, security, and
    applicable regulatory requirements.

## Roadmap

-   [ ] Add a reproducible end-to-end ingestion and indexing CLI.
-   [ ] Add a tested, pinned `requirements.txt`.
-   [ ] Add automated tests for chunking, retrieval, structured output,
    and error handling.
-   [ ] Improve insufficient-context detection, especially for
    medication and dosage questions.
-   [ ] Add retrieval and answer-quality evaluation reports.
-   [ ] Display clickable source URLs and relevant excerpts in the UI.
-   [ ] Track source versions, ingestion dates, and update/re-index
    workflows.
-   [ ] Add incremental indexing and support for additional knowledge
    collections if required.
-   [ ] Add performance measurements without storing sensitive user
    information.
-   [ ] Define resource, security, and safety requirements before
    deployment.

## Contributing

Contributions are welcome. Please keep changes scoped and reproducible,
update tests where appropriate, preserve source metadata, and test both
answerable and insufficient-context questions. Never commit credentials,
private health information, or unnecessary large binary artifacts.

## License

No license has been specified in this README. Add a `LICENSE` file
before distributing the project or accepting external contributions, and
verify the terms for source materials, model weights, and dependencies.
