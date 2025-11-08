# AEON Retail Analytics Platform - Quick Start Script
# Windows PowerShell

Write-Host "🚀 Starting AEON Retail Analytics Platform..." -ForegroundColor Cyan
Write-Host ""

# Check Python version
Write-Host "Checking Python version..." -ForegroundColor Yellow
python --version

# Start Backend
Write-Host ""
Write-Host "📦 Starting Backend Server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\backend'; python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "🎨 Starting Frontend Development Server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; npm run dev"

Write-Host ""
Write-Host "✅ Services Starting..." -ForegroundColor Green
Write-Host ""
Write-Host "📍 Backend API: http://localhost:8000/api/docs" -ForegroundColor Cyan
Write-Host "📍 Frontend UI: http://localhost:5173" -ForegroundColor Cyan
Write-Host "📍 Health Check: http://localhost:8000/api/health" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
