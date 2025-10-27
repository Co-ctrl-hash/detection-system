# Quick Start Script for Full-Stack Number Plate Detection System
# Run this script to start both backend and frontend servers

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Number Plate Detection System Startup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "Virtual environment not found. Please run setup first:" -ForegroundColor Yellow
    Write-Host "  python -m venv .venv" -ForegroundColor Yellow
    Write-Host "  .\.venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "  pip install -r requirements.txt" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment
Write-Host "[1/4] Activating virtual environment..." -ForegroundColor Green
& ".\.venv\Scripts\Activate.ps1"

# Check if database exists
if (-not (Test-Path "plates.db")) {
    Write-Host "[2/4] Initializing database..." -ForegroundColor Green
    python -c "from backend.app import app, db; app.app_context().push(); db.create_all(); print('Database initialized successfully')"
} else {
    Write-Host "[2/4] Database already exists, skipping initialization" -ForegroundColor Green
}

# Start backend in a new window
Write-Host "[3/4] Starting backend server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD'; .\.venv\Scripts\Activate.ps1; Write-Host 'Starting Flask Backend...' -ForegroundColor Cyan; python backend\app.py"

# Wait a bit for backend to start
Start-Sleep -Seconds 3

# Start frontend in a new window
Write-Host "[4/4] Starting frontend server..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PWD\frontend'; Write-Host 'Starting React Frontend...' -ForegroundColor Cyan; npm run dev"

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "System Starting..." -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend:  http://localhost:5000" -ForegroundColor Yellow
Write-Host "Frontend: http://localhost:3000" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C in each window to stop servers" -ForegroundColor Gray
Write-Host ""

# Wait for user input
Read-Host "Press Enter to exit this window"
