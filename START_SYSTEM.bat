@echo off
REM PERMANENT FIX - Start Backend and Frontend

echo ========================================
echo Starting VAJRA System - Backend & Frontend
echo ========================================
echo.

REM Kill any existing processes
taskkill /F /IM python.exe 2>nul
taskkill /F /IM node.exe 2>nul
timeout /t 2 /nobreak

REM Start Backend in new window
echo Starting Backend on Port 9000...
start "Backend - Port 9000" cmd /k "cd backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 9000 --workers 1"

REM Wait for backend to start
timeout /t 4 /nobreak

REM Start Frontend in new window
echo Starting Frontend on Port 5173...
start "Frontend - Port 5173" cmd /k "cd frontend && npm run dev"

REM Wait for frontend
timeout /t 3 /nobreak

REM Open browser
echo Opening browser...
start http://localhost:5173

echo.
echo ========================================
echo System Started!
echo ========================================
echo Backend:  http://127.0.0.1:9000
echo Frontend: http://localhost:5173
echo.
echo DO NOT CLOSE THESE WINDOWS!
echo ========================================
