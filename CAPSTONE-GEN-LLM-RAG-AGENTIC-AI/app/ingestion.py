from pathlib import Path
from typing import List
import csv
import json
import re
import xml.etree.ElementTree as ET


def load_text(file_path: str) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        try:
            import PyPDF2
        except ImportError as exc:
            raise RuntimeError("PyPDF2 is required for PDF support") from exc
        reader = PyPDF2.PdfReader(str(path))
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if suffix in {".txt", ".md"}:
        return path.read_text(encoding="utf-8")

    if suffix == ".json":
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return json.dumps(data, indent=2, ensure_ascii=False)

    if suffix in {".yaml", ".yml"}:
        try:
            import yaml
        except ImportError as exc:
            raise RuntimeError("PyYAML is required for YAML support") from exc
        with open(path, "r", encoding="utf-8") as handle:
            data = yaml.safe_load(handle)
        return json.dumps(data, indent=2, ensure_ascii=False)

    if suffix == ".xml":
        tree = ET.parse(path)
        root = tree.getroot()
        return ET.tostring(root, encoding="unicode")

    if suffix == ".csv":
        with open(path, "r", encoding="utf-8", newline="") as handle:
            rows = list(csv.reader(handle))
        return "\n".join([" | ".join(row) for row in rows])

    if suffix in {".xlsx", ".xls"}:
        try:
            import pandas as pd
        except ImportError as exc:
            raise RuntimeError("pandas is required for Excel support") from exc
        df = pd.read_excel(path)
        return df.to_string(index=False)

    raise ValueError(f"Unsupported file type: {suffix}")


def chunk_text(text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    if not normalized:
        return []

    words = normalized.split()
    chunks: List[str] = []
    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end == len(words):
            break
        start = max(0, end - overlap)
    return chunks
