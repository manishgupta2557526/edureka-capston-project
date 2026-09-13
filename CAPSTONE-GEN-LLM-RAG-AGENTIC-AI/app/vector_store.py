from typing import List, Dict


class SimpleVectorStore:
    def __init__(self) -> None:
        self._documents: List[Dict[str, str]] = []

    def add(self, chunk: str) -> None:
        self._documents.append({"chunk": chunk, "source": "uploaded-doc"})

    def search(self, query: str, top_k: int = 3) -> List[str]:
        query_terms = set(query.lower().split())
        scored = []
        for doc in self._documents:
            text = doc["chunk"].lower()
            score = sum(1 for term in query_terms if term in text)
            if score > 0:
                scored.append((score, doc["chunk"]))
        scored.sort(reverse=True)
        return [chunk for _, chunk in scored[:top_k]]
