from __future__ import annotations

import os
from typing import Dict, List, Optional

from app.vector_db import SQLiteVectorStore


class QdrantStore(SQLiteVectorStore):
    def __init__(self, host: Optional[str] = None, db_path: Optional[str] = None) -> None:
        self.host = host or os.getenv("QDRANT_HOST", "http://localhost:6333")
        self._available = False
        super().__init__(db_path=db_path or os.getenv("QDRANT_VECTOR_DB_PATH", "data/qdrant_vectors.db"))

    def is_available(self) -> bool:
        try:
            import requests

            response = requests.get(f"{self.host}/collections", timeout=3)
            self._available = response.status_code == 200
        except Exception:
            self._available = False
        return self._available

    def add(self, chunk: str, source: str = "uploaded-doc") -> None:
        super().add(chunk, source=source)

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, object]]:
        if not self.is_available():
            return super().search(query, top_k=top_k)
        return super().search(query, top_k=top_k)
