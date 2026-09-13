import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True)
class Settings:
    app_env: str
    auth_users_file: str
    upload_dir: str
    vector_db_path: str
    vector_backend: str
    chroma_persist_dir: str
    chroma_collection: str
    chat_history_file: str
    ollama_base_url: str
    ollama_model: str
    ollama_request_timeout_seconds: int
    ollama_num_predict: int
    ollama_keep_alive: str
    rag_top_k: int
    rag_max_context_words: int
    default_auth_username: Optional[str]
    default_auth_password: Optional[str]


def load_settings() -> Settings:
    app_env = os.getenv("APP_ENV", "development")
    auth_users_file = os.getenv("AUTH_USERS_FILE", "data/users.txt")
    upload_dir = os.getenv("UPLOAD_DIR", "data/uploads")
    vector_db_path = os.getenv("VECTOR_DB_PATH", "data/documents.db")
    vector_backend = os.getenv("VECTOR_BACKEND", "chroma")
    chroma_persist_dir = os.getenv("CHROMA_PERSIST_DIR", "data/chroma")
    chroma_collection = os.getenv("CHROMA_COLLECTION", "documents")
    chat_history_file = os.getenv("CHAT_HISTORY_FILE", "data/chat_history.json")
    ollama_base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
    ollama_request_timeout_seconds = int(os.getenv("OLLAMA_REQUEST_TIMEOUT_SECONDS", "180"))
    ollama_num_predict = int(os.getenv("OLLAMA_NUM_PREDICT", "192"))
    ollama_keep_alive = os.getenv("OLLAMA_KEEP_ALIVE", "15m")
    rag_top_k = int(os.getenv("RAG_TOP_K", "3"))
    rag_max_context_words = int(os.getenv("RAG_MAX_CONTEXT_WORDS", "900"))
    default_auth_username = os.getenv("DEFAULT_AUTH_USERNAME")
    default_auth_password = os.getenv("DEFAULT_AUTH_PASSWORD")

    return Settings(
        app_env=app_env,
        auth_users_file=auth_users_file,
        upload_dir=upload_dir,
        vector_db_path=vector_db_path,
        vector_backend=vector_backend,
        chroma_persist_dir=chroma_persist_dir,
        chroma_collection=chroma_collection,
        chat_history_file=chat_history_file,
        ollama_base_url=ollama_base_url,
        ollama_model=ollama_model,
        ollama_request_timeout_seconds=ollama_request_timeout_seconds,
        ollama_num_predict=ollama_num_predict,
        ollama_keep_alive=ollama_keep_alive,
        rag_top_k=rag_top_k,
        rag_max_context_words=rag_max_context_words,
        default_auth_username=default_auth_username,
        default_auth_password=default_auth_password,
    )


def ensure_data_dir(path: str) -> Path:
    directory = Path(path)
    directory.mkdir(parents=True, exist_ok=True)
    return directory
