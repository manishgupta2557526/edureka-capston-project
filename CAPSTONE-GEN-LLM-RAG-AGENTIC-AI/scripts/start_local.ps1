param(
    [string]$HostAddress = "127.0.0.1",
    [int]$ApiPort = 8000,
    [int]$UiPort = 8501,
    [bool]$RequireOllama = $true,
    [string]$OllamaBaseUrl = "http://127.0.0.1:11434",
    [string]$OllamaModel = "llama3",
    [int]$OllamaRequestTimeoutSeconds = 180,
    [string]$ChromaPersistDir = "data/chroma",
    [string]$ChromaCollection = "documents"
)

$ProjectRoot = Split-Path -Parent $PSScriptRoot
$PythonPath = Join-Path $ProjectRoot ".venv\Scripts\python.exe"

function Resolve-OllamaCommand {
    $cmd = Get-Command ollama -ErrorAction SilentlyContinue
    if ($cmd) {
        return $cmd.Source
    }

    $candidatePaths = @(
        (Join-Path $env:LOCALAPPDATA "Programs\Ollama\ollama.exe"),
        "C:\Program Files\Ollama\ollama.exe"
    )

    foreach ($path in $candidatePaths) {
        if (Test-Path $path) {
            return $path
        }
    }

    $uninstallKeys = @(
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*"
    )

    try {
        $entry = Get-ItemProperty $uninstallKeys -ErrorAction SilentlyContinue |
            Where-Object { $_.DisplayName -like "*Ollama*" -and $_.InstallLocation } |
            Select-Object -First 1

        if ($entry) {
            $exe = Join-Path $entry.InstallLocation "ollama.exe"
            if (Test-Path $exe) {
                return $exe
            }
        }
    } catch {
        # Ignore registry lookup errors and report a single actionable error below.
    }

    return $null
}

if (-not (Test-Path $PythonPath)) {
    Write-Error "Python virtual environment not found at $PythonPath. Create it with: python -m venv .venv"
    exit 1
}

if ($RequireOllama) {
    $OllamaCommand = Resolve-OllamaCommand
    if (-not $OllamaCommand) {
        Write-Error "Ollama is required. Install from https://ollama.com/download, then open a new terminal and try again."
        exit 1
    }

    $OllamaDir = Split-Path -Parent $OllamaCommand
    if (-not (($env:Path -split ';') -contains $OllamaDir)) {
        $env:Path = "$OllamaDir;$env:Path"
    }

    $ollamaReady = $false
    try {
        $null = Invoke-RestMethod -Uri "$OllamaBaseUrl/api/tags" -Method Get -TimeoutSec 3
        $ollamaReady = $true
    } catch {
        Write-Host "Starting Ollama service..."
        Start-Process -FilePath $OllamaCommand -ArgumentList "serve" -WindowStyle Hidden | Out-Null
    }

    if (-not $ollamaReady) {
        for ($attempt = 1; $attempt -le 40; $attempt++) {
            try {
                $null = Invoke-RestMethod -Uri "$OllamaBaseUrl/api/tags" -Method Get -TimeoutSec 3
                $ollamaReady = $true
                break
            } catch {
                Start-Sleep -Seconds 1
            }
        }
    }

    if (-not $ollamaReady) {
        Write-Error "Ollama API did not become available at $OllamaBaseUrl."
        exit 1
    }

    Write-Host "Ensuring Ollama model is installed: $OllamaModel"
    & $OllamaCommand pull $OllamaModel | Out-Null
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Failed to pull Ollama model $OllamaModel."
        exit 1
    }
}

$env:PYTHONPATH = $ProjectRoot
$env:VECTOR_BACKEND = "chroma"
$env:CHROMA_PERSIST_DIR = $ChromaPersistDir
$env:CHROMA_COLLECTION = $ChromaCollection
$env:OLLAMA_BASE_URL = $OllamaBaseUrl
$env:OLLAMA_MODEL = $OllamaModel
$env:OLLAMA_REQUEST_TIMEOUT_SECONDS = "$OllamaRequestTimeoutSeconds"

$apiProcess = Start-Process -FilePath $PythonPath -WorkingDirectory $ProjectRoot -ArgumentList '-m','uvicorn','app.main:app','--host',$HostAddress,'--port',"$ApiPort" -PassThru
$uiProcess = Start-Process -FilePath $PythonPath -WorkingDirectory $ProjectRoot -ArgumentList '-m','streamlit','run','app/streamlit_app.py','--server.address',$HostAddress,'--server.port',"$UiPort" -PassThru

Write-Host "Chroma persist dir: $ChromaPersistDir"
Write-Host "Chroma collection: $ChromaCollection"
if ($RequireOllama) {
    Write-Host "Ollama endpoint: $OllamaBaseUrl"
    Write-Host "Ollama model: $OllamaModel"
    Write-Host "Ollama request timeout (s): $OllamaRequestTimeoutSeconds"
}
Write-Host "Started API PID: $($apiProcess.Id)"
Write-Host "Started Streamlit PID: $($uiProcess.Id)"
Write-Host "API URL: http://${HostAddress}:$ApiPort/"
Write-Host "Streamlit URL: http://${HostAddress}:$UiPort/"
