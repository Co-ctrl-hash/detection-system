#!/bin/bash

# Setup script for Linux/Mac
echo "===== Number Plate Detection System Setup ====="
echo ""

# Check Python installation
echo "[1/8] Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✓ Found: $PYTHON_VERSION"
else
    echo "✗ Python not found! Please install Python 3.8 or higher."
    exit 1
fi

# Check Node.js installation
echo "[2/8] Checking Node.js installation..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✓ Found Node.js: $NODE_VERSION"
else
    echo "✗ Node.js not found! Please install Node.js 16 or higher."
    exit 1
fi

# Create virtual environment
echo "[3/8] Creating Python virtual environment..."
if [ -d "venv" ]; then
    echo "Virtual environment already exists, skipping..."
else
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate virtual environment
echo "[4/8] Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"

# Install Python dependencies
echo "[5/8] Installing Python dependencies..."
echo "This may take several minutes..."
pip install --upgrade pip
pip install -r requirements.txt
echo "✓ Python dependencies installed"

# Clone YOLOv7 repository
echo "[6/8] Setting up YOLOv7..."
if [ -d "external/yolov7" ]; then
    echo "YOLOv7 already exists, skipping..."
else
    mkdir -p external
    git clone https://github.com/WongKinYiu/yolov7.git external/yolov7
    echo "✓ YOLOv7 cloned successfully"
fi

# Install frontend dependencies
echo "[7/8] Installing frontend dependencies..."
cd frontend
npm install
cd ..
echo "✓ Frontend dependencies installed"

# Create necessary directories
echo "[8/8] Creating necessary directories..."
mkdir -p models uploads logs data/plates/train data/plates/val data/plates/test
echo "✓ Directories created"

# Create .env file
echo ""
echo "Creating .env file..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ .env file created from .env.example"
    echo "⚠ Please edit .env file with your configuration"
else
    echo ".env file already exists"
fi

# Download YOLOv7 weights
echo ""
echo "Downloading YOLOv7 weights..."
if [ ! -f "models/yolov7.pt" ]; then
    echo "Downloading from GitHub releases..."
    curl -L "https://github.com/WongKinYiu/yolov7/releases/download/v0.1/yolov7.pt" -o "models/yolov7.pt"
    echo "✓ YOLOv7 weights downloaded"
else
    echo "Weights already exist, skipping..."
fi

# Initialize database
echo ""
echo "Initializing database..."
python3 -c "from backend.models import db; from backend.app import app; app.app_context().push(); db.create_all(); print('Database initialized')"
echo "✓ Database initialized"

echo ""
echo "===== Setup Complete! ====="
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Run './start.sh' to start the application"
echo "3. Visit http://localhost:5173 for the frontend"
echo "4. Backend API runs at http://localhost:5000"
echo ""
