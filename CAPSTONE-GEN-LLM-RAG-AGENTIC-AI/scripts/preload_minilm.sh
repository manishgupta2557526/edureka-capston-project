#!/usr/bin/env bash
set -euo pipefail

APP_DIR="${APP_DIR:-/home/ubuntu/enterprise-doc-agent}"
USER_NAME="${USER_NAME:-ubuntu}"
MODEL_NAME="${MODEL_NAME:-sentence-transformers/all-MiniLM-L6-v2}"

mkdir -p "$APP_DIR"
mkdir -p "/home/$USER_NAME/.cache/huggingface"
chown -R "$USER_NAME:$USER_NAME" "/home/$USER_NAME/.cache/huggingface"

cd "$APP_DIR"
source .venv/bin/activate
python - <<'PY'
import os
from sentence_transformers import SentenceTransformer
model_name = os.environ.get("MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
SentenceTransformer(model_name)
print(f"Preloaded embedding model: {model_name}")
PY
