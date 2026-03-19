from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import tempfile
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="AI Knowledge Base Assistant", description="RAG-based assistant for Dell knowledge base")

# CORS middleware for Streamlit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for vector store and QA chain
vectorstore = None
qa_chain = None

class QuestionRequest(BaseModel):
    question: str

def initialize_knowledge_base(pdf_paths: list = None):
    """Initialize the knowledge base with PDFs"""
    global vectorstore, qa_chain

    documents = []

    # If no paths provided, look for PDFs in data directory
    if not pdf_paths:
        data_dir = "data"
        if os.path.exists(data_dir):
            pdf_paths = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.pdf')]

    if not pdf_paths:
        raise HTTPException(status_code=400, detail="No PDF files found in data directory")

    # Load and process PDFs
    for pdf_path in pdf_paths:
        if os.path.exists(pdf_path):
            loader = PyPDFLoader(pdf_path)
            documents.extend(loader.load())

    if not documents:
        raise HTTPException(status_code=400, detail="No documents could be loaded from PDFs")

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    texts = text_splitter.split_documents(documents)

    # Create embeddings and vector store
    embeddings = OpenAIEmbeddings()
    vectorstore = FAISS.from_documents(texts, embeddings)

    # Create QA chain
    llm = OpenAI(temperature=0.1)
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True
    )

@app.on_event("startup")
async def startup_event():
    """Initialize knowledge base on startup"""
    try:
        initialize_knowledge_base()
    except Exception as e:
        print(f"Warning: Could not initialize knowledge base on startup: {e}")

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF file to the knowledge base"""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_path = temp_file.name

    try:
        # Reinitialize knowledge base with new PDF
        initialize_knowledge_base([temp_path])
        return {"message": f"Successfully uploaded and processed {file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing PDF: {str(e)}")
    finally:
        # Clean up temp file
        os.unlink(temp_path)

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """Answer a question using the knowledge base"""
    global qa_chain

    if qa_chain is None:
        raise HTTPException(status_code=400, detail="Knowledge base not initialized. Please upload PDFs first.")

    try:
        result = qa_chain({"query": request.question})
        return {
            "answer": result["result"],
            "sources": [
                {
                    "content": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "source": doc.metadata.get("source", "Unknown")
                }
                for doc in result["source_documents"]
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing question: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "knowledge_base_loaded": vectorstore is not None}
