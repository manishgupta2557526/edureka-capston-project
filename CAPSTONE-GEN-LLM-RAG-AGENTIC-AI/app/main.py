from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
from app.ingestion import load_text, chunk_text
from app.agents import PlanningAgent, ReviewAgent
from app.frontend import get_frontend_page
from app.orchestrator import RAGOrchestrator
from app.ollama_client import OllamaClient
from app.upload_service import UploadService
from app.auth import SimpleAuth
from app.chat_history import ChatHistory
from app.config import load_settings
from app.store_factory import create_store

settings = load_settings()
app = FastAPI(title="Enterprise Document QA Agent", version="0.1.0")
store = create_store(settings)
planning_agent = PlanningAgent()
review_agent = ReviewAgent()
ollama_client = OllamaClient(
    base_url=settings.ollama_base_url,
    request_timeout_seconds=settings.ollama_request_timeout_seconds,
    num_predict=settings.ollama_num_predict,
    keep_alive=settings.ollama_keep_alive,
)
if not ollama_client.is_available():
    raise RuntimeError(
        f"Ollama is required but unavailable at {settings.ollama_base_url}. "
        "Start Ollama before launching the app."
    )
if not ollama_client.is_model_available(settings.ollama_model):
    raise RuntimeError(
        f"Required Ollama model '{settings.ollama_model}' is not installed. "
        f"Run: ollama pull {settings.ollama_model}"
    )
orchestrator = RAGOrchestrator(
    store,
    ollama_client,
    ollama_model=settings.ollama_model,
    top_k=settings.rag_top_k,
    max_context_words=settings.rag_max_context_words,
)
upload_service = UploadService(storage_dir=settings.upload_dir)
auth = SimpleAuth(users_file=settings.auth_users_file)
history = ChatHistory(history_file=settings.chat_history_file)


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return get_frontend_page()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/upload")
async def upload(file: UploadFile = File(...)) -> dict:
    if not file.filename:
        raise HTTPException(status_code=400, detail="A file is required")

    saved_path = upload_service.save_upload(file, file.filename)

    try:
        content = load_text(saved_path)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    chunks = chunk_text(content)
    for chunk in chunks:
        store.add(chunk, source=file.filename)

    return {"message": "Document uploaded and indexed", "chunks": len(chunks), "file": file.filename}


@app.post("/query")
async def query(payload: dict) -> dict:
    user_query = payload.get("query", "")
    if not user_query:
        raise HTTPException(status_code=400, detail="A query is required")

    plan = planning_agent.build_plan(user_query)
    try:
        result = orchestrator.run(user_query)
    except RuntimeError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    history.add(user_query, result["answer"])
    validated = review_agent.validate_answer(result["answer"])
    return {
        "plan": plan,
        "context": result["context"],
        "answer": result["answer"],
        "validated": validated,
        "sources": result["sources"],
    }


@app.post("/login")
async def login(payload: dict) -> dict:
    username = payload.get("username", "")
    password = payload.get("password", "")
    if auth.authenticate(username, password):
        return {"authenticated": True}
    raise HTTPException(status_code=401, detail="Invalid credentials")
