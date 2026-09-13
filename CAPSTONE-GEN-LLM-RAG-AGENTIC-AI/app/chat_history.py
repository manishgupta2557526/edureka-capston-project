from typing import List, Dict
import json
import os


class ChatHistory:
    def __init__(self, history_file: str = "data/chat_history.json") -> None:
        self.history_file = history_file
        os.makedirs(os.path.dirname(self.history_file), exist_ok=True)
        if not os.path.exists(self.history_file):
            self._write([])

    def _write(self, history: List[Dict[str, str]]) -> None:
        with open(self.history_file, "w", encoding="utf-8") as handle:
            json.dump(history, handle, indent=2)

    def load(self) -> List[Dict[str, str]]:
        with open(self.history_file, "r", encoding="utf-8") as handle:
            return json.load(handle)

    def add(self, question: str, answer: str) -> None:
        history = self.load()
        history.append({"question": question, "answer": answer})
        self._write(history)

    def clear(self) -> None:
        self._write([])
