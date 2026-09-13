# AWS EC2 deployment guide

## 1. Prepare the EC2 instance
Use an Ubuntu 22.04 or 24.04 instance with at least 2 vCPUs and 4 GB RAM.

Open these inbound ports:
- 80/tcp
- 443/tcp
- 8000/tcp
- 8501/tcp

## 2. Clone the project
```bash
git clone <your-repo-url>
cd enterprise-doc-agent
```

## 3. Run the setup script
```bash
chmod +x setup_ec2.sh
./setup_ec2.sh
```

## 4. Access the app
- API: http://<ec2-public-ip>/ 
- Streamlit UI: http://<ec2-public-ip>:8501/

## 5. Install Ollama on EC2 (mandatory)
Install Ollama on the same EC2 host where the API runs:
```bash
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl enable ollama
sudo systemctl start ollama
ollama --version
ollama pull llama3
curl http://127.0.0.1:11434/api/tags
```

Do not install Ollama only on your laptop when the app is hosted on EC2. The API must reach Ollama locally on that EC2 instance.

## 6. Production hardening
For production, add Nginx + HTTPS and replace the default authentication credentials.
