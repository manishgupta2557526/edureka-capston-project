# Enterprise Document QA Agent with Local LLM and RAG-Based Retrieval

This project is an end-to-end document question-answering system with a FastAPI backend, Streamlit frontend, ChromaDB vector store, and mandatory local Ollama model generation.

## What the system does
- Accepts document uploads in multiple formats
- Extracts and chunks text for retrieval
- Stores embeddings and chunks in ChromaDB for semantic search
- Uses MiniLM embeddings for robust paraphrase-aware retrieval
- Generates final answers with Ollama (llama3)

## Tech stack
- Python
- FastAPI
- Streamlit
- ChromaDB
- Sentence Transformers (MiniLM)
- Ollama
- Docker Compose (optional for EC2/containers)

## Quick start
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Install and run Ollama:
   ```powershell
   ollama --version
   ollama pull llama3
   ```
   If `ollama` is not recognized on Windows, run:
   ```powershell
   $env:Path = "C:\Users\$env:USERNAME\AppData\Local\Programs\Ollama;$env:Path"
   ollama --version
   ```
3. Start the full local app stack:
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts/start_local.ps1
   ```
   Note: `start_local.ps1` now auto-detects `ollama.exe` from common install locations when PATH is stale.
   If first answer generation is slow on your machine, increase Ollama timeout:
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts/start_local.ps1 -OllamaRequestTimeoutSeconds 240
   ```
4. Open:
   - API: http://127.0.0.1:8000/
   - UI: http://127.0.0.1:8501/

## Runtime configuration
The app uses these environment values:
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
OLLAMA_REQUEST_TIMEOUT_SECONDS=180
VECTOR_BACKEND=chroma
CHROMA_PERSIST_DIR=data/chroma
CHROMA_COLLECTION=documents
```

## Directory structure
```text
app/
   main.py                # FastAPI entrypoint (upload/query/login)
   streamlit_app.py       # Streamlit UI entrypoint
   ingestion.py           # Multi-format document parsing + chunking
   chroma_store.py        # ChromaDB-backed semantic store
   vector_db.py           # Embedding and retrieval helper logic
   store_factory.py       # Chroma store creation and startup enforcement
   orchestrator.py        # Retrieval + answer orchestration
   llm.py                 # Local answer utility helpers
   agents.py              # Planning and review agent modules
   auth.py                # Login/authentication logic
   chat_history.py        # Q&A persistence
   upload_service.py      # Shared upload save utility

data/
   chroma/                # Persistent Chroma vector data
   users.txt              # Auth users store
   chat_history.json      # Saved chat history
   uploads/               # Uploaded files

scripts/
   start_local.ps1        # One-line local startup (Ollama + API + Streamlit)
   preload_minilm.sh      # EC2 model pre-download script

tests/
   test_*.py              # Regression and unit tests

deploy_ec2.sh            # EC2 deployment orchestrator
setup_ec2.sh             # EC2 machine bootstrap
docker-compose.yml       # Container orchestration
Dockerfile               # Container build definition
README.md                # Quick start and project overview
PROJECT_DOCUMENTATION.md # Consolidated capstone, architecture, and viva documentation
```

## Deployment
- Local deployment: `scripts/start_local.ps1`
- Docker deployment: `docker compose up --build`
- EC2 deployment: `setup_ec2.sh` and `deploy_ec2.sh`

## Documentation
- Consolidated project documentation: `PROJECT_DOCUMENTATION.md`
- Local deployment guide: `LOCAL_DEPLOYMENT_GUIDE.md`
- EC2 production setup: `EC2_PRODUCTION_SETUP.md`
