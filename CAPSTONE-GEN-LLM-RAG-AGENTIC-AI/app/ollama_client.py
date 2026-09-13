import os
import requests
from typing import Optional


class OllamaClient:
    def __init__(
        self,
        base_url: Optional[str] = None,
        request_timeout_seconds: Optional[int] = None,
        num_predict: Optional[int] = None,
        keep_alive: Optional[str] = None,
    ) -> None:
        self.base_url = base_url or os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        env_timeout = os.getenv("OLLAMA_REQUEST_TIMEOUT_SECONDS", "180")
        self.request_timeout_seconds = request_timeout_seconds or int(env_timeout)
        env_num_predict = os.getenv("OLLAMA_NUM_PREDICT", "192")
        self.num_predict = num_predict or int(env_num_predict)
        self.keep_alive = keep_alive or os.getenv("OLLAMA_KEEP_ALIVE", "15m")

    def is_available(self) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=3)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def is_model_available(self, model: str) -> bool:
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get("models", [])
            expected_prefix = f"{model}:"
            for item in models:
                model_name = item.get("name", "")
                if model_name == model or model_name.startswith(expected_prefix):
                    return True
            return False
        except requests.RequestException:
            return False

    def generate(self, prompt: str, model: str = "llama3") -> str:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "keep_alive": self.keep_alive,
            "options": {
                "num_predict": self.num_predict,
                "temperature": 0.2,
            },
        }
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=(5, self.request_timeout_seconds),
            )
        except requests.Timeout as exc:
            raise RuntimeError(
                "Ollama generation timed out. "
                "The first response after model load can be slow. "
                "Try again or increase OLLAMA_REQUEST_TIMEOUT_SECONDS."
            ) from exc
        except requests.RequestException as exc:
            raise RuntimeError(
                f"Ollama request failed at {self.base_url}. "
                "The Ollama service may have restarted or dropped the connection. "
                "Retry once, and if it continues, restart Ollama and the app stack."
            ) from exc
        response.raise_for_status()
        return response.json().get("response", "")
