from app.config import Settings
from app.chroma_store import ChromaVectorStore


def create_store(settings: Settings):
    backend = (settings.vector_backend or "chroma").strip().lower()
    if backend != "chroma":
        raise RuntimeError(
            "This project now uses ChromaDB only. Set VECTOR_BACKEND=chroma and configure CHROMA_* settings."
        )

    chroma_store = ChromaVectorStore(
        persist_dir=settings.chroma_persist_dir,
        collection_name=settings.chroma_collection,
    )

    if not chroma_store.is_available():
        raise RuntimeError(
            "ChromaDB store is not available. Install chromadb and verify CHROMA_* settings."
        )
    return chroma_store
