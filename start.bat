@echo off
REM Quick Start Script for AEON Retail Analytics Platform
REM Windows Batch File

echo ========================================
echo  AEON Retail Analytics Platform
echo ========================================
echo.

REM Start Backend
echo Starting Backend Server...
start "Backend Server" cmd /k "cd backend && python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

REM Wait for backend to start
timeout /t 3 /nobreak > nul

REM Start Frontend
echo Starting Frontend Development Server...
start "Frontend Server" cmd /k "npm run dev"

echo.
echo ========================================
echo Services are starting...
echo.
echo Backend API:  http://localhost:8000/api/docs
echo Frontend UI:  http://localhost:5173
echo Health Check: http://localhost:8000/api/health
echo ========================================
echo.
echo Press any key to exit...
pause > nul
