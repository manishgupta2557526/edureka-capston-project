# Production-Grade EC2 Setup Guide for Ubuntu

This guide is written for Ubuntu 22.04 or 24.04 EC2 and is designed to be copy-pasted directly into the terminal.

## 1) Launch an EC2 instance
Use an Ubuntu instance with:
- 2 vCPUs or more
- 4 GB RAM or more
- Security group allowing inbound TCP 22, 80, 443, 8000, 8501

## 2) Connect to the instance
```bash
ssh ubuntu@YOUR_EC2_PUBLIC_IP
```

## 3) Run the one-command deployment
```bash
sudo apt-get update
sudo apt-get install -y git curl
cd ~
git clone YOUR_REPOSITORY_URL enterprise-doc-agent
cd enterprise-doc-agent
REPO_URL=YOUR_REPOSITORY_URL bash deploy_ec2.sh
```

If you already copied the project files to the instance, run:
```bash
cd ~/enterprise-doc-agent
REPO_DIR=/home/ubuntu/enterprise-doc-agent bash deploy_ec2.sh
```

The deployment now configures a local persistent ChromaDB store on EC2 as part of setup.

## 3.1) Install and verify Ollama on EC2 (mandatory)
Install Ollama on the EC2 instance itself:
```bash
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl enable ollama
sudo systemctl start ollama
ollama --version
ollama pull llama3
curl http://127.0.0.1:11434/api/tags
```

Note: Do not install Ollama on your local laptop if the app is running on EC2. It must run on the same host as the API service.

## 4) Expected results
- Nginx is installed and configured
- FastAPI runs on port 8000
- Streamlit runs on port 8501
- Ollama runs on the EC2 host at port 11434
- The app is reachable through the EC2 public IP
- The local MiniLM embedding model runs on the EC2 instance without requiring any paid embedding API
- The deployment scripts now preload the MiniLM model during EC2 provisioning so the first application boot is much faster
- The implementation is compatible with AWS EC2 because it uses local embedding + local ChromaDB storage and does not depend on paid services

## 5) Verify the deployment
```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8501/
grep CHROMA_ /home/ubuntu/enterprise-doc-agent/.env
curl http://127.0.0.1:11434/api/tags
ollama list
```

Expected output:
- health endpoint returns JSON with `{"status":"ok"}`
- Streamlit returns HTML content
- `.env` includes `CHROMA_PERSIST_DIR` and `CHROMA_COLLECTION`
- Ollama tags/list output includes `llama3`

## 6) Useful commands
```bash
sudo systemctl status ec2-api.service --no-pager
sudo systemctl status ec2-streamlit.service --no-pager
sudo journalctl -u ec2-api.service -f
sudo journalctl -u ec2-streamlit.service -f
sudo systemctl restart ec2-api.service ec2-streamlit.service
```

## 7) Production hardening suggestions
For a stronger production deployment, add:
- HTTPS with Let’s Encrypt or ACM
- backup strategy for `data/chroma` persistence
- stronger authentication and secrets management
- TLS termination and security headers
