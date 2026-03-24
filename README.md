# AI Knowledge Base Assistant

This is our first corporate project - an AI-powered knowledge base assistant that answers questions about Dell computer company knowledge using Retrieval-Augmented Generation (RAG) architecture.

##  Project Objective

Build an AI assistant that:
- Answers questions from a dataset (PDF documents)
- Retrieves relevant information from Dell knowledge base
- Provides context-aware responses
- Uses modern AI techniques for accurate and helpful answers

##  Architecture

### System Components

1. **Frontend (Streamlit)**
   - User interface for asking questions
   - PDF upload functionality
   - Chat-like conversation display
   - Source document references

2. **Backend (FastAPI)**
   - REST API for question answering
   - PDF processing and text extraction
   - Vector database management
   - RAG pipeline orchestration

3. **AI Components**
   - **Embeddings**: Convert text to vector representations
   - **Vector Store**: Chroma for efficient similarity search
   - **LLM**: OpenAI GPT for generating responses
   - **Retrieval**: Semantic search for relevant document chunks

### Data Flow

```
PDF Documents → Text Extraction → Text Chunking → Embeddings → Vector Store
                                                                    ↓
User Question → Embedding → Similarity Search → Retrieved Chunks → LLM → Answer
```

##  Learning Topics Covered

### 1. LLM Fundamentals
- Large Language Models (LLMs) are AI models trained on vast amounts of text data
- They can generate human-like text, answer questions, and perform various language tasks
- In this project: llama3.1:8b models for generating context-aware responses

### 2. Prompt Engineering
- Crafting effective prompts to get better responses from LLMs
- Techniques used:
  - Clear, specific questions
  - Context provision through retrieved documents
  - Temperature control for response consistency

### 3. Embeddings & Semantic Search
- **Embeddings**: Mathematical representations of text in vector space
- **Semantic Search**: Finding similar content based on meaning, not just keywords
- **How it works**:
  - Convert documents and questions to vectors
  - Use cosine similarity to find most relevant content
  - Retrieve top-k similar chunks for context

### 4. RAG (Retrieval-Augmented Generation)
- **Retrieval**: Find relevant information from knowledge base
- **Augmented**: Add retrieved context to the prompt
- **Generation**: Use LLM to generate answer based on retrieved context
- **Benefits**:
  - Reduces hallucinations
  - Provides factual, source-backed answers
  - Handles domain-specific knowledge better than base LLMs

##  Setup & Installation

### Prerequisites
- Python 3.8+
- Ollama pulled model llama3.1:8b

### Installation

1. **Clone/Download the project**
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   - Copy `.env.example` to `.env`
   - Add your OpenAI API key: `OPENAI_API_KEY=your_key_here`

4. **Add PDF documents**
   - Place Dell knowledge PDFs in the `data/` directory
   - Or upload them through the Streamlit interface

### Running the Application

**Option 1: Run both services**
```bash
# Terminal 1 - API Server
python app.py api

# Terminal 2 - Frontend
python app.py frontend
```

**Option 2: Run separately**
```bash
# API Server (FastAPI)
uvicorn api:app --host 127.0.0.1 --port 8000 --reload

# Frontend (Streamlit)
streamlit run frontend.py
```

### Accessing the Application
- **Frontend served by FastAPI**: http://127.0.0.1:8000
- **Streamlit frontend**: http://localhost:8501
- **API Documentation**: http://127.0.0.1:8000/docs

##  Project Structure

```
AI_Knowledge_Base_Assistant/
├── api.py                 # FastAPI backend
├── frontend.py            # Streamlit frontend
├── app.py                 # Application runner
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
├── data/                  # PDF documents directory
└── README.md             # This file
```

## 🔧 Key Technologies

- **FastAPI**: High-performance async web framework
- **Streamlit**: Easy-to-use web app framework for ML/AI
- **LangChain**: Framework for LLM applications
- **Olama**: LLM provider for embeddings and text generation
- **PyPDF2**: PDF text extraction

## Features

- ✅ PDF document upload and processing
- ✅ Semantic search using embeddings
- ✅ Context-aware question answering
- ✅ Source document references
- ✅ Chat-like user interface
- ✅ REST API for integration
- ✅ Automatic text chunking and indexing

## 🧪 Testing

1. Upload a Dell knowledge PDF
2. Ask questions like:
   - "What are Dell's latest laptop models?"
   - "Tell me about Dell's warranty policies"
   - "How does Dell's customer support work?"

##  Challenges Faced & Solutions

### Challenge 1: PDF Text Extraction
- **Problem**: PDFs can have complex layouts, images, tables
- **Solution**: Used PyPDF2 for reliable text extraction, focused on text-heavy documents

### Challenge 2: Chunk Size Optimization
- **Problem**: Finding the right balance between context and specificity
- **Solution**: Used 1000-character chunks with 200-character overlap for good context coverage

### Challenge 3: API Integration
- **Problem**: Coordinating between FastAPI backend and Streamlit frontend
- **Solution**: Implemented proper CORS handling and error management

### Challenge 4: Vector Store Persistence
- **Problem**: Rebuilding vector store on every restart
- **Solution**: Implemented automatic initialization on startup with file-based storage option

## Future Improvements

- Add support for multiple document formats (DOCX, TXT)
- Add document metadata and filtering capabilities
- Integrate with local LLM models for offline operation
- Add evaluation metrics and response quality assessment

##  Deliverables Checklist

- ✅ Working AI assistant
- ✅ Code repository with proper structure
- ✅ Architecture explanation (this README)
- ✅ Learning topics explanation (LLM, Prompt Engineering, Embeddings, RAG)
- ✅ Challenges documentation
- ✅ Setup and usage instructions

---

**Built with ❤️ for learning and corporate project experience**
