#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

sudo bash "$SCRIPT_DIR/setup_ec2.sh"

echo "Preloading the local MiniLM embedding model for faster first boot..."
sudo -u ubuntu APP_DIR="$SCRIPT_DIR" USER_NAME=ubuntu /usr/local/bin/preload_minilm.sh || true

echo "Starting the application services..."
sudo systemctl restart ec2-api.service ec2-streamlit.service

echo "One-command deployment complete."
echo "API health: curl http://127.0.0.1:8000/health"
echo "Streamlit UI: http://<EC2_PUBLIC_IP>:8501/"
echo "chroma check: grep CHROMA_ /home/ubuntu/enterprise-doc-agent/.env"
echo "ollama check: curl http://127.0.0.1:11434/api/tags"
