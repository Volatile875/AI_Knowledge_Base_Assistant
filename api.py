import os
import pickle
import re
from pathlib import Path
from typing import List

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"
VECTORSTORE_FILE = VECTORSTORE_DIR / "kb_store.pkl"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
RETRIEVAL_K = 3
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
OLLAMA_TIMEOUT = 120

app = FastAPI(
    title="AI Knowledge Base Assistant",
    description="RAG-based assistant for Dell knowledge base powered by Ollama",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vectorizer = None
chunk_vectors = None
chunk_store = []


class QuestionRequest(BaseModel):
    question: str


def ensure_directories() -> None:
    """Create local storage folders used by the knowledge base."""
    DATA_DIR.mkdir(exist_ok=True)
    VECTORSTORE_DIR.mkdir(exist_ok=True)


def sanitize_filename(filename: str) -> str:
    """Keep uploaded filenames safe and predictable on disk."""
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "_", Path(filename).name)
    return cleaned or "uploaded.pdf"


def get_pdf_paths() -> List[Path]:
    """Return all PDFs currently stored in the data directory."""
    ensure_directories()
    return sorted(DATA_DIR.glob("*.pdf"))


def load_documents(pdf_paths: List[Path]):
    """Extract text from all provided PDFs."""
    documents = []
    for pdf_path in pdf_paths:
        reader = PdfReader(str(pdf_path))
        for page_number, page in enumerate(reader.pages, start=1):
            text = (page.extract_text() or "").strip()
            if not text:
                continue
            documents.append(
                {
                    "source": pdf_path.name,
                    "page": page_number,
                    "content": text,
                }
            )
    return documents


def split_text(text: str) -> List[str]:
    """Chunk long text with overlap so retrieval keeps nearby context."""
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = min(start + CHUNK_SIZE, text_length)
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= text_length:
            break
        start = max(end - CHUNK_OVERLAP, start + 1)

    return chunks


def split_documents(documents):
    """Create chunk records from extracted PDF pages."""
    chunks = []
    for document in documents:
        for chunk_number, chunk_text in enumerate(split_text(document["content"]), start=1):
            chunks.append(
                {
                    "source": document["source"],
                    "page": document["page"],
                    "chunk": chunk_number,
                    "content": chunk_text,
                }
            )
    return chunks


def save_vectorstore(current_vectorizer, current_chunk_vectors, metadata: List[dict]) -> None:
    """Persist the vectorizer, chunk vectors, and chunk metadata."""
    with VECTORSTORE_FILE.open("wb") as store_file:
        pickle.dump(
            {
                "vectorizer": current_vectorizer,
                "chunk_vectors": current_chunk_vectors,
                "chunk_store": metadata,
            },
            store_file,
        )


def load_vectorstore_from_disk() -> bool:
    """Load a previously built vector store if it exists."""
    global vectorizer, chunk_vectors, chunk_store

    if not VECTORSTORE_FILE.exists():
        return False

    with VECTORSTORE_FILE.open("rb") as store_file:
        saved_store = pickle.load(store_file)

    vectorizer = saved_store["vectorizer"]
    chunk_vectors = saved_store["chunk_vectors"]
    chunk_store = saved_store["chunk_store"]
    return True


def build_knowledge_base(pdf_paths: List[Path]) -> dict:
    """Run the full PDF -> chunks -> embeddings -> vector store pipeline."""
    global vectorizer, chunk_vectors, chunk_store

    if not pdf_paths:
        raise HTTPException(status_code=400, detail="No PDF files found in the data directory.")

    documents = load_documents(pdf_paths)
    if not documents:
        raise HTTPException(status_code=400, detail="No text could be extracted from the available PDFs.")

    chunks = split_documents(documents)
    if not chunks:
        raise HTTPException(status_code=400, detail="Text extraction succeeded but no chunks were created.")

    vectorizer = TfidfVectorizer(stop_words="english")
    chunk_vectors = vectorizer.fit_transform([chunk["content"] for chunk in chunks])
    chunk_store = chunks
    save_vectorstore(vectorizer, chunk_vectors, chunk_store)

    return {
        "pdf_count": len(pdf_paths),
        "document_count": len(documents),
        "chunk_count": len(chunks),
    }


