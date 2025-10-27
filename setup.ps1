# Complete Setup Script for Number Plate Detection System
# This script will set up the entire environment

Write-Host "===== Number Plate Detection System Setup =====" -ForegroundColor Cyan
Write-Host ""

# Check Python installation
Write-Host "[1/8] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python not found! Please install Python 3.8 or higher." -ForegroundColor Red
    exit 1
}

# Check Node.js installation
Write-Host "[2/8] Checking Node.js installation..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "✓ Found Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Node.js not found! Please install Node.js 16 or higher." -ForegroundColor Red
    exit 1
}

# Create virtual environment
Write-Host "[3/8] Creating Python virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists, skipping..." -ForegroundColor Gray
} else {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "[4/8] Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"
Write-Host "✓ Virtual environment activated" -ForegroundColor Green

# Install Python dependencies
Write-Host "[5/8] Installing Python dependencies..." -ForegroundColor Yellow
Write-Host "This may take several minutes..." -ForegroundColor Gray
pip install --upgrade pip
pip install -r requirements.txt
Write-Host "✓ Python dependencies installed" -ForegroundColor Green

# Clone YOLOv7 repository
Write-Host "[6/8] Setting up YOLOv7..." -ForegroundColor Yellow
if (Test-Path "external/yolov7") {
    Write-Host "YOLOv7 already exists, skipping..." -ForegroundColor Gray
} else {
    New-Item -ItemType Directory -Force -Path "external" | Out-Null
    git clone https://github.com/WongKinYiu/yolov7.git external/yolov7
    Write-Host "✓ YOLOv7 cloned successfully" -ForegroundColor Green
}

# Install frontend dependencies
Write-Host "[7/8] Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location frontend
npm install
Set-Location ..
Write-Host "✓ Frontend dependencies installed" -ForegroundColor Green

# Create necessary directories
Write-Host "[8/8] Creating necessary directories..." -ForegroundColor Yellow
$directories = @("models", "uploads", "logs", "data/plates/train", "data/plates/val", "data/plates/test")
foreach ($dir in $directories) {
    if (!(Test-Path $dir)) {
        New-Item -ItemType Directory -Force -Path $dir | Out-Null
    }
}
Write-Host "✓ Directories created" -ForegroundColor Green

# Create .env file
Write-Host ""
Write-Host "Creating .env file..." -ForegroundColor Yellow
if (!(Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env file created from .env.example" -ForegroundColor Green
    Write-Host "⚠ Please edit .env file with your configuration" -ForegroundColor Yellow
} else {
    Write-Host ".env file already exists" -ForegroundColor Gray
}

# Download YOLOv7 weights
Write-Host ""
Write-Host "Downloading YOLOv7 weights..." -ForegroundColor Yellow
if (!(Test-Path "models/yolov7.pt")) {
    Write-Host "Downloading from GitHub releases..." -ForegroundColor Gray
    $url = "https://github.com/WongKinYiu/yolov7/releases/download/v0.1/yolov7.pt"
    Invoke-WebRequest -Uri $url -OutFile "models/yolov7.pt"
    Write-Host "✓ YOLOv7 weights downloaded" -ForegroundColor Green
} else {
    Write-Host "Weights already exist, skipping..." -ForegroundColor Gray
}

# Initialize database
Write-Host ""
Write-Host "Initializing database..." -ForegroundColor Yellow
python -c "from backend.models import db; from backend.app import app; app.app_context().push(); db.create_all(); print('Database initialized')"
Write-Host "✓ Database initialized" -ForegroundColor Green

Write-Host ""
Write-Host "===== Setup Complete! =====" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env file with your configuration" -ForegroundColor White
Write-Host "2. Run './start.ps1' to start the application" -ForegroundColor White
Write-Host "3. Visit http://localhost:5173 for the frontend" -ForegroundColor White
Write-Host "4. Backend API runs at http://localhost:5000" -ForegroundColor White
Write-Host ""
