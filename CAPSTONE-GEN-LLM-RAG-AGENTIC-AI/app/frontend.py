from fastapi import FastAPI
from fastapi.responses import HTMLResponse


def get_frontend_page() -> HTMLResponse:
    html = """
    <!DOCTYPE html>
    <html lang=\"en\">
    <head>
        <meta charset=\"UTF-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
        <title>Enterprise Document QA</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 2rem; background: #f4f7fb; }
            .card { max-width: 900px; margin: auto; background: white; padding: 2rem; border-radius: 12px; box-shadow: 0 6px 20px rgba(0,0,0,0.08); }
            input, button, textarea { width: 100%; padding: 0.8rem; margin-top: 0.7rem; border-radius: 8px; border: 1px solid #cbd5e1; }
            button { background: #2563eb; color: white; cursor: pointer; }
            pre { background: #f8fafc; padding: 1rem; border-radius: 8px; white-space: pre-wrap; }
        </style>
    </head>
    <body>
        <div class=\"card\">
            <h1>Enterprise Document QA Agent</h1>
            <p>Upload a document and ask questions using the local RAG pipeline.</p>
            <input id=\"file\" type=\"file\" />
            <button onclick=\"uploadFile()\">Upload</button>
            <textarea id=\"query\" rows=\"4\" placeholder=\"Ask a question about the uploaded documents\"></textarea>
            <button onclick=\"askQuestion()\">Ask</button>
            <pre id=\"result\">Results will appear here.</pre>
        </div>
        <script>
            async function uploadFile() {
                const fileInput = document.getElementById('file');
                const file = fileInput.files[0];
                if (!file) return alert('Select a file first');
                const formData = new FormData();
                formData.append('file', file);
                const response = await fetch('/upload', { method: 'POST', body: formData });
                const data = await response.json();
                document.getElementById('result').textContent = JSON.stringify(data, null, 2);
            }
            async function askQuestion() {
                const query = document.getElementById('query').value;
                const response = await fetch('/query', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ query })
                });
                const data = await response.json();
                document.getElementById('result').textContent = JSON.stringify(data, null, 2);
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(html)
