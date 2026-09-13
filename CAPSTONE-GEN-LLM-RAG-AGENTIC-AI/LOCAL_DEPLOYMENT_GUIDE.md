# Local Deployment Guide for Non-Technical Users

This guide explains how to install and run the project on your own computer step by step.

## 1. Install Python
If Python is not already installed:
1. Go to https://www.python.org/downloads/
2. Download Python 3.10 or newer
3. Install it and make sure the box “Add Python to PATH” is checked

To check if Python is installed:
```bash
python --version
```

## 2. Install Git (optional but recommended)
If Git is not installed:
1. Go to https://git-scm.com/downloads
2. Download and install Git

To check:
```bash
git --version
```

## 2.1 Install Ollama (required)
This project requires Ollama for answer generation.

1. Install from https://ollama.com/download
2. Verify installation:
```bash
ollama --version
```
If Windows says `ollama` is not recognized, run this in PowerShell and retry:
```powershell
$env:Path = "C:\Users\$env:USERNAME\AppData\Local\Programs\Ollama;$env:Path"
ollama --version
```
3. Pull the required model:
```bash
ollama pull llama3
```

On Windows/macOS:
1. Install Docker Desktop from https://www.docker.com/products/docker-desktop/
2. Start Docker Desktop and wait until it shows as running

To check from terminal:
```bash
docker --version
```

## 3. Download the Project
Option A: If you have Git
```bash
git clone <your-repository-url>
cd <project-folder>
```

Option B: If you received the project files as a ZIP
1. Extract the ZIP file
2. Open the extracted folder in File Explorer or VS Code

## 4. Open the Project Folder
Open the project folder in VS Code or any terminal window.

## 5. Create a Virtual Environment
Run this in the project folder:

On Windows:
```bash
python -m venv .venv
.venv\Scripts\activate
```

On macOS/Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 6. Install Project Dependencies
Run:
```bash
pip install -r requirements.txt
```

This may take a few minutes.

## 7. Start the Full Stack (ChromaDB + Ollama + API + Streamlit)
Fast one-line startup on Windows:
```powershell
powershell -ExecutionPolicy Bypass -File scripts/start_local.ps1
```

If your terminal is already inside the `scripts` folder:
```powershell
powershell -ExecutionPolicy Bypass -File .\start_local.ps1
```

If PowerShell blocks script execution in that terminal session, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Or run services manually as below.

What this script does:
- Sets `VECTOR_BACKEND=chroma`
- Sets ChromaDB persistence settings
- Starts or validates Ollama API availability
- Pulls and validates required model (`llama3` by default)
- Sets `OLLAMA_REQUEST_TIMEOUT_SECONDS` for model generation requests
- Starts FastAPI and Streamlit
- Auto-detects `ollama.exe` from common install paths if PATH is stale

### Optional script parameters
```powershell
powershell -ExecutionPolicy Bypass -File scripts/start_local.ps1 -ApiPort 8001 -UiPort 8502 -ChromaPersistDir data/chroma -ChromaCollection documents -OllamaModel llama3 -OllamaRequestTimeoutSeconds 240
```

If clicking Run RAG times out during first model response, increase `-OllamaRequestTimeoutSeconds` (for example, 240 or 300).

Run:
```bash
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

After it starts, open your browser and go to:
```text
http://127.0.0.1:8000/
```

You should see the API landing page.

## 8. Start the Streamlit UI
Open a second terminal window, go to the project folder, and run:
```bash
streamlit run app/streamlit_app.py --server.address 127.0.0.1 --server.port 8501
```

Then open:
```text
http://127.0.0.1:8501/
```

## 9. Use the Application
1. Open `http://127.0.0.1:8501/` in your browser.
2. Log in with default credentials:
	- Username: `admin`
	- Password: `admin123`
3. Drag and drop or browse and select a supported file type:
	- `pdf`, `txt`, `md`, `json`, `yaml`, `yml`, `xml`, `csv`, `xlsx`, `xls`
4. Click `Upload and index` and wait for the success message.
5. Type your question in `Ask a question about your documents`.
6. Click `Run RAG`.
7. Review the output sections:
	- `Answer`
	- `Retrieved context` (with similarity scores)
	- `Sources`
8. Scroll down to `Chat history` to see previous interactions.

The retrieval layer uses sentence-transformer embeddings with ChromaDB, so questions written in different words can still surface the right document chunks more reliably than keyword-only systems.

## 10. Common Problems and Fixes
### Problem: Python is not recognized
Install Python again and make sure “Add Python to PATH” is checked.

### Problem: pip install fails
Try upgrading pip first:
```bash
python -m pip install --upgrade pip
```

### Problem: Port already in use
Close the other running app or use a different port.

### Problem: The app does not open in the browser
Check that the terminal shows the server is running and that the URL is correct.

### Problem: ollama is not recognized
1. Open a new terminal and run `ollama --version`.
2. If still failing on Windows, run:
```powershell
$env:Path = "C:\Users\$env:USERNAME\AppData\Local\Programs\Ollama;$env:Path"
```
3. Re-run:
```powershell
ollama --version
```

## 11. Ollama Requirement
Ollama is mandatory for this application.
1. Install Ollama from https://ollama.com/
2. Ensure Ollama can run on your machine
3. Ensure model `llama3` is available (the startup script does this automatically)

If Ollama is unavailable, the app will stop at startup by design.

## 12. Stopping the App
In the terminal window where the app is running:
- Press Ctrl+C to stop it.
