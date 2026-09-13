from app.ingestion import load_text, chunk_text
from pathlib import Path


def test_load_text_supports_json(tmp_path):
    file_path = tmp_path / "sample.json"
    file_path.write_text('{"name": "demo"}', encoding="utf-8")
    text = load_text(str(file_path))
    assert "demo" in text


def test_chunk_text_handles_short_input():
    chunks = chunk_text("short content")
    assert chunks == ["short content"]
