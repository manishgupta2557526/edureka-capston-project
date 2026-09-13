# Enterprise Document QA Agent with Local LLM and RAG-Based Retrieval

This document is the single source of truth for the capstone report, technical documentation, and viva summary. Detailed deployment instructions remain separate so operational steps stay focused:

- Local deployment: [LOCAL_DEPLOYMENT_GUIDE.md](LOCAL_DEPLOYMENT_GUIDE.md)
- EC2 production deployment: [EC2_PRODUCTION_SETUP.md](EC2_PRODUCTION_SETUP.md)

## 1. Executive Summary

The Enterprise Document QA Agent with Local LLM and RAG-Based Retrieval is a local-first question-answering system for enterprise-style documents. Users upload files through a Streamlit interface, the system extracts and chunks the content, stores embeddings in ChromaDB, retrieves the most relevant chunks for a question, and generates a grounded response through Ollama.

The project was designed as a practical capstone implementation that demonstrates retrieval-augmented generation, local model serving, web application development, and deployment readiness without relying on paid AI APIs.

## 2. Problem Statement

Organizations often need fast answers from large collections of reports, manuals, policies, and operational documents. Manual search is slow, keyword search is often shallow, and paid AI services are not always suitable for local or low-cost deployments. This project addresses that gap by building a document QA workflow that is:

- grounded in uploaded source documents,
- usable through a simple web interface,
- deployable locally or on AWS EC2,
- and based on open-source components.

## 3. Project Objectives

The main objectives of the capstone project are to:

1. Support ingestion of multiple document formats.
2. Implement a retrieval-based QA pipeline.
3. Provide a usable FastAPI plus Streamlit application.
4. Run with local infrastructure instead of paid external APIs.
5. Remain easy to demonstrate, test, and deploy.

## 4. Current Architecture

The current implementation uses the following runtime architecture:

- Backend API: FastAPI
- Frontend UI: Streamlit
- Embeddings: sentence-transformer MiniLM
- Vector store: ChromaDB
- Answer generation: Ollama with `llama3`
- Persistence: local files for uploads, chat history, and Chroma collections

Important clarification: earlier drafts mentioned SQLite persistence and FAISS as the main storage layer. That is no longer the active project architecture. The live application now enforces `VECTOR_BACKEND=chroma`, and Ollama availability is validated at startup.

## 5. End-to-End Workflow

The application follows a straightforward RAG pipeline:

1. A user uploads a supported document.
2. The ingestion layer reads and normalizes the file contents.
3. The text is split into smaller chunks.
4. MiniLM embeddings are generated for each chunk.
5. ChromaDB stores chunk text, embeddings, and source metadata.
6. The user submits a natural-language question.
7. The retrieval layer returns the top matching chunks.
8. The orchestrator trims context and sends it to Ollama.
9. The final answer is shown along with retrieved context and sources.

## 6. Major Features

- Multi-format upload support for PDF, TXT, Markdown, JSON, YAML, XML, CSV, and Excel files
- Semantic retrieval using embeddings rather than keyword-only matching
- Grounded answer generation using retrieved document context
- FastAPI endpoints for health, upload, login, and query flows
- Streamlit interface for login, upload, querying, and chat review
- Local authentication and chat history persistence
- Deployment assets for local runs, Docker, and Ubuntu EC2

## 7. Module Map

### Application layer
- `app/main.py`: FastAPI entrypoint and API routes
- `app/streamlit_app.py`: Streamlit UI and user workflow
- `app/frontend.py`: HTML landing page helpers

### Retrieval and generation layer
- `app/ingestion.py`: file parsing and chunking
- `app/chroma_store.py`: ChromaDB-backed storage and search
- `app/store_factory.py`: enforces ChromaDB as the active backend
- `app/orchestrator.py`: retrieval plus answer generation flow
- `app/ollama_client.py`: Ollama health, model, and generation calls

### Supporting services
- `app/auth.py`: login and default user bootstrapping
- `app/chat_history.py`: persisted Q&A history
- `app/upload_service.py`: upload storage handling
- `app/agents.py`: planning and review helper modules

## 8. Runtime Configuration

The main environment values are:

```bash
APP_ENV=production
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
OLLAMA_REQUEST_TIMEOUT_SECONDS=180
AUTH_USERS_FILE=data/users.txt
UPLOAD_DIR=data/uploads
VECTOR_BACKEND=chroma
CHROMA_PERSIST_DIR=data/chroma
CHROMA_COLLECTION=documents
CHAT_HISTORY_FILE=data/chat_history.json
DEFAULT_AUTH_USERNAME=produser
DEFAULT_AUTH_PASSWORD=prodpass
```

Behavior that matters for deployment and demos:

- the app expects Ollama to be reachable before startup completes,
- the required model must already be available or pulled during setup,
- ChromaDB is the only supported active vector backend,
- the default user is created automatically if the users file does not yet exist.

## 9. Deployment Approaches

This repository supports two primary deployment paths:

### Local deployment

Use the local startup script for a full local run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts/start_local.ps1
```

Full step-by-step instructions are in [LOCAL_DEPLOYMENT_GUIDE.md](LOCAL_DEPLOYMENT_GUIDE.md).

### AWS EC2 deployment

For Ubuntu EC2, the project includes provisioning and deployment assets such as:

- `setup_ec2.sh`
- `deploy_ec2.sh`
- `ec2-api.service`
- `ec2-streamlit.service`
- `nginx.conf`
- `nginx-https.conf`

Full production-oriented instructions are in [EC2_PRODUCTION_SETUP.md](EC2_PRODUCTION_SETUP.md).

## 10. Testing and Validation

The project includes automated tests covering authentication, ingestion, Ollama integration, orchestration, upload handling, and RAG pipeline behavior.

Test coverage areas include:

- configuration and auth behavior,
- ingestion and document parsing,
- Ollama client fallback and request behavior,
- orchestration logic,
- upload and pipeline flows.

This provides a basic regression safety net for the core capstone functionality.

## 11. Key Results

The delivered system demonstrates that the project can:

- ingest real documents end to end,
- retrieve relevant chunks using semantic similarity,
- generate grounded answers with a local LLM,
- run through both API and UI surfaces,
- and be packaged for local and cloud-hosted deployment.

From a capstone perspective, the project successfully combines AI workflow design, backend development, frontend integration, and deployment engineering in one coherent deliverable.

## 12. Limitations

The current implementation has deliberate constraints:

- Ollama is mandatory, so the system does not run without the local model service.
- The architecture is optimized for local or small-scale deployment, not distributed production scale.
- Authentication is simple and suitable for demo use, not enterprise identity management.
- Observability, backup strategy, and security hardening are still limited compared with production-grade SaaS systems.

## 13. Future Enhancements

The most useful next improvements would be:

- stronger authentication and secrets management,
- richer monitoring and operational logging,
- role-based access control,
- improved production hardening for public deployment,
- optional scale-out architecture for larger document collections.

## 14. Viva-Ready Summary

If this project is presented briefly, the core message is:

The capstone builds a local-first enterprise document QA system using FastAPI, Streamlit, ChromaDB, MiniLM embeddings, and Ollama. Documents are uploaded, chunked, embedded, stored for semantic retrieval, and used to generate grounded answers. The project demonstrates practical RAG implementation, local AI deployment, and cloud-readiness through dedicated EC2 deployment assets.
