from typing import List, Dict
from app.vector_db import SQLiteVectorStore
from app.ollama_client import OllamaClient


class RAGOrchestrator:
    def __init__(
        self,
        store: SQLiteVectorStore,
        ollama_client: OllamaClient | None = None,
        ollama_model: str = "llama3",
        top_k: int = 3,
        max_context_words: int = 900,
    ) -> None:
        self.store = store
        self.ollama_client = ollama_client or OllamaClient()
        self.ollama_model = ollama_model
        self.top_k = top_k
        self.max_context_words = max_context_words

    def run(self, user_query: str) -> Dict[str, object]:
        context_docs = self.store.search(user_query, top_k=self.top_k)
        context_chunks = [doc["chunk"] for doc in context_docs]
        trimmed_context = self._trim_context(context_chunks)

        if not self.ollama_client.is_available():
            raise RuntimeError("Ollama is required but not reachable.")

        prompt = (
            "You are a helpful enterprise assistant. "
            "Answer in 3-6 concise sentences using only the retrieved context.\n"
            f"Question: {user_query}\n"
            f"Context: {' '.join(trimmed_context)}"
        )
        answer = self.ollama_client.generate(prompt, model=self.ollama_model)

        return {
            "answer": answer,
            "context": context_chunks,
            "sources": [doc.get("source", "unknown") for doc in context_docs],
            "retrieval_results": context_docs,
        }

    def _trim_context(self, chunks: List[str]) -> List[str]:
        words_used = 0
        trimmed: List[str] = []
        for chunk in chunks:
            chunk_words = chunk.split()
            remaining = self.max_context_words - words_used
            if remaining <= 0:
                break
            if len(chunk_words) <= remaining:
                trimmed.append(chunk)
                words_used += len(chunk_words)
            else:
                trimmed.append(" ".join(chunk_words[:remaining]))
                break
        return trimmed
