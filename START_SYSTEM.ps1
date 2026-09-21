# PERMANENT FIX - Start Backend and Frontend

Write-Host "========================================"
Write-Host "Starting VAJRA System - Backend & Frontend"
Write-Host "========================================"
Write-Host ""

# Kill any existing processes
Write-Host "Cleaning up old processes..."
Get-Process | Where-Object {$_.ProcessName -match "python|node"} | Stop-Process -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start Backend
Write-Host "Starting Backend on Port 9000..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; python -m uvicorn app.main:app --host 127.0.0.1 --port 9000 --workers 1"
Start-Sleep -Seconds 4

# Start Frontend
Write-Host "Starting Frontend on Port 5173..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"
Start-Sleep -Seconds 3

# Open Browser
Write-Host "Opening browser..."
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "========================================"
Write-Host "✅ System Started!"
Write-Host "========================================"
Write-Host "Backend:  http://127.0.0.1:9000"
Write-Host "Frontend: http://localhost:5173"
Write-Host ""
Write-Host "⚠️  DO NOT CLOSE THE BACKEND/FRONTEND WINDOWS!"
Write-Host "========================================"
