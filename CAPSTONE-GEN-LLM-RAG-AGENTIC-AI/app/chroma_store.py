from __future__ import annotations

import os
import re
from typing import Dict, List, Set
from uuid import uuid4

import numpy as np
from sentence_transformers import SentenceTransformer


class ChromaVectorStore:
    """ChromaDB-backed semantic retrieval store.

    The store keeps the same add/search interface used by the orchestrator.
    """

    STOPWORDS: Set[str] = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "how",
        "i",
        "in",
        "is",
        "it",
        "my",
        "of",
        "on",
        "or",
        "should",
        "the",
        "this",
        "to",
        "up",
        "when",
        "with",
    }
    SYNONYMS: Dict[str, Set[str]] = {
        "refund": {"refund", "return", "reimbursement", "moneyback"},
        "policy": {"policy", "rule", "procedure", "guideline"},
        "expense": {"expense", "reimbursement", "claim", "cost"},
        "submit": {"submit", "send", "file", "upload"},
        "report": {"report", "form", "document", "application"},
        "day": {"day", "days", "business", "working"},
        "employee": {"employee", "staff", "worker"},
        "within": {"within", "before", "by", "until"},
    }

    def __init__(self, persist_dir: str = "data/chroma", collection_name: str = "documents") -> None:
        os.makedirs(persist_dir, exist_ok=True)
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

        try:
            import chromadb  # type: ignore

            self._client = chromadb.PersistentClient(path=self.persist_dir)
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        except Exception as exc:
            raise RuntimeError(
                "ChromaDB is not installed or could not be initialized. Install with: pip install chromadb"
            ) from exc

    def is_available(self) -> bool:
        return self._collection is not None

    def add(self, chunk: str, source: str = "uploaded-doc") -> None:
        prepared = self._prepare_text(chunk)
        embedding = self.model.encode([prepared], convert_to_numpy=True)[0]
        normalized = self._normalize_embedding(embedding)

        self._collection.add(
            ids=[str(uuid4())],
            documents=[chunk],
            embeddings=[normalized.tolist()],
            metadatas=[{"source": source}],
        )

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, object]]:
        prepared = self._prepare_text(query)
        query_embedding = self.model.encode([prepared], convert_to_numpy=True)[0]
        normalized = self._normalize_embedding(query_embedding)

        result = self._collection.query(
            query_embeddings=[normalized.tolist()],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        rows: List[Dict[str, object]] = []
        for document, metadata, distance in zip(documents, metadatas, distances):
            similarity = 1.0 - float(distance)
            rows.append(
                {
                    "chunk": document,
                    "source": (metadata or {}).get("source", "uploaded-doc"),
                    "score": round(similarity, 3),
                }
            )
        return rows

    def _prepare_text(self, text: str) -> str:
        normalized = self._normalize_text(text)
        if not normalized:
            return ""
        terms = self._expand_terms(normalized)
        enriched = " ".join(sorted(terms))
        return f"{normalized} {enriched}".strip()

    def _normalize_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text).strip().lower()

    def _expand_terms(self, text: str) -> Set[str]:
        terms = set()
        for raw_term in re.findall(r"[a-zA-Z0-9]+", text):
            token = self._normalize_token(raw_term)
            if not token or token in self.STOPWORDS:
                continue
            terms.add(token)
            for synonym in self.SYNONYMS.get(token, set()):
                terms.add(synonym)
        return terms

    def _normalize_token(self, token: str) -> str:
        token = token.strip().lower()
        return token.rstrip("s") if token.endswith("s") and len(token) > 3 else token

    def _normalize_embedding(self, embedding: np.ndarray) -> np.ndarray:
        vector = np.asarray(embedding, dtype="float32")
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm
