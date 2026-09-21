# VAJRA TATVA - Database Setup Script
# Windows PowerShell

Write-Host "[SETUP] VAJRA TATVA Database Setup" -ForegroundColor Cyan
Write-Host ""

# Check if alembic is installed
$alembicCheck = python -c "import alembic; print('OK')" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Alembic not installed. Installing..." -ForegroundColor Red
    pip install alembic
}

# Run migrations
Write-Host "[INFO] Running database migrations..." -ForegroundColor Yellow
alembic upgrade head

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[SUCCESS] Database setup complete!" -ForegroundColor Green
    Write-Host "[SUCCESS] All tables created successfully." -ForegroundColor Green
    Write-Host ""
    Write-Host "[INFO] You can now start the server with: .\start_server.ps1" -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "[ERROR] Database migration failed!" -ForegroundColor Red
    Write-Host "[INFO] Please check your DATABASE_URL in .env file" -ForegroundColor Yellow
}
