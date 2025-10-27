# Quick Setup and Run Guide

## Prerequisites Check
- Python 3.8+ installed
- Node.js 16+ installed
- Git installed

## Fast Setup (10 minutes)

### 1. Run Automated Setup
```powershell
# Navigate to project directory
cd "c:\Users\HP\Desktop\new project"

# Run setup script
.\setup.ps1
```

This will:
- Create Python virtual environment
- Install all Python dependencies
- Clone YOLOv7 repository
- Install frontend dependencies
- Download YOLOv7 weights
- Initialize database
- Create necessary directories

### 2. Manual Setup (if automated fails)

#### Backend Setup:
```powershell
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Clone YOLOv7
git clone https://github.com/WongKinYiu/yolov7.git external/yolov7

# Download weights
New-Item -ItemType Directory -Force -Path models
Invoke-WebRequest -Uri "https://github.com/WongKinYiu/yolov7/releases/download/v0.1/yolov7.pt" -OutFile "models/yolov7.pt"

# Initialize database
python -c "from backend.models import db; from backend.app import app; app.app_context().push(); db.create_all()"
```

#### Frontend Setup:
```powershell
cd frontend
npm install
cd ..
```

### 3. Configure Environment
```powershell
# Create .env file
Copy-Item .env.example .env

# Edit .env file (optional)
notepad .env
```

### 4. Run the Application

#### Option A: Using Start Script (Recommended)
```powershell
.\start.ps1
```

This opens two windows:
- Backend server (Flask API) on http://localhost:5000
- Frontend app (React) on http://localhost:5173

#### Option B: Manual Start
```powershell
# Terminal 1 - Start Backend
.\venv\Scripts\Activate.ps1
python backend/app.py

# Terminal 2 - Start Frontend
cd frontend
npm run dev
```

### 5. Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:5000
- **API Docs**: http://localhost:5000/api/detections

## Quick Test

### Test Upload Detection:
1. Go to http://localhost:5173
2. Click "Upload File" tab
3. Upload an image with a license plate
4. View detection results

### Test Live Detection:
1. Click "Live Detection" tab
2. Allow camera access
3. Show a license plate to the camera
4. See real-time detection

## Troubleshooting

### Import Errors (cv2, torch, flask_sqlalchemy, etc.)
**Solution**: Activate virtual environment
```powershell
.\venv\Scripts\Activate.ps1
```

### "YOLOv7 not found"
**Solution**: Clone YOLOv7
```powershell
git clone https://github.com/WongKinYiu/yolov7.git external/yolov7
```

### "Model weights not found"
**Solution**: Download weights
```powershell
Invoke-WebRequest -Uri "https://github.com/WongKinYiu/yolov7/releases/download/v0.1/yolov7.pt" -OutFile "models/yolov7.pt"
```

### Frontend doesn't connect to backend
**Solution**: Check if backend is running on port 5000
```powershell
# Check if port is in use
netstat -ano | findstr :5000
```

### Database errors
**Solution**: Reinitialize database
```powershell
python -c "from backend.models import db; from backend.app import app; app.app_context().push(); db.drop_all(); db.create_all()"
```

## Next Steps

1. **Train Custom Model**: See `docs/TRAINING.md`
2. **Deploy to Production**: See `DEPLOYMENT.md`
3. **API Integration**: See `README.md` API section
4. **Contribute**: See `CONTRIBUTING.md`

## Command Reference

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run backend only
python backend/app.py

# Run frontend only
cd frontend; npm run dev

# Run both (automated)
.\start.ps1

# Install new Python package
pip install package-name
pip freeze > requirements.txt

# Install new frontend package
cd frontend
npm install package-name

# Run tests
python -m pytest tests/

# Build frontend for production
cd frontend
npm run build
```

## Project Structure
```
new project/
├── backend/           # Flask API server
├── frontend/          # React application
├── src/              # Python utilities
├── models/           # YOLOv7 weights
├── external/yolov7/  # YOLOv7 repository
├── data/             # Datasets
├── docker/           # Docker configs
└── docs/             # Documentation
```

## Support

- **Documentation**: Check `README.md` and `docs/` folder
- **Issues**: Create issue on GitHub
- **Quick fixes**: See `QUICKSTART.md`