def initialize_knowledge_base() -> None:
    """Load a saved index if one already exists."""
    ensure_directories()
    load_vectorstore_from_disk()


def generate_answer(question: str, retrieved_docs) -> str:
    """Use retrieved chunks as context for the final answer via Ollama."""
    context = "\n\n".join(
        f"Source: {doc['source']} | Page: {doc.get('page', 'Unknown')}\n{doc['content']}"
        for doc in retrieved_docs
    )

    prompt = f"""You are a helpful knowledge base assistant.
Use only the provided context to answer the question.
If the answer is not in the context, say that the knowledge base does not contain enough information.
Keep the answer concise and grounded in the source material.

Context:
{context}

Question:
{question}

Answer:"""

    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
            },
            timeout=OLLAMA_TIMEOUT,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                f"Could not reach Ollama at {OLLAMA_BASE_URL}. "
                f"Make sure the Ollama app is running and the model '{OLLAMA_MODEL}' is available. Error: {exc}"
            ),
        )

    answer = response.json().get("response", "").strip()
    if not answer:
        raise HTTPException(status_code=500, detail="Ollama returned an empty response.")
    return answer


def get_sources(retrieved_docs) -> List[dict]:
    """Format retrieved chunks for the API response."""
    sources = []
    for doc in retrieved_docs:
        content = doc["content"].strip()
        sources.append(
            {
                "source": doc.get("source", "Unknown"),
                "content": content[:250] + "..." if len(content) > 250 else content,
                "page": doc.get("page"),
            }
        )
    return sources

@app.on_event("startup")
async def startup_event():
    """Prepare the knowledge base when the API starts."""
    try:
        initialize_knowledge_base()
    except Exception as exc:
        print(f"Warning: Could not initialize knowledge base on startup: {exc}")

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Store an uploaded PDF and rebuild the shared vector index."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    ensure_directories()
    destination = DATA_DIR / sanitize_filename(file.filename)

    with destination.open("wb") as pdf_file:
        pdf_file.write(await file.read())

    try:
        stats = build_knowledge_base(get_pdf_paths())
    except Exception:
        if destination.exists():
            destination.unlink()
        raise

    return {
        "message": f"Successfully uploaded and indexed {destination.name}.",
        "stats": stats,
    }

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """Answer a question using semantic search over the indexed PDF chunks."""
    global vectorizer, chunk_vectors

    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    if vectorizer is None or chunk_vectors is None:
        pdf_paths = get_pdf_paths()
        if pdf_paths:
            build_knowledge_base(pdf_paths)
        else:
            raise HTTPException(
                status_code=400,
                detail="Knowledge base not initialized. Add PDFs to the data folder or upload one first.",
            )

    try:
        query_vector = vectorizer.transform([question])
        similarities = cosine_similarity(query_vector, chunk_vectors)[0]
        top_indices = similarities.argsort()[-RETRIEVAL_K:][::-1]
        retrieved_docs = [chunk_store[index] for index in top_indices if similarities[index] > 0]
        if not retrieved_docs:
            return {
                "answer": "I could not find relevant information in the knowledge base for that question.",
                "sources": [],
            }

        answer = generate_answer(question, retrieved_docs)
        return {"answer": answer, "sources": get_sources(retrieved_docs)}
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error processing question: {exc}")


@app.post("/rebuild")
async def rebuild_knowledge_base():
    """Rebuild the vector index from every PDF currently in the data directory."""
    stats = build_knowledge_base(get_pdf_paths())
    return {"message": "Knowledge base rebuilt successfully.", "stats": stats}

@app.get("/health")
async def health_check():
    """Basic health and knowledge-base status."""
    pdf_count = len(get_pdf_paths())
    return {
        "status": "healthy",
        "knowledge_base_loaded": vectorizer is not None and chunk_vectors is not None,
        "pdf_count": pdf_count,
        "chunk_count": len(chunk_store),
        "ollama_base_url": OLLAMA_BASE_URL,
        "ollama_model": OLLAMA_MODEL,
        "embedding_model": "tf-idf",
    }
