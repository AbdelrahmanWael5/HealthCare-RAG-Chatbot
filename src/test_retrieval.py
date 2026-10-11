
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


VECTOR_DB_DIR = Path("data/vector_db/hypertension")
MODEL_NAME = "BAAI/bge-m3"
TOP_K = 5


def load_vector_store():
    """Load the existing medical FAISS vector store."""

    if not VECTOR_DB_DIR.exists():
        raise FileNotFoundError(
            f"Vector store directory not found: {VECTOR_DB_DIR}"
        )

    embedding_model = HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
    )

    vector_store = FAISS.load_local(
        str(VECTOR_DB_DIR),
        embedding_model,
        allow_dangerous_deserialization=True,
    )

    print(f"Loaded vectors: {vector_store.index.ntotal}")
    print(f"Vector dimensions: {vector_store.index.d}")

    return vector_store


def test_query(vector_store, query, k=TOP_K):
    """Retrieve and display the most similar medical chunks."""

    print("\n" + "=" * 80)
    print(f"QUERY: {query}")
    print("=" * 80)

    results = vector_store.similarity_search_with_score(
        query,
        k=k,
    )

    for rank, (document, score) in enumerate(results, start=1):
        print(f"\n--- Result {rank} | Inner Product: {score:.4f} ---")
        print(f"Metadata: {document.metadata}")
        print(f"Text:\n{document.page_content}")


def main():
    vector_store = load_vector_store()

    test_queries = [
        "What are the risk factors for hypertension?",
        "How can I measure my blood pressure correctly at home?",
        "What lifestyle changes can help control high blood pressure?",
        "What complications can uncontrolled hypertension cause?",
    ]

    for query in test_queries:
        test_query(vector_store, query)


if __name__ == "__main__":
    main()
