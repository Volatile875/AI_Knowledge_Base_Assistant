import streamlit as st
import requests
import os
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="AI Knowledge Base Assistant",
    page_icon="🤖",
    layout="wide"
)

# API base URL
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
REQUEST_TIMEOUT = 120


def get_error_message(response):
    """Extract a readable error message from an API response."""
    try:
        return response.json().get("detail", response.text or "Unknown error")
    except ValueError:
        return response.text or "Unknown error"


def api_is_available():
    """Return True when the FastAPI backend is reachable."""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        return response.ok
    except requests.RequestException:
        return False

def upload_pdf(file):
    """Upload PDF to the API"""
    files = {"file": (file.name, file, "application/pdf")}
    response = requests.post(
        f"{API_BASE_URL}/upload-pdf",
        files=files,
        timeout=REQUEST_TIMEOUT,
    )
    return response

def ask_question(question):
    """Send question to API and get response"""
    response = requests.post(
        f"{API_BASE_URL}/ask",
        json={"question": question},
        timeout=REQUEST_TIMEOUT,
    )
    return response

def main():
    st.title("🤖 AI Knowledge Base Assistant")
    st.markdown("Ask questions about Dell computer company knowledge from uploaded PDFs")

    # Sidebar for PDF upload
    with st.sidebar:
        st.header("📄 Document Management")
        if api_is_available():
            st.success("API connected")
        else:
            st.error("API unavailable on port 8000. Start it with `python app.py api`.")

        # File uploader
        uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])

        if uploaded_file is not None:
            if st.button("Process PDF"):
                with st.spinner("Processing PDF..."):
                    try:
                        response = upload_pdf(uploaded_file)
                        if response.status_code == 200:
                            st.success("PDF processed successfully!")
                        else:
                            st.error(f"Error: {get_error_message(response)}")
                    except requests.exceptions.ConnectionError:
                        st.error("Cannot connect to the API. Start the FastAPI server on port 8000.")
                    except requests.exceptions.Timeout:
                        st.error("The upload timed out. Please try again after the API is ready.")
                    except requests.RequestException as exc:
                        st.error(f"Request failed: {exc}")

        # Display current PDFs in data directory
        st.subheader("Current PDFs")
        data_dir = Path("data")
        if data_dir.exists():
            pdfs = list(data_dir.glob("*.pdf"))
            if pdfs:
                for pdf in pdfs:
                    st.text(f"• {pdf.name}")
            else:
                st.text("No PDFs in data directory")
        else:
            st.text("Data directory not found")

    # Main chat interface
    st.header("💬 Ask Questions")

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if "sources" in message:
                with st.expander("📚 Sources"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f"**Source {i}:** {source['source']}")
                        st.text(source["content"])

    # Chat input
    if prompt := st.chat_input("Ask a question about Dell..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get response from API
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = ask_question(prompt)
                    if response.status_code == 200:
                        data = response.json()
                        answer = data["answer"]
                        sources = data.get("sources", [])

                        st.markdown(answer)

                        if sources:
                            with st.expander("📚 Sources"):
                                for i, source in enumerate(sources, 1):
                                    st.markdown(f"**Source {i}:** {source['source']}")
                                    st.text(source["content"])

                        # Add assistant response to chat history
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": answer,
                            "sources": sources
                        })
                    else:
                        error_msg = get_error_message(response)
                        st.error(f"Error: {error_msg}")
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": f"Error: {error_msg}"
                        })

                except requests.exceptions.ConnectionError:
                    st.error("Cannot connect to the API. Make sure the FastAPI server is running on port 8000.")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "Error: Cannot connect to the API. Make sure the FastAPI server is running."
                    })
                except requests.exceptions.Timeout:
                    st.error("The request timed out. The API may still be loading the model or indexing the PDF.")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "Error: The request timed out while waiting for the API."
                    })
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"Error: {str(e)}"
                    })

    # Footer
    st.markdown("---")
    st.markdown("Built with FastAPI, Streamlit, and LangChain using RAG architecture")

if __name__ == "__main__":
    main()
