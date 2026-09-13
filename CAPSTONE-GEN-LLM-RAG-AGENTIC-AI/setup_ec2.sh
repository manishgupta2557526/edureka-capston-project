#!/usr/bin/env bash
set -euo pipefail

export DEBIAN_FRONTEND=noninteractive
REPO_DIR="${REPO_DIR:-/home/ubuntu/enterprise-doc-agent}"
REPO_URL="${REPO_URL:-}"
APP_USER="${APP_USER:-ubuntu}"
OLLAMA_BASE_URL="${OLLAMA_BASE_URL:-http://127.0.0.1:11434}"
OLLAMA_MODEL="${OLLAMA_MODEL:-llama3}"
CHROMA_PERSIST_DIR="${CHROMA_PERSIST_DIR:-data/chroma}"
CHROMA_COLLECTION="${CHROMA_COLLECTION:-documents}"

sudo apt-get update
sudo apt-get install -y ca-certificates curl git nginx python3-pip python3-venv

if ! command -v ollama >/dev/null 2>&1; then
  curl -fsSL https://ollama.com/install.sh | sh
fi
sudo systemctl enable ollama
sudo systemctl start ollama

for i in {1..60}; do
  if curl -fsS "$OLLAMA_BASE_URL/api/tags" >/dev/null 2>&1; then
    break
  fi
  sleep 2
  if [ "$i" -eq 60 ]; then
    echo "Ollama API did not become ready at $OLLAMA_BASE_URL"
    sudo journalctl -u ollama --no-pager | tail -n 80 || true
    exit 1
  fi
done

ollama pull "$OLLAMA_MODEL"

sudo mkdir -p "$REPO_DIR"
sudo chown -R "$APP_USER:$APP_USER" "$REPO_DIR"

if [ -d "$REPO_DIR/.git" ]; then
  cd "$REPO_DIR"
  sudo -u "$APP_USER" git pull --ff-only || true
elif [ -n "$REPO_URL" ]; then
  sudo -u "$APP_USER" git clone "$REPO_URL" "$REPO_DIR"
  cd "$REPO_DIR"
else
  echo "REPO_URL is not set. Set REPO_URL or place the project files in $REPO_DIR before running this script."
  exit 1
fi

cd "$REPO_DIR"
if [ ! -f .env ]; then
  cp .env.example .env
fi

set_env_var() {
  local key="$1"
  local value="$2"
  if grep -q "^${key}=" .env; then
    sed -i "s#^${key}=.*#${key}=${value}#" .env
  else
    echo "${key}=${value}" >> .env
  fi
}

set_env_var "VECTOR_BACKEND" "chroma"
set_env_var "CHROMA_PERSIST_DIR" "$CHROMA_PERSIST_DIR"
set_env_var "CHROMA_COLLECTION" "$CHROMA_COLLECTION"
set_env_var "OLLAMA_BASE_URL" "$OLLAMA_BASE_URL"
set_env_var "OLLAMA_MODEL" "$OLLAMA_MODEL"

sudo -u "$APP_USER" python3 -m venv .venv
sudo -u "$APP_USER" bash -lc 'source .venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt'

sudo cp "$REPO_DIR/scripts/preload_minilm.sh" /usr/local/bin/preload_minilm.sh
sudo chmod +x /usr/local/bin/preload_minilm.sh
sudo -u "$APP_USER" APP_DIR="$REPO_DIR" USER_NAME="$APP_USER" /usr/local/bin/preload_minilm.sh

sudo cp "$REPO_DIR/nginx.conf" /etc/nginx/conf.d/enterprise-doc-agent.conf
sudo nginx -t
sudo systemctl restart nginx

sudo cp "$REPO_DIR/ec2-api.service" /etc/systemd/system/ec2-api.service
sudo cp "$REPO_DIR/ec2-streamlit.service" /etc/systemd/system/ec2-streamlit.service
sudo systemctl daemon-reload
sudo systemctl enable ec2-api.service ec2-streamlit.service
sudo systemctl restart ec2-api.service ec2-streamlit.service

echo "EC2 setup complete."
echo "API: http://$(curl -s ifconfig.me)/"
echo "Streamlit: http://$(curl -s ifconfig.me):8501/"
echo "Chroma persist dir: $CHROMA_PERSIST_DIR"
