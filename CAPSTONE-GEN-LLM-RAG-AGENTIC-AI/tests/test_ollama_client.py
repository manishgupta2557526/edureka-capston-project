from app.ollama_client import OllamaClient
import requests


def test_ollama_client_defaults_to_local_endpoint():
    client = OllamaClient(base_url="http://localhost:11434")
    assert client.base_url == "http://localhost:11434"


def test_ollama_client_reports_model_availability(monkeypatch):
    class FakeResponse:
        def raise_for_status(self):
            return None

        def json(self):
            return {"models": [{"name": "llama3:latest"}, {"name": "nomic-embed-text:latest"}]}

    def fake_get(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(requests, "get", fake_get)
    client = OllamaClient(base_url="http://localhost:11434")

    assert client.is_model_available("llama3") is True
    assert client.is_model_available("mistral") is False
