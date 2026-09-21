# VAJRA TATVA - Server Startup Script
# Windows PowerShell

Write-Host "[STARTUP] VAJRA TATVA Network Security Auditor" -ForegroundColor Cyan
Write-Host "[STARTUP] Starting backend server..." -ForegroundColor Cyan

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "[INFO] Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "[WARNING] No virtual environment found. Using global Python." -ForegroundColor Yellow
}

# Check if .env exists
if (-not (Test-Path ".env")) {
    Write-Host "[WARNING] .env file not found. Copying from .env.example..." -ForegroundColor Yellow
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "[SUCCESS] Created .env file. Please configure it!" -ForegroundColor Green
    }
}

# Start server
Write-Host "[STARTUP] Starting Uvicorn server on http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "[INFO] API Documentation: http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host "[INFO] Press CTRL+C to stop the server" -ForegroundColor Yellow
Write-Host ""

python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
