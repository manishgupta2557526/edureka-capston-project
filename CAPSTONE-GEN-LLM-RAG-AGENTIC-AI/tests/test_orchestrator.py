from app.orchestrator import RAGOrchestrator
from app.vector_db import SQLiteVectorStore


class FakeOllamaClient:
    def is_available(self) -> bool:
        return True

    def generate(self, prompt: str, model: str = "llama3") -> str:
        return "Generated answer"


def test_orchestrator_returns_context_and_answer():
    store = SQLiteVectorStore(db_path="data/test_documents.db")
    store.add("The refund policy allows returns within 30 days", source="policy")
    orchestrator = RAGOrchestrator(store, ollama_client=FakeOllamaClient())
    result = orchestrator.run("refund policy")

    assert isinstance(result["answer"], str)
    assert len(result["context"]) >= 1
    assert result["retrieval_results"]
    assert "score" in result["retrieval_results"][0]


def test_semantic_search_returns_related_chunk_for_paraphrase():
    store = SQLiteVectorStore(db_path="data/test_semantic_documents.db")
    store.add("Employees must submit expense reports within 10 business days", source="policy")

    results = store.search("When should I send my reimbursement form?", top_k=3)

    assert results
    assert any("expense reports" in result["chunk"].lower() for result in results)
