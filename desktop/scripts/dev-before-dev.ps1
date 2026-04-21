$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$backendDir = Join-Path $repoRoot "backend"
$frontendDir = Join-Path $repoRoot "frontend"
$backendPython = Join-Path $backendDir ".venv\Scripts\python.exe"

if (-not (Test-Path $backendPython)) {
    throw "Backend virtual environment was not found at $backendPython. Run the backend setup first."
}

$backendCheck = Test-NetConnection -ComputerName 127.0.0.1 -Port 8765 -InformationLevel Quiet
if (-not $backendCheck) {
    Start-Process -FilePath "powershell.exe" -ArgumentList @(
        "-NoExit",
        "-ExecutionPolicy",
        "Bypass",
        "-Command",
        "Set-Location '$backendDir'; .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8765"
    ) | Out-Null
    Start-Sleep -Seconds 2
}

npm.cmd --prefix $frontendDir run dev
