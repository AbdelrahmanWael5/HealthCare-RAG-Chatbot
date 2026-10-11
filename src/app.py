import streamlit as st

from generate import run_rag

# PAGE CONFIGURATION
st.set_page_config(page_title="Healthcare RAG", page_icon="🩺", layout="centered",)

# SESSION STATE
if "messages" not in st.session_state:

    st.session_state.messages = []

# HEADER
st.title("🩺 Healthcare RAG")
st.caption("Hypertension Medical Assistant")

st.markdown(
    """
Ask questions about **hypertension** and receive
answers grounded in the system's medical knowledge base.
"""
)

# SIDEBAR
with st.sidebar:

    st.header("About")

    st.markdown(
        """
### Healthcare RAG System

This chatbot uses a Retrieval-Augmented Generation
pipeline specialized in **hypertension**.

### Sources

The knowledge base contains medical information
from trusted healthcare sources such as Medlineplus, World Health Organization (WHO), and CDC.

---

⚠️ **Disclaimer**

This AI assistant is an educational/research tool.
It does not replace professional medical advice,
diagnosis, or treatment.
"""
    )

    if st.button(
        "Clear conversation",
        use_container_width=True,
    ):

        st.session_state.messages = []

        st.rerun()


# SOURCE PANEL
def render_sources(
    sources,
):

    if not sources:
        return

    with st.expander(
        "📚 Sources"
    ):

        st.caption(
            "Sources associated with the final reranked evidence."
        )

        for source in sources:

            source_name = source["source"]
            document = source["document"]
            section = source["section"]
            url = source["url"]

            # -------------------------------------------------------------
            # Clickable source
            # -------------------------------------------------------------

            if url:

                st.markdown(
                    f"**[{source_name}]({url})**"
                )

            else:

                st.markdown(
                    f"**{source_name}**"
                )

            # -------------------------------------------------------------
            # Document / section
            # -------------------------------------------------------------

            if document != "Unknown":

                if section != "Unknown":

                    st.caption(
                        f"{document} — {section}"
                    )

                else:

                    st.caption(
                        document
                    )

            elif section != "Unknown":

                st.caption(
                    section
                )

            st.divider()


# =============================================================================
# DISPLAY CHAT HISTORY
# =============================================================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):

        st.markdown(
            message["content"]
        )

        if (
            message["role"] == "assistant"
            and message.get("sources")
        ):

            render_sources(
                message["sources"]
            )


# =============================================================================
# USER INPUT
# =============================================================================

query = st.chat_input(
    "Ask a question about hypertension..."
)


# =============================================================================
# PROCESS QUESTION
# =============================================================================

if query:

    # -------------------------------------------------------------------------
    # Display user message
    # -------------------------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": query,
        }
    )

    with st.chat_message(
        "user"
    ):

        st.markdown(
            query
        )

    # -------------------------------------------------------------------------
    # Generate answer
    # -------------------------------------------------------------------------

    with st.chat_message(
        "assistant"
    ):

        with st.spinner(
            "Retrieving evidence and generating answer..."
        ):

            try:

                (
                    answer,
                    retrieved_chunks,
                    sources,
                ) = run_rag(
                    query
                )

                # -------------------------------------------------------------
                # Display synthesized answer
                # -------------------------------------------------------------

                st.markdown(
                    answer
                )

                # -------------------------------------------------------------
                # Display source panel
                # -------------------------------------------------------------

                render_sources(
                    sources
                )

                # -------------------------------------------------------------
                # Save assistant response
                # -------------------------------------------------------------

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    }
                )

            except Exception as error:

                error_message = (
                    "Sorry, an error occurred while "
                    "processing your question."
                )

                st.error(
                    error_message
                )

                st.exception(
                    error
                )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                        "sources": [],
                    }
                )