from __future__ import annotations

import json
import os
import re
import sqlite3
from typing import Dict, List, Set

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

try:
    import faiss
except Exception:  # pragma: no cover - optional dependency
    faiss = None


class SQLiteVectorStore:
    """Local semantic retrieval store powered by a sentence-transformer model.

    This keeps the project fully free and API-free while providing stronger
    semantic similarity search over uploaded document chunks.
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

    def __init__(self, db_path: str = "data/documents.db") -> None:
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self._init_db()
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        self.embedding_dim = self._get_embedding_dimension()
        self.index_path = f"{self.db_path}.faiss"
        self.index = None
        self._doc_ids: List[int] = []
        self._load_or_create_index()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS documents (id INTEGER PRIMARY KEY AUTOINCREMENT, chunk TEXT NOT NULL, source TEXT NOT NULL, embedding TEXT)"
            )
            columns = [row[1] for row in conn.execute("PRAGMA table_info(documents)")]
            if "embedding" not in columns:
                conn.execute("ALTER TABLE documents ADD COLUMN embedding TEXT")
            conn.commit()

    def add(self, chunk: str, source: str = "uploaded-doc") -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("INSERT INTO documents (chunk, source, embedding) VALUES (?, ?, ?)", (chunk, source, None))
            conn.commit()
            self._rebuild_embeddings(conn)

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, object]]:
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT id, chunk, source, embedding FROM documents ORDER BY id").fetchall()

        if not rows:
            return []

        try:
            query_embedding = self._normalize_embedding(
                self.model.encode([self._prepare_text(query)], convert_to_numpy=True)[0]
            )
            if faiss is not None and self.index is not None and self.index.ntotal > 0:
                distances, indices = self.index.search(query_embedding.reshape(1, -1).astype("float32"), min(top_k, self.index.ntotal))
                scored_results: List[tuple[float, str, str]] = []
                row_lookup = {(doc_id): (chunk, source) for doc_id, chunk, source, _ in rows}
                for similarity, index_position in zip(distances[0], indices[0]):
                    if index_position == -1:
                        continue
                    doc_id = self._doc_ids[int(index_position)]
                    chunk, source = row_lookup.get(doc_id, ("", ""))
                    if chunk:
                        scored_results.append((float(similarity), chunk, source))
                if scored_results:
                    scored_results.sort(key=lambda item: item[0], reverse=True)
                    return [
                        {"chunk": chunk, "source": source, "score": round(score, 3)}
                        for score, chunk, source in scored_results[:top_k]
                    ]

            corpus = [self._prepare_text(chunk) for _, chunk, _, _ in rows]
            document_embeddings = self.model.encode(corpus, convert_to_numpy=True)
            similarity_scores = cosine_similarity([query_embedding], document_embeddings)[0]

            scored_results = []
            for (doc_id, chunk, source, _), similarity in zip(rows, similarity_scores):
                if similarity > 0:
                    scored_results.append((float(similarity), chunk, source))

            scored_results.sort(key=lambda item: item[0], reverse=True)
            return [
                {"chunk": chunk, "source": source, "score": round(score, 3)}
                for score, chunk, source in scored_results[:top_k]
            ]
        except Exception:
            return []

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

    def _rebuild_embeddings(self, conn: sqlite3.Connection) -> None:
        rows = conn.execute("SELECT id, chunk, source FROM documents ORDER BY id").fetchall()
        if not rows:
            return

        texts = [self._prepare_text(chunk) for _, chunk, _ in rows]
        try:
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            normalized_embeddings = [self._normalize_embedding(embedding) for embedding in embeddings]
            for (doc_id, _, _), embedding in zip(rows, normalized_embeddings):
                embedding_json = json.dumps(embedding.tolist())
                conn.execute("UPDATE documents SET embedding = ? WHERE id = ?", (embedding_json, doc_id))
            conn.commit()

            if faiss is not None:
                self.index = faiss.IndexFlatIP(self.embedding_dim)
                self.index.add(np.stack(normalized_embeddings).astype("float32"))
                self._doc_ids = [doc_id for (doc_id, _, _) in rows]
                self._save_index()
        except Exception:
            pass

    def _load_or_create_index(self) -> None:
        if faiss is None:
            return
        try:
            if os.path.exists(self.index_path):
                self.index = faiss.read_index(self.index_path)
                self._doc_ids = [row[0] for row in sqlite3.connect(self.db_path).execute("SELECT id FROM documents ORDER BY id")]
            else:
                self.index = faiss.IndexFlatIP(self.embedding_dim)
                self._doc_ids = []
        except Exception:
            self.index = None

    def _save_index(self) -> None:
        if faiss is None or self.index is None:
            return
        try:
            faiss.write_index(self.index, self.index_path)
        except Exception:
            pass

    def _get_embedding_dimension(self) -> int:
        try:
            return int(self.model.get_sentence_embedding_dimension())
        except Exception:
            try:
                return int(self.model.get_embedding_dimension())
            except Exception:
                return 384

    def _normalize_embedding(self, embedding: np.ndarray) -> np.ndarray:
        vector = np.asarray(embedding, dtype="float32")
        norm = np.linalg.norm(vector)
        if norm == 0:
            return vector
        return vector / norm
