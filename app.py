import streamlit as st

from src.generation import (
    ask_question,
    load_generation_model,
    load_vector_store,
)


st.set_page_config(
    page_title="Hypertension Medical Assistant",
    page_icon="🩺",
    layout="centered",
)

st.title("🩺 Hypertension Medical Assistant")
st.caption(
    "A medical information assistant that answers using the project's "
    "retrieved WHO, CDC, and MedlinePlus content."
)

st.warning(
    "This tool provides general educational information only. "
    "It does not diagnose conditions or replace advice from a qualified "
    "healthcare professional. For medication dosing or urgent symptoms, "
    "contact a healthcare professional or local emergency service."
)


@st.cache_resource(show_spinner="Loading the medical knowledge base...")
def get_vector_store():
    return load_vector_store()


@st.cache_resource(show_spinner="Loading Mistral 7B (4-bit)...")
def get_generation_components():
    return load_generation_model()


def initialize_chat():
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": (
                    "Hello! Ask me a question about hypertension, such as "
                    "risk factors, prevention, complications, or measuring "
                    "blood pressure at home."
                ),
                "sources": [],
                "insufficient_information": False,
                "error": None,
            }
        ]


def show_sources(sources):
    if not sources:
        return

    with st.expander(f"Sources ({len(sources)})"):
        for index, source in enumerate(sources, start=1):
            title = source.get("document_title", "Untitled")
            source_name = source.get("source", "Unknown")
            section = source.get("section", "Unknown section")
            chunk_id = source.get("chunk_id")

            st.markdown(f"**{index}. {source_name} — {title}**")
            st.caption(f"Section: {section}")
            if chunk_id:
                st.caption(f"Chunk ID: {chunk_id}")


initialize_chat()

with st.sidebar:
    st.header("About")
    st.write(
        "This prototype retrieves relevant passages from the local "
        "hypertension FAISS vector store and uses Mistral 7B to draft "
        "a grounded response."
    )
    st.markdown("**Knowledge sources**")
    st.write("- WHO")
    st.write("- CDC")
    st.write("- MedlinePlus")
    st.divider()
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Initialize resources once per Streamlit process and reuse them.
try:
    vector_store = get_vector_store()
    tokenizer, model = get_generation_components()
except Exception as exc:
    st.error(
        "The application could not load its models or vector database. "
        "Check the terminal logs and confirm that the GPU, dependencies, "
        "and data/vector_db/hypertension files are available."
    )
    st.exception(exc)
    st.stop()

# Render chat history.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("insufficient_information"):
            st.info(
                "The retrieved context may not contain enough information "
                "to answer this question reliably."
            )

        if message.get("error"):
            st.caption(f"Request status: {message['error']}")

        if message.get("sources"):
            show_sources(message["sources"])

query = st.chat_input("Ask a question about hypertension...")

if query:
    st.session_state.messages.append(
        {
            "role": "user",
            "content": query,
        }
    )

    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Searching medical sources and preparing an answer..."):
            result = ask_question(
                query,
                vector_store,
                tokenizer,
                model,
            )

        answer = result.get(
            "answer",
            "Sorry, I couldn't process your question right now.",
        )
        sources = result.get("sources", [])
        insufficient_information = result.get(
            "insufficient_information",
            True,
        )
        error = result.get("error")

        st.markdown(answer)

        if insufficient_information:
            st.info(
                "The retrieved context may not contain enough information "
                "to answer this question reliably."
            )

        if error:
            st.caption(
                "The request could not be completed reliably. "
                "You can try rephrasing your question."
            )

        show_sources(sources)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "sources": sources,
            "insufficient_information": insufficient_information,
            "error": error,
        }
    )
