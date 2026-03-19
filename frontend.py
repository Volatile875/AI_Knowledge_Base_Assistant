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
API_BASE_URL = "http://localhost:8000"

def upload_pdf(file):
    """Upload PDF to the API"""
    files = {"file": (file.name, file, "application/pdf")}
    response = requests.post(f"{API_BASE_URL}/upload-pdf", files=files)
    return response

def ask_question(question):
    """Send question to API and get response"""
    response = requests.post(
        f"{API_BASE_URL}/ask",
        json={"question": question}
    )
    return response

def main():
    st.title("🤖 AI Knowledge Base Assistant")
    st.markdown("Ask questions about Dell computer company knowledge from uploaded PDFs")

    # Sidebar for PDF upload
    with st.sidebar:
        st.header("📄 Document Management")

        # File uploader
        uploaded_file = st.file_uploader("Upload PDF", type=['pdf'])

        if uploaded_file is not None:
            if st.button("Process PDF"):
                with st.spinner("Processing PDF..."):
                    response = upload_pdf(uploaded_file)
                    if response.status_code == 200:
                        st.success("PDF processed successfully!")
                    else:
                        st.error(f"Error: {response.json().get('detail', 'Unknown error')}")

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
                        error_msg = response.json().get('detail', 'Unknown error')
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
