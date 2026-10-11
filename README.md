# Hypertension Healthcare RAG Assistant

A medical question-answering assistant focused on
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
-   [Example Questions](#example-questions)
-   [Evaluation and Limitations](#evaluation-and-limitations)

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

- **Domain-specific knowledge base:** Focused on hypertension and blood pressure awareness.
- **Trusted medical sources:** Content collected from WHO, CDC, and MedlinePlus resources.
- **Structured data processing:** Source documents are extracted, cleaned, and organized into structured JSON files, then split into overlapping text chunks and stored as JSONL records with relevant metadata.
- **Section-aware chunking:** Creates chunks of up to approximately 500 tokens with around 100 tokens of overlap to preserve context across chunk boundaries.
- **Hybrid Retrieval:** Combines dense semantic retrieval using `BAAI/bge-m3` and FAISS with sparse lexical retrieval to capture both conceptual similarity and exact keyword matches.
- **Reciprocal Rank Fusion (RRF):** Merges the ranked results from dense and sparse retrieval into a unified ranking, leveraging the complementary strengths of both retrieval methods without requiring their raw scores to be directly comparable.
- **Reranking:** Applies a reranker to the fused candidate results to improve relevance ordering, prioritizing passages that are most relevant to the user's query before they are passed to the language model. This helps reduce irrelevant context and can improve the quality and grounding of generated answers.
- **LLM-based answer generation:** Uses `mistralai/Mistral-7B-Instruct-v0.2` to generate answers based on the retrieved context.
- **Structured output validation:** Uses Pydantic to validate the generated response structure.
- **Source attribution:** Preserves and returns source metadata to help users trace answers to the retrieved documents.
- **Interactive Streamlit interface:** Provides a chat UI with conversation history and source details.

## Architecture

```text
WHO / CDC / MedlinePlus Source Documents
                  |
                  v
       Extraction and Preprocessing
                  |
                  v
       Structured JSON Documents
                  |
                  v
        Section-Aware Chunking
                  |
                  v
      Text Chunks + Source Metadata
               (JSONL)
                  |
                  v
          BAAI/bge-m3 Embeddings
                  |
                  v
           FAISS Vector Index
                  |
                  |
             User Question
                  |
                  v
          +-------------------+
          |  Hybrid Retrieval  |
          +-------------------+
             /             \
            v               v
     Dense Retrieval   Sparse Retrieval
     (FAISS + BGE-M3)  (Lexical Search)
            |               |
            v               v
       Ranked Dense     Ranked Sparse
         Results          Results
            \               /
             v             v
          Reciprocal Rank Fusion
                 (RRF)
                  |
                  v
          Fused Candidate Results
                  |
                  v
              Reranker
                  |
                  v
       Top-Ranked Relevant Passages
             + Metadata
                  |
                  v
       Mistral-7B-Instruct-v0.2
                  |
                  v
      Structured Answer Generation
                  |
                  v
     Answer + Sources + Status Fields
                  |
                  v
           Streamlit Chat UI
```

### Retrieval-Augmented Generation (RAG)

1. **Ingest:** Extract text from source documents and normalize it into structured records while preserving relevant document metadata.
2. **Chunk:** Split the extracted text into overlapping passages while preserving document titles and section paths.
3. **Embed:** Encode chunks using `BAAI/bge-m3`, producing normalized, 1,024-dimensional embeddings.
4. **Index:** Store the embeddings and associated documents in a local FAISS vector index for dense similarity search.
5. **Hybrid Retrieve:** Retrieve candidate passages using both dense semantic retrieval and sparse lexical retrieval to capture conceptual similarity and exact keyword matches.
6. **Fuse Results:** Apply **Reciprocal Rank Fusion (RRF)** to combine the ranked results from both retrieval methods into a unified candidate list.
7. **Rerank:** Use a reranker to evaluate and reorder the fused candidates by their relevance to the user's question, prioritizing the most relevant passages for the generation stage.
8. **Generate:** Pass the selected, reranked passages to `mistralai/Mistral-7B-Instruct-v0.2` to generate a context-grounded response.
9. **Validate and Display:** Validate the structured response using Pydantic, verify that cited source numbers correspond to retrieved documents, and display the answer and source details in the Streamlit interface.

RAG, result fusion, reranking, and schema validation can improve retrieval relevance, traceability, and answer grounding, but they do not guarantee that every generated statement is factually correct or fully supported by the retrieved evidence.

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


## Technology Stack

  --------------------------------------------------------------------------------------
  Component               Technology                             Purpose
  ----------------------- -------------------------------------- -----------------------
  Language                Python                                 Core implementation

  Embedding model         `BAAI/bge-m3`                          Encodes chunks and
                                                                 questions as vectors

  Embedding integration   Hugging Face and LangChain             Loads and runs
                                                                 embeddings
                                                                    
  Dense Retrieval         FAISS                                  Retrieves semantically
                                                                 similar document chunks
                                                                        
  Sparse Retrieval        BM25                                   Matches important terms 
                                                                 and exact keywords

  Hybrid Fusion           Reciprocal Rank Fusion (RRF)           Combines dense and sparse retrieval 
                                                                 rankings into a unified candidate list

  Reranking               Cross-Encoder Reranker                 Reorders retrieved candidates according
                                                                 to their relevance to the user's query

  Generation model        `mistralai/Mistral-7B-Instruct-v0.2`   Generates answers grounded in the
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

## Installation

### 1. Clone the repository

``` bash
git clone https://github.com/AbdelrahmanWael5/HealthCare-RAG-Chatbot
cd <YOUR_REPOSITORY_DIRECTORY>
```

### 2. Install dependencies

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

## Example Questions

-   What are common risk factors for hypertension?
-   How can blood pressure be measured at home?
-   What lifestyle changes can help manage high blood pressure?
-   What complications can hypertension cause?
-   What does the available information say about monitoring blood
    pressure?
